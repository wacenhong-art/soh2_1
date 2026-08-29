# Innovation Gap Analysis

`RECENT_SOH_PROBLEM_MAP.csv` contains 19 verified 2023–2026 papers. It is a problem scan, not evidence that a proposed method will improve this repository.

## What recent work already covers

| Theme | Recent evidence | Implication |
|---|---|---|
| Source selection | 2025 Wasserstein single-source and 2026 early-cycle HD-DTW selection | Source selection is not itself an innovation; a third B0007/B0018 score is forbidden. |
| Negative transfer / multi-source | 2025 single-vs-multi-source and 2026 multi-source adaptation | Phase 9 matches a real problem, but two targets cannot support a new general rule. |
| Instance and feature weighting | 2025 feature weighting and instance-based TL | Adding weights is established prior art and needs an independent rationale. |
| Stage and early-cycle difficulty | 2024 shift-degree partition; 2026 three-stage and early-trajectory work | Early-to-later mismatch is real, but stage methods are already active. |
| Uncertainty and target anchors | 2025 latent/subdomain adaptation and recent few-shot work | Reliability is open, but current targets are not an independent evaluation surface. |
| Cross-dataset claims | Methods use their own datasets/splits and often target labels | NASA-only results cannot establish generality; CALCE cannot rescue a failed method. |

## Candidate A–D assessment

| Candidate | Existing evidence connection | Prior-art result | Current authorization | RMSE/R2 expectation |
|---|---|---|---|---|
| A. negative-transfer-aware source weighting | Phase 9: B0006 risk | Multi-source, feature and instance weighting already exist | NOT AUTHORIZED: any current rule is post-hoc to known B0005/B0006 outcomes (G3 fail) | Unknown; no mean-gain promise is defensible |
| B. sample/instance-level weighting | Hard source choice is insufficient | 2025 instance-based TL directly overlaps | NOT AUTHORIZED: not novel and needs unseen targets | Unknown; endpoint is worst-case harm |
| C. degradation-stage-aware transfer | Phase 6 shift and early-to-later mismatch | Stage/shift adaptation is active | NOT AUTHORIZED: stage cutpoint may leak later trajectory | Unknown; no two-target gain can be claimed |
| D. uncertainty-gated transfer fallback | Phase 8–9 target-dependent transfer; Phase 1 safety/accuracy split | Uncertainty-aware and low-label adaptation are active | POTENTIAL FUTURE PROBLEM ONLY: a gate must be frozen on independent targets | May reduce worst-case harm; RMSE/R2 effect unknown |

## Four problem-level candidates

### P1. Uncertainty-gated transfer safety

How can a leak-free reliability gate fall back from transfer when source knowledge is unreliable? Phase 8–9 supports the problem; the remaining gap is a pre-registered, unseen-target gate that does not inspect validation/test SOH. Threshold selection is the key leakage risk. A future direction is abstention or a convex fallback, not an attention module.

### P2. Prefix-observable degradation-stage mismatch diagnosis

Can prefix-only observables indicate an error regime before later cycles are seen? Phase 6 supports an association, not a causal mechanism. The stage definition must be frozen without later trajectory; otherwise it is post-hoc.

### P3. Robust source mixture under incompatible samples

Can multi-source transfer suppress harmful samples without hard source selection? B0006 risk motivates this problem, but it collides with both existing instance-weighting literature and the repository source-selection red lines.

### P4. Minimal target-anchor adaptation under label scarcity

How can legal scarce target labels stabilize adaptation without being called zero-shot? The literature establishes the problem, but changing target-label proportion to rescue results is prohibited.

## Gap conclusion

All four are real research problems, but none is currently a justified new method on B0007/B0018. If independent development targets were later available, P1 is the lowest-complexity problem to review; it is not an authorized method now.
