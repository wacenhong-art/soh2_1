"""Prepare the source-swap control protocol.

This script writes a protocol manifest and checks prerequisites for the
B0018+B0006 -> B0005+B0007 control experiment. It does not train models.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare source-swap protocol manifest.")
    parser.add_argument("--protocol-name", default="Source18_6_Target5_7")
    parser.add_argument("--source-batteries", default="B0018,B0006")
    parser.add_argument("--target-batteries", default="B0005,B0007")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output" / "source18_6_target5_7")
    parser.add_argument("--aug-dir", type=Path, default=ROOT / "output" / "source18_6_target5_7" / "aug")
    parser.add_argument("--model-dir", type=Path, default=ROOT / "output" / "source18_6_target5_7" / "model")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sources = parse_csv_list(args.source_batteries)
    targets = parse_csv_list(args.target_batteries)
    overlap = sorted(set(sources).intersection(targets))
    if overlap:
        raise SystemExit(f"源电池和目标电池重叠，拒绝生成协议: {overlap}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.aug_dir.mkdir(parents=True, exist_ok=True)
    args.model_dir.mkdir(parents=True, exist_ok=True)

    prerequisites = []
    for battery in sources + targets:
        prerequisites.append({
            "kind": "hf_csv",
            "battery": battery,
            "path": str(ROOT / "data" / "hf_csv" / f"{battery}_hf.csv"),
            "exists": (ROOT / "data" / "hf_csv" / f"{battery}_hf.csv").exists(),
        })
    for battery in targets:
        prerequisites.append({
            "kind": "target_aug_train_hf",
            "battery": battery,
            "path": str(args.aug_dir / f"{battery}_aug_train_hf.csv"),
            "exists": (args.aug_dir / f"{battery}_aug_train_hf.csv").exists(),
        })

    protocol = {
        "schema": "soh_source_swap_protocol/1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "protocol_name": args.protocol_name,
        "source_batteries": sources,
        "target_batteries": targets,
        "model_dir": str(args.model_dir),
        "aug_dir": str(args.aug_dir),
        "runs_root": str(args.output_dir / "runs"),
        "evaluation_split": "validation",
        "test_results_viewed": False,
        "notes": [
            "This is a source-swap control protocol and must not be merged with Source5_6_Target7_18 results.",
            "Source batteries are used to train SCF-GAN only; target batteries still use target-prefix validation.",
            "The protocol requires target augmented training HF files in aug_dir before grid training.",
            "B0005/B0007 validation metrics from this protocol are not directly comparable to B0007/B0018 from the original protocol.",
        ],
        "prerequisites": prerequisites,
    }
    protocol_path = args.output_dir / "protocol.json"
    protocol_path.write_text(json.dumps(protocol, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Protocol written to: {protocol_path}")
    print(f"Sources: {','.join(sources)}")
    print(f"Targets: {','.join(targets)}")
    for item in prerequisites:
        status = "OK" if item["exists"] else "MISSING"
        print(f"{status}: {item['kind']} {item['battery']} -> {item['path']}")


if __name__ == "__main__":
    main()
