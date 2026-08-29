"""Exact, minimal reproduction of dc931f7's S0/F1 M0 Ridge outer validation.

It reuses the historical script's frozen loading, scaling, prediction and
metric functions. Only M0 Ridge(alpha=0.1), A0/F1, and the two fixed
train/validation prefixes are executed. No raw MAT files or locked-test rows
are opened.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_SCRIPT = ROOT / "scripts" / "84_strong_baseline_raw_feature_ablation.py"
HISTORICAL_METRICS = ROOT / "output" / "strong_baseline_raw_ablation_v1" / "strong_baseline_metrics.csv"
SOURCE_COMMIT = "dc931f71be6f92f2895a7b1c26aa3158d3359fab"
OUTPUT_METRICS = ROOT / "SOH2_1_S0_REPRODUCTION_METRICS.csv"


def historical_module():
    spec = importlib.util.spec_from_file_location("historical_s0", HISTORICAL_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load recovered historical S0 script")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    m = historical_module()
    candidate = m.Candidate("M0_RIDGE", "alpha=0.1", 0.1, False)
    rows: list[dict[str, object]] = []
    history = pd.read_csv(HISTORICAL_METRICS)
    for battery in m.BATTERIES:
        x, y = m.load(battery)
        train, end = m.TRAIN_END[battery], m.VAL_END[battery]
        if len(x) != end or len(y) != end or m.TEST_LOADED is not False:
            raise RuntimeError(f"{battery}: frozen prefix/test invariant failed")
        prediction, _ = m.predict(candidate, x[:train], y[:train], x[train:end], 0)
        observed = m.metrics(y[train:end], prediction)
        old = history.loc[(history.Battery == battery) & (history.Model == "M0_RIDGE") & (history.Configuration == "alpha=0.1")]
        if len(old) != 1 or bool(old.iloc[0].TestLoaded):
            raise RuntimeError(f"{battery}: historical S0 artifact invariant failed")
        old = old.iloc[0]
        rows.append({
            "Battery": battery, "Baseline": "S0_RIDGE", "FeatureSet": "A0_FULL_F1",
            "Configuration": candidate.configuration, "TrainingRows": train,
            "ValidationRows": end - train, "FeatureCount": len(m.F1),
            "TestLoaded": False, "Seed": "deterministic",
            "HistoricalRMSE": float(old.RMSE), "CurrentRMSE": float(observed["RMSE"]),
            "AbsoluteDeltaRMSE": abs(float(observed["RMSE"]) - float(old.RMSE)),
            "HistoricalMAE": float(old.MAE), "CurrentMAE": float(observed["MAE"]),
            "AbsoluteDeltaMAE": abs(float(observed["MAE"]) - float(old.MAE)),
            "HistoricalR2": float(old.R2), "CurrentR2": float(observed["R2"]),
            "AbsoluteDeltaR2": abs(float(observed["R2"]) - float(old.R2)),
        })
    result = pd.DataFrame(rows)
    status = "PASS" if bool((result[["AbsoluteDeltaRMSE", "AbsoluteDeltaMAE", "AbsoluteDeltaR2"]] <= 1e-6).all().all()) else "FAIL"
    result["BaselineReproductionStatus"] = status
    result.to_csv(OUTPUT_METRICS, index=False, encoding="utf-8-sig")
    protocol = [
        "# soh2_1 S0 Ridge Reproduction Protocol", "",
        "```text", "REPOSITORY=soh2_1", "RECOVERY_SOURCE=soh02@dc931f7",
        "BASELINE=S0_RIDGE", "MODEL_OR_PROTOCOL_CHANGED=False", "TestLoaded=False", "```", "",
        "This one-time verification reuses the recovered historical script's `load`, `predict`, and `metrics` functions. It runs only `M0_RIDGE`, `alpha=0.1`, `A0_FULL_F1`, and the fixed chronological prefixes: B0007 [0,33) train/[33,67) validation; B0018 [0,25)/[25,51).", "",
        "The seven frozen features are `DISCHARGE_DURATION_S`, `DISCHARGE_V4P0_TO_V3P6_S`, voltage mean/std, temperature mean/std, and `DISCHARGE_ENERGY_WH`. Scaling/imputation is fit only on each training prefix. The frozen CSV has exactly 67 B0007 rows and 51 B0018 rows, all `TestLoaded=False`; no raw MAT, test feature, or test label is opened.",
    ]
    (ROOT / "SOH2_1_S0_REPRODUCTION_PROTOCOL.md").write_text("\n".join(protocol), encoding="utf-8")
    report = [
        "# soh2_1 S0 Ridge Reproduction Report", "",
        f"BASELINE_REPRODUCTION_STATUS={status}", "MODEL_OR_PROTOCOL_CHANGED=False", "TestLoaded=False", "",
        "## Historical versus current metrics", "", result.to_csv(index=False), "",
        "## Environment", "", "```json", json.dumps({
            "historical_script": str(HISTORICAL_SCRIPT.relative_to(ROOT)),
            "historical_metrics": str(HISTORICAL_METRICS.relative_to(ROOT)),
            "source_feature_sha256": sha256(m.SOURCE), "source_commit": SOURCE_COMMIT,
            "python": platform.python_version(), "numpy": np.__version__,
            "pandas": pd.__version__, "sklearn": sklearn.__version__,
        }, indent=2), "```", "",
        "This verifies only that the recovered dc931f7 strong supervised S0 Ridge baseline is reproducible. It is not a paper-method reproduction or a paper-task-compatibility claim.",
    ]
    (ROOT / "SOH2_1_S0_REPRODUCTION_REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print(f"BASELINE_REPRODUCTION_STATUS={status}")
    print("TestLoaded=False")
    if status != "PASS":
        raise RuntimeError("substantive historical S0 difference; do not tune")


if __name__ == "__main__":
    main()
