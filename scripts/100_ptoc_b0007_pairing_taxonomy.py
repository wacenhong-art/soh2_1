"""Label-free Phase-3 diagnostic: classify B0007 charge-to-discharge record grammar.

It reads only raw record types, MATLAB start-time vectors, and V/I/T/time
waveform metadata. It never accesses Capacity values, SOH labels, train/val
labels, test labels, or any prediction model.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import loadmat


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw_mat"
OUT = ROOT / "output" / "ptoc_phase3_blocker_resolution_1"
BATTERY = "B0007"
DEVELOPMENT_CANDIDATES = 67
TEST_LABEL_LOADED = False
CAPACITY_VALUES_READ = False


def series(block, name: str) -> np.ndarray:
    return np.asarray(block[name]).squeeze().astype(float)


def waveform_ok(block) -> bool:
    fields = ("Voltage_measured", "Current_measured", "Temperature_measured", "Time")
    if not all(field in block.dtype.names for field in fields):
        return False
    values = [series(block, field) for field in fields]
    return (min(map(len, values)) >= 2 and len({len(item) for item in values}) == 1
            and all(np.isfinite(item).all() for item in values)
            and np.all(np.diff(values[-1]) > 0))


def charge_ok(cycle) -> bool:
    block = cycle["data"][0, 0]
    if not waveform_ok(block):
        return False
    voltage, current = series(block, "Voltage_measured"), series(block, "Current_measured")
    reach = np.flatnonzero(voltage >= 4.2)
    return bool(len(reach) and len(np.flatnonzero(np.abs(current[int(reach[0]):]) <= 0.02)))


def discharge_ok(cycle) -> bool:
    block = cycle["data"][0, 0]
    if not waveform_ok(block):
        return False
    voltage = series(block, "Voltage_measured")
    lower_40 = np.flatnonzero(voltage <= 4.0)
    return bool(len(lower_40) and len(np.flatnonzero(voltage[int(lower_40[0]):] <= 3.6)))


def cycle_type(cycle) -> str:
    return str(cycle["type"][0])


def cycle_time(cycle) -> str:
    # Metadata-only start time; no waveform label or capacity value is read.
    values = [int(x) for x in np.asarray(cycle["time"]).squeeze()]
    return "-".join(map(str, values))


def next_valid_discharge(cycles, start: int) -> int | None:
    for index in range(start + 1, len(cycles)):
        if cycle_type(cycles[index]) == "discharge" and discharge_ok(cycles[index]):
            return index
    return None


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cycles = loadmat(RAW / f"{BATTERY}.mat")[BATTERY][0, 0]["cycle"][0]
    records: list[dict[str, object]] = []
    selected = 0
    for q_idx, q_cycle in enumerate(cycles):
        if cycle_type(q_cycle) != "charge" or not charge_ok(q_cycle):
            continue
        d_idx = next_valid_discharge(cycles, q_idx)
        if d_idx is None:
            continue
        selected += 1
        intermediate = [cycle_type(cycles[index]) for index in range(q_idx + 1, d_idx)]
        next_charge = next((index for index in range(q_idx + 1, d_idx) if cycle_type(cycles[index]) == "charge"), None)
        if d_idx == q_idx + 1:
            taxonomy = "IMMEDIATE_VALID_DISCHARGE"
        elif next_charge is not None:
            taxonomy = "INTERVENING_CHARGE_BEFORE_DISCHARGE"
        elif intermediate and all(item == "impedance" for item in intermediate):
            taxonomy = "INTERVENING_IMPEDANCE_ONLY_THEN_VALID_DISCHARGE"
        elif not intermediate:
            taxonomy = "OTHER_SEQUENCE"
        else:
            taxonomy = "INTERVENING_NONCANONICAL_OPERATION"
        records.append({
            "Battery": BATTERY,
            "LegacyCandidateOrdinal": selected,
            "RawChargeRecordIndex": q_idx,
            "RawChargeStartTime": cycle_time(q_cycle),
            "NearestValidDischargeRecordIndex": d_idx,
            "RawDischargeStartTime": cycle_time(cycles[d_idx]),
            "ImmediateNextType": cycle_type(cycles[q_idx + 1]) if q_idx + 1 < len(cycles) else "NONE",
            "IntermediateOperationSequence": "->".join(intermediate) if intermediate else "NONE",
            "InterveningRecordCount": len(intermediate),
            "InterveningChargeBeforeDischarge": next_charge is not None,
            "Taxonomy": taxonomy,
        })
        if selected >= DEVELOPMENT_CANDIDATES:
            break

    frame = pd.DataFrame(records)
    frame.to_csv(OUT / "b0007_pairing_taxonomy.csv", index=False, encoding="utf-8-sig")
    summary = (frame.groupby("Taxonomy", as_index=False)
               .agg(Count=("Taxonomy", "size"),
                    ExampleRecordIDs=("RawChargeRecordIndex", lambda s: ",".join(map(str, list(s)[:5]))),
                    ExamplePatterns=("IntermediateOperationSequence", lambda s: " | ".join(dict.fromkeys(list(s)[:3])))))
    summary.to_csv(OUT / "b0007_pairing_taxonomy_summary.csv", index=False, encoding="utf-8-sig")
    manifest = {
        "audit": "PTOC_B0007_PAIRING_TAXONOMY_V1",
        "scope": "development-side raw event ordering and waveform metadata only",
        "development_candidate_count": int(len(frame)),
        "test_label_loaded": TEST_LABEL_LOADED,
        "capacity_values_read": CAPACITY_VALUES_READ,
        "selection_definition": "first 67 charge records that satisfy frozen charge event and have a later valid discharge; capacity values are never accessed",
        "taxonomy_definition": {
            "IMMEDIATE_VALID_DISCHARGE": "next raw record is a valid discharge",
            "INTERVENING_IMPEDANCE_ONLY_THEN_VALID_DISCHARGE": "only impedance records occur before the first later valid discharge and no later charge intervenes",
            "INTERVENING_CHARGE_BEFORE_DISCHARGE": "another charge occurs before the first later valid discharge",
            "INTERVENING_NONCANONICAL_OPERATION": "a non-impedance operation occurs without an intervening charge",
        },
        "counts": {row.Taxonomy: int(row.Count) for row in summary.itertuples(index=False)},
    }
    (OUT / "b0007_pairing_taxonomy_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
