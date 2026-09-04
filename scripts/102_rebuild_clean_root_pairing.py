"""Rebuild the frozen ROOT input table with the sole approved pairing repair.

This utility is deliberately not a model-training script.  It imports the
historical extractor only to reuse its frozen feature and target functions.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = ROOT / "scripts" / "83_feature_adequacy_reassessment.py"
OLD_SOURCE = ROOT / "output" / "feature_adequacy_reassessment_v1" / "frozen_raw_features.csv"
OUT = ROOT / "output" / "root_post_completion_repair"
BATTERIES = ("B0007", "B0018")
LIMITS = {"B0007": 67, "B0018": 51}
PAIRING_RULE = "first_later_discharge_with_no_intervening_charge"
TEST_LOADED = False
F1 = (
    "DISCHARGE_DURATION_S", "DISCHARGE_V4P0_TO_V3P6_S",
    "DISCHARGE_VOLTAGE_MEAN_V", "DISCHARGE_VOLTAGE_STD_V",
    "DISCHARGE_TEMPERATURE_MEAN_C", "DISCHARGE_TEMPERATURE_STD_C",
    "DISCHARGE_ENERGY_WH",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_historical_module():
    spec = importlib.util.spec_from_file_location("root_historical_extractor", HISTORICAL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen ROOT extractor")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def legal_pairs_from_types(types: list[str]) -> tuple[list[tuple[int, int]], list[dict[str, object]]]:
    """Return eligible charge/discharge identities without looking at labels.

    The function encodes the frozen repair rule and is intentionally independent
    of waveform validity.  The extraction loop applies the original waveform
    eligibility checks afterwards.
    """
    pairs: list[tuple[int, int]] = []
    exclusions: list[dict[str, object]] = []
    for charge_index, kind in enumerate(types):
        if kind != "charge":
            continue
        discharge_index = next((i for i in range(charge_index + 1, len(types)) if types[i] == "discharge"), None)
        if discharge_index is None:
            exclusions.append({"RawChargeCycleIndex": charge_index, "Reason": "NO_LATER_DISCHARGE"})
            continue
        intervening_charge = next((i for i in range(charge_index + 1, discharge_index) if types[i] == "charge"), None)
        if intervening_charge is not None:
            exclusions.append({
                "RawChargeCycleIndex": charge_index,
                "RawDischargeCycleIndex": discharge_index,
                "InterveningChargeCycleIndex": intervening_charge,
                "Reason": "INTERVENING_CHARGE_BEFORE_TARGET_DISCHARGE",
            })
            continue
        pairs.append((charge_index, discharge_index))
    if len({d for _, d in pairs}) != len(pairs):
        raise AssertionError("pairing rule failed one-to-one discharge invariant")
    return pairs, exclusions


def regression_fixture() -> dict[str, object]:
    pairs, exclusions = legal_pairs_from_types(["charge", "charge", "discharge"])
    if pairs != [(1, 2)] or len(exclusions) != 1 or exclusions[0]["Reason"] != "INTERVENING_CHARGE_BEFORE_TARGET_DISCHARGE":
        raise AssertionError("charge->charge->discharge fixture did not retain only the unique predecessor")
    pairs_with_diagnostic, diagnostic_exclusions = legal_pairs_from_types(["charge", "impedance", "discharge"])
    if pairs_with_diagnostic != [(0, 2)] or diagnostic_exclusions:
        raise AssertionError("non-charge intermediary changed historical ROOT pairing semantics")
    return {
        "fixture": ["charge", "charge", "discharge"],
        "expected_pair": [1, 2],
        "passed": True,
        "non_charge_intermediary_fixture": ["charge", "impedance", "discharge"],
        "non_charge_intermediary_pair": [0, 2],
    }


def cycle_type(cycle) -> str:
    return str(cycle["type"][0])


def extract_clean_prefix(module, battery: str, limit: int) -> tuple[pd.DataFrame, list[dict[str, object]], list[dict[str, object]]]:
    container = module.loadmat(module.RAW / f"{battery}.mat")
    cycles = container[battery][0, 0]["cycle"][0]
    types = [cycle_type(cycle) for cycle in cycles]
    candidates, structural_exclusions = legal_pairs_from_types(types)
    rows: list[dict[str, object]] = []
    waveform_exclusions: list[dict[str, object]] = []
    for charge_index, discharge_index in candidates:
        try:
            charge = cycles[charge_index]["data"][0, 0]
            module.old_hf_valid(charge)
            discharge = cycles[discharge_index]["data"][0, 0]
            record = module.discharge_features(discharge)
            record["SOH"] = float(module.vector(discharge, "Capacity")) / 2.0
            record["RawChargeCycleIndex"] = charge_index
            record["RawDischargeCycleIndex"] = discharge_index
            rows.append(record)
        except (IndexError, ValueError, KeyError) as exc:
            waveform_exclusions.append({
                "RawChargeCycleIndex": charge_index,
                "RawDischargeCycleIndex": discharge_index,
                "Reason": "HISTORICAL_WAVEFORM_ELIGIBILITY_FAILURE",
                "Exception": type(exc).__name__,
            })
            continue
        if len(rows) >= limit:
            break
    if len(rows) != limit:
        raise RuntimeError(f"{battery}: clean repair emitted {len(rows)}, expected frozen prefix limit {limit}")
    frame = pd.DataFrame(rows)
    if frame.RawDischargeCycleIndex.duplicated().any():
        raise AssertionError(f"{battery}: duplicate discharge remains after repair")
    return frame, structural_exclusions, waveform_exclusions


def pair_id(frame: pd.DataFrame) -> pd.Series:
    return frame.Battery.astype(str) + ":q" + frame.RawChargeCycleIndex.astype(int).astype(str) + ":d" + frame.RawDischargeCycleIndex.astype(int).astype(str)


def structural_diff(old: pd.DataFrame, new: pd.DataFrame, features: tuple[str, ...]) -> dict[str, object]:
    old = old.copy(); new = new.copy()
    old["PairID"] = pair_id(old); new["PairID"] = pair_id(new)
    old_ids, new_ids = set(old.PairID), set(new.PairID)
    common = sorted(old_ids & new_ids)
    old_common = old.set_index("PairID").loc[common]
    new_common = new.set_index("PairID").loc[common]
    value_columns = [*features, "SOH", "TestLoaded"]
    unchanged_common = bool(np.allclose(
        old_common.loc[:, features + ("SOH",)].to_numpy(float),
        new_common.loc[:, features + ("SOH",)].to_numpy(float), atol=1e-12, rtol=1e-12
    ) and old_common.TestLoaded.equals(new_common.TestLoaded))
    b18_old = old.loc[old.Battery.eq("B0018")].drop(columns="PairID").reset_index(drop=True)
    b18_new = new.loc[new.Battery.eq("B0018")].drop(columns="PairID").reset_index(drop=True)
    b18_numeric = [*features, "SOH"]
    b18_unchanged = bool(
        b18_old.loc[:, ["Battery", "TestLoaded", "RawChargeCycleIndex", "RawDischargeCycleIndex"]].equals(
            b18_new.loc[:, ["Battery", "TestLoaded", "RawChargeCycleIndex", "RawDischargeCycleIndex"]]
        ) and np.allclose(
            b18_old.loc[:, b18_numeric].to_numpy(float), b18_new.loc[:, b18_numeric].to_numpy(float), atol=1e-12, rtol=1e-12
        )
    )
    return {
        "old_root_rows": int(len(old)),
        "new_root_rows": int(len(new)),
        "old_unique_discharge_records": int(old.groupby(["Battery", "RawDischargeCycleIndex"]).ngroups),
        "new_unique_discharge_records": int(new.groupby(["Battery", "RawDischargeCycleIndex"]).ngroups),
        "duplicate_discharge_before": int(old.duplicated(["Battery", "RawDischargeCycleIndex"]).sum()),
        "duplicate_discharge_after": int(new.duplicated(["Battery", "RawDischargeCycleIndex"]).sum()),
        "removed_pair_ids": sorted(old_ids - new_ids),
        "added_pair_ids": sorted(new_ids - old_ids),
        "common_pair_values_unchanged": unchanged_common,
        "feature_columns_identical": list(features) == [c for c in new.columns if c in features],
        "b0018_input_artifact_unchanged": b18_unchanged,
        "unchanged_value_columns": value_columns,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    fixture = regression_fixture()
    if args.self_test:
        print(json.dumps({"PAIRING_REGRESSION_FIXTURE": "PASS", **fixture}, indent=2))
        return
    module = load_historical_module()
    if tuple(module.RAW_FEATURES) != F1:
        raise AssertionError("historical F1 feature contract differs from the frozen repair specification")
    old = pd.read_csv(OLD_SOURCE)
    if not old.TestLoaded.eq(False).all():
        raise RuntimeError("historical ROOT source must be non-test-only")
    frames: list[pd.DataFrame] = []
    exclusions: dict[str, dict[str, list[dict[str, object]]]] = {}
    for battery in BATTERIES:
        frame, structural, waveform = extract_clean_prefix(module, battery, LIMITS[battery])
        frame.insert(0, "Battery", battery)
        frame.insert(1, "TestLoaded", TEST_LOADED)
        frames.append(frame)
        exclusions[battery] = {"structural": structural, "waveform": waveform}
    new = pd.concat(frames, ignore_index=True)
    if not new.TestLoaded.eq(False).all():
        raise AssertionError("test-loaded flag changed")
    if new.duplicated(["Battery", "RawDischargeCycleIndex"]).any():
        raise AssertionError("one-to-one discharge invariant failed")
    repeat_frames = []
    for battery in BATTERIES:
        repeated, _, _ = extract_clean_prefix(module, battery, LIMITS[battery])
        repeated.insert(0, "Battery", battery); repeated.insert(1, "TestLoaded", TEST_LOADED)
        repeat_frames.append(repeated)
    repeated = pd.concat(repeat_frames, ignore_index=True)
    if not new.equals(repeated):
        raise AssertionError("reconstruction is not deterministic")
    diff = structural_diff(old, new, tuple(module.RAW_FEATURES))
    if diff["duplicate_discharge_after"] != 0 or not diff["common_pair_values_unchanged"] or not diff["b0018_input_artifact_unchanged"]:
        raise AssertionError("structural repair invariant failed")
    OUT.mkdir(parents=True, exist_ok=True)
    clean_path = OUT / "clean_root_features.csv"
    new.to_csv(clean_path, index=False, encoding="utf-8-sig")
    manifest = {
        "artifact": str(clean_path.relative_to(ROOT)), "test_loaded": False,
        "pairing_rule": PAIRING_RULE, "feature_columns": list(module.RAW_FEATURES),
        "target_definition": "SOH = Capacity / 2.0 from paired completed discharge",
        "historical_extractor": str(HISTORICAL.relative_to(ROOT)),
        "historical_feature_source_sha256": sha256(OLD_SOURCE),
        "clean_feature_source_sha256": sha256(clean_path), "limits": LIMITS,
        "regression_fixture": fixture, "exclusions": exclusions,
        "one_to_one_charge_to_discharge": True, "deterministic_reconstruction": True,
        "ptoc_protocol_v1_changed": False,
    }
    (OUT / "clean_pairing_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (OUT / "structural_diff.json").write_text(json.dumps(diff, indent=2), encoding="utf-8")
    print("CLEAN_ROOT_RECONSTRUCTION_STATUS=PASS")
    print("TestLoaded=False")
    print(json.dumps(diff, indent=2))


if __name__ == "__main__":
    main()
