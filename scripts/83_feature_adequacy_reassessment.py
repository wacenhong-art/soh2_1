"""Frozen raw-signal feature adequacy audit (F1 is the only leakage-safe set)."""
from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from scipy.io import loadmat
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "feature_adequacy_reassessment_v1"
RAW = ROOT / "data" / "raw_mat"; HF_CSV = ROOT / "data" / "hf_csv"
BATTERIES = ("B0007", "B0018"); HF = ("HF1", "HF2", "HF3")
RAW_FEATURES = ("DISCHARGE_DURATION_S", "DISCHARGE_V4P0_TO_V3P6_S", "DISCHARGE_VOLTAGE_MEAN_V", "DISCHARGE_VOLTAGE_STD_V", "DISCHARGE_TEMPERATURE_MEAN_C", "DISCHARGE_TEMPERATURE_STD_C", "DISCHARGE_ENERGY_WH")
TRAIN_END = {"B0007": 33, "B0018": 25}; VALIDATION_END = {"B0007": 67, "B0018": 51}; ALPHA = {"B0007": 10.0, "B0018": 1.0}
SEEDS = (42, 123, 2024, 3407, 7777); HIDDEN = 32; LR = 0.001; WD = 1e-5; EPOCHS = 300; PATIENCE = 50
TEST_LOADED = False


def vector(block, field: str) -> np.ndarray:
    # `block` is already the scalar MATLAB struct after `[0, 0]`; indexing the
    # field again would select a scalar sample rather than its full waveform.
    return np.asarray(block[field]).squeeze().astype(float)


def old_hf_valid(charge) -> bool:
    """Use old formula only to retain the same row eligibility; never smooth it."""
    v, i, t = vector(charge, "Voltage_measured"), vector(charge, "Current_measured"), vector(charge, "Time")
    idx42 = np.flatnonzero(v >= 4.2)[0]
    if idx42 <= 0: raise ValueError("invalid CC segment")
    post = np.flatnonzero(np.abs(i[idx42:]) <= .02)
    if not len(post): raise ValueError("no CV cutoff")
    idx38, idx40 = np.flatnonzero(v >= 3.8)[0], np.flatnonzero(v >= 4.0)[0]
    _ = (t[idx42]-t[0], t[idx42+post[0]]-t[idx42], t[idx40]-t[idx38])
    return True


def discharge_features(discharge) -> dict[str, float]:
    v, i, temp, t = (vector(discharge, name) for name in ("Voltage_measured", "Current_measured", "Temperature_measured", "Time"))
    if min(len(v), len(i), len(temp), len(t)) < 2: raise ValueError("short discharge waveform")
    first4 = np.flatnonzero(v <= 4.0)
    if not len(first4): raise ValueError("no 4.0V downcrossing")
    idx4 = int(first4[0]); later36 = np.flatnonzero(v[idx4:] <= 3.6)
    if not len(later36): raise ValueError("no 3.6V downcrossing")
    idx36 = idx4 + int(later36[0])
    return {
        "DISCHARGE_DURATION_S": float(t[-1] - t[0]),
        "DISCHARGE_V4P0_TO_V3P6_S": float(t[idx36] - t[idx4]),
        "DISCHARGE_VOLTAGE_MEAN_V": float(np.mean(v)), "DISCHARGE_VOLTAGE_STD_V": float(np.std(v)),
        "DISCHARGE_TEMPERATURE_MEAN_C": float(np.mean(temp)), "DISCHARGE_TEMPERATURE_STD_C": float(np.std(temp)),
        "DISCHARGE_ENERGY_WH": float(abs(np.trapezoid(v * np.abs(i), t)) / 3600.0),
    }


def extract_prefix_raw(battery: str, limit: int) -> pd.DataFrame:
    """Traverse only enough raw cycles to emit the frozen train+validation prefix."""
    container = loadmat(RAW / f"{battery}.mat")
    cycles = container[battery][0, 0]["cycle"][0]; rows = []
    for idx, cycle in enumerate(cycles):
        if str(cycle["type"][0]) != "charge": continue
        try:
            charge = cycle["data"][0, 0]; old_hf_valid(charge)
            discharge_idx = next(j for j in range(idx, len(cycles)) if str(cycles[j]["type"][0]) == "discharge")
            # The next discharge is part of the same completed cycle; stop before later records.
            discharge = cycles[discharge_idx]["data"][0, 0]
            record = discharge_features(discharge)
            record["SOH"] = float(vector(discharge, "Capacity")) / 2.0
            record["RawChargeCycleIndex"] = idx; record["RawDischargeCycleIndex"] = discharge_idx
            rows.append(record)
        except (IndexError, StopIteration, ValueError, KeyError):
            continue
        if len(rows) >= limit: break
    if len(rows) != limit: raise RuntimeError(f"{battery}: only {len(rows)} valid prefix records, expected {limit}")
    return pd.DataFrame(rows)


def load_feature_sets(battery: str) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    end = VALIDATION_END[battery]
    raw = extract_prefix_raw(battery, end)
    old = pd.read_csv(HF_CSV / f"{battery}_hf.csv", nrows=end)[list(HF) + ["SOH"]].apply(pd.to_numeric, errors="coerce").reset_index(drop=True)
    if len(old) != end or not np.allclose(old.SOH.to_numpy(float), raw.SOH.to_numpy(float), atol=1e-6, rtol=0):
        raise RuntimeError(f"{battery}: old-HF and raw prefix SOH alignment failed")
    f0 = old[list(HF)].copy(); f1 = raw[list(RAW_FEATURES)].copy(); f2 = pd.concat((f0, f1), axis=1)
    return {"F0_LEGACY_HF": f0, "F1_RAW_HEALTH": f1, "F2_LEGACY_PLUS_RAW": f2}, raw


def metrics(y: np.ndarray, p: np.ndarray) -> dict[str, float | int]:
    y, p = np.asarray(y, float), np.asarray(p, float); e = p-y
    return {"RMSE": float(np.sqrt(mean_squared_error(y, p))), "MAE": float(mean_absolute_error(y, p)),
            "MAPE": float(np.mean(np.abs(e/y))*100), "R2": float(r2_score(y, p)), "PredictionBias": float(e.mean()),
            "PredictionStd": float(p.std()), "WorstAbsoluteError": float(np.max(np.abs(e))),
            "CatastrophicCount": int(np.count_nonzero((p < 50.) | (p > 110.)))}


def impute_scale(x_fit: np.ndarray, y_fit: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
    median = np.nanmedian(x_fit, axis=0); median[~np.isfinite(median)] = 0.
    filled = np.where(np.isfinite(x_fit), x_fit, median)
    mean, std = filled.mean(0), filled.std(0); std[std < 1e-8] = 1.
    return median, mean, std, float(y_fit.mean()), max(float(y_fit.std()), 1e-8)


def transform(x: np.ndarray, median: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return ((np.where(np.isfinite(x), x, median)-mean)/std).astype(np.float32)


def ridge_predict(x_fit, y_fit, x_eval, alpha):
    median, mean, std, ym, ys = impute_scale(x_fit, y_fit); model = Ridge(alpha=alpha).fit(transform(x_fit, median, mean, std), (y_fit-ym)/ys)
    return model.predict(transform(x_eval, median, mean, std))*ys+ym


class FixedMLP(nn.Module):
    def __init__(self, dim: int):
        super().__init__(); self.net = nn.Sequential(nn.Linear(dim, HIDDEN), nn.ReLU(), nn.Linear(HIDDEN, 1))
    def forward(self, x): return self.net(x)


def mlp_predict(x_fit, y_fit, x_eval, seed: int) -> tuple[np.ndarray, int]:
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.use_deterministic_algorithms(True, warn_only=True)
    median, mean, std, ym, ys = impute_scale(x_fit, y_fit); xf, xe = transform(x_fit, median, mean, std), transform(x_eval, median, mean, std); yf = ((y_fit-ym)/ys).astype(np.float32)
    cut = max(2, int(len(xf)*.8)); model = FixedMLP(xf.shape[1]); opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WD)
    a,b = torch.tensor(xf[:cut]), torch.tensor(yf[:cut]).view(-1,1); ma,mb = torch.tensor(xf[cut:]), torch.tensor(yf[cut:]).view(-1,1)
    best, wait, state = float("inf"), 0, None
    for epoch in range(1, EPOCHS+1):
        model.train(); opt.zero_grad(); loss=nn.functional.mse_loss(model(a),b); loss.backward(); opt.step(); model.eval()
        with torch.no_grad(): monitor=nn.functional.mse_loss(model(ma),mb).item()
        if monitor < best-1e-8: best,wait,state=monitor,0,{k:v.detach().clone() for k,v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= PATIENCE: break
    model.load_state_dict(state)
    with torch.no_grad(): p=model(torch.tensor(xe)).numpy().reshape(-1)*ys+ym
    return p, epoch


def quality_rows(battery: str, sets: dict[str,pd.DataFrame], y: np.ndarray) -> tuple[list[dict],list[dict]]:
    quality=[]; stability=[]; tr=TRAIN_END[battery]; va=VALIDATION_END[battery]; segments={"EARLY_PREFIX":slice(0,tr//2),"LATE_PREFIX":slice(tr//2,tr),"VALIDATION_DIAGNOSTIC":slice(tr,va)}
    for set_name, frame in sets.items():
        for col in frame:
            x=frame[col].to_numpy(float); tx=x[:tr]; ty=y[:tr]
            quality.append({"Battery":battery,"FeatureSet":set_name,"RecordType":"FEATURE","Feature":col,"FeatureA":col,"FeatureB":"",
                            "Variance":float(np.nanvar(tx)),"MissingRate":float(np.mean(~np.isfinite(tx))),"PearsonWithSOH":float(pd.Series(tx).corr(pd.Series(ty),method="pearson")),"SpearmanWithSOH":float(pd.Series(tx).corr(pd.Series(ty),method="spearman")),"PairwiseCorrelation":np.nan,"TestLoaded":TEST_LOADED})
            for segment,s in segments.items():
                sx,sy=x[s],y[s]
                stability.append({"Battery":battery,"FeatureSet":set_name,"Segment":segment,"Feature":col,"Rows":len(sx),"PearsonWithSOH":float(pd.Series(sx).corr(pd.Series(sy),method="pearson")),"SpearmanWithSOH":float(pd.Series(sx).corr(pd.Series(sy),method="spearman")),"Variance":float(np.nanvar(sx)),"MissingRate":float(np.mean(~np.isfinite(sx))),"TestLoaded":TEST_LOADED})
        for i,a in enumerate(frame.columns):
            for b in frame.columns[i+1:]:
                quality.append({"Battery":battery,"FeatureSet":set_name,"RecordType":"PAIRWISE_COLLINEARITY","Feature":"","FeatureA":a,"FeatureB":b,"Variance":np.nan,"MissingRate":np.nan,"PearsonWithSOH":np.nan,"SpearmanWithSOH":np.nan,"PairwiseCorrelation":float(pd.Series(frame[a].iloc[:tr]).corr(pd.Series(frame[b].iloc[:tr]),method="pearson")),"TestLoaded":TEST_LOADED})
    return quality,stability


def run_models(battery: str, sets: dict[str,pd.DataFrame], y: np.ndarray) -> list[dict]:
    rows=[]; tr,va,alpha=TRAIN_END[battery],VALIDATION_END[battery],ALPHA[battery]
    for set_name,frame in sets.items():
        x=frame.to_numpy(float); common={"Battery":battery,"FeatureSet":set_name,"TrainingRows":tr,"ValidationRows":va-tr,"FeatureCount":x.shape[1],"Alpha":alpha,"TestLoaded":TEST_LOADED,"FormalEligibility":"F1_ONLY" if set_name=="F1_RAW_HEALTH" else "LEGACY_REFERENCE_NOT_STRICTLY_CAUSAL"}
        p=ridge_predict(x[:tr],y[:tr],x[tr:va],alpha); rows.append({**common,"Model":"M0_RIDGE","Configuration":f"alpha={alpha}","Seed":"deterministic","BestEpoch":np.nan,**metrics(y[tr:va],p)})
        for seed in SEEDS:
            p,epoch=mlp_predict(x[:tr],y[:tr],x[tr:va],seed); rows.append({**common,"Model":"M1_FIXED_MLP","Configuration":"hidden=32;lr=0.001;wd=1e-5","Seed":seed,"BestEpoch":epoch,**metrics(y[tr:va],p)})
    return rows


def decide(performance: pd.DataFrame) -> tuple[str,str,pd.DataFrame]:
    summary=performance.groupby(["Battery","FeatureSet","Model","FormalEligibility"],as_index=False).agg(MeanRMSE=("RMSE","mean"),RMSEStd=("RMSE","std"),MeanMAE=("MAE","mean"),MeanR2=("R2","mean"),WorstR2=("R2","min"),PositiveR2Seeds=("R2",lambda x:int((x>0).sum())),Runs=("R2","count"),Catastrophic=("CatastrophicCount","sum")).fillna({"RMSEStd":0.})
    effective=[]; partial=[]
    for model in ("M0_RIDGE","M1_FIXED_MLP"):
        b7f0=summary[(summary.Battery=="B0007")&(summary.FeatureSet=="F0_LEGACY_HF")&(summary.Model==model)].iloc[0]
        b7f1=summary[(summary.Battery=="B0007")&(summary.FeatureSet=="F1_RAW_HEALTH")&(summary.Model==model)].iloc[0]
        b18f0=summary[(summary.Battery=="B0018")&(summary.FeatureSet=="F0_LEGACY_HF")&(summary.Model==model)].iloc[0]
        b18f1=summary[(summary.Battery=="B0018")&(summary.FeatureSet=="F1_RAW_HEALTH")&(summary.Model==model)].iloc[0]
        improve=b7f1.MeanRMSE <= .85*b7f0.MeanRMSE; b18ok=b18f1.MeanRMSE <= 1.05*b18f0.MeanRMSE; stable=(model=="M0_RIDGE") or b7f1.PositiveR2Seeds>=4
        if improve and b7f1.MeanR2>0 and b18ok and stable and b7f1.Catastrophic==0: effective.append(model)
        if improve and (b7f1.MeanR2<=0 or not b18ok or not stable): partial.append(model)
    decision="FEATURE_ENRICHMENT_EFFECTIVE" if effective else "FEATURE_ENRICHMENT_PARTIAL" if partial else "CURRENT_RAW_FEATURES_INSUFFICIENT"
    next_stage="SUPERVISED_PERFORMANCE_RECOVERY" if decision in ("FEATURE_ENRICHMENT_EFFECTIVE","FEATURE_ENRICHMENT_PARTIAL") else "STOP_AND_REASSESS"
    return decision,next_stage,summary


def main():
    OUT.mkdir(parents=True,exist_ok=True); allq=[]; alls=[]; allp=[]; raw_frames=[]; audit_lines=["# Current HF Audit", "", "## Definitions", "- `HF1`: charge timestamp from record start to first `Voltage_measured >= 4.2 V` (s); uses charge voltage/time.", "- `HF2`: timestamp from that 4.2-V point to first subsequent `abs(Current_measured) <= 0.02 A` (s); uses charge current/voltage/time.", "- `HF3`: charge timestamp difference between first `Voltage_measured >= 3.8 V` and first `>= 4.0 V` (s); uses charge voltage/time.", "", "## Provenance risk", "The legacy extractor applies centered rolling Hampel smoothing and bidirectional interpolation to the full battery sequence. Therefore F0 values can use future rows and are `LEGACY_REFERENCE_NOT_STRICTLY_CAUSAL`; no new feature in this audit uses that preprocessing.", "", "## Raw-feature boundary", "F1 scans only enough initial raw cycles to emit train+validation rows (B0007=67; B0018=51). It uses no future cycle, total lifetime or capacity field as an input; capacity is supervised target only. Features are available after the associated current discharge completes."]
    for battery in BATTERIES:
        print(f"[feature-audit] {battery}: extracting frozen raw prefix",flush=True); sets,raw=load_feature_sets(battery); y=raw.SOH.to_numpy(float)*100; raw.insert(0,"Battery",battery); raw.insert(1,"TestLoaded",TEST_LOADED); raw_frames.append(raw)
        q,s=quality_rows(battery,sets,y); allq+=q; alls+=s; allp+=run_models(battery,sets,y)
        for name,frame in sets.items(): audit_lines += [f"\n## {battery} {name} training-prefix summary", frame.iloc[:TRAIN_END[battery]].describe().to_csv()]
    quality,stability,performance=map(pd.DataFrame,(allq,alls,allp)); decision,next_stage,summary=decide(performance)
    pd.concat(raw_frames,ignore_index=True).to_csv(OUT/"frozen_raw_features.csv",index=False,encoding="utf-8-sig"); quality.to_csv(OUT/"feature_quality_metrics.csv",index=False,encoding="utf-8-sig"); stability.to_csv(OUT/"feature_stability_metrics.csv",index=False,encoding="utf-8-sig"); performance.to_csv(OUT/"feature_set_performance.csv",index=False,encoding="utf-8-sig"); summary.to_csv(OUT/"feature_set_performance_summary.csv",index=False,encoding="utf-8-sig")
    manifest={"experiment":"FEATURE_ADEQUACY_REASSESSMENT_v1","test_loaded":TEST_LOADED,"train_end":TRAIN_END,"validation_end":VALIDATION_END,"raw_feature_names":RAW_FEATURES,"feature_counts":{"F0":3,"F1":7,"F2":10},"legacy_f0_provenance":"centered full-series smoothing; reference only","f1_eligibility":"only leakage-safe feature set","decision_record":"DECISION_RECORD_FEATURE_ADEQUACY_REASSESSMENT.md"}; (OUT/"run_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    (ROOT/"CURRENT_HF_AUDIT.md").write_text("\n".join(audit_lines),encoding="utf-8")
    report=["# Feature Adequacy Report","",f"FEATURE_ADEQUACY_DECISION = {decision}",f"NEXT_STAGE = {next_stage}","","## Boundary","`TestLoaded=False` for every output row. F1 is the only leakage-safe feature set. F0/F2 remain legacy reference comparisons due full-series centered smoothing in the old HF extractor.","","## Performance summary","",summary.to_csv(index=False),"","## Stop","All frozen features and model runs are complete. No follow-up feature/window/model search is authorized by this report."]
    (ROOT/"FEATURE_ADEQUACY_REPORT.md").write_text("\n".join(report),encoding="utf-8"); print(f"FEATURE_ADEQUACY_DECISION={decision}; NEXT_STAGE={next_stage}",flush=True)

if __name__=="__main__": main()
