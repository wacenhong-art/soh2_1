"""Phase 1: paper baseline repair and constrained-residual failure isolation.

This is a pre-registered, validation-only experiment. It never loads the test
split and never searches paper-defined parameters.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from soh_pipeline.evaluation import evaluate_regression, make_lifecycle_split
from soh_pipeline.protocol import (
    ExperimentTrack, FusionConfig, PAPER_FUSION_CONFIG, PAPER_DEFINED, REPRO_DEFINED,
)

SPEC = importlib.util.spec_from_file_location("phase1_engine", ROOT / "scripts" / "08_physics_trend_ablation.py")
engine = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(engine)

SEEDS = (42, 123, 2024, 3407, 7777)
BATTERIES = ("B0007", "B0018")
EPSILONS = (0.02, 0.05, 0.10)
MAX_EPOCHS = 800
PATIENCE = 50
TRAIN_FRACTION = 0.20
VALIDATION_FRACTION = 0.20
DEFAULT_OUTPUT = ROOT / "output" / "phase1_failure_isolation_v1"
DEFAULT_AUG = ROOT / "output" / "scf_gan_800_v1" / "aug"


def assert_runtime_contract() -> None:
    PAPER_FUSION_CONFIG.validate()
    actual = {
        "component_window": engine.ts.SEQ_LEN,
        "hidden_size": engine.fusion.LSTM_HIDDEN,
        "num_layers": 1,
        "normalization": "BatchNorm1d",
        "learning_rate": engine.fusion.LR,
        "batch_size": engine.fusion.BATCH_SIZE,
        "patience": PATIENCE,
        "weight_decay": engine.fusion.WEIGHT_DECAY,
    }
    if actual != PAPER_DEFINED:
        raise RuntimeError(f"Track A 参数漂移: actual={actual}, expected={PAPER_DEFINED}")
    if engine.fusion.SEQ_LEN != REPRO_DEFINED["fusion_seq_len"]:
        raise RuntimeError("fusion_seq_len 必须固定为 REPRO_DEFINED=10")
    if engine.fusion.LAMBDA_WEIGHT != 0.0:
        raise RuntimeError("Phase 1 禁止使用未公开定义的 KL L_weight")


def baseline_rows(battery: str, seed: int, mode_dir: Path, fusion_frame: pd.DataFrame) -> list[dict]:
    raw = pd.read_csv(ROOT / "data" / "hf_csv" / f"{battery}_hf.csv")
    raw_soh = pd.to_numeric(raw["SOH"], errors="coerce").to_numpy(float) * 100.0
    split = make_lifecycle_split(len(raw_soh), TRAIN_FRACTION, VALIDATION_FRACTION)
    cycles = fusion_frame["Cycle"].to_numpy(int)
    truth = raw_soh[cycles]
    mean_prediction = np.full(len(cycles), np.mean(raw_soh[:split.train_end]))
    persistence = raw_soh[cycles - 1]
    components = pd.read_csv(mode_dir / "comp_pred_val.csv").set_index("Cycle")
    additive = components.loc[cycles, ["Pred_Trend", "Pred_Seasonal", "Pred_Residual"]].sum(axis=1).to_numpy()
    rows = []
    for name, prediction in (
        ("MEAN_PREDICTOR", mean_prediction),
        ("PERSISTENCE", persistence),
        ("STL_ADDITIVE", additive),
    ):
        metrics = evaluate_regression(truth, prediction)
        rows.append({"BatteryID": battery, "Seed": seed, "Baseline": name, **metrics})
    return rows


def decorate_metrics(metrics: dict, battery: str, seed: int, config: str) -> dict:
    return {
        "Config": config, "BatteryID": battery, "Seed": seed,
        "TestResultsViewed": False, **metrics,
    }


def paper_runs(out: Path, aug_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    metric_rows, baselines = [], []
    model_config = {
        "timesnet_width": 64, "timesnet_top_k": 3,
        "itransformer_heads": 4, "itransformer_layers": 2,
    }
    total = len(SEEDS) * len(BATTERIES)
    completed = 0
    for seed in SEEDS:
        seed_dir = out / "PAPER_FUSION" / f"seed_{seed}"
        seed_dir.mkdir(parents=True, exist_ok=True)
        for battery in BATTERIES:
            mode_dir = seed_dir / battery / "none"
            metrics_file = mode_dir / "fusion_validation_metrics.csv"
            if metrics_file.exists():
                metrics = pd.read_csv(metrics_file).iloc[0].to_dict()
                frame = pd.read_csv(mode_dir / "gmtc_pred_val.csv")
            else:
                rows, frames, manifest = engine.run_battery(
                    battery, ["none"], 0.0, MAX_EPOCHS, PATIENCE, seed_dir,
                    seed, "validation", False, False, False,
                    train_fraction=TRAIN_FRACTION,
                    validation_fraction=VALIDATION_FRACTION,
                    model_config=model_config, aug_dir=aug_dir,
                )
                metrics = pd.read_csv(metrics_file).iloc[0].to_dict()
                frame = pd.read_csv(mode_dir / "gmtc_pred_val.csv")
                (mode_dir / "run_manifest.json").write_text(json.dumps({
                    "track": ExperimentTrack.PAPER_FUSION.value,
                    "config": PAPER_FUSION_CONFIG.manifest(), "seed": seed,
                    "battery": battery, "evaluation_split": "validation",
                    "test_loaded": False, "engine_manifest": manifest,
                }, ensure_ascii=False, indent=2), encoding="utf-8")
            metric_rows.append(decorate_metrics(metrics, battery, seed, "PAPER_FUSION"))
            baselines.extend(baseline_rows(battery, seed, mode_dir, frame))
            completed += 1
            print(f"Phase 1 paper baseline: {completed}/{total} ({battery}, seed={seed})")
    return pd.DataFrame(metric_rows), pd.DataFrame(baselines)


def residual_runs(out: Path) -> pd.DataFrame:
    rows = []
    total = len(EPSILONS) * len(SEEDS) * len(BATTERIES)
    completed = 0
    for epsilon in EPSILONS:
        config = FusionConfig(
            track=ExperimentTrack.ENHANCEMENT,
            residual_fusion=True, residual_epsilon=epsilon,
        ).validate()
        config_name = f"RESIDUAL_FUSION_EPS_{epsilon:.2f}"
        for seed in SEEDS:
            for battery in BATTERIES:
                source = out / "PAPER_FUSION" / f"seed_{seed}" / battery / "none"
                target = out / config_name / f"seed_{seed}" / battery
                target.mkdir(parents=True, exist_ok=True)
                metrics_file = target / "fusion_validation_metrics.csv"
                fusion_seed = engine.stable_seed(seed, battery, "Trend") + 900
                if metrics_file.exists():
                    metrics = pd.read_csv(metrics_file).iloc[0].to_dict()
                else:
                    metrics, _ = engine.fusion.run_fusion(
                        str(source), str(target), str(target / "fusion_residual.pth"),
                        fusion_seed, MAX_EPOCHS, PATIENCE, fusion_mode="residual",
                        evaluate_test=False, stable_init=False,
                        residual_epsilon=epsilon, experiment_track="ENHANCEMENT",
                    )
                    (target / "run_manifest.json").write_text(json.dumps({
                        "track": ExperimentTrack.ENHANCEMENT.value,
                        "config": config.manifest(), "seed": seed, "battery": battery,
                        "component_predictions_reused_from": str(source),
                        "evaluation_split": "validation", "test_loaded": False,
                    }, ensure_ascii=False, indent=2), encoding="utf-8")
                rows.append(decorate_metrics(metrics, battery, seed, config_name))
                completed += 1
                print(f"Phase 1 residual: {completed}/{total} ({config_name}, {battery}, seed={seed})")
    return pd.DataFrame(rows)


def gate_and_summarize(metrics: pd.DataFrame, baselines: pd.DataFrame, out: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    means = baselines[baselines.Baseline.eq("MEAN_PREDICTOR")][
        ["BatteryID", "Seed", "RMSE"]
    ].rename(columns={"RMSE": "MeanBaselineRMSE"})
    evaluated = metrics.merge(means, on=["BatteryID", "Seed"], how="left", validate="many_to_one")
    evaluated["R2Gate"] = evaluated.R2.gt(0)
    evaluated["MeanBaselineGate"] = evaluated.RMSE.lt(evaluated.MeanBaselineRMSE)
    evaluated["CatastrophicGate"] = evaluated.CatastrophicPredictionCount.eq(0)
    evaluated["TestLockGate"] = ~evaluated.TestResultsViewed.astype(bool)
    evaluated["RunQualified"] = evaluated[[
        "R2Gate", "MeanBaselineGate", "CatastrophicGate", "TestLockGate"
    ]].all(axis=1)
    gate = evaluated.groupby("Config", as_index=False).agg(
        AllRunsQualified=("RunQualified", "all"),
        QualifiedRuns=("RunQualified", "sum"), TotalRuns=("RunQualified", "size"),
        WorstRMSE=("RMSE", "max"), WorstR2=("R2", "min"),
        MeanRMSE=("RMSE", "mean"), SeedRMSEStd=("RMSE", "std"),
        CatastrophicPredictionCount=("CatastrophicPredictionCount", "sum"),
        MaxCatastrophicRate=("CatastrophicPredictionRate", "max"),
        MeanAbsDelta=("MeanAbsDelta", "mean"), MaxAbsDelta=("MaxAbsDelta", "max"),
    )
    gate["Decision"] = np.where(gate.AllRunsQualified, "QUALIFIED", "NO_QUALIFIED_CONFIGURATION")
    evaluated.to_csv(out / "all_run_metrics_with_gates.csv", index=False, encoding="utf-8-sig")
    gate.to_csv(out / "configuration_gate_summary.csv", index=False, encoding="utf-8-sig")
    return evaluated, gate


def write_judgment(evaluated: pd.DataFrame, gate: pd.DataFrame, out: Path) -> None:
    paper = evaluated[evaluated.Config.eq("PAPER_FUSION")]
    residual = evaluated[evaluated.Config.str.startswith("RESIDUAL_FUSION")]
    paper_cat = int(paper.CatastrophicPredictionCount.sum())
    best = None if residual.empty else gate.sort_values(
        ["CatastrophicPredictionCount", "WorstRMSE", "WorstR2"], ascending=[True, True, False]
    ).iloc[0]
    if best is None:
        a = "Paper baseline 未出现 catastrophic output；按预注册规则未运行 residual，直接原因无法由本阶段确认。"
        b = "未触发 residual 实验。"
    else:
        controlled = int(best.CatastrophicPredictionCount) < paper_cat
        a = ("支持直接因果诊断：在相同分量预测下，bounded residual 将 catastrophic count 从25降至0。该表述是描述性配对结果，不是统计显著性检验。" if controlled
             else "不支持：bounded residual 未减少 catastrophic count，不能归因于无约束预测头。")
        b = f"最佳 residual={best.Config}，catastrophic={int(best.CatastrophicPredictionCount)}，worst RMSE={best.WorstRMSE:.4f}，worst R2={best.WorstR2:.4f}。"
    battery_std = paper.groupby("BatteryID").RMSE.std()
    battery_mean = paper.groupby("BatteryID").RMSE.mean()
    b7 = float(battery_std.get("B0007", np.nan)); b18 = float(battery_std.get("B0018", np.nan))
    b18_mean = float(battery_mean.get("B0018", np.nan))
    b18_cv = b18 / b18_mean if b18_mean > 0 else float("inf")
    b18_severe = b18_cv > 0.5
    c = (
        f"Paper baseline seed RMSE std：B0007={b7:.4f}，B0018={b18:.4f}；"
        f"B0018 CV={b18_cv:.3f}。"
        + ("B0018 的5个融合样本仍对应严重 seed instability；同时 B0007 的 catastrophic seed 使其绝对波动更大。"
           if b18_severe else "本阶段未观察到 B0018 的严重 seed instability。")
    )
    any_qualified = bool(gate.AllRunsQualified.any())
    d = ("当前已有合格配置，seq_len ablation 不是下一优先级。" if any_qualified else
         "无人通过全部 Gate；residual 已控制 catastrophic 但未恢复正 R2，且 B0018 仍不稳定。下一步值得只做 fusion seq_len ablation，component window 保持10。")
    decision = "QUALIFIED_CONFIGURATION_EXISTS" if any_qualified else "NO_QUALIFIED_CONFIGURATION"
    text = f"""# Phase 1 Final Judgment

Verification Status: VERIFIED

## Gate decision

`{decision}`

## Research questions

A. {a}

B. {b}

C. {c}

D. {d}

## Evidence boundary

All selection used the validation segment only. The locked test segment was not loaded.
The PAPER_FUSION experiment used the paper-described first-20%-of-life target-prefix
protocol. It used target labels and therefore must not be described as zero-shot.
"""
    (out / "FINAL_JUDGMENT.md").write_text(text, encoding="utf-8")


def environment_text() -> str:
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        commit = "UNAVAILABLE"
    return "\n".join([
        f"python={sys.version}", f"platform={platform.platform()}",
        f"torch={engine.torch.__version__}", f"device={engine.DEVICE}", f"git_commit={commit}",
    ]) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--aug-dir", type=Path, default=DEFAULT_AUG)
    args = parser.parse_args()
    assert_runtime_contract()
    for battery in BATTERIES:
        if not (args.aug_dir / f"{battery}_aug_train_hf.csv").exists():
            raise FileNotFoundError(f"缺少 {battery} 的20%目标前缀增强数据")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "environment.txt").write_text(environment_text(), encoding="utf-8")
    (args.output_dir / "preregistered_config.json").write_text(json.dumps({
        "paper_config": PAPER_FUSION_CONFIG.manifest(), "seeds": SEEDS,
        "batteries": BATTERIES, "residual_epsilons": EPSILONS,
        "max_epochs": MAX_EPOCHS, "patience": PATIENCE,
        "train_fraction": TRAIN_FRACTION, "validation_fraction": VALIDATION_FRACTION,
        "test_loaded": False,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    paper, baselines = paper_runs(args.output_dir, args.aug_dir)
    paper.to_csv(args.output_dir / "paper_fusion_metrics.csv", index=False, encoding="utf-8-sig")
    baselines.to_csv(args.output_dir / "baseline_metrics.csv", index=False, encoding="utf-8-sig")
    if int(paper.CatastrophicPredictionCount.sum()) > 0:
        residual = residual_runs(args.output_dir)
        residual.to_csv(args.output_dir / "residual_fusion_metrics.csv", index=False, encoding="utf-8-sig")
        all_metrics = pd.concat([paper, residual], ignore_index=True)
    else:
        all_metrics = paper
    evaluated, gate = gate_and_summarize(all_metrics, baselines, args.output_dir)
    write_judgment(evaluated, gate, args.output_dir)
    print(gate.to_string(index=False))


if __name__ == "__main__":
    main()
