"""Compare SCF-GAN augmented HF distributions across source protocols.

The comparison is diagnostic only. It checks whether synthetic HF samples in
each protocol match the real target-prefix HF distribution used for adaptation.
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
HF_COLS = ["HF1", "HF2", "HF3"]


def ks_statistic(a: np.ndarray, b: np.ndarray) -> float:
    a = np.sort(np.asarray(a, dtype=float))
    b = np.sort(np.asarray(b, dtype=float))
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) == 0 or len(b) == 0:
        return float("nan")
    values = np.sort(np.unique(np.concatenate([a, b])))
    cdf_a = np.searchsorted(a, values, side="right") / len(a)
    cdf_b = np.searchsorted(b, values, side="right") / len(b)
    return float(np.max(np.abs(cdf_a - cdf_b)))


def read_aug(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    for col in ["DatasetID", "Cycle", *HF_COLS, "SOH"]:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=HF_COLS + ["DatasetID", "Cycle"]).copy()


def protocol_target_summary(protocol: str, target: str, path: Path) -> tuple[list[dict], pd.DataFrame]:
    df = read_aug(path)
    real = df[df["DatasetID"].eq(0)].copy()
    synth = df[~df["DatasetID"].eq(0)].copy()
    if real.empty or synth.empty:
        raise RuntimeError(f"{path} 缺少真实或合成增强行")

    rows = []
    for col in HF_COLS:
        real_values = real[col].to_numpy(float)
        synth_values = synth[col].to_numpy(float)
        real_mean = float(np.mean(real_values))
        synth_mean = float(np.mean(synth_values))
        real_std = float(np.std(real_values, ddof=1))
        synth_std = float(np.std(synth_values, ddof=1))
        pooled = max(real_std, 1e-12)
        rows.append({
            "Protocol": protocol,
            "TargetBattery": target,
            "Feature": col,
            "RealRows": len(real),
            "SyntheticRows": len(synth),
            "RealMean": real_mean,
            "SyntheticMean": synth_mean,
            "MeanDelta": synth_mean - real_mean,
            "AbsStandardizedMeanDelta": abs(synth_mean - real_mean) / pooled,
            "RealStd": real_std,
            "SyntheticStd": synth_std,
            "StdRatioSyntheticToReal": synth_std / max(real_std, 1e-12),
            "RealMin": float(np.min(real_values)),
            "RealMax": float(np.max(real_values)),
            "SyntheticMin": float(np.min(synth_values)),
            "SyntheticMax": float(np.max(synth_values)),
            "SyntheticBelowRealMinRate": float(np.mean(synth_values < np.min(real_values))),
            "SyntheticAboveRealMaxRate": float(np.mean(synth_values > np.max(real_values))),
            "KSStatistic": ks_statistic(real_values, synth_values),
        })
    return rows, df


def plot_target(df: pd.DataFrame, protocol: str, target: str, out_dir: Path) -> None:
    if plt is None:
        return
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.5))
    for ax, col in zip(axes, HF_COLS):
        real = df[df["DatasetID"].eq(0)][col]
        synth = df[~df["DatasetID"].eq(0)][col]
        ax.hist(real, bins=20, alpha=0.65, density=True, label="real prefix")
        ax.hist(synth, bins=20, alpha=0.55, density=True, label="synthetic")
        ax.set_title(col)
        ax.grid(alpha=0.25)
    axes[0].legend()
    fig.suptitle(f"{protocol} {target}: synthetic vs real target-prefix HF")
    fig.tight_layout()
    fig.savefig(out_dir / f"{protocol}_{target}_hf_distribution.png", dpi=180)
    plt.close(fig)


def compare_shared_target(protocol_frames: dict[tuple[str, str], pd.DataFrame]) -> pd.DataFrame:
    rows = []
    targets = sorted({target for _, target in protocol_frames})
    protocols = sorted({protocol for protocol, _ in protocol_frames})
    if len(protocols) < 2:
        return pd.DataFrame(rows)
    for target in targets:
        available = [protocol for protocol in protocols if (protocol, target) in protocol_frames]
        if len(available) < 2:
            continue
        base = available[0]
        for other in available[1:]:
            base_synth = protocol_frames[(base, target)]
            base_synth = base_synth[~base_synth["DatasetID"].eq(0)]
            other_synth = protocol_frames[(other, target)]
            other_synth = other_synth[~other_synth["DatasetID"].eq(0)]
            for col in HF_COLS:
                a = base_synth[col].to_numpy(float)
                b = other_synth[col].to_numpy(float)
                rows.append({
                    "TargetBattery": target,
                    "ProtocolA": base,
                    "ProtocolB": other,
                    "Feature": col,
                    "ProtocolAMean": float(np.mean(a)),
                    "ProtocolBMean": float(np.mean(b)),
                    "MeanDeltaBMinusA": float(np.mean(b) - np.mean(a)),
                    "ProtocolAStd": float(np.std(a, ddof=1)),
                    "ProtocolBStd": float(np.std(b, ddof=1)),
                    "KSStatistic": ks_statistic(a, b),
                })
    return pd.DataFrame(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare augmented HF distributions across protocols.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output" / "augmented_hf_distribution_compare_v1")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    datasets = {
        ("Source5_6_Target7_18", "B0007"): ROOT / "output" / "B0007_aug_train_hf.csv",
        ("Source5_6_Target7_18", "B0018"): ROOT / "output" / "B0018_aug_train_hf.csv",
        ("Source18_6_Target5_7", "B0005"): ROOT / "output" / "source18_6_target5_7" / "aug" / "B0005_aug_train_hf.csv",
        ("Source18_6_Target5_7", "B0007"): ROOT / "output" / "source18_6_target5_7" / "aug" / "B0007_aug_train_hf.csv",
    }

    summary_rows = []
    frames = {}
    for (protocol, target), path in datasets.items():
        rows, frame = protocol_target_summary(protocol, target, path)
        summary_rows.extend(rows)
        frames[(protocol, target)] = frame
        plot_target(frame, protocol, target, args.output_dir)

    summary = pd.DataFrame(summary_rows)
    summary["DistributionShiftScore"] = (
        summary["AbsStandardizedMeanDelta"]
        + summary["KSStatistic"]
        + (summary["StdRatioSyntheticToReal"] - 1.0).abs()
        + summary["SyntheticBelowRealMinRate"]
        + summary["SyntheticAboveRealMaxRate"]
    )
    summary.to_csv(args.output_dir / "synthetic_vs_real_prefix_summary.csv", index=False, encoding="utf-8-sig")

    protocol_summary = (
        summary.groupby(["Protocol", "TargetBattery"], as_index=False)
        .agg(
            MeanShiftScore=("DistributionShiftScore", "mean"),
            MaxShiftScore=("DistributionShiftScore", "max"),
            MeanKS=("KSStatistic", "mean"),
            MeanAbsStandardizedMeanDelta=("AbsStandardizedMeanDelta", "mean"),
            MeanOutOfRealRangeRate=("SyntheticAboveRealMaxRate", "mean"),
            MeanBelowRealRangeRate=("SyntheticBelowRealMinRate", "mean"),
        )
        .sort_values(["MeanShiftScore", "MaxShiftScore"])
    )
    protocol_summary.to_csv(args.output_dir / "protocol_target_shift_ranking.csv", index=False, encoding="utf-8-sig")

    shared = compare_shared_target(frames)
    shared.to_csv(args.output_dir / "shared_target_protocol_comparison.csv", index=False, encoding="utf-8-sig")

    print(f"Distribution comparison written to: {args.output_dir}")
    print("\nProtocol/target shift ranking:")
    print(protocol_summary.to_string(index=False))
    if not shared.empty:
        print("\nShared-target synthetic comparison:")
        print(shared.to_string(index=False))


if __name__ == "__main__":
    main()
