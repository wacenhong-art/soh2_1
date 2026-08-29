# Phase 2 — Fusion Sequence Length & Sample Efficiency Ablation

This is a pre-registered, single-variable follow-up to Phase 1.  It changes
only `fusion_seq_len` in `{4, 6, 8, 10}`.  Component models and their saved
predictions are reused from the Phase 1 HF-only runs; this prevents component
randomness from becoming a second experimental variable.

The fixed settings are component window 10, Bi-LSTM hidden size 16, one layer,
BatchNorm1d weight network, learning rate 0.001, batch size 32, patience 50,
weight decay 1e-5, and `L_weight=UNVERIFIED_DISABLED`.  B0007 and B0018 use
the first 20% of cycles for labelled training and the next 20% for validation.
The locked test split is not loaded or evaluated.

For each sequence length, five seeds (`42, 123, 2024, 3407, 7777`) are run for
`PAPER_FUSION`, followed by the Phase-1-selected constrained residual fusion
with `epsilon=0.05`.  This is 80 runs.  A configuration qualifies only if all
battery × seed runs have positive R2, each beats its paired mean baseline, all
five seeds are present, no catastrophic prediction occurs, and test remains
locked.  If no configuration qualifies, the report must state
`NO_QUALIFIED_CONFIGURATION`.
