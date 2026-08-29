# Research Stage Decision

## Final decision

```text
RESEARCH_STAGE = RESEARCH_DIRECTION_REJECTED
REPRODUCTION_DECISION = STOP_REPRODUCTION
LOCKED_TEST_REMAINS_UNOPENED
NO_EXPERIMENT_AUTHORIZED
```

`RESEARCH_DIRECTION_REJECTED` applies only to a new innovation-development pivot in the current repository with the current NASA development targets. It does not reject the completed undergraduate thesis: the NASA-only reproduction/failure/negative-transfer audit remains the valid closure.

## Why not CONTINUE_REPRODUCTION

All disclosed paper parameters have been audited. The remaining differences are protocol ambiguity, reproduction-defined choices and an undefined `L_weight`, not a minimal paper-defined bug. More work would be reverse engineering rather than reproduction.

## Why not STOP_REPRODUCTION_AND_IMPROVE_FIT

B0007/B0018 have repeatedly informed development. Designing a weighting, stage or fallback rule to improve them would researcher-overfit the validation history; locked test cannot become a selection set.

## Why not START_INNOVATION_DEVELOPMENT

Recent literature already contains direct neighbors for source selection, multi-source adaptation, instance weighting, stage adaptation and uncertainty-aware transfer. Current candidates fail G3 because their rule could not be defined independently of known B0005/B0006 and B0007/B0018 outcomes.

## Why RESEARCH_DIRECTION_REJECTED

There is neither a paper-defined reproduction repair nor a Gate-authorized, literature-grounded novelty gap with an independent evaluation surface. CALCE may only validate an already supported frozen method; it cannot be used to seek a positive result after NASA failure.

## Next minimum experiment

**None is authorized now.** Before future training, obtain an independent development-target cohort and complete a new `EXPERIMENT_DECISION_TEMPLATE.md`. Only then may a low-complexity reliability-gated transfer baseline be pre-registered; it must compare `TARGET_ONLY`, `ALL_SOURCE`, and `BEST_SIMPLE_BASELINE`, freeze success/failure/stop criteria, and preserve locked test.

Stop here and await human confirmation. Do not run CALCE, alter a score, train a new model or read test.
