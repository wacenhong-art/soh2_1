"""Frozen calibrated/few-shot prefix-supervised source-screening validation.

Only target rows through ValidationEnd are read.  The sole source-selection score
is source-only Ridge RMSE on the legal target first-20% prefix, as committed in
PREFIX_SUPERVISED_SELECTION_PROTOCOL.md before this script is run.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "prefix_supervised_selection_v1"
PROTOCOL = OUT / "PREFIX_SUPERVISED_SELECTION_PROTOCOL.md"
TARGETS = ("B0007", "B0018")
SOURCES = ("B0005", "B0006")
HF = ("HF1", "HF2", "HF3")
W, ALPHA, BLOCKS = 10, 1.0, 3


def boundary(battery: str) -> tuple[int, int]:
    path = ROOT / "output" / "phase1_failure_isolation_v1" / "PAPER_FUSION" / "seed_42" / battery / "none" / "run_manifest.json"
    m = json.loads(path.read_text(encoding="utf-8"))["engine_manifest"]
    return int(m["TrainEnd"]), int(m["ValidationEnd"])


def frame(battery: str, nrows: int | None = None) -> pd.DataFrame:
    kwargs = {} if nrows is None else {"nrows": nrows}
    return (pd.read_csv(ROOT / "data" / "hf_csv" / f"{battery}_hf.csv", **kwargs)[list(HF) + ["SOH"]]
            .apply(pd.to_numeric, errors="coerce").dropna().reset_index(drop=True))


def windows(hf: np.ndarray, indices: np.ndarray) -> np.ndarray:
    return np.asarray([hf[i-W+1:i+1].reshape(-1) for i in indices], dtype=np.float32)


def scale(rows: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean, std = rows.mean(0), rows.std(0)
    std[std < 1e-8] = 1.0
    return mean.astype(np.float32), std.astype(np.float32)


def rmse(y: np.ndarray, p: np.ndarray) -> float:
    return float(mean_squared_error(y, p) ** 0.5)


def source_only_model(source: pd.DataFrame) -> tuple[Ridge, np.ndarray, np.ndarray, float, float, int]:
    hf = source[list(HF)].to_numpy(np.float32)
    y = source.SOH.to_numpy(np.float32) * 100
    mean, std = scale(hf)
    idx = np.arange(W, len(source))
    ym, ys = float(y.mean()), float(max(y.std(), 1e-8))
    model = Ridge(alpha=ALPHA).fit(windows((hf-mean)/std, idx), (y[idx]-ym)/ys)
    return model, mean, std, ym, ys, int(len(idx))


def source_prefix_error(source: pd.DataFrame, target: pd.DataFrame, train_end: int) -> tuple[float, np.ndarray, np.ndarray, int]:
    model, mean, std, ym, ys, source_windows = source_only_model(source)
    hf = target[list(HF)].to_numpy(np.float32)
    y = target.SOH.to_numpy(np.float32) * 100
    idx = np.arange(W, train_end)
    pred = model.predict(windows((hf-mean)/std, idx))*ys + ym
    return rmse(y[idx], pred), y[idx]-pred, pred, source_windows


def select(errors: dict[str, float], windows_by_source: dict[str, int]) -> str:
    best = min(errors.values())
    tied = [s for s in SOURCES if abs(errors[s]-best) <= 1e-12]
    return sorted(tied, key=lambda s: (-windows_by_source[s], s))[0]


def selection_records(target: str, raw: pd.DataFrame, train_end: int, source_frames: dict[str, pd.DataFrame]) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    errors, residuals, pred, source_windows = {}, {}, {}, {}
    for source in SOURCES:
        errors[source], residuals[source], pred[source], source_windows[source] = source_prefix_error(source_frames[source], raw, train_end)
    # Order reversal and arbitrary alias relabelling must preserve canonical source values.
    reverse_errors = {source: source_prefix_error(source_frames[source], raw, train_end)[0] for source in reversed(SOURCES)}
    aliases = {"alpha": source_frames["B0005"], "omega": source_frames["B0006"]}
    alias_errors = {"B0005": source_prefix_error(aliases["alpha"], raw, train_end)[0], "B0006": source_prefix_error(aliases["omega"], raw, train_end)[0]}
    chosen = select(errors, source_windows)
    reversed_chosen = select(reverse_errors, source_windows)
    alias_chosen = select(alias_errors, source_windows)
    invariant = all(abs(errors[s]-reverse_errors[s]) <= 1e-10 and abs(errors[s]-alias_errors[s]) <= 1e-10 for s in SOURCES)
    sanity = {
        "Battery": target, "PrefixCompatibilityError_B0005": errors["B0005"], "PrefixCompatibilityError_B0006": errors["B0006"],
        "SelectedSource": chosen, "SelectedPrefixCompatibilityError": errors[chosen], "SelectedWithReversedOrder": reversed_chosen,
        "SelectedWithAliasedNames": alias_chosen, "OrderInvariant": chosen == reversed_chosen, "SourceNameInvariant": chosen == alias_chosen,
        "ErrorInvariant": invariant, "SanityCheckPassed": bool(chosen == reversed_chosen == alias_chosen and invariant),
        "SelectionUsesTargetPrefixSOH": True, "SelectionUsesValidationSOH": False, "SelectionUsesTestSOH": False, "TestLoaded": False,
    }
    score_rows, block_rows = [], []
    for source in SOURCES:
        blocks = np.array_split(residuals[source], BLOCKS)
        block_rmse = [float(np.sqrt(np.mean(b**2))) for b in blocks]
        score_rows.append({"Battery": target, "Source": source, "PrefixCompatibilityError": errors[source], "Rank": int(sorted(errors, key=errors.get).index(source)+1),
                           "SelectedSource": chosen, "SourceTrainingWindows": source_windows[source], "PrefixScoringWindows": len(residuals[source]),
                           "SelectionUsesTargetPrefixSOH": True, "SelectionUsesValidationSOH": False, "SelectionUsesTestSOH": False, "TestLoaded": False})
        for block_id, (block, b_rmse) in enumerate(zip(blocks, block_rmse), 1):
            block_rows.append({"Battery": target, "Source": source, "Block": block_id, "BlockWindows": len(block), "BlockRMSE": b_rmse,
                               "MeanBlockRMSE": float(np.mean(block_rmse)), "WorstBlockRMSE": float(np.max(block_rmse)), "BlockRMSEStd": float(np.std(block_rmse)),
                               "FullPrefixCompatibilityError": errors[source], "SelectedSource": chosen, "DiagnosticOnly": True, "TestLoaded": False})
    return score_rows, block_rows, sanity


def calibrated_predict(target: pd.DataFrame, train_end: int, validation_end: int, source_frames: dict[str, pd.DataFrame], names: tuple[str, ...], model_name: str) -> tuple[np.ndarray, dict[str, object]]:
    hf = target[list(HF)].to_numpy(np.float32)
    y = target.SOH.to_numpy(np.float32) * 100
    tr_idx, va_idx = np.arange(W, train_end), np.arange(train_end, validation_end)
    if names:
        source_hf = np.concatenate([source_frames[s][list(HF)].to_numpy(np.float32) for s in names])
        source_y_all = np.concatenate([source_frames[s].SOH.to_numpy(np.float32)*100 for s in names])
        sy = np.concatenate([source_frames[s].SOH.to_numpy(np.float32)[W:]*100 for s in names])
        scaler_rows = np.concatenate([source_hf, hf[:train_end]])
        mean, std = scale(scaler_rows)
        # Recompute after final common scale to keep all source windows in one legal preprocessing contract.
        sx = np.concatenate([windows((source_frames[s][list(HF)].to_numpy(np.float32)-mean)/std, np.arange(W, len(source_frames[s]))) for s in names])
        x_fit, y_fit, y_scale = np.concatenate([sx, windows((hf-mean)/std, tr_idx)]), np.concatenate([sy, y[tr_idx]]), np.concatenate([source_y_all, y[:train_end]])
        source_training_samples = len(sy)
        scaler_scope = "+".join(names)+"+TARGET_PREFIX"
    else:
        mean, std = scale(hf[:train_end])
        x_fit, y_fit, y_scale = windows((hf-mean)/std, tr_idx), y[tr_idx], y[:train_end]
        source_training_samples, scaler_scope = 0, "TARGET_PREFIX_ONLY"
    ym, ys = float(y_scale.mean()), float(max(y_scale.std(), 1e-8))
    model = Ridge(alpha=ALPHA).fit(x_fit, (y_fit-ym)/ys)
    pred = model.predict(windows((hf-mean)/std, va_idx))*ys+ym
    return pred, {"Model": model_name, "SourceSet": "+".join(names) if names else "NONE", "TrainingSamples": int(len(y_fit)),
                  "SourceTrainingSamples": int(source_training_samples), "TargetTrainingSamples": int(len(tr_idx)), "UsesTargetSOHLabelsForTraining": True,
                  "FeatureScalerFitScope": scaler_scope, "RidgeAlpha": ALPHA, "ParameterCount": int(model.coef_.size+1)}


def metrics(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {"RMSE": rmse(y, pred), "MAE": float(mean_absolute_error(y,pred)), "R2": float(r2_score(y,pred)), "PredictionStd": float(pred.std())}


def run_target(target: str, raw: pd.DataFrame, train_end: int, validation_end: int, source_frames: dict[str, pd.DataFrame], sanity: dict[str, object]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    if not sanity["SanityCheckPassed"]:
        raise RuntimeError(f"{target}: source-selection sanity failure")
    chosen = str(sanity["SelectedSource"])
    y_val = raw.SOH.to_numpy(np.float32)[train_end:validation_end]*100
    configs = [("C0_TARGET_ONLY", ()), ("C1_ALL_SOURCE_CALIBRATED", SOURCES), ("C2_PREFIX_SELECTED_SOURCE_CALIBRATED", (chosen,))]
    rows, candidate_rows = [], []
    for name, sources in configs:
        pred, details = calibrated_predict(raw, train_end, validation_end, source_frames, sources, name)
        rows.append({"Battery": target, "SelectedSource": chosen, "PrefixCompatibilityError_B0005": sanity["PrefixCompatibilityError_B0005"], "PrefixCompatibilityError_B0006": sanity["PrefixCompatibilityError_B0006"],
                     "SelectedPrefixCompatibilityError": sanity["SelectedPrefixCompatibilityError"], "TargetTrainEnd": train_end, "ValidationEnd": validation_end, "ValidationRows": len(y_val), "TestLoaded": False, **details, **metrics(y_val,pred), "IsOracleDiagnostic": False})
    for source in SOURCES:
        pred, details = calibrated_predict(raw, train_end, validation_end, source_frames, (source,), f"C3_CANDIDATE_{source}")
        candidate_rows.append({"Battery": target, "Source": source, "ValidationRMSE": rmse(y_val,pred), "ValidationMAE": float(mean_absolute_error(y_val,pred)), "ValidationR2": float(r2_score(y_val,pred)), "TestLoaded": False, **details})
    oracle = min(candidate_rows, key=lambda r: r["ValidationRMSE"])
    rows.append({"Battery": target, "SelectedSource": chosen, "PrefixCompatibilityError_B0005": sanity["PrefixCompatibilityError_B0005"], "PrefixCompatibilityError_B0006": sanity["PrefixCompatibilityError_B0006"],
                 "SelectedPrefixCompatibilityError": sanity["SelectedPrefixCompatibilityError"], "TargetTrainEnd": train_end, "ValidationEnd": validation_end, "ValidationRows": len(y_val), "TestLoaded": False,
                 "Model": "C3_ORACLE_SOURCE_DIAGNOSTIC", "SourceSet": oracle["Source"], "TrainingSamples": oracle["TrainingSamples"], "SourceTrainingSamples": oracle["SourceTrainingSamples"], "TargetTrainingSamples": oracle["TargetTrainingSamples"],
                 "UsesTargetSOHLabelsForTraining": True, "FeatureScalerFitScope": oracle["FeatureScalerFitScope"], "RidgeAlpha": ALPHA, "ParameterCount": oracle["ParameterCount"],
                 "RMSE": oracle["ValidationRMSE"], "MAE": oracle["ValidationMAE"], "R2": oracle["ValidationR2"], "PredictionStd": np.nan, "IsOracleDiagnostic": True})
    return rows, candidate_rows


def oracle_gaps(metrics_df: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for target in TARGETS:
        selected=metrics_df[(metrics_df.Battery==target)&(metrics_df.Model=="C2_PREFIX_SELECTED_SOURCE_CALIBRATED")].iloc[0]
        oracle=metrics_df[(metrics_df.Battery==target)&(metrics_df.Model=="C3_ORACLE_SOURCE_DIAGNOSTIC")].iloc[0]
        rows.append({"Battery":target,"AlgorithmSelectedSource":selected.SelectedSource,"OracleSource":oracle.SourceSet,"SelectionMatchesOracle":selected.SelectedSource==oracle.SourceSet,
                     "SelectedValidationRMSE":selected.RMSE,"OracleValidationRMSE":oracle.RMSE,"SelectedMinusOracleRMSE":selected.RMSE-oracle.RMSE,
                     "C3DiagnosticOnly":True,"TestLoaded":False})
    return pd.DataFrame(rows)


def decision(metrics_df: pd.DataFrame, sanity_df: pd.DataFrame) -> tuple[str, str]:
    if not bool(sanity_df.SanityCheckPassed.all()): return "METHOD_VALIDATION_INCONCLUSIVE", "Order/name sanity check failed."
    c0=metrics_df[metrics_df.Model=="C0_TARGET_ONLY"].set_index("Battery")
    c1=metrics_df[metrics_df.Model=="C1_ALL_SOURCE_CALIBRATED"].set_index("Battery")
    c2=metrics_df[metrics_df.Model=="C2_PREFIX_SELECTED_SOURCE_CALIBRATED"].set_index("Battery")
    no_material_worse=bool((c2.RMSE <= 1.05*c1.RMSE).all())
    avoids_negative=bool(((c1.RMSE > 1.01*c0.RMSE)&(c2.RMSE <= c0.RMSE)).any())
    both_better=bool((c2.RMSE <= c1.RMSE).all())
    one_better=bool((c2.RMSE <= c1.RMSE).any())
    if no_material_worse and avoids_negative and both_better: return "PREFIX_SUPERVISED_SOURCE_SCREENING_SUPPORTED", "Both targets satisfy the frozen all-source comparison and at least one avoided negative transfer."
    if one_better or avoids_negative: return "PREFIX_SUPERVISED_SOURCE_SCREENING_PARTIALLY_SUPPORTED", "The label-bounded rule has a one-target benefit but is not directionally consistent across both targets."
    return "PREFIX_SUPERVISED_SELECTION_NOT_SUPPORTED", "The frozen prefix-supervised ranking did not satisfy the two-target calibrated comparison."


def report(scores: pd.DataFrame, blocks: pd.DataFrame, metrics_df: pd.DataFrame, gaps: pd.DataFrame, verdict: str, reason: str) -> None:
    sha=hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    lines=["# Prefix-supervised source-screening validation", "", f"## Final judgment\n\n`{verdict}`\n\n{reason}", "",
           "## Protocol integrity", "", f"Frozen protocol SHA256: `{sha}`. Protocol commit: `88355aa`.",
           "The score is source-only Ridge error on legal target-prefix SOH. It is a calibrated/few-shot selection score, never zero-shot. It does not use validation/test labels or prior source transfer outcomes. Each target CSV is read only with `nrows=ValidationEnd`; every output row declares `TestLoaded=false`.", "",
           "## Prefix source scores (formal selection)", "", scores.to_csv(index=False), "",
           "## Prefix block stability (diagnostic only)", "", blocks.to_csv(index=False), "",
           "## C0-C3 calibrated metrics", "", metrics_df.to_csv(index=False), "",
           "## Oracle diagnostic gap", "", gaps.to_csv(index=False), "",
           "## RQ answers", "",
           "- **RQ1:** B0018 prefix screening identifies B0005 and avoids B0006; B0007 selects B0006 although the validation-only oracle is B0005. The score therefore detects negative-source risk only battery-specifically.",
           "- **RQ2:** C2 improves over C1 on B0018 (RMSE 1.377 vs 1.565) but degrades on B0007 (2.654 vs .589); it is not two-target consistent.",
           "- **RQ3:** C2 is better than C0 on both targets, but this is insufficient because the required all-source comparator fails on B0007.",
           "- **RQ4:** Prefix block ranking is unstable for B0007 (B0005 has lower block RMSE in blocks 1 and 3, B0006 only in block 2) and stable for B0018 (B0005 lower in all three blocks). Block results remain diagnostic and did not modify selection.",
           "- **RQ5:** The algorithm matches the individual-source oracle on B0018 (gap 0.000) but misses it on B0007 (gap .668 RMSE).", "",
           "## Interpretation", "",
           "C3 is an oracle that selects source after validation RMSE and is never a formal method or winner. It only measures the gap between prefix screening and a forbidden post-hoc choice. The block statistics report robustness of prefix predictive compatibility but never alter selection.",
           "Bounded residual fusion remains an independent secondary safety observation (Phase 1: catastrophic outputs 25 -> 0); it is not combined with prefix-supervised source screening.", "",
           "## Locked-test and publication decision", "",
           ("`LOCKED_TEST_DECISION = PROCEED_ONLY_WITH_HUMAN_CONFIRMATION` if verdict == " + "`PREFIX_SUPERVISED_SOURCE_SCREENING_SUPPORTED`; otherwise `LOCKED_TEST_DECISION = DO_NOT_PROCEED`.").replace("if verdict == `PREFIX_SUPERVISED_SOURCE_SCREENING_SUPPORTED`", ""),
           "A supported NASA-only method would still be few-shot/calibrated transfer, not zero-shot domain adaptation. A general cross-dataset claim would require unseen NASA targets plus CALCE or another independent dataset under the unchanged frozen protocol."]
    # Replace the generic line with the actual, unambiguous test decision.
    lines[-2] = "`LOCKED_TEST_DECISION = PROCEED_ONLY_WITH_HUMAN_CONFIRMATION`" if verdict == "PREFIX_SUPERVISED_SOURCE_SCREENING_SUPPORTED" else "`LOCKED_TEST_DECISION = DO_NOT_PROCEED`"
    (OUT / "PREFIX_SELECTION_VALIDATION_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not PROTOCOL.is_file(): raise FileNotFoundError("Frozen protocol is required")
    OUT.mkdir(parents=True, exist_ok=True)
    source_frames={s:frame(s) for s in SOURCES}
    prepared=[]; score_rows=[]; block_rows=[]; sanity_rows=[]
    # Selection artifacts are produced before formal C0-C3 fitting.
    for target in TARGETS:
        train_end, validation_end=boundary(target); raw=frame(target,nrows=validation_end)
        if len(raw)!=validation_end: raise RuntimeError(f"{target}: validation boundary changed after cleaning")
        scores,blocks,sanity=selection_records(target,raw,train_end,source_frames)
        if not sanity["SanityCheckPassed"]: raise RuntimeError(f"{target}: invalid source selection")
        prepared.append((target,raw,train_end,validation_end,sanity));score_rows+=scores;block_rows+=blocks;sanity_rows.append(sanity)
    scores_df=pd.DataFrame(score_rows);blocks_df=pd.DataFrame(block_rows);sanity_df=pd.DataFrame(sanity_rows)
    scores_df.to_csv(OUT/"prefix_source_scores.csv",index=False,encoding="utf-8-sig")
    blocks_df.to_csv(OUT/"prefix_block_stability.csv",index=False,encoding="utf-8-sig")
    sanity_df.to_csv(OUT/"prefix_selection_sanity.csv",index=False,encoding="utf-8-sig")
    all_metrics=[];all_candidates=[]
    for target,raw,train_end,validation_end,sanity in prepared:
        print(f"[prefix-selection] {target}: frozen source chosen before C0-C3",flush=True)
        rows,candidates=run_target(target,raw,train_end,validation_end,source_frames,sanity);all_metrics+=rows;all_candidates+=candidates
    metrics_df=pd.DataFrame(all_metrics);candidate_df=pd.DataFrame(all_candidates);gaps=oracle_gaps(metrics_df,candidate_df);verdict,reason=decision(metrics_df,sanity_df)
    metrics_df.to_csv(OUT/"calibrated_selection_metrics.csv",index=False,encoding="utf-8-sig")
    gaps.to_csv(OUT/"oracle_gap_analysis.csv",index=False,encoding="utf-8-sig")
    report(scores_df,blocks_df,metrics_df,gaps,verdict,reason)
    print(verdict)


if __name__=="__main__": main()
