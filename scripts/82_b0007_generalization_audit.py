"""Frozen diagnostic audit for the B0007 supervised generalization bottleneck.

This program is deliberately not a model search.  It never reads locked-test
rows and marks all validation-internal fits DIAGNOSTIC_ONLY.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "b0007_generalization_audit_v1"
RECOVERY = ROOT / "output" / "supervised_performance_recovery_v1"
BATTERIES = ("B0007", "B0018")
HF = ("HF1", "HF2", "HF3")
TRAIN_END = {"B0007": 33, "B0018": 25}
VALIDATION_END = {"B0007": 67, "B0018": 51}
RIDGE_ALPHA = {"B0007": 10.0, "B0018": 1.0}
ROLLING_FRACTIONS = (0.50, 0.60, 0.70, 0.80)
LABEL_BUDGET_ROWS = {"B0007": ((10, 16), (15, 24), (20, 33)), "B0018": ((10, 12), (15, 18), (20, 25))}
SEEDS = (42, 123, 2024, 3407, 7777)
MLP_HIDDEN, MLP_LR, MLP_WEIGHT_DECAY, MLP_EPOCHS, MLP_PATIENCE = 32, 0.001, 1e-5, 300, 50
TEST_LOADED = False


def seed_everything(seed: int) -> None:
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)


def load_prefix(battery: str) -> pd.DataFrame:
    path = ROOT / "data" / "hf_csv" / f"{battery}_hf.csv"
    end = VALIDATION_END[battery]
    raw = pd.read_csv(path, nrows=end)[list(HF) + ["SOH"]]
    raw = raw.apply(pd.to_numeric, errors="coerce").dropna().reset_index(drop=True)
    if len(raw) != end:
        raise RuntimeError(f"{battery}: cleaning changed frozen ValidationEnd")
    return raw


def metrics(y: np.ndarray, p: np.ndarray) -> dict[str, float | int]:
    y, p = np.asarray(y, float), np.asarray(p, float)
    residual = p - y
    return {
        "RMSE": float(np.sqrt(mean_squared_error(y, p))), "MAE": float(mean_absolute_error(y, p)),
        "R2": float(r2_score(y, p)), "PredictionBias": float(residual.mean()),
        "ResidualStd": float(residual.std()), "PredictionMean": float(p.mean()),
        "PredictionStd": float(p.std()), "WorstError": float(np.max(np.abs(residual))),
    }


def scale_fit(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, float, float]:
    mean, std = x.mean(axis=0), x.std(axis=0); std[std < 1e-8] = 1.0
    y_mean, y_std = float(y.mean()), max(float(y.std()), 1e-8)
    return mean, std, y_mean, y_std


def ridge_predict(x_fit: np.ndarray, y_fit: np.ndarray, x_eval: np.ndarray, alpha: float) -> tuple[np.ndarray, dict]:
    mean, std, y_mean, y_std = scale_fit(x_fit, y_fit)
    model = Ridge(alpha=alpha).fit((x_fit - mean) / std, (y_fit - y_mean) / y_std)
    prediction = model.predict((x_eval - mean) / std) * y_std + y_mean
    detail = {
        "FeatureMean": mean, "FeatureStd": std, "TargetMean": y_mean, "TargetStd": y_std,
        "StandardizedCoefficient": model.coef_ * y_std, "Intercept": float(y_mean + model.intercept_ * y_std),
    }
    return prediction, detail


class FixedMLP(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.net = nn.Sequential(nn.Linear(3, MLP_HIDDEN), nn.ReLU(), nn.Linear(MLP_HIDDEN, 1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def mlp_predict(x_fit: np.ndarray, y_fit: np.ndarray, x_eval: np.ndarray, seed: int) -> tuple[np.ndarray, int]:
    seed_everything(seed)
    mean, std, y_mean, y_std = scale_fit(x_fit, y_fit)
    x_fit = ((x_fit - mean) / std).astype(np.float32)
    x_eval = ((x_eval - mean) / std).astype(np.float32)
    y_fit = ((y_fit - y_mean) / y_std).astype(np.float32)
    cut = max(2, int(len(x_fit) * 0.80))
    model = FixedMLP(); optimizer = torch.optim.AdamW(model.parameters(), lr=MLP_LR, weight_decay=MLP_WEIGHT_DECAY)
    fit_x, fit_y = torch.tensor(x_fit[:cut]), torch.tensor(y_fit[:cut]).view(-1, 1)
    monitor_x, monitor_y = torch.tensor(x_fit[cut:]), torch.tensor(y_fit[cut:]).view(-1, 1)
    best, wait, state = float("inf"), 0, None
    for epoch in range(1, MLP_EPOCHS + 1):
        model.train(); optimizer.zero_grad(); loss = nn.functional.mse_loss(model(fit_x), fit_y); loss.backward(); optimizer.step()
        model.eval()
        with torch.no_grad(): monitor = nn.functional.mse_loss(model(monitor_x), monitor_y).item()
        if monitor < best - 1e-8:
            best, wait = monitor, 0; state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= MLP_PATIENCE: break
    if state is None: raise RuntimeError("MLP did not checkpoint")
    model.load_state_dict(state)
    with torch.no_grad(): prediction = model(torch.tensor(x_eval)).numpy().reshape(-1) * y_std + y_mean
    return prediction, epoch


def baseline_reproduction(battery: str, x: np.ndarray, y: np.ndarray) -> dict:
    train_end, val_end, alpha = TRAIN_END[battery], VALIDATION_END[battery], RIDGE_ALPHA[battery]
    previous = pd.read_csv(RECOVERY / "performance_recovery_metrics.csv")
    old = previous[(previous.Battery == battery) & (previous.FeatureSet == "F0_HF_CURRENT") & (previous.ModelFamily == "M0_RIDGE")].iloc[0]
    prediction, _ = ridge_predict(x[:train_end], y[:train_end], x[train_end:val_end], alpha)
    current = metrics(y[train_end:val_end], prediction)
    return {"Battery": battery, "Model": "F0_RIDGE", "Alpha": alpha, "FeatureSet": "F0_HF_CURRENT",
            "TrainingSamples": train_end, "ValidationSamples": val_end - train_end,
            "PreviousRMSE": float(old.RMSE), "PreviousR2": float(old.R2), **current,
            "RMSEAbsoluteDifference": abs(current["RMSE"] - float(old.RMSE)),
            "R2AbsoluteDifference": abs(current["R2"] - float(old.R2)),
            "ReproducedWithin1e-6": abs(current["RMSE"] - float(old.RMSE)) <= 1e-6 and abs(current["R2"] - float(old.R2)) <= 1e-6,
            "TestLoaded": TEST_LOADED}


def rolling_origin(battery: str, x: np.ndarray, y: np.ndarray) -> list[dict]:
    rows, train_end, alpha = [], TRAIN_END[battery], RIDGE_ALPHA[battery]
    for fraction in ROLLING_FRACTIONS:
        cut = int(train_end * fraction)
        prediction, _ = ridge_predict(x[:cut], y[:cut], x[cut:train_end], alpha)
        rows.append({"Battery": battery, "Diagnostic": "PREFIX_ROLLING_ORIGIN", "TrainFraction": fraction,
                     "TrainRows": cut, "EvaluationRows": train_end-cut, "Model": "F0_RIDGE", "Alpha": alpha,
                     "DIAGNOSTIC_ONLY": True, "TestLoaded": TEST_LOADED, **metrics(y[cut:train_end], prediction)})
    return rows


def mapping_drift(battery: str, x: np.ndarray, y: np.ndarray) -> list[dict]:
    rows, tr, va, alpha = [], TRAIN_END[battery], VALIDATION_END[battery], RIDGE_ALPHA[battery]
    segments = {"TRAIN_PREFIX": (x[:tr], y[:tr]), "VALIDATION_DIAGNOSTIC": (x[tr:va], y[tr:va])}
    ridge_details: dict[str, dict] = {}
    for segment, (xs, ys) in segments.items():
        prediction, detail = ridge_predict(xs, ys, xs, alpha); ridge_details[segment] = detail
        slope = float(np.polyfit(np.arange(len(ys), dtype=float), ys, 1)[0])
        for index, feature in enumerate(HF):
            rows.append({"Battery": battery, "RecordType": "FEATURE_MAPPING", "Segment": segment, "Feature": feature,
                         "Mean": float(xs[:, index].mean()), "Std": float(xs[:, index].std()), "Min": float(xs[:, index].min()), "Max": float(xs[:, index].max()),
                         "Pearson": float(pd.Series(xs[:, index]).corr(pd.Series(ys), method="pearson")),
                         "Spearman": float(pd.Series(xs[:, index]).corr(pd.Series(ys), method="spearman")),
                         "SOHSlopePerCycle": slope, "StandardizedRidgeCoefficient": float(detail["StandardizedCoefficient"][index]),
                         "RidgeIntercept": detail["Intercept"], "DIAGNOSTIC_ONLY": True, "NOT_AVAILABLE_FOR_MODEL_SELECTION": True,
                         "TestLoaded": TEST_LOADED})
        rows.append({"Battery": battery, "RecordType": "RIDGE_RESIDUAL", "Segment": segment, "Feature": "ALL",
                     "Mean": np.nan, "Std": np.nan, "Min": np.nan, "Max": np.nan, "Pearson": np.nan, "Spearman": np.nan,
                     "SOHSlopePerCycle": slope, "StandardizedRidgeCoefficient": np.nan, "RidgeIntercept": detail["Intercept"],
                     "DIAGNOSTIC_ONLY": True, "NOT_AVAILABLE_FOR_MODEL_SELECTION": True, "TestLoaded": TEST_LOADED, **metrics(ys, prediction)})
    cross_pred, _ = ridge_predict(x[:tr], y[:tr], x[tr:va], alpha)
    rows.append({"Battery": battery, "RecordType": "PREFIX_RIDGE_ON_VALIDATION", "Segment": "VALIDATION_DIAGNOSTIC", "Feature": "ALL",
                 "Mean": np.nan, "Std": np.nan, "Min": np.nan, "Max": np.nan, "Pearson": np.nan, "Spearman": np.nan,
                 "SOHSlopePerCycle": float(np.polyfit(np.arange(va-tr, dtype=float), y[tr:va], 1)[0]), "StandardizedRidgeCoefficient": np.nan,
                 "RidgeIntercept": ridge_details["TRAIN_PREFIX"]["Intercept"], "DIAGNOSTIC_ONLY": True, "NOT_AVAILABLE_FOR_MODEL_SELECTION": True,
                 "TestLoaded": TEST_LOADED, **metrics(y[tr:va], cross_pred)})
    return rows


def validation_internal(battery: str, x: np.ndarray, y: np.ndarray) -> list[dict]:
    rows, tr, va, alpha = [], TRAIN_END[battery], VALIDATION_END[battery], RIDGE_ALPHA[battery]
    xs, ys = x[tr:va], y[tr:va]; cut = len(xs) // 2
    ridge_pred, _ = ridge_predict(xs[:cut], ys[:cut], xs[cut:], alpha)
    common = {"Battery": battery, "Diagnostic": "DIAGNOSTIC_ORACLE_LIKE_FIT", "TrainRows": cut,
              "EvaluationRows": len(xs)-cut, "DIAGNOSTIC_ONLY": True, "NOT_AVAILABLE_FOR_MODEL_SELECTION": True,
              "TestLoaded": TEST_LOADED}
    rows.append({**common, "Model": "F0_RIDGE", "Configuration": f"alpha={alpha}", "Seed": "deterministic", "BestEpoch": np.nan, **metrics(ys[cut:], ridge_pred)})
    for seed in SEEDS:
        pred, epoch = mlp_predict(xs[:cut], ys[:cut], xs[cut:], seed)
        rows.append({**common, "Model": "FIXED_SMALL_MLP", "Configuration": "hidden=32;lr=0.001;wd=1e-5", "Seed": seed, "BestEpoch": epoch, **metrics(ys[cut:], pred)})
    return rows


def label_budget(battery: str, x: np.ndarray, y: np.ndarray) -> list[dict]:
    rows, va, alpha = [], VALIDATION_END[battery], RIDGE_ALPHA[battery]
    for percentage, rows_used in LABEL_BUDGET_ROWS[battery]:
        prediction, _ = ridge_predict(x[:rows_used], y[:rows_used], x[TRAIN_END[battery]:va], alpha)
        rows.append({"Battery": battery, "Diagnostic": "LABEL_BUDGET_DIAGNOSTIC", "LabelBudgetPercent": percentage,
                     "TrainingRows": rows_used, "ValidationRows": va-TRAIN_END[battery], "Model": "F0_RIDGE", "Alpha": alpha,
                     "DIAGNOSTIC_ONLY": True, "NOT_AVAILABLE_FOR_MODEL_SELECTION": True, "TestLoaded": TEST_LOADED,
                     **metrics(y[TRAIN_END[battery]:va], prediction)})
    return rows


def attribution(rolling: pd.DataFrame, drift: pd.DataFrame, internal: pd.DataFrame, budget: pd.DataFrame, baseline: pd.DataFrame) -> tuple[str, str, str, dict]:
    b7_roll = rolling[rolling.Battery == "B0007"]
    b7_feature = drift[(drift.Battery == "B0007") & (drift.RecordType == "FEATURE_MAPPING")]
    pivot = b7_feature.pivot(index="Feature", columns="Segment", values=["Pearson", "StandardizedRidgeCoefficient"])
    correlation_change = (pivot[("Pearson", "TRAIN_PREFIX")] - pivot[("Pearson", "VALIDATION_DIAGNOSTIC")]).abs()
    coefficient_flip = (pivot[("StandardizedRidgeCoefficient", "TRAIN_PREFIX")] * pivot[("StandardizedRidgeCoefficient", "VALIDATION_DIAGNOSTIC")]) < 0
    b7_internal = internal[internal.Battery == "B0007"]
    ridge_r2 = float(b7_internal[b7_internal.Model == "F0_RIDGE"].iloc[0].R2)
    mlp = b7_internal[b7_internal.Model == "FIXED_SMALL_MLP"]
    mlp_r2_mean, mlp_positive = float(mlp.R2.mean()), int((mlp.R2 > 0).sum())
    prefix_positive = int((b7_roll.R2 > 0).sum())
    baseline_r2 = float(baseline[baseline.Battery == "B0007"].iloc[0].R2)
    b7_budget = budget[budget.Battery == "B0007"].sort_values("LabelBudgetPercent")
    values = b7_budget.RMSE.to_numpy(float)
    label_rule = bool(np.all(np.diff(values) < 0) and values[0] > 0 and (values[0]-values[-1])/values[0] >= .15)
    drift_rule = int((correlation_change >= .50).sum()) >= 2 or bool(coefficient_flip.any())
    mapping_rule = prefix_positive >= 3 and baseline_r2 < 0 and (ridge_r2 > 0 or (mlp_r2_mean > 0 and mlp_positive >= 4)) and drift_rule
    hf_rule = prefix_positive <= 1 and ridge_r2 <= 0 and mlp_r2_mean <= 0 and not mapping_rule
    model_rule = (float(mlp.RMSE.mean()) <= .80 * float(b7_internal[b7_internal.Model == "F0_RIDGE"].iloc[0].RMSE) and mlp_positive >= 4 and ridge_r2 <= 0 and not mapping_rule)
    if mapping_rule:
        primary, secondary, next_stage = "EARLY_TO_LATE_MAPPING_SHIFT", "TRAIN_PREFIX_TOO_SMALL" if label_rule else "NONE", "STAGE_AWARE_PERFORMANCE_REPAIR"
    elif label_rule:
        primary, secondary, next_stage = "TRAIN_PREFIX_TOO_SMALL", "NONE", "LABEL_EFFICIENT_SUPERVISED_REPAIR"
    elif hf_rule:
        primary, secondary, next_stage = "HF_INFORMATION_LIMITATION", "NONE", "FEATURE_ENRICHMENT"
    elif model_rule:
        primary, secondary, next_stage = "MODEL_FIT_LIMITATION", "NONE", "MODEL_FIT_REPAIR"
    else:
        primary, secondary, next_stage = "BOTTLENECK_INCONCLUSIVE", "NONE", "STOP_AND_REASSESS"
    evidence = {"B0007RollingPositiveR2Count": prefix_positive, "B0007BaselineValidationR2": baseline_r2,
                "B0007ValidationInternalRidgeR2": ridge_r2, "B0007ValidationInternalMLPMeanR2": mlp_r2_mean,
                "B0007ValidationInternalMLPPositiveSeeds": mlp_positive, "DriftFeatureCountPearsonChangeGE0.5": int((correlation_change >= .50).sum()),
                "DriftAnyCoefficientSignFlip": bool(coefficient_flip.any()), "LabelBudgetRule": label_rule,
                "MappingRule": mapping_rule, "HFInformationRule": hf_rule, "ModelFitRule": model_rule}
    return primary, secondary, next_stage, evidence


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    baseline_rows: list[dict] = []; rolling_rows: list[dict] = []; drift_rows: list[dict] = []; internal_rows: list[dict] = []; budget_rows: list[dict] = []
    for battery in BATTERIES:
        print(f"[audit] {battery}: prefix-only load", flush=True)
        raw = load_prefix(battery); x = raw[list(HF)].to_numpy(np.float32); y = raw.SOH.to_numpy(np.float32) * 100
        baseline_rows.append(baseline_reproduction(battery, x, y))
        rolling_rows += rolling_origin(battery, x, y)
        drift_rows += mapping_drift(battery, x, y)
        internal_rows += validation_internal(battery, x, y)
        budget_rows += label_budget(battery, x, y)
    baseline, rolling, drift, internal, budget = map(pd.DataFrame, (baseline_rows, rolling_rows, drift_rows, internal_rows, budget_rows))
    if not baseline["ReproducedWithin1e-6"].all():
        raise RuntimeError("BASELINE_REPRODUCTION_FAILED")
    primary, secondary, next_stage, evidence = attribution(rolling, drift, internal, budget, baseline)
    baseline.to_csv(OUT / "baseline_reproduction.csv", index=False, encoding="utf-8-sig")
    rolling.to_csv(OUT / "prefix_rolling_origin_metrics.csv", index=False, encoding="utf-8-sig")
    drift.to_csv(OUT / "mapping_drift_metrics.csv", index=False, encoding="utf-8-sig")
    internal.to_csv(OUT / "validation_internal_predictability.csv", index=False, encoding="utf-8-sig")
    budget.to_csv(OUT / "label_budget_diagnostic.csv", index=False, encoding="utf-8-sig")
    manifest = {"experiment": "B0007_GENERALIZATION_AUDIT_v1", "diagnostic_only": True, "test_loaded": TEST_LOADED,
                "train_end": TRAIN_END, "validation_end": VALIDATION_END, "ridge_alpha": RIDGE_ALPHA, "rolling_fractions": ROLLING_FRACTIONS,
                "seeds": SEEDS, "decision_record": "DECISION_RECORD_B0007_GENERALIZATION_AUDIT.md"}
    (OUT / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    report = ["# B0007 Generalization Audit", "", "## Boundary", "All raw loads use `nrows=ValidationEnd`; every output row is `TestLoaded=False`.", "", "## Independent baseline reproduction", "", baseline.to_csv(index=False), "", "## Frozen decision", f"PRIMARY_BOTTLENECK = {primary}", f"SECONDARY_BOTTLENECK = {secondary}", f"NEXT_STAGE = {next_stage}", "", "## Evidence", "", json.dumps(evidence, indent=2), "", "## Development-only limitation", "The validation-only fits are `DIAGNOSTIC_ONLY` and `NOT_AVAILABLE_FOR_MODEL_SELECTION`. They are not formal predictor results and do not establish cross-battery generalization."]
    (ROOT / "B0007_GENERALIZATION_AUDIT.md").write_text("\n".join(report), encoding="utf-8")
    bottleneck = ["# Supervised Bottleneck Report", "", f"PRIMARY_BOTTLENECK = {primary}", f"SECONDARY_BOTTLENECK = {secondary}", f"NEXT_STAGE = {next_stage}", "", "## Evidence boundary", "This is one frozen NASA development diagnostic, not an innovation claim. Test data were not loaded and no diagnostic result was used to select or improve a model.", "", "## Frozen evidence values", "", json.dumps(evidence, indent=2), "", "## Stop", "This diagnostic is complete. The indicated next stage is a gate, not authorization to run another experiment."]
    (ROOT / "SUPERVISED_BOTTLENECK_REPORT.md").write_text("\n".join(bottleneck), encoding="utf-8")
    print(f"PRIMARY_BOTTLENECK={primary}; SECONDARY_BOTTLENECK={secondary}; NEXT_STAGE={next_stage}", flush=True)


if __name__ == "__main__": main()
