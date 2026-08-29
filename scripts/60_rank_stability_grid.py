"""Rank multi-seed validation-grid results by stability.

This script reads validation-only grid results and writes a compact ranking.
It does not train models and does not read target-test labels.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GRID_ROOT = ROOT / "output" / "hyperparameter_grid_refined_v1"
DEFAULT_STAGE = "D_stability_screen"


def load_tunables(grid_root: Path, stage: str) -> pd.DataFrame:
    config_dir = grid_root / "configs" / stage
    rows = []
    for path in sorted(config_dir.glob("*.json")):
        config = json.loads(path.read_text(encoding="utf-8"))
        rows.append({
            "AttemptID": config["attempt_id"],
            "ConfigHash": config["config_hash"],
            **config["tunable"],
        })
    if not rows:
        raise FileNotFoundError(f"没有找到配置 JSON: {config_dir}")
    return pd.DataFrame(rows)


def rank_results(
    metrics_path: Path,
    tunables: pd.DataFrame,
    r2_floor: float,
    max_std_r2: float | None,
) -> pd.DataFrame:
    if not metrics_path.exists():
        raise FileNotFoundError(f"没有找到结果文件: {metrics_path}")

    df = pd.read_csv(metrics_path)
    df = df[df["Status"].eq("completed")].copy()
    if df.empty:
        raise RuntimeError(f"{metrics_path} 中没有 completed 结果")
    if df["TestResultsViewed"].astype(str).str.lower().ne("false").any():
        raise RuntimeError("发现 TestResultsViewed 不是 False，停止排名。")

    seed_level = (
        df.groupby(["AttemptID", "ConfigHash", "Seed"], as_index=False)
        .agg(
            SeedMeanR2=("R2", "mean"),
            SeedMinR2=("R2", "min"),
            SeedMeanRMSE=("RMSE", "mean"),
            BatteryCount=("BatteryID", "nunique"),
            NegativeBatteryRows=("R2", lambda s: int((s < r2_floor).sum())),
        )
    )

    ranked = (
        seed_level.groupby(["AttemptID", "ConfigHash"], as_index=False)
        .agg(
            MeanSeedR2=("SeedMeanR2", "mean"),
            StdSeedR2=("SeedMeanR2", "std"),
            WorstSeedMeanR2=("SeedMeanR2", "min"),
            BestSeedMeanR2=("SeedMeanR2", "max"),
            WorstBatteryR2=("SeedMinR2", "min"),
            MeanRMSE=("SeedMeanRMSE", "mean"),
            SeedsCompleted=("Seed", "nunique"),
            NegativeBatteryRows=("NegativeBatteryRows", "sum"),
        )
    )
    ranked["StdSeedR2"] = ranked["StdSeedR2"].fillna(0.0)
    ranked["AllBatteryR2Nonnegative"] = ranked["NegativeBatteryRows"].eq(0) & ranked["WorstBatteryR2"].ge(r2_floor)
    ranked["WorstSeedPass"] = ranked["WorstSeedMeanR2"].ge(r2_floor)
    if max_std_r2 is None:
        ranked["StdSeedPass"] = True
    else:
        ranked["StdSeedPass"] = ranked["StdSeedR2"].le(max_std_r2)
    ranked["StabilityPass"] = (
        ranked["AllBatteryR2Nonnegative"]
        & ranked["WorstSeedPass"]
        & ranked["StdSeedPass"]
    )

    ranked = ranked.merge(tunables, on=["AttemptID", "ConfigHash"], how="left")
    sort_cols = [
        "StabilityPass",
        "AllBatteryR2Nonnegative",
        "MeanSeedR2",
        "WorstSeedMeanR2",
        "WorstBatteryR2",
        "StdSeedR2",
        "MeanRMSE",
    ]
    ranked = ranked.sort_values(
        sort_cols,
        ascending=[False, False, False, False, False, True, True],
    ).reset_index(drop=True)
    ranked.insert(0, "StabilityRank", range(1, len(ranked) + 1))
    return ranked


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rank multi-seed validation stability results.")
    parser.add_argument("--grid-root", type=Path, default=DEFAULT_GRID_ROOT)
    parser.add_argument("--runs-root", type=Path, default=None)
    parser.add_argument("--stage", default=DEFAULT_STAGE)
    parser.add_argument("--r2-floor", type=float, default=0.0)
    parser.add_argument("--max-std-r2", type=float, default=None)
    parser.add_argument("--top-n", type=int, default=20)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs_root = args.runs_root if args.runs_root is not None else args.grid_root / "runs"
    metrics_path = runs_root / args.stage / "stage_validation_metrics.csv"
    output_path = runs_root / args.stage / "stability_ranking.csv"
    tunables = load_tunables(args.grid_root, args.stage)
    ranked = rank_results(metrics_path, tunables, args.r2_floor, args.max_std_r2)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ranked.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Ranking written to: {output_path}")
    print(f"Total configs ranked: {len(ranked)}")
    print(f"StabilityPass configs: {int(ranked['StabilityPass'].sum())}")
    print(ranked.head(args.top_n).to_string(index=False))


if __name__ == "__main__":
    main()
