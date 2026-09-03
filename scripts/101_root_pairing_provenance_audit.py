"""Label-safe audit of frozen ROOT row identity and discharge-pair uniqueness.

This script deliberately projects only provenance columns from the frozen
feature artifact.  It never loads SOH, feature values, model outputs, or any
test material.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "feature_adequacy_reassessment_v1" / "frozen_raw_features.csv"
TAXONOMY = ROOT / "output" / "ptoc_phase3_blocker_resolution_1" / "b0007_pairing_taxonomy.csv"
OUT = ROOT / "output" / "root_pairing_provenance_audit"
PROVENANCE_COLUMNS = ["Battery", "TestLoaded", "RawChargeCycleIndex", "RawDischargeCycleIndex"]
TAXONOMY_COLUMNS = ["Battery", "RawChargeRecordIndex", "Taxonomy"]


def read_provenance() -> pd.DataFrame:
    """Read the four explicitly approved identity columns; no labels/features."""
    rows = pd.read_csv(SOURCE, usecols=PROVENANCE_COLUMNS)
    if not rows["TestLoaded"].eq(False).all():
        raise RuntimeError("frozen input artifact does not certify TestLoaded=False")
    return rows.sort_values(["Battery", "RawChargeCycleIndex"]).reset_index(drop=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = read_provenance()
    taxonomy = pd.read_csv(TAXONOMY, usecols=TAXONOMY_COLUMNS)
    patterns = {
        (str(r.Battery), int(r.RawChargeRecordIndex)): str(r.Taxonomy)
        for r in taxonomy.itertuples(index=False)
    }

    maps: list[dict[str, object]] = []
    for battery, group in rows.groupby("Battery", sort=True):
        discharge_counts = Counter(int(v) for v in group.RawDischargeCycleIndex)
        for ordinal, r in enumerate(group.itertuples(index=False), start=1):
            charge = int(r.RawChargeCycleIndex)
            discharge = int(r.RawDischargeCycleIndex)
            pattern = patterns.get((str(battery), charge), "IMMEDIATE_VALID_DISCHARGE")
            maps.append(
                {
                    "ROOT_ROW_ID": f"{battery}_{ordinal:03d}",
                    "BATTERY": str(battery),
                    "CHARGE_RECORD_ID": charge,
                    "DISCHARGE_RECORD_ID": discharge,
                    "CHARGE_POSITION": charge,
                    "DISCHARGE_POSITION": discharge,
                    "PAIRING_PATTERN": pattern,
                    "DUPLICATE_DISCHARGE_ID": discharge if discharge_counts[discharge] > 1 else None,
                    "PROVENANCE_CONFIDENCE": "LEVEL_A__DC931F7_FROZEN_ARTIFACT_IDENTICAL",
                }
            )

    duplicate_groups: dict[str, list[dict[str, object]]] = {}
    for item in maps:
        if item["DUPLICATE_DISCHARGE_ID"] is not None:
            key = f"{item['BATTERY']}:{item['DISCHARGE_RECORD_ID']}"
            duplicate_groups.setdefault(key, []).append(item)
    summary = {
        "audit": "ROOT_HISTORICAL_PAIRING_MAP_LABEL_SAFE",
        "source": str(SOURCE.relative_to(ROOT)),
        "columns_read": PROVENANCE_COLUMNS,
        "explicitly_not_read": ["SOH", "all feature values", "metrics", "predictions", "test data"],
        "test_loaded": False,
        "n_root_rows": len(maps),
        "n_unique_discharge_records": len({(x["BATTERY"], x["DISCHARGE_RECORD_ID"]) for x in maps}),
        "n_duplicated_discharge_assignments": len(duplicate_groups),
        "n_rows_involved_in_duplication": sum(len(v) for v in duplicate_groups.values()),
        "affected_batteries": sorted({x["BATTERY"] for v in duplicate_groups.values() for x in v}),
        "duplicate_groups": duplicate_groups,
        "root_historical_pairing_map": maps,
    }
    (OUT / "root_historical_pairing_map.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    inventory = {
        "frozen_feature_artifact": str(SOURCE.relative_to(ROOT)),
        "taxonomy_artifact": str(TAXONOMY.relative_to(ROOT)),
        "source_columns_read": PROVENANCE_COLUMNS,
        "source_columns_not_read": ["SOH", "DISCHARGE_DURATION_S", "DISCHARGE_ENERGY_WH", "all other F1 features"],
        "test_loaded": False,
        "artifact_status": "AVAILABLE_AND_LABEL_SAFE_PROJECTED",
    }
    (OUT / "artifact_inventory.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in summary if k.startswith("n_") or k == "affected_batteries"}, indent=2))


if __name__ == "__main__":
    main()
