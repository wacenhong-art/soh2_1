# PTOC External Dataset Manifest — Source Eligibility Only

```text
AUDIT_SCOPE=metadata__source__license__published_description
DATA_DOWNLOAD=False
EXTERNAL_EXPERIMENT=False
TestLoaded=False
```

| Field | NMC/C–SiO (Luh & Blank) | RWTH ISEA NMC/graphite |
|---|---|---|
| Source | [Scientific Data (2024)](https://doi.org/10.1038/s41597-024-03831-x) | [Dataset DOI](https://doi.org/10.18154/RWTH-2021-04545), [repository](https://github.com/isea-rwth-aachen/battery-degradation-trajectory-prediction) |
| Chemistry/cells | LG INR18650HG2 NMC/C–SiO; 228 cells | Sanyo/Panasonic UR18650E NMC/graphite; 48 cells |
| Raw V/I/T | Reported at 2 s | Reported in public Rawdata.zip |
| Charge/discharge evidence | Cyclic state/capacity records reported | Raw waveform plus capacity/energy reported |
| License/access | Public; CC-BY-4.0 reported | Public; CC-BY-4.0 reported |
| L1/L2/L3 feasibility | Conditional on schema/event/pair audit | Conditional on schema/event/pair audit |
| Status | `PASS_FOR_SOURCE_ELIGIBILITY` | `PASS_FOR_SOURCE_ELIGIBILITY` |

`TOP_EXTERNAL_DATASET_1=Luh_Blank_NMC_C-SiO`; it combines many cells, raw
V/I/T and a public license. `TOP_EXTERNAL_DATASET_2=RWTH_ISEA_NMC_GRAPHITE` is
an independent backup. Neither status authorizes download, processing or an
external experiment. Exact file-level pairing, reference-capacity semantics
and event extraction remain a later frozen-protocol audit.
