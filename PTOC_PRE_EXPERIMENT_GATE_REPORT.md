# PTOC Phase ③ — Pre-Experiment Gate Report

```text
PHASE=③ PTOC PRE-EXPERIMENT GATE
DATE=2026-09-03
ROOT_STATUS=FROZEN
ROOT_MODIFIED=False
PERFORMANCE_EXPERIMENT_RUN=False
OUTER_VALIDATION_LOADED=False
TestLoaded=False
PRIMARY_INNOVATION_COUNT=1
PRIMARY_INNOVATION=PTOC
```

## Final decision

```text
PTOC_PRE_EXPERIMENT_GATE=BLOCKED
BLOCKING_GATE_1=G2_DIRECT_COLLISION_ACCEPTABLE__UNRESOLVED
BLOCKING_GATE_2=MATCHED_CYCLE__FAIL_UNDER_FROZEN_STRICT_PAIR_RULE_FOR_B0007
EXPERIMENT_AUTHORIZATION=BLOCKED
NEXT_STAGE=HUMAN_REVIEW
```

This is a negative pre-experiment result. It does not claim PTOC novelty,
ROOT failure, or the existence of any L1/L2/L3 performance result.

## ③-A — Direct-collision verification

Two independent 2024–2026 searches covered SOH, prediction timing,
observability/information boundary, full/partial discharge, matched cycles,
capacity proxy and deployment-aware evaluation. Closest verified works are:

| Work | Verified scope | Classification |
|---|---|---|
| Rizanov et al., *Batteries* (2026), [DOI](https://doi.org/10.3390/batteries12070255) | Metadata/review topic verified; full-text conclusion scope was not independently available here. | `PRINCIPLE_ONLY__UNVERIFIED_FULL_TEXT_SCOPE` |
| Pandit & Ahlawat, *Future Batteries* (2025), [DOI](https://doi.org/10.1016/j.fub.2025.100099) | Standardized comparative/evaluation framing. | `PARTIAL_METHOD` |
| Guo et al., *EnergyZ* (2026), [article](https://www.oaepress.com/articles/energyz.2025.08) | Target/signal/deployment alignment. | `PRINCIPLE_ONLY` |
| Petrella et al., *JES* (2025), [DOI](https://doi.org/10.1016/j.est.2025.118747) | Partial-charge SOH method. | `PARTIAL_METHOD` |
| Zhang & Lai, *WEVJ* (2025), [DOI](https://doi.org/10.3390/wevj16050277) | Partial-discharge-profile method. | `PARTIAL_METHOD` |
| Ma et al., *Energies* (2026), [DOI](https://doi.org/10.3390/en19061506) | Lab-to-field/data-measurement gap. | `PRINCIPLE_ONLY` |

No retrieved source was verified to implement the conjunction of explicit
prediction time, causal boundary, cycle completeness, capacity-adjacent
flagging, identical target semantics, matched population, and prohibition of
cross-contract R² as a direct model ranking. But adjacent work prevents any
absence-of-search novelty claim.

```text
DIRECT_COLLISION_LEVEL=PARTIAL_METHOD
NARROW_NOVELTY_STATUS=UNRESOLVED__CONCEPTUAL_PRIOR_EXISTS__EXECUTABLE_PROTOCOL_NOT_YET_RETRIEVED
G2_DIRECT_COLLISION_ACCEPTABLE=PENDING
```

Full-text/citation-chaining verification, especially for Rizanov, is required
before any methodology novelty claim can pass.

## ③-B / ③-C — Checklist and triviality gates

PTOC has executable compliance effects only if later-cycle information makes an
earlier contract ineligible, every level shares a predeclared cycle
intersection, capacity-adjacent features are disclosed, and cross-contract R²
cannot be treated as a direct leaderboard. Its frozen nontrivial claim is:

> With a common SOH target and matched cycle population, an error metric is
> deployment-interpretable only together with its prediction-time information
> contract; cross-contract error differences alone do not establish general
> model superiority.

The direction must fail if results only establish “later/more information gives
lower error,” without a changed deployment interpretation or an executable
compliance consequence.

```text
CHECKLIST_NOT_FATAL=PASS_FOR_PROTOCOL_ONLY
TRIVIALITY_NOT_FATAL=PASS_FOR_PROTOCOL_ONLY
MORE_INFORMATION_TRIVIALITY_RISK=HIGH
```

## ③-D — Target semantics

For qualifying pair `(q(c), d(c))`, `Y_c = 100 × Capacity(d(c)) / Q_nom`.
The label timestamp is `discharge_end(d(c))`; L1 emits after charge CV cutoff,
L2 at the first predeclared 3.6 V discharge event, and L3 at discharge end. A
later acquired held-out label is not future-feature leakage. Leakage arises if
later discharge duration, energy, tail waveform, selection, scaler statistics,
or future-cycle information enters an earlier predictor.

```text
L1_TARGET_SEMANTICS=VALID_WITH_FROZEN_CONDITIONS
L2_TARGET_SEMANTICS=VALID_WITH_FROZEN_CONDITIONS
L3_TARGET_SEMANTICS=VALID
TARGET_SEMANTICS_GATE=PASS_WITH_CONDITIONS
```

## ③-E — Matched-cycle raw-event audit

The predeclared rule was not changed after inspection: a qualifying charge must
be immediately followed by a qualifying discharge. Charge: `V>=4.2`, later
`abs(I)<=0.02`; discharge: first `V<=4.0`, later `V<=3.6`. The audit inspected
raw V/I/T/time metadata and record order only. It did not read capacity values
or locked test labels, although it loaded raw MAT containers; this is raw
metadata access, not a claim of zero raw-file access.

| Battery | Required frozen ROOT rows | Strict eligible pairs | Status |
|---|---:|---:|---|
| B0007 | 67 | 31 | FAIL |
| B0018 | 51 | 51 | PASS |

Exclusions were 151 `AMBIGUOUS_PAIR_NEXT_IMPEDANCE`, 2 next-charge conflicts,
and three data/event exceptions. Detailed evidence is in
`output/ptoc_pre_experiment_gate_v1/matched_cycle_event_audit.csv` and
`matched_cycle_event_manifest.json`.

```text
MATCHED_CYCLE_RULE=FROZEN_STRICT_IMMEDIATE_PAIR
MATCHED_CYCLE_B0007=FAIL__31_OF_67
MATCHED_CYCLE_B0018=PASS__51_OF_51
MATCHED_CYCLE=FAIL
```

The pairing rule is not relaxed here. Any future change requires explicit human
approval and `MASTER_PLAN_CHANGE_REQUIRED=True`.

## ③-F — External dataset manifest

No external data were downloaded or run. Source eligibility only:

| Rank | Dataset | Evidence | Status |
|---|---|---|---|
| 1 | Luh & Blank NMC/C–SiO | 228 LG INR18650HG2 cells; raw V/I/T, capacity/state records, public CC-BY-4.0. [DOI](https://doi.org/10.1038/s41597-024-03831-x) | `PASS_FOR_SOURCE_ELIGIBILITY__EXECUTION_CONDITIONAL` |
| 2 | RWTH ISEA NMC/graphite | 48 Sanyo/Panasonic UR18650E cells; public raw V/I/T and capacity/energy. [Dataset DOI](https://doi.org/10.18154/RWTH-2021-04545) | `PASS_FOR_SOURCE_ELIGIBILITY__EXECUTION_CONDITIONAL` |
| Conditional | CALCE | Public portal, but per-file V/I/T/pairing/license conditions are unverified. [Portal](https://calce.umd.edu/data) | `CONDITIONAL_ONLY` |

```text
EXTERNAL_MANIFEST=PASS_FOR_SOURCE_ELIGIBILITY
EXTERNAL_EXECUTION_READINESS=CONDITIONAL
TOP_EXTERNAL_DATASET_1=Luh_Blank_NMC_C-SiO
TOP_EXTERNAL_DATASET_2=RWTH_ISEA_NMC_GRAPHITE
```

## ③-G / ③-H — Controls and falsification

The non-executable protocol freezes deterministic target-only
`Ridge(alpha=0.1)` at every level with contract-causal features, train-only
preprocessing and no retuning. ROOT remains the L3 reference; a refit over the
matched population is `L3_RIDGE_SAME_POPULATION_CONTROL`, not ROOT
reproduction. Train-prefix mean is the simple baseline; persistence is legal
only when its historical capacity input is legal at the timestamp.

```text
CONTROL_AND_FALSIFICATION_FREEZE=PASS_FOR_NONEXECUTABLE_PROTOCOL
CAN_BE_CHANGED_AFTER_EXPERIMENT=False
```

## Integrity review

### Idea-evaluator assessment

PTOC is a **new evaluation setting/methodology candidate**, not a new SOH
network. Its one-sentence story is: a high-R² SOH estimate must be interpreted
under the prediction-time information it was allowed to observe. The reviewer
fatal-flaw audit identifies two major risks: F1, an executable-benchmark
collision not yet fully ruled out; and F4, a data-refuted matched-cycle
mechanism under the predeclared strict B0007 rule. The second has no permitted
in-Phase repair.

| Dimension | Score | Evidence and limitation |
|---|---:|---|
| Higher | 5/10 | It does not claim an accuracy increase. |
| Faster | 6/10 | Ridge controls and contract cards are cheap, but no run is authorized. |
| Stronger | 6/10 | Could prevent deployment overclaim, pending valid matched evaluation. |
| Cheaper | 7/10 | Uses simple controls and published metadata, not a new deep model. |
| Broader | 7/10 | Contract framing could span waveform datasets, subject to external audit. |

First-principles and elephant-in-the-room probes are positive: the field often
reports error without making the information-emission boundary executable.
Hamming's Rule is only conditionally positive: it matters if the contract
changes permitted BMS conclusions, not if it merely repeats that more samples
improve error. The reviewer-style verdict is therefore
`REJECT_AND_PIVOT_THIS_STRICT_PAIRING_VARIANT`, not a rejection of every
possible PTOC formulation. A human must decide whether a scientifically
justified, pre-result pairing-policy amendment is worth reopening through
master-plan control.

### Final Vibe Research review

The six rules were applied: AI was used for source organisation and mechanical
auditing; the human research question remains the user's decision; citations
were bounded to verified scope; no data/result was fabricated; no conclusion
was substituted for researcher judgment; and venue AI-disclosure remains a
user verification duty. The audit did not lower novelty standards, treat a new
name as novelty, reinterpret ROOT as a failure, use a test label, introduce a
second contribution, or change ROOT to fit PTOC.

Requested workflow, deep research, and reviewer-style idea evaluation were
applied. No performance result, validation/test label, external dataset run,
model fit, hyperparameter change, ROOT modification, new feature, or second
innovation was introduced.

```text
VIBE_RESEARCH_WORKFLOW_USED=True
DEEP_RESEARCH_USED=True
IDEA_EVALUATOR_USED=True
FINAL_VIBE_INTEGRITY_REVIEW=PASS
SUPERVISOR_SKILLS_GATE=PASS
LEAKAGE_FOUND=False
ROOT_MODIFIED=False
TestLoaded=False
```
