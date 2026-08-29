"""Train validation-only hyperparameter-grid configurations.

The builder in ``58_build_hyperparameter_grid.py`` writes candidate JSON files.
This runner reads those JSON files and executes the supported stage.  It is
deliberately validation-only by default: do not use it for final test runs.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GRID_ROOT = ROOT / "output" / "hyperparameter_grid_refined_v1"
SUPPORTED_STAGES = [
    "D_trend_physics",
    "D_top4_validation",
    "D_local_best",
    "D_stability_screen",
    "D_exhaustive_1000",
]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise ImportError(path)
    spec.loader.exec_module(module)
    return module


def load_configs(grid_root: Path, stage: str) -> list[dict]:
    config_dir = grid_root / "configs" / stage
    if not config_dir.exists():
        raise FileNotFoundError(
            f"缺少配置目录: {config_dir}. 请先运行 58_build_hyperparameter_grid.py 生成该阶段配置。"
        )
    configs = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(config_dir.glob("*.json"))
    ]
    if not configs:
        raise RuntimeError(f"{config_dir} 中没有 JSON 配置")
    return sorted(configs, key=lambda config: int(str(config["attempt_id"])[1:]))


def parse_seeds(args: argparse.Namespace) -> list[int]:
    if not args.seeds:
        return [int(args.seed)]
    seeds = []
    for item in args.seeds.split(","):
        item = item.strip()
        if item:
            seeds.append(int(item))
    if not seeds:
        raise SystemExit("--seeds 没有解析到有效 seed")
    return seeds


def tunable_seed_key(config: dict, seed: int) -> tuple:
    tunable = config["tunable"]
    return (
        str(tunable["physics_mode"]),
        f"{float(tunable['lambda_phy']):.12g}",
        f"{float(tunable['lambda_weight']):.12g}",
        int(tunable["physics_epoch_cap"]),
        int(tunable["physics_patience"]),
        int(seed),
    )


def load_equivalent_completed_keys(grid_root: Path) -> set[tuple]:
    keys = set()
    runs_root = grid_root / "runs"
    if not runs_root.exists():
        return keys
    for manifest_path in runs_root.glob("*/*/run_manifest.json"):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if manifest.get("status") != "completed":
            continue
        config = manifest.get("config")
        seed = manifest.get("seed")
        if not config or seed is None:
            continue
        try:
            keys.add(tunable_seed_key(config, int(seed)))
        except (KeyError, TypeError, ValueError):
            continue
    return keys


def runs_root(args: argparse.Namespace) -> Path:
    return args.runs_root if args.runs_root is not None else args.grid_root / "runs"


def run_d_trend_physics(config: dict, args: argparse.Namespace, engine, seed: int) -> list[dict]:
    tunable = config["tunable"]
    mode = str(tunable["physics_mode"])
    lam = float(tunable["lambda_phy"])
    lambda_weight = float(tunable["lambda_weight"])
    epochs = int(tunable["physics_epoch_cap"])
    patience = int(tunable["physics_patience"])

    if mode != "monotonic":
        raise ValueError(f"{config['stage']} 当前只允许运行 monotonic，收到: {mode}")

    run_dir = (
        runs_root(args) / args.stage /
        f"{config['attempt_id']}_{config['config_hash'][:10]}_seed{seed}"
    )
    marker = run_dir / "run_manifest.json"
    if marker.exists() and not args.rerun:
        return [{
            "AttemptID": config["attempt_id"],
            "ConfigHash": config["config_hash"],
            "Status": "skipped_completed",
            "RunDir": str(run_dir),
            "TestResultsViewed": False,
        }]

    run_dir.mkdir(parents=True, exist_ok=True)
    engine.reset_seed(seed)
    engine.fusion.LAMBDA_WEIGHT = lambda_weight

    rows: list[dict] = []
    frames = []
    protocols = []
    for battery in args.batteries.split(","):
        battery = battery.strip()
        battery_rows, battery_frames, protocol = engine.run_battery(
            battery=battery,
            modes=[mode],
            lam=lam,
            epochs=epochs,
            patience=patience,
            out_dir=run_dir,
            seed=seed,
            evaluation_split="validation",
            fusion_stable_init=args.fusion_stable_init,
            use_component_lag=not args.hf_only_components,
            clip_recursive_state=args.clip_recursive_state,
            train_fraction=args.train_fraction,
            validation_fraction=args.validation_fraction,
            aug_dir=args.aug_dir,
        )
        rows.extend(battery_rows)
        frames.extend(battery_frames)
        protocols.append(protocol)

    metrics = pd.DataFrame(rows)
    predictions = pd.concat(frames, ignore_index=True)
    for frame in (metrics, predictions):
        frame.insert(0, "AttemptID", config["attempt_id"])
        frame.insert(1, "ConfigHash", config["config_hash"])
        frame.insert(2, "Seed", seed)
        frame.insert(3, "TestResultsViewed", False)

    metrics.to_csv(run_dir / "validation_metrics.csv", index=False, encoding="utf-8-sig")
    predictions.to_csv(run_dir / "validation_predictions.csv", index=False, encoding="utf-8-sig")

    manifest = {
        "schema": "soh_hyperparameter_grid_run/1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "status": "completed",
        "stage": args.stage,
        "protocol_name": args.protocol_name,
        "source_batteries": [item.strip() for item in args.source_batteries.split(",") if item.strip()],
        "config": config,
        "seed": seed,
        "batteries": [item.strip() for item in args.batteries.split(",")],
        "evaluation_split": "validation",
        "test_results_viewed": False,
        "protocols": protocols,
    }
    marker.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = []
    for row in metrics.to_dict("records"):
        row.update({
            "AttemptID": config["attempt_id"],
            "ConfigHash": config["config_hash"],
            "Seed": seed,
            "Status": "completed",
            "RunDir": str(run_dir),
            "TestResultsViewed": False,
        })
        summary.append(row)
    return summary


def write_summary(rows: list[dict], summary_path: Path) -> None:
    if not rows:
        return
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(
        summary_path,
        mode="a",
        header=not summary_path.exists(),
        index=False,
        encoding="utf-8-sig",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train validation-only hyperparameter grid configs.")
    parser.add_argument("--stage", default="D_trend_physics", choices=SUPPORTED_STAGES)
    parser.add_argument("--grid-root", type=Path, default=DEFAULT_GRID_ROOT)
    parser.add_argument("--runs-root", type=Path, default=None)
    parser.add_argument("--start-index", type=int, default=1, help="1-based config index.")
    parser.add_argument("--max-configs", type=int, default=1)
    parser.add_argument("--preview-limit", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--seeds", default="", help="Comma-separated seeds, e.g. 42,52,62,72,82.")
    parser.add_argument("--batteries", default="B0007,B0018")
    parser.add_argument("--source-batteries", default="B0005,B0006")
    parser.add_argument("--protocol-name", default="Source5_6_Target7_18")
    parser.add_argument("--aug-dir", type=Path, default=ROOT / "output")
    parser.add_argument("--train-fraction", type=float, default=0.6)
    parser.add_argument("--validation-fraction", type=float, default=0.2)
    parser.add_argument("--fusion-stable-init", action="store_true")
    parser.add_argument("--hf-only-components", action="store_true")
    parser.add_argument("--clip-recursive-state", action="store_true")
    parser.add_argument(
        "--skip-equivalent-completed",
        action="store_true",
        help="Skip runs whose tunable parameters and seed were completed in any grid stage.",
    )
    parser.add_argument("--rerun", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.start_index < 1:
        raise SystemExit("--start-index 必须 >= 1")
    if args.max_configs < 1:
        raise SystemExit("--max-configs 必须 >= 1")

    configs = load_configs(args.grid_root, args.stage)
    selected = configs[args.start_index - 1: args.start_index - 1 + args.max_configs]
    if not selected:
        raise SystemExit("选择范围内没有配置")
    seeds = parse_seeds(args)

    print(f"Stage: {args.stage}")
    print(f"Selected configs: {len(selected)} / {len(configs)}")
    print(f"Start index: {args.start_index}")
    print(f"Seeds: {','.join(str(seed) for seed in seeds)}")
    print(f"Protocol: {args.protocol_name}")
    print(f"Source batteries: {args.source_batteries}")
    print(f"Target batteries: {args.batteries}")
    print(f"Aug dir: {args.aug_dir}")
    print(f"Runs root: {runs_root(args)}")
    print(f"Skip equivalent completed: {args.skip_equivalent_completed}")
    print("Validation only: True")
    preview_limit = max(args.preview_limit, 0)
    preview_configs = selected[:preview_limit]
    for config in preview_configs:
        print(f"  {config['attempt_id']} {config['tunable']}")
    hidden_count = len(selected) - len(preview_configs)
    if hidden_count > 0:
        tail_configs = selected[-5:] if hidden_count > 5 else []
        print(f"  ... {hidden_count} configs hidden by --preview-limit {preview_limit}")
        for config in tail_configs:
            print(f"  {config['attempt_id']} {config['tunable']}")
    if args.dry_run:
        if args.skip_equivalent_completed:
            completed_keys = load_equivalent_completed_keys(args.grid_root)
            planned = [
                (config, seed)
                for config in selected
                for seed in seeds
            ]
            skip_count = sum(
                1 for config, seed in planned
                if tunable_seed_key(config, seed) in completed_keys
            )
            print(f"Equivalent completed runs known: {len(completed_keys)}")
            print(f"Dry-run skip count: {skip_count}")
            print(f"Dry-run train count: {len(planned) - skip_count}")
        return

    engine = load_module(ROOT / "scripts" / "08_physics_trend_ablation.py", "physics_engine")
    summary_path = runs_root(args) / args.stage / "stage_validation_metrics.csv"
    completed_keys = load_equivalent_completed_keys(args.grid_root) if args.skip_equivalent_completed else set()
    if completed_keys:
        print(f"Equivalent completed runs known: {len(completed_keys)}")

    total_runs = len(selected) * len(seeds)
    run_number = 0
    for config in selected:
        for seed in seeds:
            run_number += 1
            if args.skip_equivalent_completed and tunable_seed_key(config, seed) in completed_keys:
                rows = [{
                    "AttemptID": config["attempt_id"],
                    "ConfigHash": config["config_hash"],
                    "Seed": seed,
                    "Status": "skipped_equivalent_completed",
                    "RunDir": "",
                    "TestResultsViewed": False,
                }]
                write_summary(rows, summary_path)
                print(f"[{run_number}/{total_runs}] skipped equivalent completed {config['attempt_id']} seed={seed}")
                continue
            print(f"[{run_number}/{total_runs}] training {config['attempt_id']} seed={seed}")
            try:
                rows = run_d_trend_physics(config, args, engine, seed)
            except Exception as exc:
                rows = [{
                    "AttemptID": config["attempt_id"],
                    "ConfigHash": config["config_hash"],
                    "Seed": seed,
                    "Status": "failed",
                    "Error": repr(exc),
                    "Traceback": traceback.format_exc(),
                    "TestResultsViewed": False,
                }]
                print(f"[{run_number}/{total_runs}] failed: {exc}")
            write_summary(rows, summary_path)
            print(f"[{run_number}/{total_runs}] summary written: {summary_path}")


if __name__ == "__main__":
    main()
