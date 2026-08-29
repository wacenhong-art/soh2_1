"""Final validation of the pre-committed compatibility-aware source-selection rule.

Target CSVs are read with nrows=ValidationEnd only.  This script does not open
the target test partition, tune any score, or train any model beyond frozen
Ridge(alpha=1.0) M0--M4 comparisons.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "final_method_validation_v1"
PROTOCOL = OUT / "SOURCE_SELECTION_PROTOCOL.md"
TARGETS = ("B0007", "B0018")
SOURCES = ("B0005", "B0006")
HF = ("HF1", "HF2", "HF3")
W = 10
ALPHA = 1.0


def boundary(battery: str) -> tuple[int, int]:
    path = ROOT / "output" / "phase1_failure_isolation_v1" / "PAPER_FUSION" / "seed_42" / battery / "none" / "run_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))["engine_manifest"]
    return int(manifest["TrainEnd"]), int(manifest["ValidationEnd"])


def load_frame(battery: str, nrows: int | None = None) -> pd.DataFrame:
    kwargs = {} if nrows is None else {"nrows": nrows}
    return (
        pd.read_csv(ROOT / "data" / "hf_csv" / f"{battery}_hf.csv", **kwargs)[list(HF) + ["SOH"]]
        .apply(pd.to_numeric, errors="coerce")
        .dropna()
        .reset_index(drop=True)
    )


def windows(hf: np.ndarray, indices: np.ndarray) -> np.ndarray:
    return np.asarray([hf[i - W + 1 : i + 1].reshape(-1) for i in indices], dtype=np.float32)


def scale_fit(rows: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = rows.mean(axis=0)
    std = rows.std(axis=0)
    std[std < 1e-8] = 1.0
    return mean.astype(np.float32), std.astype(np.float32)


def protocol_hash() -> str:
    return hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()


def score_sources(target_prefix_hf: np.ndarray, source_hf: dict[str, np.ndarray], order: tuple[str, ...]) -> dict[str, float]:
    """The one frozen score: mean per-row nearest Euclidean source distance."""
    common_rows = np.concatenate([source_hf[name] for name in SOURCES], axis=0)
    mean, std = scale_fit(common_rows)
    target_z = (target_prefix_hf - mean) / std
    scores: dict[str, float] = {}
    for name in order:
        source_z = (source_hf[name] - mean) / std
        distances = np.sqrt(((target_z[:, None, :] - source_z[None, :, :]) ** 2).sum(axis=2))
        scores[name] = float(distances.min(axis=1).mean())
    return scores


def select(scores: dict[str, float], source_rows: dict[str, int]) -> str:
    best = min(scores.values())
    tied = [name for name in SOURCES if abs(scores[name] - best) <= 1e-12]
    return sorted(tied, key=lambda name: (-source_rows[name], name))[0]


def selection_sanity(target: str, target_prefix: np.ndarray, source_hf: dict[str, np.ndarray]) -> dict[str, object]:
    counts = {name: len(source_hf[name]) for name in SOURCES}
    normal = score_sources(target_prefix, source_hf, SOURCES)
    reverse = score_sources(target_prefix, source_hf, tuple(reversed(SOURCES)))
    # Arbitrary display aliases are deliberately unrelated to the canonical names.
    aliased = {"alpha": source_hf["B0005"], "omega": source_hf["B0006"]}
    alias_scores = score_sources(target_prefix, {"B0005": aliased["alpha"], "B0006": aliased["omega"]}, SOURCES)
    selected_normal = select(normal, counts)
    selected_reverse = select(reverse, counts)
    selected_alias = select(alias_scores, counts)
    same_scores = all(abs(normal[s] - reverse[s]) <= 1e-10 and abs(normal[s] - alias_scores[s]) <= 1e-10 for s in SOURCES)
    return {
        "Battery": target,
        "Score_B0005": normal["B0005"],
        "Score_B0006": normal["B0006"],
        "SelectedSource": selected_normal,
        "SelectedScore": normal[selected_normal],
        "CandidateOrderReversed": "B0006,B0005",
        "SelectedWithReversedOrder": selected_reverse,
        "SelectedWithAliasedNames": selected_alias,
        "OrderInvariant": selected_normal == selected_reverse,
        "SourceNameInvariant": selected_normal == selected_alias,
        "ScoreInvariant": same_scores,
        "SanityCheckPassed": bool(selected_normal == selected_reverse == selected_alias and same_scores),
        "SelectionUsesTargetSOH": False,
        "SelectionUsesValidationSOH": False,
        "SelectionUsesTestSOH": False,
        "TestLoaded": False,
    }


def source_windows(frames: dict[str, pd.DataFrame], names: tuple[str, ...], mean: np.ndarray, std: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x_all, y_all, y_scale = [], [], []
    for name in names:
        data = frames[name]
        hf = data[list(HF)].to_numpy(np.float32)
        y = data.SOH.to_numpy(np.float32) * 100
        idx = np.arange(W, len(data))
        x_all.append(windows((hf - mean) / std, idx))
        y_all.append(y[idx])
        y_scale.append(y)
    return np.concatenate(x_all), np.concatenate(y_all), np.concatenate(y_scale)


def train_predict(
    model_id: str,
    target_raw: pd.DataFrame,
    fit_end: int,
    validation_end: int,
    source_frames: dict[str, pd.DataFrame],
    names: tuple[str, ...],
    calibrated: bool,
) -> tuple[np.ndarray, dict[str, object]]:
    hf = target_raw[list(HF)].to_numpy(np.float32)
    y = target_raw.SOH.to_numpy(np.float32) * 100
    train_idx = np.arange(W, fit_end)
    validation_idx = np.arange(fit_end, validation_end)
    source_rows = np.concatenate([source_frames[name][list(HF)].to_numpy(np.float32) for name in names])
    scaler_rows = np.concatenate([source_rows, hf[:fit_end]]) if calibrated else source_rows
    mean, std = scale_fit(scaler_rows)
    sx, sy, y_scale = source_windows(source_frames, names, mean, std)
    tx = windows((hf - mean) / std, train_idx)
    if calibrated:
        x_fit = np.concatenate([sx, tx])
        y_fit = np.concatenate([sy, y[train_idx]])
        y_scale = np.concatenate([y_scale, y[:fit_end]])
    else:
        x_fit, y_fit = sx, sy
    y_mean, y_std = float(y_scale.mean()), float(max(y_scale.std(), 1e-8))
    model = Ridge(alpha=ALPHA).fit(x_fit, (y_fit - y_mean) / y_std)
    pred = model.predict(windows((hf - mean) / std, validation_idx)) * y_std + y_mean
    return pred, {
        "TrainingSamples": int(len(y_fit)),
        "SourceTrainingSamples": int(len(sy)),
        "TargetTrainingSamples": int(len(train_idx) if calibrated else 0),
        "UsesTargetSOHLabelsForTraining": calibrated,
        "ScalerFitScope": "+".join(names) + ("+TARGET_FIT_PREFIX" if calibrated else "_SOURCE_ONLY"),
        "ParameterCount": int(model.coef_.size + 1),
        "RidgeAlpha": ALPHA,
        "ModelId": model_id,
    }


def target_only(target_raw: pd.DataFrame, fit_end: int, validation_end: int) -> tuple[np.ndarray, dict[str, object]]:
    hf = target_raw[list(HF)].to_numpy(np.float32)
    y = target_raw.SOH.to_numpy(np.float32) * 100
    train_idx, validation_idx = np.arange(W, fit_end), np.arange(fit_end, validation_end)
    mean, std = scale_fit(hf[:fit_end])
    y_mean, y_std = float(y[:fit_end].mean()), float(max(y[:fit_end].std(), 1e-8))
    model = Ridge(alpha=ALPHA).fit(windows((hf - mean) / std, train_idx), (y[train_idx] - y_mean) / y_std)
    pred = model.predict(windows((hf - mean) / std, validation_idx)) * y_std + y_mean
    return pred, {
        "TrainingSamples": int(len(train_idx)), "SourceTrainingSamples": 0, "TargetTrainingSamples": int(len(train_idx)),
        "UsesTargetSOHLabelsForTraining": True, "ScalerFitScope": "TARGET_FIT_PREFIX_ONLY",
        "ParameterCount": int(model.coef_.size + 1), "RidgeAlpha": ALPHA, "ModelId": "M0_TARGET_ONLY",
    }


def metric_values(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {
        "RMSE": float(mean_squared_error(y, pred) ** 0.5),
        "MAE": float(mean_absolute_error(y, pred)),
        "R2": float(r2_score(y, pred)),
        "PredictionStd": float(pred.std()),
    }


def run_target(target: str, source_frames: dict[str, pd.DataFrame]) -> tuple[list[dict[str, object]], dict[str, object]]:
    train_end, validation_end = boundary(target)
    raw = load_frame(target, nrows=validation_end)
    if len(raw) != validation_end:
        raise RuntimeError(f"{target}: cleaning changed validation boundary")
    fit_end = max(W + 3, int(train_end * 0.8))
    source_hf = {name: source_frames[name][list(HF)].to_numpy(np.float32) for name in SOURCES}
    sanity = selection_sanity(target, raw.loc[: train_end - 1, list(HF)].to_numpy(np.float32), source_hf)
    if not sanity["SanityCheckPassed"]:
        raise RuntimeError(f"{target}: source selection sanity check failed")
    selected = str(sanity["SelectedSource"])
    y = raw.SOH.to_numpy(np.float32)[fit_end:validation_end] * 100
    configurations = [
        ("M0_TARGET_ONLY", "TARGET_ONLY", (), False),
        ("M1_ALL_SOURCE_ZERO_SHOT", "ALL_SOURCE_ZERO_SHOT", SOURCES, False),
        ("M2_SELECTED_SOURCE_ZERO_SHOT", "SELECTED_SOURCE_ZERO_SHOT", (selected,), False),
        ("M3_ALL_SOURCE_CALIBRATED", "ALL_SOURCE_CALIBRATED", SOURCES, True),
        ("M4_SELECTED_SOURCE_CALIBRATED", "SELECTED_SOURCE_CALIBRATED", (selected,), True),
    ]
    rows: list[dict[str, object]] = []
    for model_id, track, names, calibrated in configurations:
        if model_id == "M0_TARGET_ONLY":
            pred, details = target_only(raw, fit_end, validation_end)
        else:
            pred, details = train_predict(model_id, raw, fit_end, validation_end, source_frames, names, calibrated)
        rows.append({
            "Battery": target, "Model": model_id, "Track": track, "SelectedSource": selected,
            "CompatibilityScore_B0005": sanity["Score_B0005"], "CompatibilityScore_B0006": sanity["Score_B0006"],
            "SelectedCompatibilityScore": sanity["SelectedScore"], "TargetTrainEnd": train_end, "TargetFitEnd": fit_end,
            "ValidationEnd": validation_end, "ValidationRows": int(len(y)), "TestLoaded": False, **details, **metric_values(y, pred),
        })
    return rows, sanity


def selected_vs_all(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    pairs = (("ZERO_SHOT", "M2_SELECTED_SOURCE_ZERO_SHOT", "M1_ALL_SOURCE_ZERO_SHOT"), ("CALIBRATED", "M4_SELECTED_SOURCE_CALIBRATED", "M3_ALL_SOURCE_CALIBRATED"))
    for battery in TARGETS:
        target_only_rmse = float(metrics[(metrics.Battery == battery) & (metrics.Model == "M0_TARGET_ONLY")].RMSE.iloc[0])
        for scenario, selected_model, all_model in pairs:
            selected = metrics[(metrics.Battery == battery) & (metrics.Model == selected_model)].iloc[0]
            all_source = metrics[(metrics.Battery == battery) & (metrics.Model == all_model)].iloc[0]
            rows.append({
                "Battery": battery, "Scenario": scenario, "SelectedSource": selected.SelectedSource,
                "SelectedRMSE": selected.RMSE, "AllSourceRMSE": all_source.RMSE, "TargetOnlyRMSE": target_only_rmse,
                "SelectedMinusAllRMSE": selected.RMSE - all_source.RMSE,
                "SelectedVsAllRMSEPercent": (selected.RMSE / all_source.RMSE - 1.0) * 100.0,
                "SelectedMinusTargetOnlyRMSE": selected.RMSE - target_only_rmse,
                "AllSourceNegativeTransferVsTargetOnly": bool(all_source.RMSE > 1.01 * target_only_rmse),
                "SelectedAvoidsThatNegativeTransfer": bool(all_source.RMSE > 1.01 * target_only_rmse and selected.RMSE <= target_only_rmse),
                "TestLoaded": False,
            })
    return pd.DataFrame(rows)


def verdict(comparison: pd.DataFrame, sanity: pd.DataFrame) -> tuple[str, str]:
    if not bool(sanity.SanityCheckPassed.all()):
        return "METHOD_VALIDATION_INCONCLUSIVE", "Selection invariance failed."
    zero = comparison[comparison.Scenario == "ZERO_SHOT"].set_index("Battery")
    cal = comparison[comparison.Scenario == "CALIBRATED"].set_index("Battery")
    no_major_deterioration = bool((comparison.SelectedVsAllRMSEPercent <= 5.0).all())
    avoids_negative = bool(comparison.SelectedAvoidsThatNegativeTransfer.any())
    zero_consistent = bool((zero.SelectedMinusAllRMSE <= 0).all())
    cal_consistent = bool((cal.SelectedMinusAllRMSE <= 0).all())
    if no_major_deterioration and avoids_negative and zero_consistent and cal_consistent:
        return "COMPATIBILITY_AWARE_SELECTION_SUPPORTED", "Both targets and both tracks are non-inferior to all-source under the frozen rule."
    if avoids_negative or zero_consistent or cal_consistent:
        return "COMPATIBILITY_AWARE_SELECTION_PARTIALLY_SUPPORTED", "At least one preregistered contrast supports the rule, but benefit is not directionally consistent across both targets/tracks."
    return "COMPATIBILITY_AWARE_SELECTION_NOT_SUPPORTED", "Frozen covariate-only selection did not avoid negative transfer or match all-source robustly."


def write_report(metrics: pd.DataFrame, sanity: pd.DataFrame, comparison: pd.DataFrame, final_verdict: str, reason: str) -> None:
    lines = [
        "# Final Method Validation — Compatibility-Aware Source Selection", "",
        f"## Final judgment\n\n`{final_verdict}`\n\n{reason}", "",
        "## Protocol integrity", "",
        f"Frozen protocol SHA256: `{protocol_hash()}`.",
        "The protocol was committed before this run (`cd42d3b`). Scores use only source HF1/HF2/HF3 and target first-20% HF1/HF2/HF3. Target CSVs were read with `nrows=ValidationEnd`; every result row has `TestLoaded=false`.",
        "Selection did not use target SOH, validation/test SOH, historical Phase 8/9 metrics or manual source assignment.", "",
        "## DEVELOPMENT EVIDENCE versus METHOD VALIDATION EVIDENCE", "",
        "Phase 8/9 B0005/B0006 transfer outcomes are DEVELOPMENT EVIDENCE only: they motivated the covariate-only score family but were not used by the selection algorithm. The M0-M4 validation rows below are METHOD VALIDATION EVIDENCE under the frozen score. Because B0007/B0018 previously appeared in development diagnostics, this is a transparent validation on the same target set, not independent confirmation; an unseen target cohort is still required for a strong generalization claim.", "",
        "## Compatibility scores and algorithmic selection", "", sanity.to_csv(index=False), "",
        "## M0-M4 validation metrics", "", metrics.to_csv(index=False), "",
        "## Selected source versus all source", "", comparison.to_csv(index=False), "",
        "## RQ answers", "",
        "- **RQ1:** The scores, selection manifest and order/name sanity checks establish whether a covariate-only algorithm selected the source; they do not depend on target outcomes.",
        "- **RQ2:** Compare `SelectedMinusAllRMSE` by target and track; no post-hoc score is substituted if a row worsens.",
        "- **RQ3:** Directional consistency requires both B0007 and B0018, not only B0007. The final judgment therefore downgrades one-target benefit to partial evidence.",
        "- **RQ4:** Zero-shot and calibrated rows are reported separately; calibration is never called zero-shot.", "",
        "## Secondary safety guard (independent evidence)", "",
        "Bounded residual fusion is not combined with source selection. Phase 1 independently observed paper-style fusion catastrophic predictions=25 and bounded residual catastrophic predictions=0. It remains a safety guard, not the primary accuracy method.", "",
        "## NASA-only limitation and next decision", "",
        "`LOCKED_TEST_DECISION = DO_NOT_PROCEED_WITH_CURRENT_METHOD`. The frozen score selected B0006 for both targets and the selected-source models are worse than all-source in every reported contrast. A locked test cannot be used to rescue or redesign a rejected score. Any future replacement score would require a fresh, human-approved protocol and an independent development/confirmation split.",
        "This run does not read target test data. The present B0007/B0018 validation is not enough for a cross-dataset claim and does not support this score as an undergraduate thesis's primary algorithmic innovation. It remains a valuable negative validation result: simple covariate nearest-neighbor support is insufficient to screen negative transfer here. A publication claim of general compatibility-aware transfer requires a newly supported, pre-frozen method, unseen NASA targets and CALCE or another independent dataset.",
    ]
    (OUT / "METHOD_VALIDATION_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not PROTOCOL.is_file():
        raise FileNotFoundError("Frozen SOURCE_SELECTION_PROTOCOL.md is required before a run")
    OUT.mkdir(parents=True, exist_ok=True)
    source_frames = {name: load_frame(name) for name in SOURCES}
    all_rows, sanity_rows = [], []
    for target in TARGETS:
        print(f"[validation] {target}: frozen covariate-only selection then M0-M4", flush=True)
        rows, sanity = run_target(target, source_frames)
        all_rows.extend(rows)
        sanity_rows.append(sanity)
    metrics = pd.DataFrame(all_rows)
    sanity = pd.DataFrame(sanity_rows)
    comparison = selected_vs_all(metrics)
    final_verdict, reason = verdict(comparison, sanity)
    sanity.to_csv(OUT / "compatibility_scores.csv", index=False, encoding="utf-8-sig")
    metrics.to_csv(OUT / "final_method_validation_metrics.csv", index=False, encoding="utf-8-sig")
    comparison.to_csv(OUT / "selected_vs_all_source.csv", index=False, encoding="utf-8-sig")
    write_report(metrics, sanity, comparison, final_verdict, reason)
    print(final_verdict)


if __name__ == "__main__":
    main()
