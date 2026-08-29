"""Phase 2: locked-test fusion sequence-length ablation.

Only the Bi-LSTM fusion sequence length changes.  Saved Phase-1 component
predictions are deliberately reused so component-training randomness cannot
confound the 4/6/8/10 comparison.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
PHASE1_ROOT = ROOT / "output" / "phase1_failure_isolation_v1"
DEFAULT_OUTPUT = ROOT / "output" / "phase2_fusion_seq_ablation_v1"
BATTERIES = ("B0007", "B0018")
SEEDS = (42, 123, 2024, 3407, 7777)
SEQ_LENS = (4, 6, 8, 10)
RESIDUAL_EPSILON = 0.05
COMPONENT_WINDOW = 10
EPOCHS = 800
PATIENCE = 50


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


phase1 = load_module("phase1_failure_isolation", ROOT / "scripts" / "65_phase1_failure_isolation.py")
fusion = phase1.engine.fusion
protocol = load_module("soh_protocol_phase2", ROOT / "soh_pipeline" / "protocol.py")


def source_dir(seed: int, battery: str) -> Path:
    return PHASE1_ROOT / "PAPER_FUSION" / f"seed_{seed}" / battery / "none"


def source_manifest(seed: int, battery: str) -> dict:
    path = source_dir(seed, battery) / "run_manifest.json"
    if not path.exists():
        raise FileNotFoundError(f"缺少 Phase 1 组件预测来源：{path}")
    saved = json.loads(path.read_text(encoding="utf-8"))
    value = saved["engine_manifest"]
    expected = {
        "ComponentInput": "HF1/HF2/HF3-only", "ValidationLabelsUsedForComponentTraining": False,
        "TestLabelsUsedAsFeatures": False, "Protocol": "target-first-20%-labeled-adaptation; next-20%-validation; remainder-strict-test",
    }
    for key, wanted in expected.items():
        if value.get(key) != wanted:
            raise ValueError(f"{path}: {key}={value.get(key)!r}，应为 {wanted!r}")
    if saved.get("test_loaded") is not False or saved.get("evaluation_split") != "validation":
        raise ValueError(f"{path}: Phase 1 source must have an unopened test split")
    return value


def fusion_arrays(component_dir: Path, seq_len: int):
    """Build the actual Dataset arrays using the production fusion helpers."""
    train = pd.read_csv(component_dir / "comp_pred_train.csv")
    val = pd.read_csv(component_dir / "comp_pred_val.csv")
    old_seq = fusion.SEQ_LEN
    fusion.SEQ_LEN = seq_len
    try:
        fusion.validate_component_df(train, "train")
        fusion.validate_component_df(val, "val")
        comps = train[["Pred_Trend", "Pred_Seasonal", "Pred_Residual"]].to_numpy(dtype=np.float32)
        comp_mean, comp_std = fusion.zscore_fit(comps, axis=0)
        raw_features = fusion.build_causal_features(train, comp_mean, comp_std)
        feat_mean, feat_std = fusion.zscore_fit(raw_features, axis=0)
        y = fusion.true_soh_target(train)
        y_mean, y_std = float(y.mean()), float(y.std())
        y_std = 1.0 if y_std < 1e-8 else y_std
        train_arrays, _ = fusion.prepare_split(train, comp_mean, comp_std, feat_mean, feat_std, y_mean, y_std)
        val_arrays, _ = fusion.prepare_split(val, comp_mean, comp_std, feat_mean, feat_std, y_mean, y_std)
        return train_arrays, val_arrays
    finally:
        fusion.SEQ_LEN = old_seq


def component_training_windows(manifest: dict, battery: str) -> int:
    augmented = Path(manifest["AugmentationDir"]) / f"{battery}_aug_train_hf.csv"
    frame = pd.read_csv(augmented)
    fit_end = int(manifest["ComponentFitEndExclusive"])
    total = 0
    for _, group in frame.loc[frame["Cycle"] < fit_end].groupby("DatasetID", sort=True):
        values = group[["HF1", "HF2", "HF3"]].to_numpy(dtype=np.float32)
        target = group["SOH"].to_numpy(dtype=np.float32)
        x, _ = phase1.engine.ts.windows(values, target, seq_len=COMPONENT_WINDOW)
        total += len(x)
    return total


def build_sample_counts() -> pd.DataFrame:
    rows = []
    for battery in BATTERIES:
        manifest = source_manifest(SEEDS[0], battery)
        train_cycles = len(pd.read_csv(source_dir(SEEDS[0], battery) / "comp_pred_train.csv"))
        val_cycles = len(pd.read_csv(source_dir(SEEDS[0], battery) / "comp_pred_val.csv"))
        component_windows = component_training_windows(manifest, battery)
        for seq_len in SEQ_LENS:
            train_arrays, val_arrays = fusion_arrays(source_dir(SEEDS[0], battery), seq_len)
            rows.append({
                "Battery": battery, "TrainCycles": train_cycles, "ValidationCycles": val_cycles,
                "ComponentWindow": COMPONENT_WINDOW,
                "ComponentTrainingWindows": component_windows,
                "FusionSeqLen": seq_len,
                "FusionTrainingSamples": len(train_arrays[0]),
                "FusionValidationSamples": len(val_arrays[0]),
            })
    return pd.DataFrame(rows)


def metric_row(name: str, y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    return {
        "Baseline": name, "MAE": float(mean_absolute_error(y_true, y_pred)),
        "MAPE": float(np.abs(y_true - y_pred).sum() / np.abs(y_true).sum() * 100),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))), "R2": float(r2_score(y_true, y_pred)),
    }


def paired_baselines(battery: str, seed: int, component_dir: Path, fusion_frame: pd.DataFrame) -> list[dict]:
    # Reuse the verified Phase-1 baseline definition so comparisons remain paired.
    rows = phase1.baseline_rows(battery, seed, component_dir, fusion_frame)
    for row in rows:
        row["Battery"] = row.pop("BatteryID")
        row["EvaluationSplit"] = "validation"
        row["TestLoaded"] = False
        row["TestEvaluated"] = False
    return rows


def run_one(output_root: Path, sample_counts: pd.DataFrame, fusion_type: str, seq_len: int,
            seed: int, battery: str) -> tuple[dict, list[dict]]:
    component_dir = source_dir(seed, battery)
    manifest = source_manifest(seed, battery)
    run_dir = output_root / fusion_type / f"seq_{seq_len:02d}" / f"seed_{seed}" / battery
    metric_path = run_dir / "fusion_validation_metrics.csv"
    counts = sample_counts.query("Battery == @battery and FusionSeqLen == @seq_len").iloc[0].to_dict()
    if metric_path.exists() and (run_dir / "run_manifest.json").exists():
        metrics = pd.read_csv(metric_path).iloc[0].to_dict()
        frame = pd.read_csv(run_dir / "gmtc_pred_validation_result.csv")
    else:
        old_seq = fusion.SEQ_LEN
        fusion.SEQ_LEN = seq_len
        try:
            if fusion_type == "PAPER_FUSION":
                config = protocol.FusionConfig(
                    track=protocol.ExperimentTrack.PAPER_FUSION, fusion_seq_len=seq_len,
                    allow_fusion_seq_ablation=True,
                ).validate()
                mode, epsilon, track = "paper", None, "PAPER_FUSION"
            else:
                config = protocol.FusionConfig(
                    track=protocol.ExperimentTrack.ENHANCEMENT, fusion_seq_len=seq_len,
                    allow_fusion_seq_ablation=True, residual_fusion=True,
                    residual_epsilon=RESIDUAL_EPSILON,
                ).validate()
                mode, epsilon, track = "residual", RESIDUAL_EPSILON, "ENHANCEMENT"
            run_dir.mkdir(parents=True, exist_ok=True)
            metrics, frame = fusion.run_fusion(
                str(component_dir), str(run_dir), str(run_dir / "fusion_model.pth"),
                phase1.engine.stable_seed(seed, battery, "Trend") + 900,
                EPOCHS, PATIENCE, fusion_mode=mode, evaluate_test=False,
                stable_init=False, residual_epsilon=epsilon, experiment_track=track,
            )
            metadata = {
                "Phase": "PHASE2_FUSION_SEQUENCE_ABLATION", "FusionType": fusion_type,
                "FusionSeqLen": seq_len, "ComponentWindow": COMPONENT_WINDOW,
                "FusionTrainingSamples": int(counts["FusionTrainingSamples"]),
                "FusionValidationSamples": int(counts["FusionValidationSamples"]),
                "ComponentTrainingWindows": int(counts["ComponentTrainingWindows"]),
                "ComponentPredictionsReusedFrom": str(component_dir),
                "TestLoaded": False, "TestEvaluated": False,
            }
            metrics = {**metrics, **metadata}
            pd.DataFrame([metrics]).to_csv(metric_path, index=False)
            (run_dir / "run_manifest.json").write_text(json.dumps({
                "FusionConfig": config.manifest(), "SourceComponentManifest": manifest,
                "TestLoaded": False, "TestEvaluated": False, "FixedParameters": {
                    "component_window": 10, "hidden_size": 16, "num_layers": 1,
                    "normalization": "BatchNorm1d", "learning_rate": 0.001,
                    "batch_size": 32, "patience": 50, "weight_decay": 1e-5,
                    "l_weight": "UNVERIFIED_DISABLED",
                },
            }, ensure_ascii=False, indent=2), encoding="utf-8")
        finally:
            fusion.SEQ_LEN = old_seq
    metrics.update({"Battery": battery, "Seed": seed, "FusionType": fusion_type,
                    "FusionSeqLen": seq_len, "TestLoaded": False, "TestEvaluated": False})
    return metrics, paired_baselines(battery, seed, component_dir, frame)


def aggregate(metrics: pd.DataFrame, baselines: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    means = baselines.loc[baselines["Baseline"] == "MEAN_PREDICTOR", ["Battery", "Seed", "RMSE"]]
    means = means.drop_duplicates(["Battery", "Seed"]).rename(columns={"RMSE": "MeanBaselineRMSE"})
    all_runs = metrics.merge(means, on=["Battery", "Seed"], validate="many_to_one")
    all_runs["R2Gate"] = all_runs["R2"] > 0
    all_runs["MeanBaselineGate"] = all_runs["RMSE"] < all_runs["MeanBaselineRMSE"]
    all_runs["CatastrophicGate"] = all_runs["CatastrophicPredictionCount"] == 0
    all_runs["TestLockGate"] = (~all_runs["TestLoaded"].astype(bool)) & (~all_runs["TestEvaluated"].astype(bool))
    all_runs["RunQualified"] = all_runs[["R2Gate", "MeanBaselineGate", "CatastrophicGate", "TestLockGate"]].all(axis=1)
    rows = []
    for (fusion_type, seq_len), group in all_runs.groupby(["FusionType", "FusionSeqLen"], sort=True):
        complete = set(group["Seed"]) == set(SEEDS) and set(group["Battery"]) == set(BATTERIES) and len(group) == 10
        rows.append({
            "FusionType": fusion_type, "FusionSeqLen": int(seq_len), "CompletedRuns": len(group),
            "CompletedSeeds": group.groupby("Battery")["Seed"].nunique().min(),
            "AllRunsQualified": bool(group["RunQualified"].all() and complete),
            "WorstBatteryR2": float(group.groupby("Battery")["R2"].mean().min()),
            "WorstSeedRMSE": float(group["RMSE"].max()),
            "FailureRate": float((group["CatastrophicPredictionCount"] > 0).mean()),
            "RMSEStd": float(group["RMSE"].std(ddof=0)), "MeanRMSE": float(group["RMSE"].mean()),
            "MeanR2": float(group["R2"].mean()), "WorstR2": float(group["R2"].min()),
            "MeanWeightEntropy": float(group["WeightEntropy"].mean()),
        })
    ranked = pd.DataFrame(rows).sort_values(
        ["AllRunsQualified", "WorstBatteryR2", "WorstSeedRMSE", "FailureRate", "RMSEStd", "MeanRMSE"],
        ascending=[False, False, True, True, True, True], kind="stable",
    ).reset_index(drop=True)
    return all_runs, ranked


def plot_results(output_root: Path, all_runs: pd.DataFrame, counts: pd.DataFrame):
    for battery in BATTERIES:
        local = all_runs.loc[all_runs["Battery"] == battery]
        summary = local.groupby(["FusionType", "FusionSeqLen"], as_index=False).agg(
            MeanRMSE=("RMSE", "mean"), WorstRMSE=("RMSE", "max"), MeanR2=("R2", "mean"),
            WorstR2=("R2", "min"), RMSEStd=("RMSE", lambda x: x.std(ddof=0)),
            WeightEntropy=("WeightEntropy", "mean"),
        )
        fig, axes = plt.subplots(2, 4, figsize=(18, 8))
        axes = axes.ravel()
        sample = counts.loc[counts["Battery"] == battery]
        axes[0].plot(sample["FusionSeqLen"], sample["FusionTrainingSamples"], marker="o")
        axes[0].set_title("fusion training samples")
        for ax, field, label in zip(axes[1:7], ["MeanRMSE", "WorstRMSE", "MeanR2", "WorstR2", "RMSEStd", "WeightEntropy"],
                                    ["mean RMSE", "worst RMSE", "mean R2", "worst R2", "RMSE std", "weight entropy"]):
            for fusion_type, group in summary.groupby("FusionType"):
                ax.plot(group["FusionSeqLen"], group[field], marker="o", label=fusion_type)
            ax.set_title(label); ax.legend(fontsize=8)
        axes[7].axis("off")
        for ax in axes[:7]:
            ax.set_xlabel("fusion_seq_len"); ax.grid(alpha=.25)
        fig.suptitle(f"{battery}: Phase 2 fusion sequence-length ablation")
        fig.tight_layout()
        fig.savefig(output_root / f"{battery}_fusion_seq_ablation.png", dpi=160)
        plt.close(fig)


def write_report(output_root: Path, counts: pd.DataFrame, all_runs: pd.DataFrame, ranked: pd.DataFrame):
    def markdown_table(frame: pd.DataFrame) -> str:
        view = frame.copy()
        for column in view.select_dtypes(include=[np.number]).columns:
            view[column] = view[column].map(lambda value: f"{value:.6g}")
        header = "| " + " | ".join(map(str, view.columns)) + " |"
        divider = "| " + " | ".join(["---"] * len(view.columns)) + " |"
        body = ["| " + " | ".join(map(str, row)) + " |" for row in view.itertuples(index=False, name=None)]
        return "\n".join([header, divider, *body])
    b18 = all_runs.loc[all_runs["Battery"] == "B0018"].groupby(["FusionType", "FusionSeqLen"], as_index=False).agg(
        MeanRMSE=("RMSE", "mean"), RMSEStd=("RMSE", lambda x: x.std(ddof=0)), MeanR2=("R2", "mean"),
        WorstR2=("R2", "min"), FailureRate=("CatastrophicPredictionCount", lambda x: (x > 0).mean()),
    )
    b18_samples = counts.loc[counts["Battery"] == "B0018"].set_index("FusionSeqLen")["FusionTrainingSamples"]
    increase = (b18_samples.loc[4] / b18_samples.loc[10] - 1.0) * 100.0
    no_primary = not bool(ranked["AllRunsQualified"].any()) and float(b18["MeanR2"].max()) <= 0
    lines = [
        "# Phase 2 — Fusion Sequence Length & Sample Efficiency Ablation", "",
        "## Protocol", "", "Only `fusion_seq_len` was changed: 4, 6, 8, and 10.  The Phase-1 saved component predictions were reused.",
        "All runs used B0007/B0018, seeds 42/123/2024/3407/7777, target first-20% labelled training, next-20% validation, and an unopened locked test split.",
        "Paper Fusion was completed first, then constrained residual fusion with the Phase-1-selected epsilon=0.05.", "",
        "## Actual sample counts", "", markdown_table(counts), "",
        "## Robustness ranking", "", markdown_table(ranked), "",
        "## B0018 special report", "",
        f"B0018 fusion training samples increase from {int(b18_samples.loc[10])} at seq_len=10 to {int(b18_samples.loc[4])} at seq_len=4 ({increase:.1f}%).",
        markdown_table(b18), "",
        "## Research-question answers", "",
        "RQ2.1: sample efficiency is reported from the actual production Dataset arrays above, not an approximation.",
        "RQ2.2: compare the per-configuration RMSE standard deviations in the ranking and battery plots; lower is more seed-stable.",
        "RQ2.3: the residual-fusion rows isolate whether shorter context reduces catastrophic predictions under the same epsilon=0.05 bound.",
        "RQ2.4: Paper Fusion and residual fusion are separate lines in every plot and table; they are not merged into a paper claim.",
        "RQ2.5: weight entropy and temporal variation are logged per run; Phase 2 does not introduce KL or smoothing.",
        "RQ2.6: qualification requires every battery × seed run to pass all preregistered gates, rather than choosing a best seed.", "",
        "## Decision", "",
        "NO_QUALIFIED_CONFIGURATION" if not bool(ranked["AllRunsQualified"].any()) else "QUALIFIED_CONFIGURATION_EXISTS",
        "SEQUENCE_LENGTH_NOT_PRIMARY_BOTTLENECK" if no_primary else "SEQUENCE_LENGTH_EFFECT_REQUIRES_FURTHER_INTERPRETATION",
        "", "Stop condition reached: no LayerNorm, KL, smoothing, transfer, CALCE, or grid-search experiment was started.",
    ]
    (output_root / "PHASE2_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_environment(output_root: Path):
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        commit = "UNAVAILABLE"
    (output_root / "environment.txt").write_text(
        f"python={sys.version}\ntorch={torch.__version__}\nplatform={platform.platform()}\ngit_commit={commit}\n",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--sample-count-only", action="store_true")
    args = parser.parse_args()
    output_root = args.output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    counts = build_sample_counts()
    counts.to_csv(output_root / "sample_count_by_seq.csv", index=False, encoding="utf-8-sig")
    print(counts.to_string(index=False), flush=True)
    if args.sample_count_only:
        return
    all_metrics, all_baselines = [], []
    total = 2 * len(SEQ_LENS) * len(SEEDS) * len(BATTERIES)
    index = 0
    for fusion_type in ("PAPER_FUSION", "IPRF_RESIDUAL_FUSION"):
        for seq_len in SEQ_LENS:
            for seed in SEEDS:
                for battery in BATTERIES:
                    index += 1
                    print(f"[Phase 2 {index}/{total}] {fusion_type} seq={seq_len} seed={seed} battery={battery}", flush=True)
                    metrics, baselines = run_one(output_root, counts, fusion_type, seq_len, seed, battery)
                    all_metrics.append(metrics); all_baselines.extend(baselines)
    metrics_frame = pd.DataFrame(all_metrics)
    baseline_frame = pd.DataFrame(all_baselines)
    all_runs, ranked = aggregate(metrics_frame, baseline_frame)
    all_runs.to_csv(output_root / "all_run_metrics_with_gates.csv", index=False, encoding="utf-8-sig")
    baseline_frame.to_csv(output_root / "baseline_metrics.csv", index=False, encoding="utf-8-sig")
    ranked.to_csv(output_root / "ranked_configurations.csv", index=False, encoding="utf-8-sig")
    write_environment(output_root)
    plot_results(output_root, all_runs, counts)
    write_report(output_root, counts, all_runs, ranked)
    print(ranked.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
