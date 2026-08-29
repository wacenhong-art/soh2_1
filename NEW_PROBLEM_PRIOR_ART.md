# New Problem Prior-Art Review

## Candidate A: early-to-late degradation mapping shift

Closest papers include BatteryGPT (Nature Communications 2026), shift-degree transfer strategies (JES 2024), three-stage domain adaptation (Energy 2026), latent-space consistency (Energy 2025), and degradation-aligned SSL (arXiv:2608.16612). They already model early degradation, stage/shift behavior, adaptation, or cycle-order representation. The arXiv work most directly learns aging-consistent representations by a cycle-order ranking task. A proposal that merely adds cycle order, a GRU, contrastive/ranking loss, or a stage label would be a copy/combination, so it is **REJECTED** on novelty now.

## Candidate B: degradation context missing

Closest papers include the weak-label SSL framework, BatteryGPT, the general DG model (JPS 2024), GANN-DG/TTA (JES 2026), and physics-informed SOH (Energy 2024). They use temporal context, learned representations, virtual domains, test-time adaptation, or degradation constraints. Current data only demonstrates that a scalar normalized cycle fails; it does not define a distinct context mechanism. **REJECTED**.

## Candidate C: label-efficient degradation representation

Closest papers include weak-label SSL, ERMN meta-learning, GCNNs-MAML few-shot SOH, latent consistency, and degradation-aligned SSL. Label-efficient representation learning is already a heavily populated route, and the direct order-supervision variant appeared in 2026. **REJECTED**.

## Candidate D: small-source domain generalization

Closest papers include DG-based SOH (JPS 2024), unsupervised subdomain adaptation (Energy 2025), GANN-DG/TTA (JES 2026), cross-material three-stage DA, and multi-source EV transfer. These methods typically rely on multiple domains/datasets. Few-source DG is a possible research question, but the current repository lacks an unseen target cohort for a non-circular test. **REJECTED FOR CURRENT DATA**, not disproven in general.

## Accuracy gate

Only Candidate A has a direct hypothesized route to lower later-validation bias: if an early-to-late mapping shift were independently established, a context mechanism could reduce systematic bias. But the present evidence is associative, and its closest mechanism is already prior art. No candidate therefore passes both novelty and feasibility without violating G3/G5.
