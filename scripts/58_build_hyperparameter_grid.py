"""Build a maximal validation-only hyperparameter grid for the SOH G-MTC project.

This script only creates candidate configuration files. It does not train
models and never reads target-test labels. Use the generated registry to pick
small, validation-only batches before locking any final test run.

Continuous hyperparameters have infinitely many possible values, so this file
defines a maximal discrete grid: broad logarithmic values for optimizer knobs
and broad integer/categorical values for architecture knobs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "output" / "hyperparameter_grid_refined_v1"
DEFAULT_MAX_CONFIGS_WITHOUT_CONFIRM = 1_000_000


PAPER_FIXED = {
    "source_batteries": ["B0005", "B0006"],
    "target_batteries": ["B0007", "B0018"],
    "target_labeled_prefix_fraction": 0.20,
    "validation_only": True,
    "test_results_viewed": False,
    "selection_metric": "mean validation RMSE across B0007 and B0018",
    "selection_rule": "rank only configs with finite validation metrics for both targets",
    "do_not_tune_on": ["target test labels", "future cycles outside validation protocol"],
    "grid_type": "maximal discrete grid, not continuous exhaustive search",
}


GRID_STAGES = {
    "A_representation": {
        "description": (
            "Architecture and decomposition parameters. Values from the completed "
            "A-stage grid with negative R2 on validation are excluded."
        ),
        "parameters": {
            "sequence_length": [4, 6, 14, 16, 20, 24, 28, 32],
            "stl_period": [4, 6, 10, 20, 24, 30, 36],
            "timesnet_width": [16, 48, 96, 128, 192, 256],
            "timesnet_top_k": [1, 4, 5, 6, 8],
            "itransformer_heads": [1, 8, 16],
            "itransformer_layers": [3, 4, 5, 6],
        },
    },
    "B_component_training": {
        "description": "Training knobs for Trend/Seasonal TimesNet and Residual iTransformer.",
        "parameters": {
            "component_learning_rate": [0.00001, 0.00003, 0.0001, 0.0003, 0.0005, 0.001, 0.002, 0.003, 0.005, 0.01],
            "component_batch_size": [4, 8, 16, 32, 64, 128],
            "component_weight_decay": [0.0, 0.0000001, 0.000001, 0.000003, 0.00001, 0.00003, 0.0001, 0.0003, 0.001, 0.003, 0.01],
            "component_epoch_cap": [150, 300, 500, 800, 1200, 1600, 2000],
            "component_patience": [20, 50, 80, 120, 200, 300],
            "gradient_clip_norm": [0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
            "component_adam_beta1": [0.5, 0.9, 0.95],
            "component_adam_beta2": [0.99, 0.999, 0.9999],
            "component_adam_eps": [0.00000001, 0.0000001],
        },
    },
    "C_fusion_training": {
        "description": "Training and capacity knobs for Attention Bi-LSTM fusion.",
        "parameters": {
            "fusion_hidden_size": [8, 16, 24, 32, 48, 64, 96, 128],
            "fusion_num_layers": [1, 2, 3],
            "fusion_learning_rate": [0.00001, 0.00003, 0.0001, 0.0003, 0.0005, 0.001, 0.002, 0.003, 0.005, 0.01],
            "fusion_batch_size": [4, 8, 16, 32, 64, 128],
            "fusion_weight_decay": [0.0, 0.0000001, 0.000001, 0.000003, 0.00001, 0.00003, 0.0001, 0.0003, 0.001, 0.003, 0.01],
            "fusion_weight_regularization": [0.0, 0.0001, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0],
            "fusion_dropout": [0.0, 0.1, 0.2, 0.3, 0.5, 0.7],
            "fusion_epoch_cap": [150, 300, 500, 800, 1200, 1600, 2000],
            "fusion_patience": [30, 50, 80, 120, 200, 300],
            "lr_decay_factor": [0.1, 0.3, 0.5, 0.7, 0.8],
            "lr_decay_patience": [5, 10, 20, 40, 80],
            "min_learning_rate": [0.00000001, 0.0000001, 0.000001],
            "fusion_adam_beta1": [0.5, 0.9, 0.95],
            "fusion_adam_beta2": [0.99, 0.999, 0.9999],
            "fusion_adam_eps": [0.00000001, 0.0000001],
        },
    },
    "D_trend_physics": {
        "description": (
            "Conservative Trend-only physics loss. It keeps only parameter "
            "families that already produced nonnegative validation R2 on both "
            "B0007 and B0018 in the completed D-grid snapshot."
        ),
        "parameters": {
            "physics_mode": ["monotonic"],
            "lambda_phy": [0.0003, 0.003],
            "lambda_weight": [0.0, 0.0001, 0.001, 0.01],
            "physics_epoch_cap": [150, 300, 500, 800, 1200],
            "physics_patience": [30, 80, 120, 200, 300],
        },
        "constraints": {
            "lambda_phy": {
                "none": [0.0],
                "monotonic": [0.0003, 0.003],
                "smooth": [],
                "both": [],
            }
        },
    },
    "D_top4_validation": {
        "description": (
            "Top-4 validation configs from the completed 47-config conservative "
            "D grid. They share lambda_phy=0.0003, lambda_weight=0.01, "
            "patience=30, and differ only in epoch cap."
        ),
        "parameters": {
            "physics_mode": ["monotonic"],
            "lambda_phy": [0.0003],
            "lambda_weight": [0.01],
            "physics_epoch_cap": [300, 500, 800, 1200],
            "physics_patience": [30],
        },
        "constraints": {"lambda_phy": {"monotonic": [0.0003]}},
    },
    "D_local_best": {
        "description": (
            "Fine local search around the current best validation family: "
            "lambda_phy=0.0003 and lambda_weight=0.01. This is still "
            "validation-only and should be followed by multi-seed replication."
        ),
        "parameters": {
            "physics_mode": ["monotonic"],
            "lambda_phy": [0.00025, 0.0003, 0.00035, 0.0004, 0.00045, 0.0005],
            "lambda_weight": [0.006, 0.008, 0.01, 0.012, 0.015],
            "physics_epoch_cap": [300, 500, 800, 1200],
            "physics_patience": [20, 30, 40],
        },
        "constraints": {"lambda_phy": {"monotonic": [0.00025, 0.0003, 0.00035, 0.0004, 0.00045, 0.0005]}},
    },
    "D_stability_screen": {
        "description": (
            "Small multi-seed stability screen after D_top4_validation showed "
            "strong seed sensitivity. It searches around lambda_phy=0.0003 "
            "while also testing lower lambda_weight values and shorter epoch caps."
        ),
        "parameters": {
            "physics_mode": ["monotonic"],
            "lambda_phy": [0.0002, 0.0003, 0.0004],
            "lambda_weight": [0.0, 0.001, 0.01],
            "physics_epoch_cap": [150, 300],
            "physics_patience": [20, 30],
        },
        "constraints": {"lambda_phy": {"monotonic": [0.0002, 0.0003, 0.0004]}},
    },
    "D_exhaustive_1000": {
        "description": (
            "Capped exhaustive Trend-only physics grid with 1000 discrete "
            "candidates. Use the trainer's equivalent-completed skip to avoid "
            "rerunning tunable+seed combinations already completed in earlier D stages."
        ),
        "parameters": {
            "physics_mode": ["monotonic"],
            "lambda_phy": [0.0, 0.00001, 0.00003, 0.0001, 0.0002, 0.0003, 0.0005, 0.001, 0.003, 0.01],
            "lambda_weight": [0.0, 0.00001, 0.00003, 0.0001, 0.0003, 0.001, 0.003, 0.01, 0.03, 0.1],
            "physics_epoch_cap": [50, 100, 150, 300, 500],
            "physics_patience": [10, 20],
        },
        "constraints": {"lambda_phy": {"monotonic": [0.0, 0.00001, 0.00003, 0.0001, 0.0002, 0.0003, 0.0005, 0.001, 0.003, 0.01]}},
    },
    "E_scf_gan_sensitivity": {
        "description": "Optional SCF-GAN sensitivity check. Keep paper defaults unless validation evidence requires this stage.",
        "parameters": {
            "scf_gan_noise_dim": [4, 8, 16, 32, 64],
            "scf_gan_learning_rate": [0.00001, 0.00003, 0.0001, 0.0003, 0.0005, 0.001, 0.002, 0.003, 0.005],
            "scf_gan_batch_size": [4, 8, 16, 32, 64, 128],
            "scf_gan_hidden_width": [64, 128, 256, 384, 512, 768, 1024],
            "scf_gan_feature_matching_lambda": [0.0, 0.001, 0.01, 0.03, 0.05, 0.1, 0.3, 0.5, 1.0],
            "scf_gan_epoch_cap": [400, 800, 1200, 1600, 2000],
            "scf_gan_adam_beta1": [0.5, 0.9, 0.95],
            "scf_gan_adam_beta2": [0.99, 0.999, 0.9999],
            "scf_gan_adam_eps": [0.00000001, 0.0000001],
        },
    },
}


RECOMMENDED_ORDER = [
    "A_representation",
    "C_fusion_training",
    "B_component_training",
    "D_trend_physics",
    "E_scf_gan_sensitivity",
]


def digest(value: dict) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def iter_stage_records(stage_name: str):
    stage = GRID_STAGES[stage_name]
    params = stage["parameters"]
    keys = list(params)
    number = 0
    for values in itertools.product(*(params[key] for key in keys)):
        tunable = dict(zip(keys, values))
        if not is_allowed(stage, tunable):
            continue
        number += 1
        record = {
            "schema": "soh_hyperparameter_grid_config/1",
            "stage": stage_name,
            "attempt_id": f"{stage_name[0]}{number:03d}",
            "description": stage["description"],
            "paper_fixed": PAPER_FIXED,
            "tunable": tunable,
            "test_results_viewed": False,
            "status": "pending",
        }
        record["config_hash"] = digest(record)
        yield record


def count_stage_records(stage_name: str) -> int:
    stage = GRID_STAGES[stage_name]
    params = stage["parameters"]
    if stage_name.startswith("D_") or stage_name == "A_representation":
        return sum(1 for _ in iter_stage_records(stage_name))
    return math.prod(len(values) for values in params.values())


def is_allowed(stage: dict, tunable: dict) -> bool:
    if "timesnet_width" in tunable and "itransformer_heads" in tunable:
        if tunable["timesnet_width"] % tunable["itransformer_heads"] != 0:
            return False
    if "physics_mode" in tunable:
        lam = float(tunable["lambda_phy"])
        lw = float(tunable["lambda_weight"])
        epochs = int(tunable["physics_epoch_cap"])
        patience = int(tunable["physics_patience"])
        if tunable["physics_mode"] != "monotonic":
            return False
        if stage.get("description", "").startswith("Top-4 validation"):
            return lam == 0.0003 and lw == 0.01 and patience == 30
        if stage.get("description", "").startswith("Fine local search"):
            return True
        if stage.get("description", "").startswith("Small multi-seed stability screen"):
            return True
        if stage.get("description", "").startswith("Capped exhaustive"):
            return True
        # Proven stable family: all completed patience=30 D-grid runs were
        # nonnegative on both validation batteries for these weights.
        if patience == 30 and lam in {0.0003, 0.003} and lw in {0.0, 0.0001, 0.001, 0.01}:
            return True
        # Best observed family: D1108-D1110 around lambda_phy=0.003,
        # lambda_weight=0.01, epoch=500 gave the best mean validation R2.
        if lam == 0.003 and lw == 0.01 and epochs == 500 and patience in {120, 200, 300}:
            return True
        # Secondary stable family: lambda_phy=0.0003 with no fusion weight
        # regularization at epoch=150 was positive for patience 80/120/200/300.
        if lam == 0.0003 and lw == 0.0 and epochs == 150 and patience in {80, 120, 200, 300}:
            return True
        return False
    constraints = stage.get("constraints", {})
    if "lambda_phy" not in constraints:
        return True
    mode = tunable["physics_mode"]
    allowed = constraints["lambda_phy"][mode]
    return tunable["lambda_phy"] in allowed


def estimate(stages: list[str]) -> dict[str, int]:
    return {stage_name: count_stage_records(stage_name) for stage_name in stages}


def build(out_dir: Path, stages: list[str], allow_huge: bool, max_configs: int) -> None:
    stage_counts = estimate(stages)
    total = sum(stage_counts.values())
    if total > max_configs and not allow_huge:
        print("Grid is too large to write by accident.")
        for stage_name in stages:
            print(f"{stage_name}: {stage_counts[stage_name]} configs")
        print(f"Total: {total} configs")
        print(f"Re-run with --allow-huge to write all files, or use --stages to build one stage.")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    registry_path = out_dir / "grid_registry.csv"
    fieldnames: list[str] = [
        "AttemptID", "Stage", "ConfigHash", "ValidationOnly", "TestResultsViewed"
    ]
    for stage_name in stages:
        for key in GRID_STAGES[stage_name]["parameters"]:
            if key not in fieldnames:
                fieldnames.append(key)

    with registry_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for stage_name in stages:
            stage_dir = out_dir / "configs" / stage_name
            stage_dir.mkdir(parents=True, exist_ok=True)
            for old_config in stage_dir.glob("*.json"):
                old_config.unlink()
            for record in iter_stage_records(stage_name):
                path = stage_dir / f"{record['attempt_id']}_{record['config_hash'][:10]}.json"
                path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
                writer.writerow({
                    "AttemptID": record["attempt_id"],
                    "Stage": stage_name,
                    "ConfigHash": record["config_hash"],
                    "ValidationOnly": True,
                    "TestResultsViewed": False,
                    **record["tunable"],
                })

    protocol = {
        "schema": "soh_hyperparameter_grid_protocol/1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "output_dir": str(out_dir),
        "paper_fixed": PAPER_FIXED,
        "recommended_order": RECOMMENDED_ORDER,
        "stages": GRID_STAGES,
        "stage_counts": stage_counts,
        "notes": [
            "Use validation metrics only for selection.",
            "A excludes completed A-stage values whose validation R2 was negative for the searched configs.",
            "Run A before broad optimizer searches because sequence length changes sample count.",
            "D keeps only Trend monotonic physics because none/smooth/both had negative R2 in completed validation runs.",
            "D refined ranges are based on partial D-grid results through the current stage_validation_metrics.csv snapshot.",
            "Keep D_trend_physics Trend-only; do not apply physics penalties to final SOH.",
            "E_scf_gan_sensitivity is optional and should not replace the paper-default SCF-GAN baseline.",
        ],
    }
    protocol["protocol_hash"] = digest(protocol)
    (out_dir / "grid_protocol.json").write_text(
        json.dumps(protocol, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Grid written to: {out_dir}")
    for stage_name in stages:
        print(f"{stage_name}: {stage_counts[stage_name]} configs")
    print(f"Total: {total} configs")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build SOH validation-only hyperparameter grids.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--estimate-only", action="store_true")
    parser.add_argument("--allow-huge", action="store_true")
    parser.add_argument("--max-configs-without-confirm", type=int, default=DEFAULT_MAX_CONFIGS_WITHOUT_CONFIRM)
    parser.add_argument(
        "--stages",
        default=",".join(RECOMMENDED_ORDER),
        help=f"Comma-separated stages. Choices: {','.join(GRID_STAGES)}",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stages = [item.strip() for item in args.stages.split(",") if item.strip()]
    unknown = sorted(set(stages).difference(GRID_STAGES))
    if unknown:
        raise SystemExit(f"Unknown stages: {unknown}")
    if args.estimate_only:
        counts = estimate(stages)
        for stage_name in stages:
            print(f"{stage_name}: {counts[stage_name]} configs")
        print(f"Total: {sum(counts.values())} configs")
        return
    build(args.output_dir, stages, args.allow_huge, args.max_configs_without_confirm)


if __name__ == "__main__":
    main()
