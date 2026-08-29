"""Audit per-cycle outliers for the four NASA SOH batteries.

The audit is deliberately non-destructive: it flags suspicious cycles and
writes reports/figures, but it never edits the HF CSV files or removes rows.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BATTERIES = ["B0005", "B0006", "B0007", "B0018"]
VALUE_COLUMNS = ["SOH", "HF1", "HF2", "HF3"]


def robust_zscore(values: pd.Series) -> pd.Series:
    median = values.median()
    mad = (values - median).abs().median()
    if not np.isfinite(mad) or mad <= 1e-12:
        return pd.Series(np.zeros(len(values)), index=values.index, dtype=float)
    return 0.6745 * (values - median) / mad


def rolling_mad_zscore(values: pd.Series, window: int) -> pd.Series:
    median = values.rolling(window, center=True, min_periods=3).median()
    deviation = (values - median).abs()
    mad = deviation.rolling(window, center=True, min_periods=3).median()
    scale = 1.4826 * mad
    z = deviation / scale.replace(0, np.nan)
    return z.fillna(0.0)


def audit_battery(path: Path, battery: str, window: int, level_z: float, jump_z: float) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in VALUE_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.reset_index(drop=True)
    df.insert(0, "Cycle", np.arange(len(df), dtype=int))
    df.insert(0, "BatteryID", battery)

    reason_lists = [[] for _ in range(len(df))]
    for col in VALUE_COLUMNS:
        missing = df[col].isna()
        for idx in df.index[missing]:
            reason_lists[idx].append(f"{col}:missing_or_non_numeric")

        non_positive = df[col].le(0) & df[col].notna()
        for idx in df.index[non_positive]:
            reason_lists[idx].append(f"{col}:non_positive")

        level_score = robust_zscore(df[col].dropna())
        df[f"{col}_LevelRobustZ"] = level_score.reindex(df.index).fillna(0.0).abs()
        for idx in df.index[df[f"{col}_LevelRobustZ"].gt(level_z)]:
            reason_lists[idx].append(f"{col}:level_z>{level_z:g}")

        local_score = rolling_mad_zscore(df[col], window)
        df[f"{col}_LocalMadZ"] = local_score
        for idx in df.index[local_score.gt(level_z)]:
            reason_lists[idx].append(f"{col}:local_mad_z>{level_z:g}")

        diff = df[col].diff()
        diff_score = robust_zscore(diff.dropna())
        df[f"{col}_JumpRobustZ"] = diff_score.reindex(df.index).fillna(0.0).abs()
        for idx in df.index[df[f"{col}_JumpRobustZ"].gt(jump_z)]:
            reason_lists[idx].append(f"{col}:jump_z>{jump_z:g}")

    soh_jump_up = df["SOH"].diff().gt(0.01)
    for idx in df.index[soh_jump_up.fillna(False)]:
        reason_lists[idx].append("SOH:increase>0.01")

    df["OutlierReasons"] = [";".join(items) for items in reason_lists]
    df["IsOutlier"] = df["OutlierReasons"].ne("")
    df["OutlierReasonCount"] = [len(items) for items in reason_lists]
    return df


def plot_battery(audit: pd.DataFrame, out_dir: Path, battery: str) -> None:
    if plt is None:
        return
    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    for ax, col in zip(axes, VALUE_COLUMNS):
        ax.plot(audit["Cycle"], audit[col], lw=1.2, label=col)
        flagged = audit[audit["IsOutlier"]]
        ax.scatter(flagged["Cycle"], flagged[col], s=18, c="crimson", label="flagged", zorder=3)
        ax.set_ylabel(col)
        ax.grid(alpha=0.25)
        ax.legend(loc="best")
    axes[-1].set_xlabel("Cycle")
    fig.suptitle(f"{battery} per-cycle outlier audit")
    fig.tight_layout()
    fig.savefig(out_dir / f"{battery}_outlier_audit.png", dpi=180)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit four-battery HF/SOH outliers without deleting data.")
    parser.add_argument("--batteries", default=",".join(DEFAULT_BATTERIES))
    parser.add_argument("--input-dir", type=Path, default=ROOT / "data" / "hf_csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output" / "four_battery_outlier_audit_v1")
    parser.add_argument("--window", type=int, default=7)
    parser.add_argument("--level-z", type=float, default=6.0)
    parser.add_argument("--jump-z", type=float, default=6.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    batteries = [item.strip() for item in args.batteries.split(",") if item.strip()]
    args.output_dir.mkdir(parents=True, exist_ok=True)

    all_frames = []
    summary_rows = []
    for battery in batteries:
        path = args.input_dir / f"{battery}_hf.csv"
        if not path.exists():
            raise FileNotFoundError(path)
        audit = audit_battery(path, battery, args.window, args.level_z, args.jump_z)
        audit.to_csv(args.output_dir / f"{battery}_cycle_outliers.csv", index=False, encoding="utf-8-sig")
        plot_battery(audit, args.output_dir, battery)
        all_frames.append(audit)
        summary_rows.append({
            "BatteryID": battery,
            "Rows": len(audit),
            "OutlierRows": int(audit["IsOutlier"].sum()),
            "OutlierRate": float(audit["IsOutlier"].mean()),
            "SOH_Min": float(audit["SOH"].min()),
            "SOH_Max": float(audit["SOH"].max()),
            "HF1_Min": float(audit["HF1"].min()),
            "HF1_Max": float(audit["HF1"].max()),
            "HF2_Min": float(audit["HF2"].min()),
            "HF2_Max": float(audit["HF2"].max()),
            "HF3_Min": float(audit["HF3"].min()),
            "HF3_Max": float(audit["HF3"].max()),
        })

    combined = pd.concat(all_frames, ignore_index=True)
    combined.to_csv(args.output_dir / "four_battery_cycle_outliers.csv", index=False, encoding="utf-8-sig")
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(args.output_dir / "outlier_audit_summary.csv", index=False, encoding="utf-8-sig")

    readme = args.output_dir / "README.md"
    readme.write_text(
        "\n".join([
            "# Four-Battery Outlier Audit",
            "",
            "This audit flags suspicious cycles only; it does not remove or overwrite source data.",
            "Plots are written when matplotlib is available; CSV outputs are always written.",
            f"Batteries: {', '.join(batteries)}",
            f"Rolling window: {args.window}",
            f"Level/local z threshold: {args.level_z:g}",
            f"Jump z threshold: {args.jump_z:g}",
            "",
            "Use the CSV files to review flagged cycles before deciding on any fixed cleaning rule.",
        ]),
        encoding="utf-8",
    )

    print(f"Outlier audit written to: {args.output_dir}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
