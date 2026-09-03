# SOH Research Master Plan

> Version: `1.0.0`  
> Status source: `RESEARCH_GUARDRAILS.md` remains the highest authority for
> research safety and experimental authorization. This document is the durable
> route map, phase-state register, and change-control record.

## CURRENT PROJECT STATUS

```text
CURRENT_PHASE=③ PTOC PRE-EXPERIMENT GATE
CURRENT_PHASE_STATUS=BLOCKED
LAST_COMPLETED_PHASE=② RESEARCH GOVERNANCE
LAST_COMPLETED_GATE=METHODOLOGY_BENCHMARK_GATE=PASS_FOR_PLANNING
PRIMARY_INNOVATION=PTOC
PRIMARY_INNOVATION_COUNT=1
ROOT_STATUS=FROZEN
EXPERIMENT_AUTHORIZATION=BLOCKED_PENDING_PTOC_PRE_EXPERIMENT_GATE
LOCKED_TEST_STATUS=NOT_LOADED
NEXT_ALLOWED_ACTION=HUMAN_DECISION_ON_L1_REFERENCE_TEST_SEMANTICS_AND_EXTERNAL_OPERATION_ADAPTER_AUDIT
```

## ⓪ Overall Research Objective

围绕已经冻结的 ROOT 强基线，只保留一个主创新点：
`Prediction-Time Observability Contract (PTOC)`。目标是形成一篇
protocol-rigorous、reproducible、falsifiable、deployment-interpretable 且
externally validated 的 SOH methodology paper。

```text
PRIMARY_INNOVATION_COUNT=1
PRIMARY_INNOVATION=PTOC
ROOT_STATUS=FROZEN
```

主论文故事：

```text
ROOT
  -> post-completed-discharge high-observability contract
  -> PTOC formalization
  -> prediction-time-specific information boundaries
  -> matched-cycle evaluation
  -> same-model / controlled comparison
  -> external dataset replication
  -> deployment-eligibility interpretation
```

ROOT 不是 PTOC method，也不是 paper-method reproduction。它是一个 strong,
target-only, supervised, high-observability reference。

## PHASE PROGRESS

| Symbol | Phase | Status | Gate | Next |
|---|---|---|---|---|
| ① | ROOT Freeze | PASS | ROOT freeze PASS | ② |
| ② | Research Governance | PASS | `METHODOLOGY_BENCHMARK_GATE=PASS_FOR_PLANNING` | ③ |
| ③ | PTOC Pre-Experiment Gate | BLOCKED | G2 partial collision acceptable; V1 pairing fails; proposed v1.1 is semantically/external-schema blocked | HUMAN_REVIEW |
| ④ | PTOC Development Experiment | BLOCKED | Requires ③ PASS + human authorization | ⑤ |
| ⑤ | External Validation | BLOCKED | Requires ④ PASS + human authorization | ⑥ |
| ⑥ | Robustness & Necessary Controls | BLOCKED | Requires ⑤ PASS + human authorization | ⑦ |
| ⑦ | Paper Evidence Freeze | BLOCKED | Requires ⑥ PASS + human authorization | ⑧ |
| ⑧ | Manuscript | BLOCKED | Requires ⑦ PASS + human authorization | ⑨ |
| ⑨ | Final Research Integrity Audit | BLOCKED | Requires ⑧ PASS | `SUBMISSION_READY` |

## FROZEN PROJECT CONSTRAINTS

```text
ROOT_STATUS=FROZEN
ROOT_ROLE=HIGH_OBSERVABILITY_REFERENCE
PRIMARY_INNOVATION_COUNT=1
PRIMARY_INNOVATION=PTOC
NO_SECOND_INNOVATION=True
LOCKED_TEST_DEFAULT=NOT_LOADED
NO_FORCE_PUSH=True
NO_HARD_RESET=True
NO_HISTORY_REWRITE=True
```

Changing any frozen constraint requires `MASTER_PLAN_CHANGE_REQUIRED=True`, a
new Decision Record, and explicit human-researcher authorization. It must not
be changed as a response to an unfavourable result.

---

## ① ROOT Freeze

### STATUS

`PASS`

### OBJECTIVE

Establish an auditable strong supervised reference without presenting it as the
paper reproduction or as PTOC itself.

### SCIENTIFIC QUESTION

What can a transparent target-only, post-completed-discharge estimator achieve
when it is allowed capacity-adjacent current-discharge information?

### INPUTS

Recovered clean ROOT implementation, frozen F1 feature contract, chronological
target prefixes, and S0 protocol/legality audits.

### ALLOWED

Read and cite frozen ROOT artifacts; preserve ROOT as the L3 reference.

### FORBIDDEN

Changing ROOT model, alpha, features, target, split, or interpreting it as an
online/partial-curve estimator or paper-method reproduction.

### REQUIRED TASKS

- Freeze `Ridge(alpha=0.1)` semantics and F1 feature provenance.
- Verify train-only preprocessing and locked-test non-access.
- Mark duration and discharge energy as legal but capacity-adjacent.

### GATES

- `ROOT_FREEZE`: PASS only if model/feature/split contract is recorded and no
  test leakage is found; FAIL if ROOT semantics drift.
- `INTERPRETATION_BOUNDARY`: PASS only if ROOT remains post-completed-discharge.
  UNRESOLVED requires claim restriction, never a silent reinterpretation.

### REQUIRED OUTPUTS

`S0_ACTUAL_PROTOCOL.md`, `S0_FEATURE_LEGALITY_AUDIT.md`, reproduction artifacts,
and Git provenance.

### ADVANCEMENT CONDITION

Frozen, auditable ROOT and a documented interpretation boundary.

### NEXT PHASE

② Research Governance.

### COMPLETION RECORD

```text
COMPLETED_DATE=historical__see_ROOT_artifacts
COMPLETED_COMMIT=dc931f7_source_provenance__historical
FINAL_STATUS=PASS
KEY_RESULT=Ridge(alpha=0.1), target-only; B0007 R2≈0.966 and B0018 R2≈0.987 in frozen historical outer-validation artifacts.
FAILED_OR_UNRESOLVED_ITEMS=ROOT is not online, partial-curve, transfer, or paper-method evidence.
DECISION=Retain ROOT only as a frozen high-observability reference.
```

---

## ② Research Governance

### STATUS

`PASS`

### OBJECTIVE

Provide a strict route for methodology/benchmark research without inventing a
ROOT predictive failure or weakening existing integrity controls.

### SCIENTIFIC QUESTION

Can a documented evaluation-validity/deployment-eligibility problem legitimately
open research planning while retaining all leakage, test, falsification and
external-validation controls?

### INPUTS

`RESEARCH_GUARDRAILS.md`, Phase-A PTOC audit, and the PTOC primary-direction
Decision Record.

### ALLOWED

Governance audit, decision records, literature/protocol planning, and minimal
amendments that preserve existing red lines.

### FORBIDDEN

Using “methodology” as a general G1 exemption; test access; experiment launch;
ROOT modification; post-hoc problem reframing.

### REQUIRED TASKS

- Compare direct G1 modification, narrow exception, and independent gate.
- Reject any option that weakens G2–G7 or permits protocol drift.
- Record PTOC as an unresolved sole candidate, not as a validated innovation.

### GATES

- `METHODOLOGY_BENCHMARK_GATE`: PASS_FOR_PLANNING only when the problem is
  pre-documented, concrete and auditable; baseline/target/split stay frozen;
  G2–G7 remain binding; external validation is required for general claims.
- FAIL if the amendment creates a loophole, alters test/leakage policy, or
  automatically authorizes experiments. UNRESOLVED remains BLOCKED.

### REQUIRED OUTPUTS

`RESEARCH_GUARDRAILS.md` amendment, `DECISION_RECORD_PTOC_PRIMARY_DIRECTION.md`,
and Git archive.

### ADVANCEMENT CONDITION

Only planning is enabled. PTOC must still pass every mandatory item in ③ and
receive explicit human authorization before ④.

### NEXT PHASE

③ PTOC Pre-Experiment Gate.

### COMPLETION RECORD

```text
COMPLETED_DATE=2026-09-03
COMPLETED_COMMIT=7ddbecd
FINAL_STATUS=PASS
KEY_RESULT=OPTION_C selected: independent METHODOLOGY_BENCHMARK_GATE; original model-research G1 unchanged.
FAILED_OR_UNRESOLVED_ITEMS=PTOC scientific novelty, semantics, external-data feasibility and experiment authorization remain unresolved.
DECISION=Open PTOC planning only; block all PTOC performance experiments pending ③.
```

---

## ③ PTOC Pre-Experiment Gate

### STATUS

`BLOCKED`

### OBJECTIVE

Resolve the scientific and protocol-level kill conditions before any L1/L2/L3
performance experiment is implemented.

### SCIENTIFIC QUESTION

Does PTOC survive novelty, semantics, matched-population, nontriviality,
external-data and reproducibility checks strongly enough to justify a frozen
development protocol?

### INPUTS

① ROOT Freeze PASS; ② Governance PASS; `DECISION_RECORD_PTOC_PRIMARY_DIRECTION.md`;
the Phase-A PTOC integration audit.

### ALLOWED

Read-only literature verification, manifest/schema/license audits, code and
raw-event feasibility inspection without loading test labels, protocol design,
Decision Record updates, and falsification/provenance planning.

### FORBIDDEN

L1/L2/L3 training; Ridge fitting; test access; external-data download or
processing; ROOT changes; new features/models; hyperparameter searches;
introducing a second innovation; using results to redefine any gate.

### REQUIRED TASKS

- **③-A Direct Collision Verification:** complete a second independent search
  for an executable prediction-time-specific matched-cycle SOH benchmark.
- **③-B Checklist-vs-Methodology Gate:** specify what PTOC enforces that a
  reporting list cannot, or stop.
- **③-C More-Information-Triviality Gate:** predefine what deployment or
  comparison conclusion would be nontrivial beyond L1<L2<L3 error ordering.
- **③-D Target Semantics Gate:** freeze retrospective-label conditions and
  explicitly separate future-label acquisition from future-feature leakage.
- **③-E Matched-Cycle Feasibility:** conduct an index/event intersection audit
  without test labels and freeze the eligible population rule.
- **③-F External Dataset Manifest:** verify public availability, license, raw
  V/I/T, charge/discharge events, capacity target pairing and contract fit.
- **③-G Baseline / Model Control Freeze:** freeze L1/L2/L3 compatible simple
  baselines, same-model Ridge control, preprocessing and no-retuning rule.
- **③-H Falsification Matrix Freeze:** freeze success, failure and stop rules,
  including a failure if results only show more-information-is-better.
- **③-I PTOC Protocol v1 Freeze:** create the versioned, immutable protocol
  and obtain final Vibe integrity review.

### GATES

- `G2_DIRECT_COLLISION_ACCEPTABLE`: PASS only if no direct-method collision
  remains or a narrow, evidenced distinction survives; FAIL closes PTOC.
- `CHECKLIST_NOT_FATAL`: PASS only if the protocol has executable compliance
  effects; FAIL closes PTOC.
- `TRIVIALITY_NOT_FATAL`: PASS only if the pre-frozen claim is falsifiable and
  not reducible to “more information gives lower error”; FAIL closes PTOC.
- `TARGET_SEMANTICS`: PASS when valid or valid-with-frozen-conditions; FAIL
  if target/future-label semantics cannot be made consistent.
- `MATCHED_CYCLE`: PASS only with a predeclared common eligible intersection;
  FAIL if this requires artificial deletion or is infeasible.
- `EXTERNAL_MANIFEST`: PASS only with an independent viable dataset and clear
  license/event/label evidence; UNRESOLVED keeps ③ BLOCKED.
- `CONTROL_AND_FALSIFICATION_FREEZE`: PASS only after model controls and stop
  rules are immutable before performance evidence.
- `FINAL_VIBE_INTEGRITY`: PASS only if no citation overclaim, test leakage,
  protocol drift or second innovation is present.

### REQUIRED OUTPUTS

Collision audit, checklist/triviality decision, target-semantics audit,
matched-cycle manifest, external-data manifest, frozen protocol v1,
falsification matrix, Decision Record update, and Git commit.

### ADVANCEMENT CONDITION

`PTOC_PRE_EXPERIMENT_GATE=PASS` only after every listed Gate passes. This still
requires explicit human researcher authorization before ④.

### NEXT PHASE

④ PTOC Development Experiment.

### COMPLETION RECORD

```text
COMPLETED_DATE=2026-09-03
COMPLETED_COMMIT=48de81e
FINAL_STATUS=BLOCKED
KEY_RESULT=External source eligibility is documented, but direct-method novelty remains unresolved and B0007 has only 31/67 strict immediate charge/discharge pairs.
FAILED_OR_UNRESOLVED_ITEMS=G2 direct-collision verification remains pending; MATCHED_CYCLE fails under the predeclared strict pair rule; no L1/L2/L3 performance evidence exists.
DECISION=Do not run PTOC experiments. Any proposal to change the pair rule requires explicit human review and master-plan change control.
```

### POST-COMPLETION AMENDMENT — PTOC-003-AMENDMENT-001

```text
AMENDMENT_ID=PTOC-003-AMENDMENT-001
DATE=2026-09-03
TRIGGER=Label-free reconstruction found that “31/67” mixed whole-file strict-pair count with the 67 historical development candidates.
DISCOVERED_DURING_PHASE=③ PTOC Pre-Experiment Gate
AFFECTED_COMPLETED_PHASE=③ PTOC Pre-Experiment Gate
ORIGINAL_DECISION=Keep Phase ③ BLOCKED; do not run PTOC experiments under strict immediate adjacency.
NEW_EVIDENCE=Exact historical-candidate mapping is 23/67 immediate pairs, 42 impedance-only intermediaries and 2 intervening-charge ambiguities; G2 is ACCEPTABLE_PARTIAL_COLLISION rather than PENDING.
WHAT_CHANGED=Blocker characterization and next allowed action: human review of a v1.1 design-only amendment proposal.
WHAT_DID_NOT_CHANGE=ROOT remains frozen; no model/metric/test/validation label was loaded; PTOC v1 remains non-executable; Phase ④ remains blocked.
DOWNSTREAM_IMPACT=No phase advancement. If approved, a new Decision Record and immutable protocol v1.1 are required before any Phase ④ authorization.
REQUIRES_REOPENING=True
REOPENING_STATUS=BLOCKED_PENDING_HUMAN_PROTOCOL_AMENDMENT_DECISION
GIT_COMMIT=2424fe1
```

### CURRENT-PHASE PROVENANCE CORRECTION — PTOC-003-PROVENANCE-CORRECTION-001

```text
CORRECTION_ID=PTOC-003-PROVENANCE-CORRECTION-001
DATE=2026-09-03
CORRECTS_CLASSIFICATION_OF=PTOC-003-AMENDMENT-001
POST_COMPLETION_AMENDMENT_STATUS=MISCLASSIFIED
REASON=The current register identifies Phase ③ as BLOCKED and Phase ② as the last completed phase. A blocked current phase cannot be a post-completion-amendment target.
CORRECT_CLASSIFICATION=CURRENT_PHASE_BLOCKER_AND_PROVENANCE_UPDATE
WHAT_REMAINS_VALID=The 31/67-to-23/67 correction, pairing taxonomy, G2 result, ROOT freeze, test lock, V1 immutability and Phase ④ block.
WHAT_DOES_NOT_FOLLOW=No model run, ROOT rerun, label access or Phase ④ authorization.
CURRENT_PROTOCOL_DECISION=PTOC_PROTOCOL_V1_1_AMENDMENT_GATE=BLOCKED; V1.1 has not been created.
GIT_COMMIT=c6f8c70
```

---

## ④ PTOC Development Experiment

### STATUS

`BLOCKED`

### OBJECTIVE

Execute the frozen PTOC v1 development protocol without changing ROOT,
contracts, model controls, targets, splits, or falsification rules.

### SCIENTIFIC QUESTION

Under matched cycles and frozen contracts, does PTOC change the permitted
interpretation/deployment eligibility of SOH estimates beyond a trivial error
ordering?

### INPUTS

③ PASS, frozen protocol v1, human authorization, and approved manifest.

### ALLOWED

Only the pre-registered implementation and runs:

- **④-A** Contract-stratified L1/L2/L3 estimation;
- **④-B** matched-cycle comparison;
- **④-C** same-model Ridge control;
- **④-D** capacity-adjacent information audit.

### FORBIDDEN

Any hyperparameter/model/feature search; target or split change; external-data
work; test access; second innovation; rerunning after results to alter PTOC.

### REQUIRED TASKS

Run frozen tasks, save complete provenance, apply the frozen falsification
matrix, and record all negative results.

### GATES

- `PROTOCOL_COMPLIANCE`: PASS only if every run matches PTOC v1.
- `NONTRIVIAL_CLAIM`: PASS only if predeclared nontrivial evidence appears;
  FAIL if the result is only “more information improves error.”
- `LEAKAGE_AND_TEST_LOCK`: any violation is FAIL and stops the direction.

### REQUIRED OUTPUTS

Immutable config/manifest, metrics, contract cards, matched-cycle records,
figures/tables, failure report, Decision Record result update and Git commit.

### ADVANCEMENT CONDITION

④ PASS requires all frozen gates and explicit human authorization for ⑤.

### NEXT PHASE

⑤ External Validation.

### COMPLETION RECORD

```text
COMPLETED_DATE=NOT_APPLICABLE
COMPLETED_COMMIT=NOT_APPLICABLE
FINAL_STATUS=NOT_STARTED
KEY_RESULT=NOT_APPLICABLE
FAILED_OR_UNRESOLVED_ITEMS=Blocked by ③.
DECISION=NOT_APPLICABLE
```

---

## ⑤ External Validation

### STATUS

`BLOCKED`

### OBJECTIVE

Validate frozen PTOC on at least one independent, manifest-qualified public
dataset without adapting the protocol to its result.

### SCIENTIFIC QUESTION

Can the contract boundary, target semantics, matched evaluation and nontrivial
claim be reconstructed outside NASA development evidence?

### INPUTS

④ PASS, a ③-approved external manifest, frozen PTOC protocol, and human
authorization.

### ALLOWED

Only protocol-preserving external replication and declared dataset-specific
schema adapters.

### FORBIDDEN

Changing PTOC to rescue external results; selecting datasets after seeing
results; transfer learning, target calibration expansion, test access, or a
new innovation.

### REQUIRED TASKS

Reconstruct natural events/contracts, confirm label pairing, run frozen
comparison, and report compatible/incompatible cases honestly.

### GATES

- `EXTERNAL_PROTOCOL_FIDELITY`: PASS only if the contract is preserved.
- `EXTERNAL_NONTRIVIAL_REPLICATION`: PASS only if the predeclared claim is
  supported; FAIL closes the general methodology claim.
- `NO_ADAPTIVE_REDESIGN`: any PTOC change after external results is FAIL.

### REQUIRED OUTPUTS

External manifest confirmation, protocol conformance audit, metrics,
contract cards, failure cases, Git commit.

### ADVANCEMENT CONDITION

⑤ PASS plus human authorization is required for ⑥.

### NEXT PHASE

⑥ Robustness & Necessary Controls.

### COMPLETION RECORD

```text
COMPLETED_DATE=NOT_APPLICABLE
COMPLETED_COMMIT=NOT_APPLICABLE
FINAL_STATUS=NOT_STARTED
KEY_RESULT=NOT_APPLICABLE
FAILED_OR_UNRESOLVED_ITEMS=Blocked by ④.
DECISION=NOT_APPLICABLE
```

---

## ⑥ Robustness & Necessary Controls

### STATUS

`BLOCKED`

### OBJECTIVE

Complete only reviewer-required controls, sensitivity analyses, capacity-adjacent
audits and protocol-robustness checks necessary to interpret PTOC.

### SCIENTIFIC QUESTION

Does the frozen PTOC conclusion survive necessary controls without new
methodological contributions?

### INPUTS

⑤ PASS and human authorization.

### ALLOWED

Reviewer-required controls, predeclared sensitivity analysis, capacity-adjacent
audit, and reproducibility checks.

### FORBIDDEN

Second innovation, complex networks, new loss/modules, open-ended ablation, or
result-rescue experiments.

### REQUIRED TASKS

Freeze the exact control list and distinguish necessary evidence from optional
exploration.

### GATES

- `NECESSITY`: every run must answer a reviewer-critical question.
- `NO_SCOPE_CREEP`: any new innovation/model path is FAIL.
- `ROBUSTNESS`: negative controls are reported, not hidden.

### REQUIRED OUTPUTS

Control protocol, results, provenance, limitations update, Git commit.

### ADVANCEMENT CONDITION

⑥ PASS plus human authorization is required for ⑦.

### NEXT PHASE

⑦ Paper Evidence Freeze.

### COMPLETION RECORD

```text
COMPLETED_DATE=NOT_APPLICABLE
COMPLETED_COMMIT=NOT_APPLICABLE
FINAL_STATUS=NOT_STARTED
KEY_RESULT=NOT_APPLICABLE
FAILED_OR_UNRESOLVED_ITEMS=Blocked by ⑤.
DECISION=NOT_APPLICABLE
```

---

## ⑦ Paper Evidence Freeze

### STATUS

`BLOCKED`

### OBJECTIVE

Freeze evidence before manuscript writing so the paper cannot be shaped by
post-hoc protocol changes.

### SCIENTIFIC QUESTION

Is every eventual claim traced to a frozen, reproducible and appropriately
scoped artifact?

### INPUTS

⑥ PASS and human authorization.

### ALLOWED

Provenance and claim/evidence audit; freeze final protocol, manifests, code
commits, metrics, figures, tables, failures and dataset versions.

### FORBIDDEN

Changing experiments to improve the paper story or excluding unfavourable
results.

### REQUIRED TASKS

Create claim/evidence mapping and a reproducibility inventory.

### GATES

- `EVIDENCE_TRACEABILITY`: all claims have frozen evidence.
- `NEGATIVE_RESULT_INCLUSION`: known failures are represented.
- `REPRODUCIBILITY`: config/data/code provenance is complete.

### REQUIRED OUTPUTS

Evidence-freeze record, claim/evidence matrix, artifact manifest and Git
commit.

### ADVANCEMENT CONDITION

⑦ PASS plus human authorization is required for ⑧.

### NEXT PHASE

⑧ Manuscript.

### COMPLETION RECORD

```text
COMPLETED_DATE=NOT_APPLICABLE
COMPLETED_COMMIT=NOT_APPLICABLE
FINAL_STATUS=NOT_STARTED
KEY_RESULT=NOT_APPLICABLE
FAILED_OR_UNRESOLVED_ITEMS=Blocked by ⑥.
DECISION=NOT_APPLICABLE
```

---

## ⑧ Manuscript

### STATUS

`BLOCKED`

### OBJECTIVE

Write the methodology paper from frozen evidence with exactly one primary
contribution.

### SCIENTIFIC QUESTION

Can the evidence support the PTOC research question at its authorized scope?

### INPUTS

⑦ PASS and human authorization.

### ALLOWED

Draft and revise the following structure: Introduction; Related Work; Problem
Formulation; Prediction-Time Observability Contract; Experimental Protocol;
Results; Discussion; Limitations; Conclusion.

### FORBIDDEN

Adding a second contribution, claiming novelty without verified citation
evidence, or silently revising frozen results/protocols.

### REQUIRED TASKS

Maintain one contribution statement and cite only verified sources.

### GATES

- `ONE_PRIMARY_CONTRIBUTION`: PASS only if all sections support PTOC alone.
- `CLAIM_SCOPE`: PASS only if claims match evidence and external validation.
- `CITATION_INTEGRITY`: FAIL on unsupported novelty/future-work assertions.

### REQUIRED OUTPUTS

Manuscript source, reference audit, claim/evidence crosswalk, Git commit.

### ADVANCEMENT CONDITION

⑧ PASS is required before ⑨.

### NEXT PHASE

⑨ Final Research Integrity Audit.

### COMPLETION RECORD

```text
COMPLETED_DATE=NOT_APPLICABLE
COMPLETED_COMMIT=NOT_APPLICABLE
FINAL_STATUS=NOT_STARTED
KEY_RESULT=NOT_APPLICABLE
FAILED_OR_UNRESOLVED_ITEMS=Blocked by ⑦.
DECISION=NOT_APPLICABLE
```

---

## ⑨ Final Research Integrity Audit

### STATUS

`BLOCKED`

### OBJECTIVE

Perform final independent integrity and evidence review before a
`SUBMISSION_READY` decision.

### SCIENTIFIC QUESTION

Do the final claims, data boundaries, citations, protocol, Git history and
contribution count withstand a full adversarial audit?

### INPUTS

⑧ PASS and frozen manuscript/evidence artifacts.

### ALLOWED

Read-only audit of novelty claims, citations, leakage, locked test, protocol
drift, target semantics, reproducibility, Git history, external validation and
claim/evidence mapping.

### FORBIDDEN

New experiments, silent manuscript/result edits, new innovation, history
rewrite, or hiding adverse results.

### REQUIRED TASKS

Use appropriate research-integrity review; verify contribution count, data
provenance and all paper claims.

### GATES

- `FINAL_INTEGRITY`: PASS only if all evidence and citation boundaries hold.
- `EXTERNAL_VALIDATION`: PASS only if external claim requirements are met.
- `REPRODUCIBILITY_AND_HISTORY`: PASS only with traceable artifacts and Git
  provenance.

### REQUIRED OUTPUTS

Final integrity report, final evidence checklist, final Git commit.

### ADVANCEMENT CONDITION

All final gates PASS.

### NEXT PHASE

`SUBMISSION_READY` — still requires human approval.

### COMPLETION RECORD

```text
COMPLETED_DATE=NOT_APPLICABLE
COMPLETED_COMMIT=NOT_APPLICABLE
FINAL_STATUS=NOT_STARTED
KEY_RESULT=NOT_APPLICABLE
FAILED_OR_UNRESOLVED_ITEMS=Blocked by ⑧.
DECISION=NOT_APPLICABLE
```

---

# PLAN MAINTENANCE RULES

1. Before every SOH research, code, experiment, audit, Git operation or paper
   task, read `RESEARCH_GUARDRAILS.md`, then this file, then inspect Git HEAD
   and working-tree status.
2. Do not work outside the current Phase unless this plan is formally updated
   first with its reason and Gate impact.
3. Do not change frozen hypotheses, Gates or success criteria after seeing an
   experiment result.
4. If implementation exposes a factual error, infeasible condition, data-schema
   incompatibility, protocol conflict or safety conflict, stop the nonessential
   work and set `MASTER_PLAN_CHANGE_REQUIRED=True`.
5. Do not silently edit a completed Phase's historical conclusion.
6. Completed Phase fields (`STATUS`, `FINAL_STATUS`, `KEY_RESULT`, `DECISION`)
   are immutable records. Later evidence is added only as a post-completion
   amendment.
7. Every major phase transition requires explicit human researcher
   authorization even after its formal Gate passes.

## POST-COMPLETION AMENDMENT template

```text
AMENDMENT_ID=
DATE=
TRIGGER=
DISCOVERED_DURING_PHASE=
AFFECTED_COMPLETED_PHASE=
ORIGINAL_DECISION=
NEW_EVIDENCE=
WHAT_CHANGED=
WHAT_DID_NOT_CHANGE=
DOWNSTREAM_IMPACT=
REQUIRES_REOPENING=
REOPENING_STATUS=
GIT_COMMIT=
```

## Mandatory change-control response

If a change is necessary during implementation, stop and report:

```text
MASTER_PLAN_CHANGE_REQUIRED=True
CHANGE_TRIGGER=
CURRENT_PHASE=
AFFECTED_PHASE=
WHY_EXISTING_PLAN_IS_INVALID_OR_INCOMPLETE=
PROPOSED_CHANGE=
SCIENTIFIC_IMPACT=
PROTOCOL_IMPACT=
GATE_IMPACT=
DOWNSTREAM_PHASE_IMPACT=
```

Update this plan before implementation continues. Changes to completed phases
must use the post-completion amendment template; current/future phase changes
must update their Objective, Tasks, Gates and Advancement Condition.

## Mandatory feedback block

Every SOH-project final response must include:

```text
MASTER PLAN ALIGNMENT
MASTER_PLAN_READ=True
CURRENT_PHASE=
CURRENT_PHASE_SYMBOL=
CURRENT_PHASE_STATUS_BEFORE=
THIS_TASK_OBJECTIVE=
THIS_TASK_WITHIN_PLAN=True/False
PREVIOUS_GATE=
PREVIOUS_GATE_STATUS=
TASK_GATE_RESULT=
CURRENT_PHASE_STATUS_AFTER=
ADVANCEMENT_ALLOWED=True/False
NEXT_PHASE=
NEXT_ACTION=
MASTER_PLAN_UPDATE_REQUIRED=True/False
MASTER_PLAN_UPDATED=True/False
POST_COMPLETION_AMENDMENT_CREATED=True/False
PLAN_CHANGE_ID=NONE/PLAN-CHANGE-XXXX
ROOT_STATUS=
LOCKED_TEST_STATUS=
PRIMARY_INNOVATION_COUNT=
PRIMARY_INNOVATION=
```

# MASTER PLAN CHANGE LOG

## PLAN-CHANGE-0001

```text
DATE=2026-09-03
TRIGGER=Initial establishment of the single long-lived SOH/PTOC master plan.
CURRENT_PHASE=③ PTOC PRE-EXPERIMENT GATE
CHANGED_SECTION=Entire new RESEARCH_MASTER_PLAN.md
OLD_PLAN_SUMMARY=No repository-level phase navigation, maintenance rule or feedback-alignment template existed.
NEW_PLAN_SUMMARY=Created stable phase map ①–⑨, status register, Gate progression, amendment process and mandatory feedback block.
RATIONALE=Prevent phase skipping, protocol drift, hypothesis shopping and historical-result rewriting.
EVIDENCE=RESEARCH_GUARDRAILS.md; S0/ROOT artifacts; DECISION_RECORD_PTOC_PRIMARY_DIRECTION.md.
GATE_IMPACT=No scientific Gate changed; ③ remains NOT_STARTED and experiments remain blocked.
DOWNSTREAM_IMPACT=All future SOH tasks must align to this plan before action.
APPROVED_BY=human researcher request in current task
GIT_COMMIT=743678e
```

## PLAN-CHANGE-0002

```text
DATE=2026-09-03
TRIGGER=Protocol-amendment audit found a current Phase ③ evidence entry was misclassified as a post-completion amendment.
CURRENT_PHASE=③ PTOC PRE-EXPERIMENT GATE
CHANGED_SECTION=Phase ③ provenance classification and next-action description.
OLD_PLAN_SUMMARY=PTOC-003-AMENDMENT-001 was labelled POST-COMPLETION AMENDMENT and named ③ as an affected completed phase.
NEW_PLAN_SUMMARY=The old record is preserved; PTOC-003-PROVENANCE-CORRECTION-001 records a current-phase blocker/provenance update. V1.1 remains blocked, not frozen.
RATIONALE=Correct provenance without weakening any gate or treating a blocked phase as completed.
EVIDENCE=PTOC_PHASE3_PROTOCOL_AMENDMENT_DECISION.md; PTOC_PHASE3_BLOCKER_RESOLUTION_1.md; current status register.
GATE_IMPACT=G2 remains ACCEPTABLE_PARTIAL_COLLISION; F4 remains FAIL_FOR_V1; ③ and ④ remain BLOCKED.
DOWNSTREAM_IMPACT=No advancement. Next action is human decision on L1 reference-test semantics and external operation-adapter audit.
APPROVED_BY=human researcher request in current task
GIT_COMMIT=c6f8c70
```
