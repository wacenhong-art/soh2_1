"""One authorized M0-only reassessment of the repaired clean ROOT artifact."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_SCRIPT = ROOT / "scripts" / "84_strong_baseline_raw_feature_ablation.py"
SOURCE = ROOT / "output" / "root_post_completion_repair" / "clean_root_features.csv"
OUT = ROOT / "output" / "root_post_completion_repair"
BATTERIES = ("B0007", "B0018")
TRAIN_END = {"B0007": 33, "B0018": 25}
VAL_END = {"B0007": 67, "B0018": 51}
TEST_LOADED = False


def historical_module():
    spec = importlib.util.spec_from_file_location("root_historical_m0", HISTORICAL_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen M0 Ridge implementation")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    m = historical_module()
    table = pd.read_csv(SOURCE)
    if not table.TestLoaded.eq(False).all():
        raise RuntimeError("clean source violates test lock")
    candidate = m.Candidate("M0_RIDGE", "alpha=0.1", 0.1, False)
    rows: list[dict[str, object]] = []
    for battery in BATTERIES:
        subset = table.loc[table.Battery.eq(battery)].sort_values("RawChargeCycleIndex").reset_index(drop=True)
        train, end = TRAIN_END[battery], VAL_END[battery]
        if len(subset) != end:
            raise RuntimeError(f"{battery}: clean input rows {len(subset)} do not match frozen prefix {end}")
        x = subset.loc[:, m.F1].to_numpy(float)
        y = subset.SOH.to_numpy(float) * 100.0
        prediction, _ = m.predict(candidate, x[:train], y[:train], x[train:end], 0)
        observed = m.metrics(y[train:end], prediction)
        rows.append({
            "Battery": battery, "Baseline": "ROOT_V2_CLEAN_M0_RIDGE",
            "FeatureSet": "A0_FULL_F1", "Configuration": "alpha=0.1",
            "TrainingRows": train, "ValidationRows": end - train,
            "FeatureCount": len(m.F1), "TestLoaded": False,
            "MetricPopulation": "frozen_nonlocked_chronological_validation_prefix",
            **observed,
        })
    result = pd.DataFrame(rows)
    payload = {
        "reassessment_status": "LEGAL_M0_ONLY_COMPLETED",
        "test_loaded": False, "model": "Ridge(alpha=0.1)",
        "feature_set": "A0_FULL_F1", "source": str(SOURCE.relative_to(ROOT)),
        "split": {b: {"train": [0, TRAIN_END[b]], "validation": [TRAIN_END[b], VAL_END[b]]} for b in BATTERIES},
        "no_model_selection": True, "no_hyperparameter_tuning": True,
        "metrics": result.to_dict(orient="records"),
    }
    (OUT / "root_clean_reassessment.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    result.to_csv(OUT / "root_clean_reassessment_metrics.csv", index=False, encoding="utf-8-sig")
    print("ROOT_CLEAN_REASSESSMENT_STATUS=LEGAL_M0_ONLY_COMPLETED")
    print("TestLoaded=False")
    print(result.to_csv(index=False))


if __name__ == "__main__":
    main()
