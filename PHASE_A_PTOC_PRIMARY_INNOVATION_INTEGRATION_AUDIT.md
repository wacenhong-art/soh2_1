# Phase A — PTOC Primary Innovation Integration Audit

## Status and scope

```text
PHASE=PHASE_A_PTOC_PRIMARY_INNOVATION_INTEGRATION_AUDIT
DATE=2026-09-03
ROOT=FROZEN_S0_RIDGE_ALPHA_0P1
ROOT_MODIFIED=False
EXPERIMENT_EXECUTED=False
OUTER_VALIDATION_LOADED=False
TestLoaded=False
PRIMARY_INNOVATION_COUNT=1
PRIMARY_INNOVATION=PREDICTION_TIME_OBSERVABILITY_CONTRACT__PTOC
```

This is a research and protocol audit, not a performance experiment. It does
not claim that PTOC is novel, successful, or authorized for implementation.
The human researcher owns the research question, novelty claim, experimental
design, and eventual conclusion.

## Supervisor-Skills execution log

| Ordered step | Skill actually invoked | Output used in this audit |
|---|---|---|
| 1 | `vibe-research-workflow` | Research reframing is treated as a methodology/benchmark question; AI only performs mechanical evidence organisation and integrity checks. |
| 2 | `deep-research` | Two-round 2024–2026 literature scout: direct search for prediction-time/observability/matched-cycle benchmarks, then adversarial searches for partial/full-cycle and capacity-proxy work. |
| 3 | Codex technical audit | Read-only ROOT, feature, legality, raw-event, split, and dataset audit. |
| 4 | `idea-evaluator` | Fatal-flaw, five-dimension, First Principles, Elephant in the Room, Hamming's Rule, feasibility, and reviewer-attack assessment. |
| 5 | `vibe-research-workflow` | Final integrity review: no experiment/result invention, no citation overclaim, no protocol modification, and human decision retained. |

### Vibe initial research constraints

1. AI may search, organize, audit code, and draft an auditable protocol; it
   cannot own PTOC novelty or the final scholarly conclusion.
2. Every citation and its claimed implication require researcher verification
   against the original paper before manuscript use.
3. No fabricated results, data, labels, procedures, or favourable reframing.
4. No new model, ROOT change, validation/test access, or protocol change is
   permitted in this phase.
5. Target-venue and AI-disclosure compliance remain researcher attestations.

## ROOT: factual PTOC anchor

The frozen ROOT is a deterministic target-only `Ridge(alpha=0.1)`, trained on
the target battery's chronological training prefix. It has no source battery,
transfer, pretrained representation, GAN, or sequence model. Recovered
outer-validation artifacts report approximately `R2=0.966` for B0007 and
`R2=0.987` for B0018; these historical values were not recomputed here.

| Contract field | ROOT evidence |
|---|---|
| `prediction_time` | After the paired current discharge completes. |
| `required_raw_signals` | Discharge voltage, current/time-derived quantities, and temperature. |
| `features` | Duration; 4.0-to-3.6 V duration; voltage mean/std; temperature mean/std; energy. |
| `capacity_adjacent_access` | Current-discharge duration and integrated discharge energy are explicit capacity-adjacent quantities. |
| `current_cycle_completeness` | Full current discharge required. |
| `history_requirement` | Target-battery labelled chronological training history; B0007 `[0,33)`, B0018 `[0,25)`. |
| `future_information` | None in inputs; train-only scaling/imputation. |
| `online_eligibility` | False. |
| `partial_curve_eligibility` | False. |
| `deployment_interpretation` | End-of-current-completed-discharge capacity-adjacent SOH estimate only. |

`ROOT_AS_EMPIRICAL_ANCHOR=MODERATE`: ROOT makes the observation boundary
concrete and auditable, but it is not indispensable theory. Any transparent
completed-discharge estimator could be the high-observability reference. Its
very high accuracy is therefore evidence about the value of its available
information, not evidence for online, partial-curve, or model-method novelty.

## Deep-research: collision map

### Search brief

RQ1: Has prior work already created an executable battery-SOH benchmark that
simultaneously fixes prediction time, observable signals, target semantics,
matched cycles, information boundaries, and the handling of capacity-adjacent
features?

RQ2: Do recent works support the practical importance of distinguishing
full-cycle/post-discharge from earlier/partial-cycle estimates?

RQ3: Is a NASA-only matched-cycle study sufficient to support a methodology
claim?

Two rounds used the frozen query families: `battery SOH prediction time
benchmark`, `observability benchmark`, `information boundary`, `matched cycle`,
`full discharge partial discharge benchmark`, `capacity proxy`,
`deployment-aware benchmark`, and their partial/full-cycle adversarial
variants.

### Verified and bounded findings

| Work | Verification status | Collision level | What the source supports |
|---|---|---|---|
| Rizanov et al., *Toward Trustworthy and Transferable SOH/RUL Estimation…*, *Batteries* 2026, DOI [10.3390/batteries12070255](https://doi.org/10.3390/batteries12070255) | Publisher text read | `PRINCIPLE_LEVEL_COLLISION` and `REPORTING_LEVEL_COLLISION` | Observability, sensing assumptions, validation fidelity and BMS-facing acceptance criteria must accompany accuracy. It is a review/framework, not verified as an executable three-level matched-cycle benchmark. |
| Guo et al., *Towards reliable energy storage…*, *EnergyZ* 2026, [article page](https://www.oaepress.com/articles/energyz.2025.08) | Full accessible article text read | `PRINCIPLE_LEVEL_COLLISION` | Health target, field observability, representation, evaluation and deployment objective need alignment; cross-study comparison is difficult when these differ. No matching executable contract benchmark was identified in the accessible text. |
| Pandit & Ahlawat, *A standardized comparative framework for ML techniques in Li-ion SOH estimation*, *Future Batteries* 2025, DOI [10.1016/j.fub.2025.100099](https://doi.org/10.1016/j.fub.2025.100099) | Metadata/accessible abstract and article context checked | `REPORTING_LEVEL_COLLISION` only | Standardizes comparative protocol/model tuning. It was not found to define full/partial prediction-time contracts or capacity-adjacent restrictions. Exact conclusion/future-work wording remains `UNVERIFIED`. |
| Lab-to-real-world SOH assessment framework, *Energies* 2026, DOI [10.3390/en19061506](https://doi.org/10.3390/en19061506) | Publisher record/abstract checked | `PARTIAL_METHOD` nearby | Addresses validation fidelity across vehicles, time and operating conditions, not verified as a prediction-time contract benchmark. |
| Wang et al., *Open access dataset, code library and benchmarking…*, *Journal of Energy Storage* 2023, [article](https://www.sciencedirect.com/science/article/pii/S2352152X23032826) | Publisher abstract checked | `REPORTING_LEVEL_COLLISION` nearby | Shows established demand for reproducible preprocessing and fair benchmarking, but not a timing-contract framework. |

`DIRECT_COLLISION_LEVEL=PRINCIPLE_ONLY`.

No 2024–2026 source was retrieved that *clearly* satisfies all eight narrow
conditions: formal prediction time; observable signal set; common target;
matched population; controlled boundary; later-information prohibition;
explicit capacity-adjacent treatment; and non-ranking interpretation of
cross-contract metrics. This is an **absence-of-retrieval finding, not a
novelty claim**. A manuscript must not say “first” without an independently
reviewed, broader search and citation verification.

### Exact unresolved gap, if any

The only defensible narrow gap is an *executable empirical protocol*, not the
principle of observability:

> For one fixed capacity-SOH target and one valid-cycle intersection, specify
> the event time, allowed raw signals, completion state, capacity-adjacent
> access, history and future-information permissions; evaluate only
> contract-compatible baselines, and report cross-contract metrics as a
> timeliness–information–accuracy trade-off rather than a direct model rank.

`NARROW_NOVELTY_STATUS=UNRESOLVED__REQUIRES_EXTERNAL_DATA_AND_SECONDARY_LITERATURE_VERIFICATION`.

## Minimal PTOC formal definition

For an estimator (m), its contract is

\[
C_m=\{t_p,\;\mathcal{X}_{\leq t_p},\;\kappa,\;a,\;h,\;f,\;y,\;d,\;p\}.
\]

| Field | Meaning | Status |
|---|---|---|
| (t_p) | physical event/time at which output may be emitted | Necessary |
| \(\mathcal{X}_{\leq t_p}\) | allowed raw signals and causal transformations | Necessary |
| \(\kappa) | current-cycle completion state | Necessary; avoids hiding full-vs-partial differences. |
| (a) | capacity-adjacent access and provenance | Necessary; it distinguishes ROOT-like inputs from early inputs. |
| (h) | permitted labelled/unlabelled history and fitting regime | Necessary |
| (f) | future-information permission, including centred smoothing and life metadata | Necessary |
| (y) | target semantic definition and reference measurement | Necessary |
| (d) | deployment eligibility / intended operating setting | Necessary; prevents post-discharge claims becoming online claims. |
| (p) | evaluation population and split rule | Necessary; matched-cycle comparison cannot otherwise be audited. |

No additional field is justified at this stage. Model architecture and
hyperparameters are intentionally not PTOC fields; they belong to a baseline
control plan.

## Proposed natural contracts — design only

| Contract | Prediction event | Allowed information | Prohibited information |
|---|---|---|---|
| `L1_POST_CHARGE_PRE_DISCHARGE` | Current charge has reached 4.2 V and its real CV cutoff; current discharge has not begun. | Causal charge V/I/T/time descriptors through that cutoff. | Any current-discharge sample; later cycles; centred/full-series processing. |
| `L2_PARTIAL_DISCHARGE` | The following discharge first reaches a predeclared 3.6 V event after the 4.0 V crossing. | L1 plus causal V/I/T/time/discharge integrals through 3.6 V. | Any waveform sample after 3.6 V, including full duration/energy. |
| `L3_POST_COMPLETED_DISCHARGE` | Associated discharge ends. | ROOT frozen F1 contract. | Future cycles, target/lifetime metadata as input. |

The raw sets are nested: `L1 ⊂ L2 ⊂ L3`. These are not random feature
deletions: all three are physically occurring, timestamped waveform events.
The legacy F0 health-feature table is ineligible because its centred Hampel
smoothing and bidirectional interpolation are noncausal. A future protocol
would need new causal raw extractors frozen before evaluation.

### Target semantics

`L1_TARGET_SEMANTICS=VALID_WITH_CONDITIONS`.

For all levels, the target may be the capacity-derived SOH of the same paired
discharge, measured later. This is standard supervised retrospective labeling:
the later capacity measurement is a ground-truth outcome, not a feature
available to the predictor. It is valid only if (i) no downstream capacity,
duration, energy, end-of-discharge state, or label-derived quantity enters L1
or L2 inputs; (ii) the label definition is identical across L1–L3; (iii) the
training labels are historically available under the declared history rule;
and (iv) each claim says *prediction at (t_p), evaluated after the eventual
reference measurement*. It becomes target leakage if the later measurement,
or a proxy computed from it, enters the input/selection pipeline.

`MATCHED_CYCLE_FEASIBILITY=CONDITIONAL_PASS`: existing raw-protocol artifacts
show valid paired B0007/B0018 records meeting charge and discharge event
requirements, but no new completeness audit was run. A future study must
freeze and report the cycle intersection before any labels/metrics are used.

## Comparability rules

| Condition | Status | Permitted interpretation |
|---|---|---|
| Same target, unit, evaluation-cycle intersection, split philosophy, and same prediction time/allowed information | `DIRECTLY_COMPARABLE` | Lower RMSE/MAE or higher R2 may rank estimators within the contract. |
| Same target/intersection/split but different prediction time or allowed information | `CONDITIONALLY_COMPARABLE` | Plot/report together as an information–timeliness–accuracy frontier; do **not** describe raw R2 as direct model superiority. |
| Different target semantics, cycle populations, reference capacity procedure, or split logic | `NOT_DIRECTLY_COMPARABLE` | No direct metric ranking; only contextual discussion after harmonization. |

Thus L1/L2/L3 are comparable for a *contract trade-off* once matched, but not
interchangeable prediction tasks. The paper's unit of comparison would be
“estimator under declared contract,” not “algorithm name.”

## Model-control and minimal experiment plan

`MODEL_CONTROL_PLAN=PLAN_C`.

Use (a) a primary same-family Ridge control for L1/L2/L3, with each contract's
frozen causal feature vector and training-only preprocessing, and (b) the
simplest established baseline compatible with each contract. ROOT stays frozen
at L3. This avoids attributing information effects to hidden neural capacity
while also avoiding a claim that Ridge is universally optimal.

| Experiment | Question | Frozen control | Primary readout | Falsification result |
|---|---|---|---|---|
| E1 Contract-stratified estimation | What is the performance/timing trade-off under L1/L2/L3? | Same target/split; contract-specific causal features | RMSE; MAE/R2 secondary; prediction time/card | No meaningful change in eligibility/interpretation beyond an obvious accuracy ordering. |
| E2 Matched-cycle intersection | Are reported differences an availability artifact? | Same paired valid cycles for every level | Eligibility counts and per-cycle comparison | Intersection too small or differs by level. |
| E3 Same-model control | Does any conclusion persist under one simple family? | Ridge, frozen preprocessing policy | Contract-stratified metrics | Result disappears or reverses solely with model family. |
| E4 Capacity-adjacent audit | Which accuracy comes from later capacity-proximal information? | Provenance table and no backfilling to earlier levels | Contract cards, not a composite score | Features cannot be temporally/provenance classified. |
| E5 External replication | Does the protocol survive another raw-waveform source? | Frozen events, target semantics and model-control policy | Same contract cards and conditional comparison | The dataset lacks pairable raw events/labels, or protocol is materially inapplicable. |

## External-dataset audit

Only candidates with public raw waveform evidence are listed. Their exact
event completeness, cell pairing and licensing still require a pre-experiment
read-only manifest audit; no dataset is implicitly authorized for download or
experimentation.

| Dataset | Public-source evidence | Chemistry/cells | Raw V/I/T | Charge/discharge | Capacity label / pairing | L1/L2/L3 feasibility | Access/license status | PTOC fit |
|---|---|---|---|---|---|---|---|---|
| CALCE CS2/CX2 | [CALCE archive](https://calce.umd.edu/data) | CS2 LiCoO2-family; CX2 chemistry/protocol variants; exact selected cell count must be frozen | V/I available; T only for named subsets | Charge and discharge protocols documented | Capacity-related cycling records; pairing must be audited per file | L1/L2/L3 `CONDITIONAL` | Public downloads; publication attribution requirements stated by CALCE; detailed license `UNVERIFIED` | Good protocol diversity, but heterogeneous file/event schema risk. |
| Oxford Battery Degradation / energy-trading data | [Oxford archive](https://intelligent-earth.ox.ac.uk/publication/1480568/ora-hyrax) | Six cells in energy-trading set; chemistry details must be read from README | V/I/T reported | Cycling data plus periodic capacity measurements | Monthly capacity reference, not necessarily a same-cycle paired label | L1/L2 `CONDITIONAL`; L3 likely `NOT_SAME_SEMANTICS` until label pairing is confirmed | Public archive; README license governs | Strong real-duty-profile relevance; weak for same-cycle L1–L3 labels. |
| RWTH/ISEA NMC/C-SiO aging data | [Scientific Data record](https://www.nature.com/articles/s41597-024-03831-x) | NMC/C-SiO cell(s); cell count must be frozen from data descriptor | Raw V/I/T reported | Cycling plus characterisation | Capacity/health fields reported; exact alignment must be audited | `CONDITIONAL` | Public scientific dataset; specific reuse terms require verification | Strong instrumentation, but possible single-cell generalization weakness. |

`TOP_EXTERNAL_DATASET_1=CALCE__CONDITIONAL`

`TOP_EXTERNAL_DATASET_2=RWTH_ISEA_NMC_CSiO__CONDITIONAL`

Oxford is useful for a subsequent deployment-timing study, but is not selected
for the primary same-cycle L1–L3 replication until label/event pairing is
proven.

`EXTERNAL_VALIDATION_FEASIBILITY=CONDITIONAL__REQUIRES_MANIFEST_AND_LICENSE_AUDIT`.

## Idea-evaluator assessment

### Fatal flaws

| Flaw | Severity | Evidence and required defense |
|---|---|---|
| F1: broad novelty collision | MAJOR | Rizanov and Guo already articulate observability/deployment-aligned evaluation. Restrict any claim to an executable, matched-cycle, prediction-time contract protocol and verify that distinction again. |
| F6/F9: trivial or solution-hunting contribution | MAJOR | NASA-only L1<L2<L3 can merely show that later/full data help. Demonstrate changed validity of model ranking/eligibility and a BMS decision implication, not just better metrics. |

### Higher, Faster, Stronger, Cheaper, Broader

| Dimension | Score | Evidence |
|---|---:|---|
| Higher | 3/10 | PTOC does not seek a higher-R2 estimator. |
| Faster | 4/10 | Earlier reporting may be timelier, but no timing benefit has been measured. |
| Stronger | 6/10, mechanism-based | Explicit contracts could prevent invalid deployment claims; no empirical robustness evidence yet. |
| Cheaper | 5/10 | Contract disclosure could expose sensing cost, but no cost mechanism/measurement is frozen. |
| Broader | 6/10, mechanism-based | One contract representation could unify charge, partial-discharge and post-discharge reports; current data scope is narrow. |

First Principles: `PARTIAL` — challenges the hidden habit of ranking estimates
without binding them to prediction time. Elephant in the Room: `YES` —
full-cycle capacity proxies are often operationally unlike online inputs.
Technology Cycle: `NO` — the work could have been attempted earlier. Hamming's
Rule: `PARTIAL` — it matters if it changes what BMS-facing claims are accepted,
but only if external replication supports it. Disruptive potential: `POSSIBLE`,
not established.

| Score | Value | Basis |
|---|---:|---|
| Novel problem | 4/10 | Broad principle collides; narrow executable protocol unverified. |
| Methodology novelty | 5/10 | A differentiating axis exists but no external validation yet. |
| Real-world significance | 9/10 | Prediction-time and sensing eligibility are material BMS constraints. |
| ROOT compatibility | 7/10 | ROOT is a clear L3 example, not a universal benchmark. |
| NASA feasibility | 5/10 | Supports design feasibility, not paper-level generalization. |
| External-data feasibility | 5/10 | Candidate raw data exist, but pairing/licenses remain unverified. |
| Scientific necessity | 6/10 | Strong if it changes comparison validity; weak if it only adds reporting. |
| Reviewer defensibility | 4/10 | Dependent on matched-cycle, controls, external replication and nontrivial decision analysis. |
| Collision risk | 8/10 | High at principle/reporting level. |
| Paper story | 5/10 | Could become coherent as methodology, not as ROOT-plus-table. |
| Expected paper ceiling | 5/10 now; 7/10 conditional | NASA-only is not paper-ready; robust multi-dataset external validation may support a JES/JPS-class methodology submission, not guaranteed. |

## Reviewer attack sheet

| Attack | Severity | Current defense | Evidence needed | Fatal if unresolved? |
|---|---|---|---|---|
| R1 More information naturally improves prediction. | Critical | PTOC must show a change in validity/eligibility of comparisons, not the monotone result itself. | Ranking/claim changes under contract cards and external replication. | Yes |
| R2 Why not only report time and feature list? | Major | A prose checklist cannot prevent later signals entering earlier models or enforce matched cycles. | Executable schema, compliance checks, and a result not reducible to a table. | Yes |
| R3 Why PTOC rather than a checklist? | Major | Only if fields control actual extraction/evaluation permissions. | Reproducible contract validator/specification. | Yes |
| R4 Difference from Rizanov 2026? | Critical | Rizanov is principle/framework; PTOC must be the operational matched-cycle instantiation. | Source-by-source differentiation and independent review. | Yes |
| R5 Three levels are different tasks. | Major | They are conditionally comparable only for a trade-off on same target/intersection, never direct R2 ranking. | Formal comparability rules and matched population. | Yes |
| R6 Later capacity label leaks into L1. | Major | Later label is supervised ground truth, not a predictor; features must remain causal. | Feature-provenance and leakage audit. | Yes |
| R7 ROOT energy is near capacity. | Major | Precisely why L3 needs capacity-adjacent flagging; high R2 is not online-method evidence. | Provenance/capacity-adjacent audit. | No, but claim must be limited. |
| R8 What does ROOT's R2≈0.99 mean? | Major | It demonstrates a high-observability reference only. | Same-model/contract controls. | No |
| R9 Why are B0007/B0018 enough? | Critical | They are not enough for generalization. | External, frozen replication. | Yes |
| R10 External data behave differently. | Major | That is a valid falsification, not a reason to tune PTOC after results. | Predeclared external protocol and negative-result reporting. | Yes |
| R11 Why methodology, not feature study? | Major | Scope is contract compliance and comparison validity across estimators, not new features. | Multi-model/contract audit beyond ROOT. | Yes |
| R12 Why should a reviewer care? | Major | BMS deployment decisions require knowing when a number can be emitted and what sensing burden it uses. | Concrete decision/use-case interpretation. | Yes |

`MORE_INFORMATION_TRIVIALITY_RISK=FATAL` unless the study demonstrates the
following narrower claim:

> **For capacity-SOH estimators, reported error is interpretable only jointly
> with a machine-checkable prediction-time information contract; matched-cycle
> contract stratification can change which estimator is eligible for a claimed
> deployment setting, even when all estimates share the same target.**

If results only show “more information gives lower error,” PTOC must be
rejected rather than extended with another module or metric.

## Falsification gates

| Gate | Status | Evidence |
|---|---|---|
| PTOC_F1 near-identical executable benchmark exists | `UNRESOLVED` | No direct one retrieved; broader search/independent researcher verification still required. |
| PTOC_F2 only a reporting checklist | `UNRESOLVED` | Becomes `FAIL` unless extraction permissions and matched-cycle controls affect conclusions. |
| PTOC_F3 inconsistent L1/L2/L3 targets | `PASS_WITH_CONDITIONS` | Same paired capacity-SOH target is semantically valid if later label never becomes input. |
| PTOC_F4 cannot match cycles | `UNRESOLVED` | Plausible for B0007/B0018 artifacts; no newly run completeness audit. |
| PTOC_F5 needs artificial deletion | `PASS_WITH_CONDITIONS` | Events are native waveform events; causal fresh extraction is required. |
| PTOC_F6 only proves more information helps | `UNRESOLVED__HIGH_RISK` | Requires evidence of comparison/deployment consequences. |
| PTOC_F7 capacity-adjacent access cannot be handled | `PASS_DESIGN_ONLY` | Field (a) and provenance tags define handling; implementation untested. |
| PTOC_F8 ROOT is not meaningful anchor | `PASS_LIMITED` | It is a transparent L3 anchor, not an indispensable method. |
| PTOC_F9 external public data cannot validate | `UNRESOLVED` | CALCE/RWTH candidates need manifests, event pairing and license audit. |
| PTOC_F10 lacks BMS decision value | `UNRESOLVED` | Motivation is credible; a concrete decision analysis is not yet designed. |

## G1 governance conflict

`G1_GOVERNANCE_CONFLICT=True`.

The present `RESEARCH_GUARDRAILS.md` requires every new experiment to solve an
*observed failure* in the existing development work. PTOC is a
human-governed methodology/benchmark reframing, not a proposed repair for a
ROOT predictive failure. ROOT's documented post-discharge boundary is an
observed applicability limitation, but it is not evidence that ROOT failed.
Calling it a failure merely to pass G1 would violate the guardrail's
truthfulness rule.

### Minimal guardrail amendment proposal — not applied

Add a separate, equally strict path:

```text
METHODOLOGY_BENCHMARK_EXCEPTION

Allowed only when a documented protocol/applicability mismatch exists.
The Decision Record must state the non-performance problem, give prior-work
evidence, freeze an executable protocol and falsification criteria, preserve
G3 leakage/test locks, include strong simple baselines, and reserve an
independent external dataset for G5. It may not claim model superiority from
cross-contract metrics. G1 is replaced only by M1: a directly documented
evaluation-validity or deployment-eligibility problem.
```

This amendment does **not** relax leakage, locked-test, protocol-freezing,
external-validation, or post-negative-result stopping requirements. It must
be explicitly approved and written by the human researcher before any PTOC
experiment or code implementation.

## Paper integration map — design only

```text
Existing ROOT (transparent L3 reference)
        ↓
Observed information-boundary / applicability mismatch
        ↓
PTOC formulation and contract cards
        ↓
Natural L1/L2/L3 timing contracts and matched-cycle rule
        ↓
Contract-compatible simple baselines + same-model control
        ↓
External frozen replication
        ↓
Deployment interpretation: eligibility, timeliness, information burden
```

| Section | Purpose | Key claim | Required evidence |
|---|---|---|---|
| 1 Introduction | Motivate the comparability problem. | Error alone lacks deployment meaning without a contract. | Literature and real BMS context. |
| 2 Related Work | Separate evaluation frameworks, partial-cycle methods and benchmarks. | PTOC is narrower than general observability guidance. | Verified collision table. |
| 3 Problem Formulation | Define target and conditional comparability. | Estimator-plus-contract is the comparison unit. | Formal definition. |
| 4 PTOC | Specify executable fields and compliance rules. | Later information cannot enter earlier contracts. | Contract cards/provenance. |
| 5 Experimental Protocol | Freeze events, cycle intersection, models and splits. | No model-capacity or availability confounding. | Pre-registration and controls. |
| 6 Results | Report frontier, not raw cross-contract winner. | Contract changes eligibility/interpretation. | E1–E5. |
| 7 Discussion | Explain BMS meaning and nontrivial outcomes. | No claim follows from accuracy alone. | Decision/use-case analysis. |
| 8 Limitations | State data/event/label constraints. | PTOC scope is not universal. | Negative/external results. |
| 9 Conclusion | Answer the methodology question only. | Validated only if gates survived. | Frozen evidence. |

## One-primary-contribution wording — provisional, not a manuscript claim

**Research question:** Can capacity-SOH estimators that emit at different
physical times be evaluated under one reproducible, matched-cycle protocol
without treating their raw error metrics as direct model rankings?

**Hypothesis:** If prediction-time information access is formalized and
enforced, then otherwise similar reported metrics will map to different
deployment eligibility claims, rather than a single unconditional notion of
estimator superiority.

**Primary contribution:** PTOC is a machine-checkable evaluation formulation
that binds an SOH estimate to its prediction time, causal information boundary,
capacity-adjacent access, history, target and eligible deployment claim.

**One contribution bullet:** We formulate and externally test PTOC as an
executable matched-cycle evaluation protocol for interpreting SOH accuracy
under distinct natural prediction-time information contracts.

## Final integrity review and decision

The final Vibe Research review found: no fabricated experimental result; no
validation/test access; no change to ROOT; no second innovation; citations are
bounded to accessed material; inaccessible conclusions/future-work text is
marked `UNVERIFIED`; and unfavourable principle-level collisions are retained.
The researcher must still verify citations, own the final novelty/design
decision, and check venue AI-disclosure rules.

```text
FINAL_VIBE_INTEGRITY_REVIEW=PASS
SUPERVISOR_SKILLS_GATE=PASS
FINAL_VERDICT=PTOC_REQUIRES_GUARDRAIL_DECISION
NEXT_STAGE=HUMAN_REVIEW_ONLY
```

PTOC cannot enter protocol design under the current guardrail because G1 has
no methodology/benchmark route. Even if the proposed minimal amendment is
approved, the first required action is a Decision Record plus a read-only
external-data manifest audit—not an experiment.
