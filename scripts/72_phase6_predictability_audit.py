"""Phase 6: prefix-only representation and component-predictability audit.

This runner intentionally does not load test rows, train component models, use GAN
data, or change Phase 5's window/scaler/boundary contract.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from scipy.stats import ks_2samp, pearsonr, spearmanr, wasserstein_distance
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from statsmodels.tsa.seasonal import STL

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "phase6_predictability_audit_v1"
PHASE5 = ROOT / "output" / "phase5_complexity_ablation_v1"
BATTERIES = ("B0007", "B0018")
SEEDS = (42, 123, 2024, 3407, 7777)
HF = ("HF1", "HF2", "HF3")
WINDOW = 10
STL_PERIOD = 12
LR = 0.001
WEIGHT_DECAY = 1e-5
PATIENCE = 50
EPOCHS = 300


def seed_everything(seed: int) -> None:
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)


def boundaries(battery: str) -> tuple[int, int]:
    manifest_path = ROOT / "output" / "phase1_failure_isolation_v1" / "PAPER_FUSION" / "seed_42" / battery / "none" / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))["engine_manifest"]
    return int(manifest["TrainEnd"]), int(manifest["ValidationEnd"])


def safe_corr(a: np.ndarray, b: np.ndarray, method: str) -> float:
    if len(a) < 3 or np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return np.nan
    return float(pearsonr(a, b).statistic if method == "pearson" else spearmanr(a, b).statistic)


def regression_metrics(true: np.ndarray, pred: np.ndarray) -> dict:
    true, pred = np.asarray(true, float), np.asarray(pred, float)
    return {
        "RMSE": float(np.sqrt(mean_squared_error(true, pred))),
        "MAE": float(mean_absolute_error(true, pred)), "R2": float(r2_score(true, pred)),
        "PredictionStd": float(pred.std()), "TrueStd": float(true.std()),
        "Correlation": safe_corr(true, pred, "pearson"),
    }


def range_overlap(train: np.ndarray, val: np.ndarray) -> dict:
    lo, hi = max(float(train.min()), float(val.min())), min(float(train.max()), float(val.max()))
    width_train, width_val = float(train.max() - train.min()), float(val.max() - val.min())
    width = max(0.0, hi - lo)
    return {
        "OverlapMin": lo, "OverlapMax": hi, "OverlapWidth": width,
        "TrainRangeOverlapFraction": width / max(width_train, 1e-12),
        "ValidationRangeOverlapFraction": width / max(width_val, 1e-12),
        "ValidationOutsideTrainFraction": float(np.mean((val < train.min()) | (val > train.max()))),
    }


def describe(values: np.ndarray, label: str) -> dict:
    q = np.quantile(values, [.05, .25, .5, .75, .95])
    return {f"{label}Mean": float(np.mean(values)), f"{label}Std": float(np.std(values)),
            f"{label}Min": float(np.min(values)), f"{label}Max": float(np.max(values)),
            f"{label}Q05": float(q[0]), f"{label}Q25": float(q[1]), f"{label}Median": float(q[2]),
            f"{label}Q75": float(q[3]), f"{label}Q95": float(q[4])}


def acf(values: np.ndarray, lag: int) -> float:
    if len(values) <= lag + 1: return np.nan
    return safe_corr(values[:-lag], values[lag:], "pearson")


class TinySOHMLP(nn.Module):
    """Fixed small control: flattened 10-step HF (+ optional current cycle)."""
    def __init__(self, input_dim: int):
        super().__init__(); self.net = nn.Sequential(nn.Linear(input_dim, 12), nn.ReLU(), nn.Linear(12, 1))
    def forward(self, x): return self.net(x)


def train_mlp(x: np.ndarray, y: np.ndarray, seed: int):
    seed_everything(seed)
    model = TinySOHMLP(x.shape[1])
    x_t, y_t = torch.tensor(x, dtype=torch.float32), torch.tensor(y, dtype=torch.float32).view(-1, 1)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    cut = max(1, int(len(y) * .8)); best, wait, state = float("inf"), 0, None
    for epoch in range(EPOCHS):
        model.train(); optimizer.zero_grad(); loss = nn.functional.mse_loss(model(x_t[:cut]), y_t[:cut]); loss.backward(); optimizer.step()
        model.eval()
        with torch.no_grad(): monitor = nn.functional.mse_loss(model(x_t[cut:]), y_t[cut:]).item() if cut < len(y) else loss.item()
        if monitor < best - 1e-7:
            best, wait = monitor, 0; state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= PATIENCE: break
    model.load_state_dict(state)
    with torch.no_grad(): return model, model(torch.tensor(x, dtype=torch.float32)).numpy().reshape(-1), epoch + 1


def make_features(hf_norm: np.ndarray, target_indices: np.ndarray, train_end: int, with_cycle: bool) -> np.ndarray:
    rows = [hf_norm[i - WINDOW + 1:i + 1].reshape(-1) for i in target_indices]
    x = np.asarray(rows, np.float32)
    # No total-life normalization: cycle / train_end uses only the known labelled prefix scale.
    if with_cycle: x = np.c_[x, np.asarray(target_indices, np.float32) / float(train_end)]
    return x


def direct_soh_controls(battery: str, raw: pd.DataFrame, train_end: int, val_end: int) -> list[dict]:
    soh = raw.SOH.to_numpy(np.float32) * 100
    fit_end = max(WINDOW + 3, int(train_end * .8))  # Exact Phase 5 scaler/model-fit boundary.
    hf = raw[list(HF)].to_numpy(np.float32); mean, std = hf[:fit_end].mean(0), hf[:fit_end].std(0); std[std < 1e-8] = 1
    norm_hf = (hf - mean) / std
    train_idx, val_idx = np.arange(WINDOW, fit_end), np.arange(train_end, val_end)
    rows = []
    for with_cycle, feature_set in ((False, "HF_ONLY"), (True, "HF_PLUS_TRAIN_SCALED_CYCLE")):
        x_train, x_val = make_features(norm_hf, train_idx, train_end, with_cycle), make_features(norm_hf, val_idx, train_end, with_cycle)
        y_mean, y_std = float(soh[:fit_end].mean()), max(float(soh[:fit_end].std()), 1e-8)
        y_train = (soh[train_idx] - y_mean) / y_std
        ridge = Ridge(alpha=1.0).fit(x_train, y_train)
        pred = ridge.predict(x_val) * y_std + y_mean
        rows.append({"Battery": battery, "Model": "RIDGE", "Seed": "deterministic", "FeatureSet": feature_set,
                     "ParameterCount": int(ridge.coef_.size + 1), "TrainingSamples": len(train_idx), "FitEnd": fit_end,
                     "TestLoaded": False, **regression_metrics(soh[val_idx], pred)})
        for seed in SEEDS:
            model, _, epoch = train_mlp(x_train, y_train, seed)
            with torch.no_grad(): p = model(torch.tensor(x_val, dtype=torch.float32)).numpy().reshape(-1) * y_std + y_mean
            rows.append({"Battery": battery, "Model": "TINY_MLP", "Seed": seed, "FeatureSet": feature_set,
                         "ParameterCount": sum(p.numel() for p in model.parameters()), "TrainingSamples": len(train_idx),
                         "FitEnd": fit_end, "BestEpoch": epoch, "TestLoaded": False, **regression_metrics(soh[val_idx], p)})
    return rows


def analyze_battery(battery: str):
    train_end, val_end = boundaries(battery)
    # Hard boundary: test rows are never read into the process.
    raw = pd.read_csv(ROOT / "data" / "hf_csv" / f"{battery}_hf.csv", nrows=val_end)[list(HF) + ["SOH"]]
    raw = raw.apply(pd.to_numeric, errors="coerce").dropna().reset_index(drop=True)
    if len(raw) != val_end: raise RuntimeError(f"{battery}: numeric cleaning changed the locked prefix boundary")
    soh = raw.SOH.to_numpy(np.float32) * 100
    train_stl = STL(soh[:train_end], period=STL_PERIOD, robust=True).fit()
    prefix_stl = STL(soh[:val_end], period=STL_PERIOD, robust=True).fit()
    attr = {"Trend": "trend", "Seasonal": "seasonal", "Residual": "resid"}
    train_target = {k: np.asarray(getattr(train_stl, v), np.float32) for k, v in attr.items()}
    prefix_target = {k: np.asarray(getattr(prefix_stl, v), np.float32) for k, v in attr.items()}
    train_values = {"SOH": soh[:train_end], **train_target}
    val_values = {"SOH": soh[train_end:val_end], **{k: v[train_end:val_end] for k, v in prefix_target.items()}}

    shift, relation, component, stability = [], [], [], []
    for feature in HF:
        train_x, val_x = raw[feature].to_numpy(float)[:train_end], raw[feature].to_numpy(float)[train_end:val_end]
        shift.append({"Battery": battery, "Feature": feature, "TrainRows": train_end, "ValidationRows": val_end-train_end,
                      **describe(train_x, "Train"), **describe(val_x, "Validation"), **range_overlap(train_x, val_x),
                      "KSStatistic": float(ks_2samp(train_x, val_x).statistic), "KSPValue": float(ks_2samp(train_x, val_x).pvalue),
                      "WassersteinDistance": float(wasserstein_distance(train_x, val_x)),
                      "StandardizedWasserstein": float(wasserstein_distance(train_x, val_x) / max(np.std(train_x), 1e-8)), "TestLoaded": False})
        for split, x in (("train", train_x), ("validation", val_x)):
            for target in ("SOH", "Trend", "Seasonal", "Residual"):
                y = train_values[target] if split == "train" else val_values[target]
                relation.append({"Battery": battery, "Split": split, "Feature": feature, "Target": target, "Rows": len(x),
                                 "Pearson": safe_corr(x, y, "pearson"), "Spearman": safe_corr(x, y, "spearman"), "TestLoaded": False})
    for name in attr:
        tr, va = train_target[name], prefix_target[name][train_end:val_end]
        stability.append({"Battery": battery, "Component": name, "TrainRows": train_end, "ValidationRows": len(va),
                          "RMSETrainPrefixVsFullPrefix": float(np.sqrt(mean_squared_error(tr, prefix_target[name][:train_end]))),
                          "MAETrainPrefixVsFullPrefix": float(mean_absolute_error(tr, prefix_target[name][:train_end])),
                          "TrainComponentStd": float(np.std(tr)), "RelativeRMSEToTrainStd": float(np.sqrt(mean_squared_error(tr, prefix_target[name][:train_end])) / max(np.std(tr), 1e-8)),
                          "TrainPrefixCorrelation": safe_corr(tr, prefix_target[name][:train_end], "pearson"), "TestLoaded": False})
        component.append({"Battery": battery, "Component": name, "TrainRows": len(tr), "ValidationRows": len(va),
                          **describe(tr, "Train"), **describe(va, "Validation"), **range_overlap(tr, va),
                          "KSStatistic": float(ks_2samp(tr, va).statistic), "KSPValue": float(ks_2samp(tr, va).pvalue),
                          "WassersteinDistance": float(wasserstein_distance(tr, va)),
                          "TrainACF1": acf(tr, 1), "ValidationACF1": acf(va, 1), "TrainACFPeriod12": acf(tr, STL_PERIOD), "ValidationACFPeriod12": acf(va, STL_PERIOD),
                          "TrainFirstDifferenceVariance": float(np.var(np.diff(tr))), "ValidationFirstDifferenceVariance": float(np.var(np.diff(va))),
                          "TrainSmoothnessMADiff": float(np.mean(np.abs(np.diff(tr)))), "ValidationSmoothnessMADiff": float(np.mean(np.abs(np.diff(va)))),
                          "TestLoaded": False})
    return shift, relation, component, stability, direct_soh_controls(battery, raw, train_end, val_end)


def relation_shift(frame: pd.DataFrame) -> pd.DataFrame:
    pivot = frame.pivot_table(index=["Battery", "Feature", "Target"], columns="Split", values=["Pearson", "Spearman"], aggfunc="first").reset_index()
    pivot.columns = ["_".join(c).strip("_") if isinstance(c, tuple) else c for c in pivot.columns]
    pivot["PearsonAbsoluteChange"] = (pivot.Pearson_train - pivot.Pearson_validation).abs()
    pivot["SpearmanAbsoluteChange"] = (pivot.Spearman_train - pivot.Spearman_validation).abs()
    pivot["RelationshipShiftFlag"] = (pivot.PearsonAbsoluteChange >= .5) | (pivot.SpearmanAbsoluteChange >= .5)
    return pivot


def direct_summary(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.groupby(["Battery", "Model", "FeatureSet"], as_index=False).agg(
        MeanRMSE=("RMSE", "mean"), RMSEStd=("RMSE", lambda x: float(np.std(x, ddof=0))), WorstRMSE=("RMSE", "max"),
        MeanMAE=("MAE", "mean"), MeanR2=("R2", "mean"), WorstR2=("R2", "min"), Runs=("Seed", "count"), TestLoaded=("TestLoaded", "max"))


def attribution(shift: pd.DataFrame, rel_wide: pd.DataFrame, components: pd.DataFrame, stl: pd.DataFrame, direct: pd.DataFrame) -> list[str]:
    flags = []
    # Predeclared descriptive thresholds; they are diagnostic flags, not hypothesis tests.
    b0007_shift = shift[shift.Battery == "B0007"].StandardizedWasserstein.mean() > shift[shift.Battery == "B0018"].StandardizedWasserstein.mean() * 1.25
    relation = rel_wide.RelationshipShiftFlag.any()
    stl_unstable = (stl.RelativeRMSEToTrainStd >= .25).any()
    direct_s = direct_summary(direct)
    direct_vs_phase5 = []
    phase5 = pd.read_csv(PHASE5 / "hybrid_reconstruction_metrics.csv")
    for battery in BATTERIES:
        direct_best = direct_s[(direct_s.Battery == battery) & (direct_s.FeatureSet == "HF_ONLY")].MeanRMSE.min()
        h0 = phase5[(phase5.Battery == battery) & (phase5.Hybrid == "H0_PAPER_COMPONENTS")].RMSE.mean()
        direct_vs_phase5.append(direct_best < h0)
    cycle_help = []
    for battery in BATTERIES:
        base = direct_s[(direct_s.Battery == battery) & (direct_s.FeatureSet == "HF_ONLY")].MeanRMSE.min()
        cycle = direct_s[(direct_s.Battery == battery) & (direct_s.FeatureSet == "HF_PLUS_TRAIN_SCALED_CYCLE")].MeanRMSE.min()
        cycle_help.append(cycle <= .75 * base)
    intrinsic = ((components.ValidationACF1.abs() < .25) & (components.ValidationFirstDifferenceVariance > components.TrainFirstDifferenceVariance)).any()
    if relation: flags.append("HF_COMPONENT_RELATIONSHIP_SHIFT")
    if stl_unstable: flags.append("STL_PREFIX_INSTABILITY")
    if all(direct_vs_phase5): flags.append("STL_DECOMPOSITION_HURTS_PREDICTABILITY")
    if all(cycle_help): flags.append("HF_FEATURES_MISSING_DEGRADATION_CONTEXT")
    if intrinsic: flags.append("COMPONENT_TARGET_INTRINSICALLY_UNSTABLE")
    if not flags: flags.append("REPRESENTATION_NOT_PRIMARY_BOTTLENECK")
    if b0007_shift: flags.append("B0007_SHIFT_MORE_SEVERE_EVIDENCE")
    return flags


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    all_shift, all_relation, all_component, all_stl, all_direct = [], [], [], [], []
    for battery in BATTERIES:
        print(f"[Phase6] {battery}: prefix-only audit", flush=True)
        shift, relation, component, stl, direct = analyze_battery(battery)
        all_shift += shift; all_relation += relation; all_component += component; all_stl += stl; all_direct += direct
    shift, relation, component, stl, direct = map(pd.DataFrame, (all_shift, all_relation, all_component, all_stl, all_direct))
    rel_wide = relation_shift(relation)
    shift.to_csv(OUT / "hf_distribution_shift.csv", index=False, encoding="utf-8-sig")
    relation.to_csv(OUT / "hf_component_relationship.csv", index=False, encoding="utf-8-sig")
    rel_wide.to_csv(OUT / "hf_component_relationship_shift_summary.csv", index=False, encoding="utf-8-sig")
    component.to_csv(OUT / "component_predictability.csv", index=False, encoding="utf-8-sig")
    stl.to_csv(OUT / "stl_prefix_stability.csv", index=False, encoding="utf-8-sig")
    direct.to_csv(OUT / "direct_soh_control.csv", index=False, encoding="utf-8-sig")
    final_flags = attribution(shift, rel_wide, component, stl, direct)
    report = ["# Phase 6 — Component Predictability & Representation Audit", "", "## Final attribution", *[f"- {flag}" for flag in final_flags], "", "## Protocol", "REAL_ONLY; B0007/B0018; same first-20% train / next-20% validation boundaries and 10-step HF windows as Phase 5.", "Raw data is read with `nrows=ValidationEnd`; TestLoaded=false for every row.", "Full-prefix STL exists only as a diagnostic reference. It is never used to train a model.", "The direct controls are fixed Ridge(alpha=1.0) and a fixed 12-hidden-unit MLP; they are not a model search.", "Cycle uses cycle/train_end, not total-life normalization.", "", "## Evidence boundaries", "HF_COMPONENT_RELATIONSHIP_SHIFT is observed relative to the current train-only-STL versus prefix-STL evaluation targets. Because the STL audit independently shows those targets move when validation cycles are appended, this flag does not by itself prove a physical HF mapping change.", "STL_DECOMPOSITION_HURTS_PREDICTABILITY means the current paper component pipeline (H0) is worse than the direct HF controls on both batteries. It is not proof that STL alone is causal: the all-Ridge component reconstruction in Phase 5 is nearly equivalent to direct Ridge, so the evidence implicates the combined decomposition-plus-component-model pipeline.", "", "## Distribution shift", shift.groupby("Battery").agg(MeanKS=("KSStatistic", "mean"), MeanWasserstein=("WassersteinDistance", "mean"), MeanStandardizedWasserstein=("StandardizedWasserstein", "mean"), MeanValidationOutsideTrain=("ValidationOutsideTrainFraction", "mean")).reset_index().to_csv(index=False), "", "## Relationship shift", rel_wide.groupby("Battery").agg(MaxPearsonChange=("PearsonAbsoluteChange", "max"), MaxSpearmanChange=("SpearmanAbsoluteChange", "max"), FlaggedPairs=("RelationshipShiftFlag", "sum")).reset_index().to_csv(index=False), "", "## STL prefix stability", stl.groupby("Battery").agg(MaxRelativeRMSE=("RelativeRMSEToTrainStd", "max"), MeanRelativeRMSE=("RelativeRMSEToTrainStd", "mean")).reset_index().to_csv(index=False), "", "## Direct SOH control", direct_summary(direct).to_csv(index=False)]
    (OUT / "PHASE6_REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print(" | ".join(final_flags))


if __name__ == "__main__": main()
