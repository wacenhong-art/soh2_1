"""Frozen v1 supervised-performance recovery experiment.

Only rows before ValidationEnd are loaded.  This is an engineering baseline
diagnostic, not an innovation experiment; see the committed Decision Record.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "supervised_performance_recovery_v1"
BATTERIES = ("B0007", "B0018")
HF = ("HF1", "HF2", "HF3")
SEEDS = (42, 123, 2024, 3407, 7777)
TRAIN_END = {"B0007": 33, "B0018": 25}
VALIDATION_END = {"B0007": 67, "B0018": 51}
INNER_FIT_FRACTION = 0.60
TEMPORAL_WINDOW = 4
EPOCHS = 300
PATIENCE = 50
LR = 0.001
WEIGHT_DECAY = 1e-5
TEST_LOADED = False


@dataclass(frozen=True)
class Candidate:
    family: str
    config_name: str
    stochastic: bool
    value: float | int


CANDIDATES = (
    *(Candidate("M0_RIDGE", f"alpha={a}", False, a) for a in (0.1, 1.0, 10.0)),
    *(Candidate("M1_ELASTICNET", f"alpha={a};l1_ratio=0.5", False, a) for a in (0.001, 0.01, 0.1)),
    *(Candidate("M2_RANDOM_FOREST", f"max_depth={d};n_estimators=200;min_samples_leaf=2", True, d) for d in (2, 3, 4)),
    *(Candidate("M3_HIST_GRADIENT_BOOSTING", f"max_leaf_nodes={n};l2=1.0", False, n) for n in (3, 5, 7)),
    *(Candidate("M4_SMALL_MLP", f"hidden={h}", True, h) for h in (8, 16, 32)),
    *(Candidate("M5_SMALL_GRU", f"hidden={h};layers=1", True, h) for h in (8, 16)),
)


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)


def metric_row(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float | int]:
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    return {
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "MAPE": float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100.0),
        "R2": float(r2_score(y_true, y_pred)),
        "PredictionMean": float(y_pred.mean()),
        "PredictionStd": float(y_pred.std()),
        "WorstError": float(np.max(np.abs(y_true - y_pred))),
        "CatastrophicCount": int(np.count_nonzero((y_pred < 50.0) | (y_pred > 110.0))),
    }


def load_prefix(battery: str) -> tuple[pd.DataFrame, int, int]:
    train_end, validation_end = TRAIN_END[battery], VALIDATION_END[battery]
    path = ROOT / "data" / "hf_csv" / f"{battery}_hf.csv"
    # This nrows guard is the primary no-test contract.
    raw = pd.read_csv(path, nrows=validation_end)[list(HF) + ["SOH"]]
    raw = raw.apply(pd.to_numeric, errors="coerce").dropna().reset_index(drop=True)
    if len(raw) != validation_end:
        raise RuntimeError(f"{battery}: prefix cleaning changed frozen boundary")
    return raw, train_end, validation_end


def tabular_features(hf: np.ndarray, train_end: int, feature_set: str) -> tuple[np.ndarray, np.ndarray]:
    if feature_set == "F0_HF_CURRENT":
        idx = np.arange(len(hf))
        return hf.copy(), idx
    if feature_set != "F1_HF_CAUSAL_TEMPORAL":
        raise ValueError(feature_set)
    rows, idx = [], []
    for t in range(TEMPORAL_WINDOW - 1, len(hf)):
        history = hf[t - TEMPORAL_WINDOW + 1:t + 1]
        delta = hf[t] - hf[t - 1]
        mean = history.mean(axis=0)
        std = history.std(axis=0)
        slope = np.polyfit(np.arange(TEMPORAL_WINDOW, dtype=float), history, 1)[0]
        rows.append(np.concatenate((hf[t], delta, mean, std, slope, [t / float(train_end)])))
        idx.append(t)
    return np.asarray(rows, np.float32), np.asarray(idx, int)


def gru_features(hf: np.ndarray, feature_set: str) -> tuple[np.ndarray, np.ndarray]:
    if feature_set == "F0_HF_CURRENT":
        return hf[:, None, :].astype(np.float32), np.arange(len(hf))
    rows = [hf[t - TEMPORAL_WINDOW + 1:t + 1] for t in range(TEMPORAL_WINDOW - 1, len(hf))]
    return np.asarray(rows, np.float32), np.arange(TEMPORAL_WINDOW - 1, len(hf))


def scale_fit(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
    flat = x.reshape(len(x), -1)
    mean, std = flat.mean(axis=0), flat.std(axis=0)
    std[std < 1e-8] = 1.0
    y_mean, y_std = float(y.mean()), max(float(y.std()), 1e-8)
    # Preserve [samples, time, features] for GRU inputs after normalization.
    return mean, std, ((flat - mean) / std).reshape(x.shape).astype(np.float32), y_mean, y_std


def scale_apply(x: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return ((x.reshape(len(x), -1) - mean) / std).reshape(x.shape).astype(np.float32)


class SmallMLP(nn.Module):
    def __init__(self, inputs: int, hidden: int):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(inputs, hidden), nn.ReLU(), nn.Linear(hidden, 1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class SmallGRU(nn.Module):
    def __init__(self, inputs: int, hidden: int):
        super().__init__()
        self.gru = nn.GRU(inputs, hidden, batch_first=True)
        self.head = nn.Linear(hidden, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        output, _ = self.gru(x)
        return self.head(output[:, -1])


def train_neural(
    candidate: Candidate, x_fit: np.ndarray, y_fit: np.ndarray, x_monitor: np.ndarray,
    y_monitor: np.ndarray, seed: int,
) -> tuple[nn.Module, int, list[dict[str, float | int]]]:
    seed_everything(seed)
    if candidate.family == "M4_SMALL_MLP":
        model: nn.Module = SmallMLP(x_fit.shape[1], int(candidate.value))
    elif candidate.family == "M5_SMALL_GRU":
        model = SmallGRU(x_fit.shape[-1], int(candidate.value))
    else:
        raise ValueError(candidate.family)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    fit_x = torch.tensor(x_fit, dtype=torch.float32)
    fit_y = torch.tensor(y_fit, dtype=torch.float32).view(-1, 1)
    mon_x = torch.tensor(x_monitor, dtype=torch.float32)
    mon_y = torch.tensor(y_monitor, dtype=torch.float32).view(-1, 1)
    best_loss, wait, best_state, history = float("inf"), 0, None, []
    for epoch in range(1, EPOCHS + 1):
        model.train(); optimizer.zero_grad()
        train_loss = nn.functional.mse_loss(model(fit_x), fit_y)
        train_loss.backward(); optimizer.step()
        model.eval()
        with torch.no_grad():
            monitor_loss = nn.functional.mse_loss(model(mon_x), mon_y).item()
        history.append({"Epoch": epoch, "TrainLoss": float(train_loss.item()), "MonitorLoss": float(monitor_loss)})
        if monitor_loss < best_loss - 1e-8:
            best_loss, wait = monitor_loss, 0
            best_state = {key: value.detach().clone() for key, value in model.state_dict().items()}
        else:
            wait += 1
            if wait >= PATIENCE:
                break
    if best_state is None:
        raise RuntimeError("neural model never produced a checkpoint")
    model.load_state_dict(best_state)
    return model, epoch, history


def fit_predict(
    candidate: Candidate, x_fit: np.ndarray, y_fit: np.ndarray, x_eval: np.ndarray,
    seed: int, monitor_x: np.ndarray | None = None, monitor_y: np.ndarray | None = None,
) -> tuple[np.ndarray, int | None, int, list[dict[str, float | int]]]:
    mean, std, x_fit_scaled, y_mean, y_std = scale_fit(x_fit, y_fit)
    x_eval_scaled = scale_apply(x_eval, mean, std)
    y_fit_scaled = (y_fit - y_mean) / y_std
    if candidate.family == "M0_RIDGE":
        model = Ridge(alpha=float(candidate.value)).fit(x_fit_scaled.reshape(len(x_fit_scaled), -1), y_fit_scaled)
        pred = model.predict(x_eval_scaled.reshape(len(x_eval_scaled), -1))
        return pred * y_std + y_mean, None, int(model.coef_.size + 1), []
    if candidate.family == "M1_ELASTICNET":
        model = ElasticNet(alpha=float(candidate.value), l1_ratio=0.5, max_iter=20000, random_state=0).fit(x_fit_scaled.reshape(len(x_fit_scaled), -1), y_fit_scaled)
        pred = model.predict(x_eval_scaled.reshape(len(x_eval_scaled), -1))
        return pred * y_std + y_mean, None, int(model.coef_.size + 1), []
    if candidate.family == "M2_RANDOM_FOREST":
        model = RandomForestRegressor(n_estimators=200, max_depth=int(candidate.value), min_samples_leaf=2, random_state=seed, n_jobs=1).fit(x_fit_scaled.reshape(len(x_fit_scaled), -1), y_fit_scaled)
        pred = model.predict(x_eval_scaled.reshape(len(x_eval_scaled), -1))
        return pred * y_std + y_mean, None, sum(tree.tree_.node_count for tree in model.estimators_), []
    if candidate.family == "M3_HIST_GRADIENT_BOOSTING":
        model = HistGradientBoostingRegressor(max_leaf_nodes=int(candidate.value), l2_regularization=1.0, random_state=0).fit(x_fit_scaled.reshape(len(x_fit_scaled), -1), y_fit_scaled)
        pred = model.predict(x_eval_scaled.reshape(len(x_eval_scaled), -1))
        return pred * y_std + y_mean, None, int(candidate.value), []
    if monitor_x is None or monitor_y is None:
        # Final refit receives a chronological holdout from the labelled prefix for early stopping.
        cut = max(2, int(len(x_fit_scaled) * 0.80))
        monitor_x, monitor_y = x_fit_scaled[cut:], y_fit_scaled[cut:]
        neural_x, neural_y = x_fit_scaled[:cut], y_fit_scaled[:cut]
    else:
        monitor_x = scale_apply(monitor_x, mean, std)
        monitor_y = (monitor_y - y_mean) / y_std
        neural_x, neural_y = x_fit_scaled, y_fit_scaled
    model, best_epoch, history = train_neural(candidate, neural_x, neural_y, monitor_x, monitor_y, seed)
    with torch.no_grad():
        pred = model(torch.tensor(x_eval_scaled, dtype=torch.float32)).numpy().reshape(-1)
    params = sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
    return pred * y_std + y_mean, best_epoch, params, history


def candidate_seeds(candidate: Candidate) -> tuple[int, ...]:
    return SEEDS if candidate.stochastic else (0,)


def select_candidate(
    battery: str, feature_set: str, candidate: Candidate, x: np.ndarray, indices: np.ndarray,
    soh: np.ndarray, history_rows: list[dict],
) -> list[dict]:
    train_mask = indices < TRAIN_END[battery]
    x_train, idx_train = x[train_mask], indices[train_mask]
    y_train = soh[idx_train]
    cut = max(2, int(len(x_train) * INNER_FIT_FRACTION))
    rows = []
    for seed in candidate_seeds(candidate):
        pred, best_epoch, params, history = fit_predict(candidate, x_train[:cut], y_train[:cut], x_train[cut:], seed)
        metric = metric_row(y_train[cut:], pred)
        row = {"Battery": battery, "FeatureSet": feature_set, "ModelFamily": candidate.family,
               "Configuration": candidate.config_name, "Seed": "deterministic" if not candidate.stochastic else seed,
               "InnerFitSamples": cut, "InnerSelectionSamples": len(x_train) - cut,
               "BestEpoch": best_epoch, "ParameterCount": params, "TestLoaded": TEST_LOADED, **metric}
        rows.append(row)
        for item in history:
            history_rows.append({"Stage": "inner_selection", **{key: row[key] for key in ("Battery", "FeatureSet", "ModelFamily", "Configuration", "Seed")}, **item})
    return rows


def choose_configuration(rows: list[dict], candidates: tuple[Candidate, ...]) -> Candidate:
    summary = pd.DataFrame(rows).groupby("Configuration", sort=False).RMSE.mean().to_dict()
    ordered = [candidate for candidate in candidates if candidate.family == rows[0]["ModelFamily"]]
    return min(ordered, key=lambda candidate: (summary[candidate.config_name], ordered.index(candidate)))


def evaluate_selected(
    battery: str, feature_set: str, candidate: Candidate, x: np.ndarray, indices: np.ndarray,
    soh: np.ndarray, history_rows: list[dict], selection_rows: list[dict], prediction_rows: list[dict],
) -> list[dict]:
    train_mask, val_mask = indices < TRAIN_END[battery], (indices >= TRAIN_END[battery]) & (indices < VALIDATION_END[battery])
    x_train, y_train = x[train_mask], soh[indices[train_mask]]
    x_val, y_val = x[val_mask], soh[indices[val_mask]]
    chosen_inner_rmse = float(pd.DataFrame(selection_rows)[lambda f: f.Configuration == candidate.config_name].RMSE.mean())
    rows = []
    for seed in candidate_seeds(candidate):
        pred, best_epoch, params, history = fit_predict(candidate, x_train, y_train, x_val, seed)
        metric = metric_row(y_val, pred)
        rows.append({"Battery": battery, "FeatureSet": feature_set, "ModelFamily": candidate.family,
                     "Configuration": candidate.config_name, "Seed": "deterministic" if not candidate.stochastic else seed,
                     "TrainingSamples": len(x_train), "ValidationSamples": len(x_val),
                     "SelectionMeanRMSE": chosen_inner_rmse, "BestEpoch": best_epoch,
                     "ParameterCount": params, "TestLoaded": TEST_LOADED, **metric})
        for cycle, truth, prediction in zip(indices[val_mask], y_val, pred):
            prediction_rows.append({"Battery": battery, "FeatureSet": feature_set, "ModelFamily": candidate.family,
                                    "Configuration": candidate.config_name, "Seed": "deterministic" if not candidate.stochastic else seed,
                                    "CycleIndex": int(cycle), "TrueSOH": float(truth), "Prediction": float(prediction),
                                    "TestLoaded": TEST_LOADED})
        for item in history:
            history_rows.append({"Stage": "full_prefix_refit", "Battery": battery, "FeatureSet": feature_set,
                                 "ModelFamily": candidate.family, "Configuration": candidate.config_name,
                                 "Seed": "deterministic" if not candidate.stochastic else seed, **item})
    return rows


def simple_baselines(battery: str, soh: np.ndarray) -> list[dict]:
    y_train, y_val = soh[:TRAIN_END[battery]], soh[TRAIN_END[battery]:VALIDATION_END[battery]]
    rows = []
    for name, pred in (("B0_MEAN", np.full(len(y_val), y_train.mean())), ("B1_PERSISTENCE", np.full(len(y_val), y_train[-1]))):
        rows.append({"Battery": battery, "FeatureSet": "BASELINE", "ModelFamily": name, "Configuration": "fixed",
                     "Seed": "deterministic", "TrainingSamples": len(y_train), "ValidationSamples": len(y_val),
                     "SelectionMeanRMSE": np.nan, "BestEpoch": np.nan, "ParameterCount": 0,
                     "TestLoaded": TEST_LOADED, **metric_row(y_val, pred)})
    return rows


def static_feature_audit(battery: str, raw: pd.DataFrame, train_end: int, validation_end: int) -> list[dict]:
    rows = []
    for column in HF:
        train, val = raw[column].to_numpy(float)[:train_end], raw[column].to_numpy(float)[train_end:validation_end]
        train_soh, val_soh = raw.SOH.to_numpy(float)[:train_end] * 100, raw.SOH.to_numpy(float)[train_end:validation_end] * 100
        rows.append({"Battery": battery, "Feature": column, "TrainMean": float(train.mean()), "TrainStd": float(train.std()),
                     "ValidationMean": float(val.mean()), "ValidationStd": float(val.std()),
                     "TrainValidationRangeOverlap": float(max(0.0, min(train.max(), val.max()) - max(train.min(), val.min()))),
                     "TrainPearsonSOH": float(np.corrcoef(train, train_soh)[0, 1]),
                     "ValidationPearsonSOH": float(np.corrcoef(val, val_soh)[0, 1]), "TestLoaded": TEST_LOADED})
    return rows


def write_root_audit(frame: pd.DataFrame) -> None:
    lines = ["# Supervised Feature Audit — Frozen-run Results", "", "## Boundary", "Only rows before `ValidationEnd` were read; every record has `TestLoaded=False`.", "", "## Static HF/SOH associations", "", frame.to_csv(index=False), "", "## Interpretation boundary", "These descriptive associations do not choose a feature or model. The F0/F1 inventory and every candidate configuration were committed before this audit ran."]
    (ROOT / "SUPERVISED_FEATURE_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def classify(metrics: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    model_summary = metrics[metrics.ModelFamily.str.startswith("M")].groupby(["FeatureSet", "ModelFamily"], as_index=False).agg(
        MeanRMSE=("RMSE", "mean"), RMSEStd=("RMSE", "std"), MeanMAE=("MAE", "mean"), MeanMAPE=("MAPE", "mean"), MeanR2=("R2", "mean"),
        WorstR2=("R2", "min"), CatastrophicCount=("CatastrophicCount", "sum"),
    ).fillna({"RMSEStd": 0.0})
    qualifying = []
    model_rows = metrics[metrics.ModelFamily.str.startswith("M")]
    for feature_set, family in model_rows[["FeatureSet", "ModelFamily"]].drop_duplicates().itertuples(index=False):
        by_battery = model_rows[(model_rows.FeatureSet == feature_set) & (model_rows.ModelFamily == family)].groupby("Battery").agg(MeanRMSE=("RMSE", "mean"), MeanR2=("R2", "mean"), Catastrophic=("CatastrophicCount", "sum"))
        if set(by_battery.index) == set(BATTERIES):
            qualifying.append(((feature_set, family), by_battery.loc["B0007", "MeanRMSE"] <= 5.389 and by_battery.loc["B0018", "MeanRMSE"] <= 1.642 and by_battery.MeanR2.gt(0).all() and by_battery.Catastrophic.eq(0).all(), by_battery))
    if any(passed for _, passed, _ in qualifying):
        return "STRONG_BASELINE_RECOVERED", model_summary
    b7_improved = model_rows[model_rows.Battery == "B0007"].groupby(["FeatureSet", "ModelFamily"]).RMSE.mean().le(5.389).any()
    b18_ok = model_rows[model_rows.Battery == "B0018"].groupby(["FeatureSet", "ModelFamily"]).RMSE.mean().le(1.642).any()
    return ("PARTIAL_RECOVERY" if b7_improved and b18_ok else "SUPERVISED_PERFORMANCE_NOT_RECOVERED"), model_summary


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    all_selection, all_metrics, all_history, all_audit, all_predictions = [], [], [], [], []
    for battery in BATTERIES:
        print(f"[recovery] {battery}: loading prefix only", flush=True)
        raw, train_end, validation_end = load_prefix(battery)
        hf, soh = raw[list(HF)].to_numpy(np.float32), raw.SOH.to_numpy(np.float32) * 100
        all_audit += static_feature_audit(battery, raw, train_end, validation_end)
        all_metrics += simple_baselines(battery, soh)
        for feature_set in ("F0_HF_CURRENT", "F1_HF_CAUSAL_TEMPORAL"):
            for family in ("M0_RIDGE", "M1_ELASTICNET", "M2_RANDOM_FOREST", "M3_HIST_GRADIENT_BOOSTING", "M4_SMALL_MLP", "M5_SMALL_GRU"):
                x, indices = (gru_features(hf, feature_set) if family == "M5_SMALL_GRU" else tabular_features(hf, train_end, feature_set))
                family_candidates = tuple(candidate for candidate in CANDIDATES if candidate.family == family)
                selection_rows = []
                for candidate in family_candidates:
                    selection_rows += select_candidate(battery, feature_set, candidate, x, indices, soh, all_history)
                all_selection += selection_rows
                selected = choose_configuration(selection_rows, CANDIDATES)
                print(f"[recovery] {battery} {feature_set} {family}: {selected.config_name}", flush=True)
                all_metrics += evaluate_selected(battery, feature_set, selected, x, indices, soh, all_history, selection_rows, all_predictions)
    selection, metrics, history, audit, predictions = map(pd.DataFrame, (all_selection, all_metrics, all_history, all_audit, all_predictions))
    verdict, ablation = classify(metrics)
    metrics.to_csv(OUT / "performance_recovery_metrics.csv", index=False, encoding="utf-8-sig")
    selection.to_csv(OUT / "inner_selection_metrics.csv", index=False, encoding="utf-8-sig")
    ablation.to_csv(OUT / "feature_ablation_metrics.csv", index=False, encoding="utf-8-sig")
    history.to_csv(OUT / "training_history.csv", index=False, encoding="utf-8-sig")
    predictions.to_csv(OUT / "predictions.csv", index=False, encoding="utf-8-sig")
    audit.to_csv(OUT / "static_feature_audit.csv", index=False, encoding="utf-8-sig")
    manifest = {"experiment": "SUPERVISED_PERFORMANCE_RECOVERY_v1", "batteries": BATTERIES, "seeds": SEEDS,
                "train_end": TRAIN_END, "validation_end": VALIDATION_END, "test_loaded": TEST_LOADED,
                "feature_sets": ["F0_HF_CURRENT", "F1_HF_CAUSAL_TEMPORAL"], "candidate_count": len(CANDIDATES),
                "protocol": "PERFORMANCE_RECOVERY_PROTOCOL.md", "decision_record": "DECISION_RECORD_SUPERVISED_PERFORMANCE_RECOVERY.md"}
    (OUT / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    report = ["# Supervised Performance Recovery Report", "", f"## Verdict\n\n`{verdict}`", "", "## Boundary", "`TestLoaded=False`; only first-20% target labels trained models; next-20% is external validation.", "", "## Selected-model outer-validation summary", "", metrics.groupby(["Battery", "FeatureSet", "ModelFamily"], as_index=False).agg(MeanRMSE=("RMSE", "mean"), RMSEStd=("RMSE", "std"), MeanMAE=("MAE", "mean"), MeanMAPE=("MAPE", "mean"), MeanR2=("R2", "mean"), WorstR2=("R2", "min"), Catastrophic=("CatastrophicCount", "sum")).fillna({"RMSEStd": 0.0}).to_csv(index=False), "", "## F0/F1 selected-family summary", "", ablation.to_csv(index=False), "", "## Stop condition", "All pre-registered configurations have been run once. No test, feature follow-up, model expansion, transfer, source selection, SSL/DG, CALCE or additional grid is authorized by this result."]
    (OUT / "PERFORMANCE_RECOVERY_REPORT.md").write_text("\n".join(report), encoding="utf-8")
    write_root_audit(audit)
    print(verdict, flush=True)


if __name__ == "__main__":
    main()
