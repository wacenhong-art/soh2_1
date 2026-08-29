"""One frozen F1 baseline/ablation run; no test records are ever loaded."""
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "feature_adequacy_reassessment_v1" / "frozen_raw_features.csv"
OUT = ROOT / "output" / "strong_baseline_raw_ablation_v1"
BATTERIES = ("B0007", "B0018")
TRAIN_END = {"B0007": 33, "B0018": 25}
VAL_END = {"B0007": 67, "B0018": 51}
SEEDS = (42, 123, 2024, 3407, 7777)
F1 = (
    "DISCHARGE_DURATION_S", "DISCHARGE_V4P0_TO_V3P6_S",
    "DISCHARGE_VOLTAGE_MEAN_V", "DISCHARGE_VOLTAGE_STD_V",
    "DISCHARGE_TEMPERATURE_MEAN_C", "DISCHARGE_TEMPERATURE_STD_C",
    "DISCHARGE_ENERGY_WH",
)
FEATURE_SETS = {
    "A0_FULL_F1": F1,
    "A1_NO_DURATION": tuple(x for x in F1 if x != "DISCHARGE_DURATION_S"),
    "A2_NO_ENERGY": tuple(x for x in F1 if x != "DISCHARGE_ENERGY_WH"),
    "A3_NO_DURATION_ENERGY": tuple(x for x in F1 if x not in {"DISCHARGE_DURATION_S", "DISCHARGE_ENERGY_WH"}),
}
TEST_LOADED = False


@dataclass(frozen=True)
class Candidate:
    family: str
    configuration: str
    value: float | int
    stochastic: bool


CANDIDATES = (
    *(Candidate("M0_RIDGE", f"alpha={v}", v, False) for v in (0.1, 1.0, 10.0)),
    *(Candidate("M1_ELASTICNET", f"alpha={v};l1_ratio=0.5", v, False) for v in (0.001, 0.01, 0.1)),
    *(Candidate("M2_HIST_GRADIENT_BOOSTING", f"max_leaf_nodes={v};min_samples_leaf=2;l2=1.0", v, False) for v in (3, 5, 7)),
    *(Candidate("M3_SMALL_MLP", f"hidden={v};lr=0.001;wd=1e-5", v, True) for v in (8, 16, 32)),
)
MODEL_ORDER = ("M0_RIDGE", "M1_ELASTICNET", "M2_HIST_GRADIENT_BOOSTING", "M3_SMALL_MLP")


def seed_all(seed: int) -> None:
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)


def metrics(y: np.ndarray, p: np.ndarray) -> dict[str, float | int]:
    e = p - y
    return {
        "RMSE": float(np.sqrt(mean_squared_error(y, p))),
        "MAE": float(mean_absolute_error(y, p)),
        "MAPE": float(np.mean(np.abs(e / y)) * 100),
        "R2": float(r2_score(y, p)),
        "PredictionMean": float(p.mean()), "PredictionStd": float(p.std()),
        "PredictionBias": float(e.mean()), "WorstAbsoluteError": float(np.abs(e).max()),
        "CatastrophicCount": int(np.count_nonzero((p < 50) | (p > 110))),
    }


def scale_fit(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
    med = np.nanmedian(x, axis=0); med[~np.isfinite(med)] = 0.0
    clean = np.where(np.isfinite(x), x, med)
    mean, std = clean.mean(axis=0), clean.std(axis=0); std[std < 1e-8] = 1.0
    return med, mean, std, float(y.mean()), max(float(y.std()), 1e-8)


def apply_scale(x: np.ndarray, med: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return ((np.where(np.isfinite(x), x, med) - mean) / std).astype(np.float32)


class MLP(nn.Module):
    def __init__(self, d: int, h: int) -> None:
        super().__init__(); self.net = nn.Sequential(nn.Linear(d, h), nn.ReLU(), nn.Linear(h, 1))
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def mlp_predict(x_fit: np.ndarray, y_fit: np.ndarray, x_eval: np.ndarray, hidden: int, seed: int) -> tuple[np.ndarray, int]:
    seed_all(seed)
    med, mean, std, ymean, ystd = scale_fit(x_fit, y_fit)
    xf, xe = apply_scale(x_fit, med, mean, std), apply_scale(x_eval, med, mean, std)
    yf = ((y_fit - ymean) / ystd).astype(np.float32)
    cut = max(2, int(len(xf) * .8)); cut = min(cut, len(xf) - 1)
    a, b = torch.tensor(xf[:cut]), torch.tensor(yf[:cut]).view(-1, 1)
    va, vb = torch.tensor(xf[cut:]), torch.tensor(yf[cut:]).view(-1, 1)
    m = MLP(xf.shape[1], hidden); opt = torch.optim.AdamW(m.parameters(), lr=.001, weight_decay=1e-5)
    best, best_state, stale = float("inf"), None, 0
    for epoch in range(1, 301):
        m.train(); opt.zero_grad(); loss = nn.functional.mse_loss(m(a), b); loss.backward(); opt.step()
        m.eval()
        with torch.no_grad(): current = nn.functional.mse_loss(m(va), vb).item()
        if current < best - 1e-8:
            best, stale = current, 0; best_state = {k: v.detach().clone() for k, v in m.state_dict().items()}
        else:
            stale += 1
            if stale >= 50: break
    if best_state is None: raise RuntimeError("MLP early stopping produced no model state")
    m.load_state_dict(best_state)
    with torch.no_grad(): p = m(torch.tensor(xe)).numpy().reshape(-1) * ystd + ymean
    return p, epoch


def predict(c: Candidate, xfit: np.ndarray, yfit: np.ndarray, xeval: np.ndarray, seed: int) -> tuple[np.ndarray, int | None]:
    if c.family == "M3_SMALL_MLP": return mlp_predict(xfit, yfit, xeval, int(c.value), seed)
    med, mean, std, ym, ys = scale_fit(xfit, yfit)
    xf, xe, yf = apply_scale(xfit, med, mean, std), apply_scale(xeval, med, mean, std), (yfit - ym) / ys
    if c.family == "M0_RIDGE": model = Ridge(alpha=float(c.value))
    elif c.family == "M1_ELASTICNET": model = ElasticNet(alpha=float(c.value), l1_ratio=.5, max_iter=20000, random_state=0)
    elif c.family == "M2_HIST_GRADIENT_BOOSTING": model = HistGradientBoostingRegressor(max_leaf_nodes=int(c.value), min_samples_leaf=2, l2_regularization=1., random_state=0)
    else: raise ValueError(c.family)
    return model.fit(xf, yf).predict(xe) * ys + ym, None


def seeds(c: Candidate) -> tuple[int, ...]: return SEEDS if c.stochastic else (0,)


def load(battery: str) -> tuple[np.ndarray, np.ndarray]:
    table = pd.read_csv(SOURCE)
    table = table.loc[table.Battery.eq(battery)].sort_values("RawChargeCycleIndex").reset_index(drop=True)
    if len(table) != VAL_END[battery]: raise RuntimeError(f"{battery}: source must have exactly frozen train+validation rows")
    if not table.TestLoaded.eq(False).all(): raise RuntimeError(f"{battery}: TestLoaded source flag is true")
    return table.loc[:, F1].to_numpy(float), table.SOH.to_numpy(float) * 100


def inner_rows(battery: str, c: Candidate, x: np.ndarray, y: np.ndarray) -> list[dict[str, object]]:
    train = TRAIN_END[battery]; cut = max(2, int(train * .6)); records = []
    for seed in seeds(c):
        p, epoch = predict(c, x[:cut], y[:cut], x[cut:train], seed); m = metrics(y[cut:train], p)
        records.append({"Battery": battery, "FeatureSet": "A0_FULL_F1", "Model": c.family, "Configuration": c.configuration, "Seed": seed if c.stochastic else "deterministic", "InnerFitRows": cut, "InnerValidationRows": train-cut, "NormalizedInnerRMSE": m["RMSE"] / max(float(y[cut:train].std()), 1e-8), "BestEpoch": epoch, "TestLoaded": TEST_LOADED, **m})
    return records


def choose(inner: pd.DataFrame, battery: str, family: str) -> Candidate:
    scores = inner.loc[(inner.Battery == battery) & (inner.Model == family)].groupby("Configuration").NormalizedInnerRMSE.mean()
    choices = [c for c in CANDIDATES if c.family == family]
    return min(choices, key=lambda c: (float(scores[c.configuration]), choices.index(c)))


def outer_rows(battery: str, stage: str, set_name: str, cols: tuple[str, ...], c: Candidate, x: np.ndarray, y: np.ndarray) -> list[dict[str, object]]:
    train, end = TRAIN_END[battery], VAL_END[battery]; records = []
    for seed in seeds(c):
        p, epoch = predict(c, x[:train], y[:train], x[train:end], seed)
        records.append({"Battery":battery,"Stage":stage,"FeatureSet":set_name,"Model":c.family,"Configuration":c.configuration,"Seed":seed if c.stochastic else "deterministic","TrainingRows":train,"ValidationRows":end-train,"FeatureCount":len(cols),"BestEpoch":epoch,"TestLoaded":TEST_LOADED,**metrics(y[train:end],p)})
    return records


def proximity() -> None:
    meta = {
        "DISCHARGE_DURATION_S": ("s", "current discharge Time", "direct capacity-adjacent fixed-protocol duration"),
        "DISCHARGE_V4P0_TO_V3P6_S": ("s", "current discharge Voltage_measured + Time", "indirect voltage-traversal duration"),
        "DISCHARGE_VOLTAGE_MEAN_V": ("V", "current discharge Voltage_measured", "indirect discharge-profile descriptor"),
        "DISCHARGE_VOLTAGE_STD_V": ("V", "current discharge Voltage_measured", "indirect profile-spread descriptor"),
        "DISCHARGE_TEMPERATURE_MEAN_C": ("degC", "current discharge Temperature_measured", "indirect thermal-state descriptor"),
        "DISCHARGE_TEMPERATURE_STD_C": ("degC", "current discharge Temperature_measured", "indirect thermal-variability descriptor"),
        "DISCHARGE_ENERGY_WH": ("Wh", "current discharge Voltage_measured/Current_measured/Time", "direct capacity-adjacent delivered-energy proxy"),
    }
    lines = ["# Raw Feature Label-Proximity Audit", "", "All correlations below use only first-20% labelled training prefixes. `label-adjacent != leakage`: F1 is derived only from the current completed discharge waveform; SOH/Capacity labels, future cycles and total life are never features. Inputs are legal for end-of-current-cycle estimation only, not early/future/RUL prediction.", "", "| Feature | Unit | Raw source | Current/history | Pearson / Spearman | Physical relation | Leakage status |", "|---|---|---|---|---|---|---|"]
    for f in F1:
        corrs=[]
        for b in BATTERIES:
            x,y=load(b); v=pd.Series(x[:TRAIN_END[b],F1.index(f)]); target=pd.Series(y[:TRAIN_END[b]])
            corrs.append(f"{b}: {v.corr(target,method='pearson'):.3f}/{v.corr(target,method='spearman'):.3f}")
        unit, source, meaning=meta[f]
        lines.append(f"| `{f}` | {unit} | {source} | current completed discharge | {'; '.join(corrs)} | {meaning} | `LEGAL_POST_DISCHARGE_LABEL_ADJACENT_NOT_LEAKAGE` |")
    lines += ["", "## Interpretation", "Duration and energy are physically close to a capacity measurement under a fixed discharge protocol. This makes them label-adjacent but not true label leakage: neither is calculated from SOH nor uses a future cycle. Their role is therefore explicitly isolated by A1–A3 and must not be represented as an early-prediction or algorithmic-innovation result."]
    (ROOT / "RAW_FEATURE_LABEL_PROXIMITY.md").write_text("\n".join(lines),encoding="utf-8")


def classify(a0: pd.DataFrame, ab: pd.DataFrame) -> tuple[str,str,str,pd.DataFrame,dict[str,str]]:
    summary=a0.groupby(["Battery","Model"],as_index=False).agg(MeanRMSE=("RMSE","mean"),RMSEStd=("RMSE","std"),MeanR2=("R2","mean"),WorstR2=("R2","min"),PositiveR2Seeds=("R2",lambda x:int((x>=.277).sum())),Runs=("R2","count"),Catastrophic=("CatastrophicCount","sum")).fillna({"RMSEStd":0.})
    strong=[]; partial=[]
    for model in MODEL_ORDER:
        b7=summary.loc[(summary.Battery=="B0007")&(summary.Model==model)].iloc[0]; b18=summary.loc[(summary.Battery=="B0018")&(summary.Model==model)].iloc[0]
        stable=model!="M3_SMALL_MLP" or b7.PositiveR2Seeds>=4
        if b7.MeanRMSE<=1.729 and b7.MeanR2>=.277 and b18.MeanRMSE<=.394 and b18.MeanR2>0 and stable and b7.Catastrophic==0 and b18.Catastrophic==0: strong.append(model)
        elif b7.MeanRMSE<2.034 or b7.MeanR2>.177: partial.append(model)
    ridge=summary.loc[summary.Model=="M0_RIDGE"].set_index("Battery"); near=True
    for model in MODEL_ORDER[1:]:
        for b in BATTERIES:
            row=summary.loc[(summary.Battery==b)&(summary.Model==model)].iloc[0]; base=ridge.loc[b]
            if row.MeanRMSE<.95*base.MeanRMSE and row.MeanR2>base.MeanR2+.05: near=False
    decision="STRONG_SUPERVISED_BASELINE_RECOVERED" if strong else ("RIDGE_ALREADY_NEAR_FEATURE_LIMIT" if near else "SUPERVISED_BASELINE_PARTIAL")
    per={}
    for b in BATTERIES:
        g=ab.loc[ab.Battery==b].groupby("FeatureSet").agg(MeanRMSE=("RMSE","mean"),MeanR2=("R2","mean")); base,both=g.loc["A0_FULL_F1"],g.loc["A3_NO_DURATION_ENERGY"]
        dominated=both.MeanRMSE/base.MeanRMSE-1>=.25 and base.MeanR2-both.MeanR2>=.20
        robust=all(g.loc[s].MeanRMSE/base.MeanRMSE-1<=.10 and base.MeanR2-g.loc[s].MeanR2<=.10 for s in ("A1_NO_DURATION","A2_NO_ENERGY","A3_NO_DURATION_ENERGY"))
        per[b]="CAPACITY_PROXY_DOMINATED" if dominated else ("ROBUST_MULTI_FEATURE_SIGNAL" if robust else "MIXED_FEATURE_DEPENDENCE")
    dep="ROBUST_MULTI_FEATURE_SIGNAL" if set(per.values())=={"ROBUST_MULTI_FEATURE_SIGNAL"} else ("CAPACITY_PROXY_DOMINATED" if set(per.values())=={"CAPACITY_PROXY_DOMINATED"} else "MIXED_FEATURE_DEPENDENCE")
    nxt="TASK_VALIDITY_REASSESSMENT" if dep=="CAPACITY_PROXY_DOMINATED" else ("INNOVATION_GAP_SEARCH" if decision=="STRONG_SUPERVISED_BASELINE_RECOVERED" and dep in {"ROBUST_MULTI_FEATURE_SIGNAL","MIXED_FEATURE_DEPENDENCE"} else "FEATURE_OR_TASK_REASSESSMENT")
    return decision,dep,nxt,summary,per


def main() -> None:
    if not SOURCE.exists(): raise FileNotFoundError(SOURCE)
    OUT.mkdir(parents=True,exist_ok=True); proximity(); data={b:load(b) for b in BATTERIES}
    inner_records=[]
    for b in BATTERIES:
        for c in CANDIDATES: inner_records.extend(inner_rows(b,c,*data[b]))
    inner=pd.DataFrame(inner_records); selected={b:{f:choose(inner,b,f) for f in MODEL_ORDER} for b in BATTERIES}
    score=[]
    for f in MODEL_ORDER:
        score.append((float(np.mean([inner.loc[(inner.Battery==b)&(inner.Model==f)&(inner.Configuration==selected[b][f].configuration),"NormalizedInnerRMSE"].mean() for b in BATTERIES])),f))
    best_family=min(score,key=lambda x:(x[0],MODEL_ORDER.index(x[1])))[1]
    a0_records=[]
    for b in BATTERIES:
        for f in MODEL_ORDER: a0_records.extend(outer_rows(b,"EXPERIMENT_A","A0_FULL_F1",F1,selected[b][f],*data[b]))
    a0=pd.DataFrame(a0_records); ab_records=[]
    for b in BATTERIES:
        x,y=data[b]; c=selected[b][best_family]
        for name,cols in FEATURE_SETS.items(): ab_records.extend(outer_rows(b,"EXPERIMENT_B",name,cols,c,x[:,[F1.index(v) for v in cols]],y))
    ab=pd.DataFrame(ab_records)
    ab["DeltaRMSEvsA0"]=ab.groupby(["Battery","Model"])["RMSE"].transform(lambda s:s-s.iloc[0]); ab["DeltaR2vsA0"]=ab.groupby(["Battery","Model"])["R2"].transform(lambda s:s-s.iloc[0])
    decision,dep,nxt,summary,per=classify(a0,ab)
    inner.to_csv(OUT/"inner_selection_metrics.csv",index=False,encoding="utf-8-sig"); a0.to_csv(OUT/"strong_baseline_metrics.csv",index=False,encoding="utf-8-sig"); ab.to_csv(OUT/"raw_feature_ablation_metrics.csv",index=False,encoding="utf-8-sig"); summary.to_csv(OUT/"strong_baseline_summary.csv",index=False,encoding="utf-8-sig")
    manifest={"experiment":"STRONG_BASELINE_RAW_ABLATION_v1","test_loaded":False,"source_feature_file":str(SOURCE.relative_to(ROOT)),"feature_sets":{k:list(v) for k,v in FEATURE_SETS.items()},"seeds":list(SEEDS),"selected_family_from_inner_prefix_only":best_family,"selected_target_configs":{b:{f:selected[b][f].configuration for f in MODEL_ORDER} for b in BATTERIES}}
    (OUT/"run_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    report=["# Strong Baseline & Raw-Feature Contribution Report","",f"BASELINE_DECISION = {decision}",f"FEATURE_DEPENDENCE = {dep}",f"NEXT_STAGE = {nxt}","",f"Experiment-B family selected from inner prefixes only: `{best_family}`.","","## Experiment A summary","",summary.to_csv(index=False),"","## Per-battery feature dependence",* [f"- `{b}`: `{per[b]}`" for b in BATTERIES],"","All formal rows are `TestLoaded=False`. F1 is current completed-discharge end-of-cycle estimation only; it is not future/RUL prediction, cross-dataset generalization, or an innovation claim.","","## Stop","This frozen comparison is complete. No extra model, feature, ablation, score or tuning run is authorized by its results."]
    (ROOT/"STRONG_BASELINE_REPORT.md").write_text("\n".join(report),encoding="utf-8")
    print(f"BASELINE_DECISION={decision}; FEATURE_DEPENDENCE={dep}; NEXT_STAGE={nxt}")


if __name__ == "__main__": main()
