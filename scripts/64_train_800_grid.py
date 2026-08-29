"""Validation-only, staged 800-epoch search for the strict paper pipeline.

The search never loads the target test split.  It first screens a compact
two-level structural factorial, then tunes the reproduction-defined
``lambda_weight`` on promoted structures, and finally repeats the strongest
validation candidates across five fixed seeds.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import torch


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

GRID_ROOT = ROOT / "output" / "paper_800_grid_v1"
DEFAULT_AUG_DIR = ROOT / "output" / "scf_gan_800_v1" / "aug"
TARGETS = ("B0007", "B0018")
MAX_EPOCHS = 800
DEFAULT_PATIENCE = 100
PHASE_SEEDS = {
    "coarse": (42,),
    "promotion": (42, 52, 62),
    "final": (42, 52, 62, 72, 82),
}


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise ImportError(path)
    spec.loader.exec_module(module)
    return module


def stable_id(prefix: str, tunable: dict) -> str:
    payload = json.dumps(tunable, sort_keys=True, ensure_ascii=False).encode()
    return f"{prefix}_{hashlib.sha256(payload).hexdigest()[:10]}"


def make_record(phase: str, tunable: dict, parent: str | None = None) -> dict:
    return {
        "schema": "strict_validation_grid/1",
        "config_id": stable_id(phase[0].upper(), tunable),
        "phase": phase,
        "parent_config_id": parent,
        "tunable": tunable,
        "training": {"max_epochs": MAX_EPOCHS, "early_stopping": True},
        "data_boundary": {
            "sources": ["B0005", "B0006"],
            "targets": list(TARGETS),
            "target_train_prefix": 0.20,
            "target_validation_fraction": 0.20,
            "test_loaded": False,
        },
        "l_weight": {
            "paper_definition_disclosed": False,
            "status": "REPRO_DEFINED_NOT_PAPER_ORIGINAL",
            "formula": "KL(mean_batch(component_weights) || Uniform(3))",
        },
    }


def coarse_records() -> list[dict]:
    """16 factorial corners plus two centre controls (18 candidates)."""
    records = []
    architectures = (
        {"timesnet_top_k": 2, "itransformer_heads": 2, "itransformer_layers": 1},
        {"timesnet_top_k": 3, "itransformer_heads": 4, "itransformer_layers": 2},
    )
    for seq, period, width, arch in itertools.product(
        (8, 12), (8, 16), (32, 64), architectures
    ):
        tunable = {
            "sequence_length": seq,
            "stl_period": period,
            "timesnet_width": width,
            **arch,
            "lambda_weight": 0.01,
        }
        records.append(make_record("coarse", tunable))
    for width, arch in ((32, architectures[0]), (64, architectures[1])):
        records.append(make_record("coarse", {
            "sequence_length": 10, "stl_period": 12, "timesnet_width": width,
            **arch, "lambda_weight": 0.01,
        }))
    return records


def config_path(phase: str) -> Path:
    return GRID_ROOT / "configs" / f"{phase}.json"


def write_phase(phase: str, records: list[dict]) -> None:
    path = config_path(phase)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{phase}: 已写入 {len(records)} 个配置 -> {path}")


def read_phase(phase: str) -> list[dict]:
    path = config_path(phase)
    if not path.exists():
        raise FileNotFoundError(f"缺少 {path}；请先运行相应 build 命令")
    return json.loads(path.read_text(encoding="utf-8"))


def result_files(phase: str) -> list[Path]:
    return list((GRID_ROOT / "runs" / phase).glob("*/seed*/validation_metrics.csv"))


def rank_phase(phase: str) -> pd.DataFrame:
    files = result_files(phase)
    if not files:
        raise RuntimeError(f"{phase} 尚无验证结果")
    frame = pd.concat((pd.read_csv(p) for p in files), ignore_index=True)
    required = {"ConfigID", "Seed", "BatteryID", "RMSE", "MAE", "R2", "TestResultsViewed"}
    if missing := required.difference(frame.columns):
        raise ValueError(f"验证结果缺少列：{sorted(missing)}")
    if frame["TestResultsViewed"].astype(str).str.lower().isin(["true", "1"]).any():
        raise RuntimeError("发现访问测试结果的记录，拒绝用于超参数选择")
    per_run = frame.groupby(["ConfigID", "Seed"], as_index=False).agg(
        MeanRMSE=("RMSE", "mean"), WorstBatteryRMSE=("RMSE", "max"),
        MeanMAE=("MAE", "mean"), MeanR2=("R2", "mean"), BatteryCount=("BatteryID", "nunique"),
    )
    per_run = per_run[per_run.BatteryCount.eq(len(TARGETS))]
    ranked = per_run.groupby("ConfigID", as_index=False).agg(
        ValidationRMSE=("MeanRMSE", "mean"),
        ValidationRMSEStd=("MeanRMSE", "std"),
        WorstBatteryRMSE=("WorstBatteryRMSE", "mean"),
        ValidationMAE=("MeanMAE", "mean"), ValidationR2=("MeanR2", "mean"),
        CompletedSeeds=("Seed", "nunique"),
    )
    ranked["ValidationRMSEStd"] = ranked["ValidationRMSEStd"].fillna(0.0)
    ranked = ranked.sort_values(
        ["ValidationRMSE", "WorstBatteryRMSE", "ValidationRMSEStd", "ConfigID"]
    ).reset_index(drop=True)
    ranked.insert(0, "ValidationRank", np.arange(1, len(ranked) + 1))
    out = GRID_ROOT / "rankings"
    out.mkdir(parents=True, exist_ok=True)
    ranked.to_csv(out / f"{phase}_validation_ranking.csv", index=False, encoding="utf-8-sig")
    return ranked


def build(args: argparse.Namespace) -> None:
    if args.phase == "coarse":
        write_phase("coarse", coarse_records())
        return
    parent_phase = "coarse" if args.phase == "promotion" else "promotion"
    parent_records = {r["config_id"]: r for r in read_phase(parent_phase)}
    ranking = rank_phase(parent_phase)
    expected = len(PHASE_SEEDS[parent_phase])
    eligible = ranking[ranking.CompletedSeeds.eq(expected)]
    top_n = 4 if args.phase == "promotion" else 3
    if len(eligible) < top_n:
        raise RuntimeError(f"{parent_phase} 完整候选不足 {top_n} 个，不能晋级")
    selected = eligible.head(top_n).ConfigID.tolist()
    records = []
    if args.phase == "promotion":
        for parent_id in selected:
            base = dict(parent_records[parent_id]["tunable"])
            for value in (0.0, 0.001, 0.01, 0.1):
                tunable = {**base, "lambda_weight": value}
                records.append(make_record("promotion", tunable, parent_id))
    else:
        for parent_id in selected:
            base = dict(parent_records[parent_id]["tunable"])
            records.append(make_record("final", base, parent_id))
    write_phase(args.phase, records)


def validate_augmented_data(aug_dir: Path) -> None:
    for battery in TARGETS:
        path = aug_dir / f"{battery}_aug_train_hf.csv"
        if not path.exists():
            raise FileNotFoundError(f"缺少 {path}；请先完成 SCF-GAN 800轮重训与增强")


def progress_bar(current: int, total: int, width: int = 24) -> str:
    """Return a dependency-free terminal progress bar."""
    total = max(total, 1)
    filled = round(width * current / total)
    return f"[{'#' * filled}{'-' * (width - filled)}] {current}/{total}"


def run(args: argparse.Namespace) -> None:
    if args.epochs != MAX_EPOCHS:
        raise ValueError(f"该协议固定 max_epochs={MAX_EPOCHS}，拒绝改为 {args.epochs}")
    aug_dir = Path(args.aug_dir).resolve()
    validate_augmented_data(aug_dir)
    records = read_phase(args.phase)
    wanted = set(x.strip() for x in args.config_ids.split(",") if x.strip()) if args.config_ids else None
    if wanted:
        records = [r for r in records if r["config_id"] in wanted]
    seeds = tuple(int(x) for x in args.seeds.split(",")) if args.seeds else PHASE_SEEDS[args.phase]
    if not set(seeds).issubset(PHASE_SEEDS[args.phase]):
        raise ValueError(f"{args.phase} 只允许预注册 seeds={PHASE_SEEDS[args.phase]}")
    engine = load(ROOT / "scripts" / "08_physics_trend_ablation.py", "strict_grid_engine")
    total_groups = len(records)
    total_runs = total_groups * len(seeds)
    completed_runs = 0
    print(
        f"{args.phase} 进度：{progress_bar(0, total_groups)} 组配置；"
        f"训练 0/{total_runs} 次"
    )
    for group_index, record in enumerate(records, start=1):
        cfg = record["tunable"]
        for seed in seeds:
            print(
                f"\r{args.phase}：第 {group_index}/{total_groups} 组 "
                f"({record['config_id']})，seed={seed}；"
                f"训练 {completed_runs + 1}/{total_runs}",
                end="", flush=True,
            )
            out = GRID_ROOT / "runs" / args.phase / record["config_id"] / f"seed{seed}"
            metrics_path = out / "validation_metrics.csv"
            if metrics_path.exists() and not args.rerun:
                completed_runs += 1
                print(" 已完成，跳过")
                continue
            out.mkdir(parents=True, exist_ok=True)
            engine.ts.SEQ_LEN = int(cfg["sequence_length"])
            engine.ts.STL_PERIOD = int(cfg["stl_period"])
            engine.fusion.LAMBDA_WEIGHT = float(cfg["lambda_weight"])
            rows, manifests = [], []
            for battery in TARGETS:
                battery_rows, _, manifest = engine.run_battery(
                    battery, ["none"], 0.0, MAX_EPOCHS, args.patience, out,
                    seed, "validation", False, True, False,
                    train_fraction=0.20, validation_fraction=0.20,
                    model_config=cfg, aug_dir=aug_dir,
                )
                for row in battery_rows:
                    row.update({
                        "ConfigID": record["config_id"], "Phase": args.phase,
                        "Seed": seed, "TestResultsViewed": False, **cfg,
                    })
                rows.extend(battery_rows)
                manifests.append(manifest)
            pd.DataFrame(rows).to_csv(metrics_path, index=False, encoding="utf-8-sig")
            (out / "manifest.json").write_text(json.dumps({
                "completed_at": datetime.now().isoformat(), "record": record,
                "seed": seed, "max_epochs": MAX_EPOCHS, "patience": args.patience,
                "evaluation_split": "validation", "test_labels_loaded": False,
                "augmentation_dir": str(aug_dir), "battery_manifests": manifests,
            }, ensure_ascii=False, indent=2), encoding="utf-8")
            completed_runs += 1
            print(" 完成")
        print(
            f"{args.phase} 组进度：{progress_bar(group_index, total_groups)}；"
            f"训练 {completed_runs}/{total_runs} 次"
        )


def show_rank(args: argparse.Namespace) -> None:
    ranked = rank_phase(args.phase)
    print(ranked.head(args.top).to_string(index=False))


def run_all(args: argparse.Namespace) -> None:
    """Execute the pre-registered search phases in their required order."""
    for phase in ("coarse", "promotion", "final"):
        print(f"\n{'=' * 20} 开始阶段：{phase} {'=' * 20}")
        build(argparse.Namespace(phase=phase))
        run(argparse.Namespace(
            phase=phase,
            epochs=MAX_EPOCHS,
            patience=args.patience,
            seeds=None,
            config_ids=None,
            aug_dir=args.aug_dir,
            rerun=args.rerun,
        ))
        show_rank(argparse.Namespace(phase=phase, top=20))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    build_parser = sub.add_parser("build")
    build_parser.add_argument("--phase", choices=PHASE_SEEDS, required=True)
    run_parser = sub.add_parser("run")
    run_parser.add_argument("--phase", choices=PHASE_SEEDS, required=True)
    run_parser.add_argument("--epochs", type=int, default=MAX_EPOCHS)
    run_parser.add_argument("--patience", type=int, default=DEFAULT_PATIENCE)
    run_parser.add_argument("--seeds")
    run_parser.add_argument("--config-ids")
    run_parser.add_argument("--aug-dir", default=str(DEFAULT_AUG_DIR))
    run_parser.add_argument("--rerun", action="store_true")
    rank_parser = sub.add_parser("rank")
    rank_parser.add_argument("--phase", choices=PHASE_SEEDS, required=True)
    rank_parser.add_argument("--top", type=int, default=20)
    all_parser = sub.add_parser("all")
    all_parser.add_argument("--patience", type=int, default=DEFAULT_PATIENCE)
    all_parser.add_argument("--aug-dir", default=str(DEFAULT_AUG_DIR))
    all_parser.add_argument("--rerun", action="store_true")
    args = parser.parse_args()
    {"build": build, "run": run, "rank": show_rank, "all": run_all}[args.command](args)


if __name__ == "__main__":
    main()
