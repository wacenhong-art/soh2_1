"""Read-only PTOC matched-cycle event audit; never reads Capacity values or trains a model."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import loadmat


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw_mat"
OUT = ROOT / "output" / "ptoc_pre_experiment_gate_v1"
TARGET_ROWS = {"B0007": 67, "B0018": 51}
TEST_LABEL_LOADED = False


def array(block, name: str) -> np.ndarray:
    return np.asarray(block[name]).squeeze().astype(float)


def waveform_status(block, names: tuple[str, ...]) -> tuple[bool, str]:
    if not all(name in block.dtype.names for name in names):
        return False, "MISSING_FIELD"
    values = [array(block, name) for name in names]
    if min(map(len, values)) < 2 or len({len(v) for v in values}) != 1:
        return False, "UNALIGNED_OR_SHORT"
    if any(not np.isfinite(v).all() for v in values):
        return False, "NONFINITE"
    time = values[-1]
    if not np.all(np.diff(time) > 0):
        return False, "NONMONOTONIC_TIME"
    return True, "OK"


def classify_charge(block) -> tuple[bool, str]:
    valid, reason = waveform_status(block, ("Voltage_measured", "Current_measured", "Temperature_measured", "Time"))
    if not valid:
        return False, f"CHARGE_{reason}"
    voltage, current, _, _ = (array(block, name) for name in ("Voltage_measured", "Current_measured", "Temperature_measured", "Time"))
    to_42 = np.flatnonzero(voltage >= 4.2)
    if not len(to_42):
        return False, "CHARGE_NO_4P2"
    if not len(np.flatnonzero(np.abs(current[int(to_42[0]):]) <= 0.02)):
        return False, "CHARGE_NO_CV_CUTOFF"
    return True, "OK"


def classify_discharge(block) -> tuple[bool, str]:
    valid, reason = waveform_status(block, ("Voltage_measured", "Current_measured", "Temperature_measured", "Time"))
    if not valid:
        return False, f"DISCHARGE_{reason}"
    voltage = array(block, "Voltage_measured")
    to_40 = np.flatnonzero(voltage <= 4.0)
    if not len(to_40):
        return False, "DISCHARGE_NO_4P0"
    if not len(np.flatnonzero(voltage[int(to_40[0]):] <= 3.6)):
        return False, "DISCHARGE_NO_3P6"
    # Field existence only: capacity numbers are neither read nor stored here.
    if "Capacity" not in block.dtype.names:
        return False, "DISCHARGE_NO_CAPACITY_FIELD"
    return True, "OK"


def audit_battery(name: str, required: int) -> tuple[pd.DataFrame, dict[str, object]]:
    cycles = loadmat(RAW / f"{name}.mat")[name][0, 0]["cycle"][0]
    rows: list[dict[str, object]] = []
    for q_index, cycle in enumerate(cycles):
        if str(cycle["type"][0]) != "charge":
            continue
        charge_ok, charge_reason = classify_charge(cycle["data"][0, 0])
        if not charge_ok:
            rows.append({"Battery": name, "RawChargeCycleIndex": q_index, "Eligible": False, "ExclusionReason": charge_reason})
            continue
        next_index = q_index + 1
        if next_index >= len(cycles):
            rows.append({"Battery": name, "RawChargeCycleIndex": q_index, "Eligible": False, "ExclusionReason": "NO_FOLLOWING_RECORD"})
            continue
        next_type = str(cycles[next_index]["type"][0])
        if next_type != "discharge":
            rows.append({"Battery": name, "RawChargeCycleIndex": q_index, "Eligible": False, "ExclusionReason": f"AMBIGUOUS_PAIR_NEXT_{next_type.upper()}"})
            continue
        discharge_ok, discharge_reason = classify_discharge(cycles[next_index]["data"][0, 0])
        rows.append({
            "Battery": name,
            "RawChargeCycleIndex": q_index,
            "RawDischargeCycleIndex": next_index,
            "Eligible": discharge_ok,
            "ExclusionReason": "OK" if discharge_ok else discharge_reason,
        })
        if discharge_ok and sum(bool(row["Eligible"]) for row in rows) >= required:
            break
    frame = pd.DataFrame(rows)
    eligible = int(frame.Eligible.sum()) if not frame.empty else 0
    return frame, {
        "battery": name,
        "required_valid_rows": required,
        "eligible_rows_found": eligible,
        "metadata_audit_pass": eligible == required,
        "test_label_loaded": TEST_LABEL_LOADED,
        "capacity_values_read": False,
        "stopped_after_required_rows": eligible == required,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    frames, summaries = [], []
    for battery, required in TARGET_ROWS.items():
        frame, summary = audit_battery(battery, required)
        frames.append(frame); summaries.append(summary)
    records = pd.concat(frames, ignore_index=True)
    records.to_csv(OUT / "matched_cycle_event_audit.csv", index=False, encoding="utf-8-sig")
    manifest = {
        "audit": "PTOC_MATCHED_CYCLE_METADATA_AUDIT_V1",
        "scope": "development prefix raw event metadata only",
        "test_label_loaded": TEST_LABEL_LOADED,
        "capacity_values_read": False,
        "pairing_rule": "qualifying charge must be immediately followed by qualifying discharge",
        "event_rules": {"charge": "V>=4.2 then abs(I)<=0.02", "discharge": "first V<=4.0 then later first V<=3.6"},
        "summaries": summaries,
    }
    (OUT / "matched_cycle_event_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
