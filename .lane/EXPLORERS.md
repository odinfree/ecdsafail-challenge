# Explorer board

Frozen before new measurement on 2026-08-23.

| rank | explorer | mechanism | expected price | falsifier | status |
|---:|---|---|---|---|---|
| 1 | E-001 replay-fold 55 | Keep one more low carry bit in both fused replay cells. | Measured +1329.01 same-seed diag T. | Exact profile measured Q1273 at multiply replay. | killed standalone |
| 1 | E-001b fold55 + peak1271 | Pay one bit less chunk allowance to host the widened fold inside global Q1272. | Measured +2251.20 same-seed diag T. | Still Q1273 at multiply fold. | killed |
| 1 | E-001c selector alias + fold55 | Eliminate materialized multiply `plus_2f` because its XOR factors are already live, then spend that wire on the wider fold. | Measured Q1272 and +1389.03 exact H T. | Replay 126→65, but exact result 0→1; predictor needed a lossy-POP fix. | held opt-in |
| 2 | E-002 endpoint fold 21 | Keep one more carry position in terminal negation/seed helpers. | Unknown T; possible peak pressure at terminal loan. | Run only if E-001 closes cleanly and terminal remains binding. | queued |
| 3 | E-003 walkback fold 55 | Widen the sparse round-zero reverse fold. | Roughly one sparse controlled carry bit per traversal. | Needs an isolated source knob and exact reverse miter. | queued |
| 4 | E-004 final-y boundary carry | Localized nonce `444000000032`, shot 7997 exactly to final y-sub, then tried only the predeclared LSBS 53→54 repair. | R1 measured +5 emitted ops and Q1272; T intentionally not measured after the first gate failed. | R1 moved the error from `+2^53` to `+2^54`; no adaptive width or H64 run. | localized; R1 killed |
| 4 | E-006 final-y boundary borrow | Preserve one borrow qubit across the low53/high203 split, decrement the high suffix, then erase the borrow from corrected low bits. | Measured Q1272 and diagnostic T916996.73 (`+879.61`); final-y peak stayed Q1026. | Fixed inputs passed exactly, but focused 64-lane miter produced phase mask `0x2c`. | value-supported; implementation killed |
| 4 | E-007 post-low boundary predicate | Recompute `b = anc && (z_low >= 0x1ffffefffffc2f)`, decrement all high203 bits, then recompute/uncompute the same predicate. | Q1272, diagnostic T918043.41, exact full T918104.700; final-y Q1026. | Fixed pair and 13-case reversible miter passed; inherited `11/12/0`, but its numeric mismatch set was not a subset of held `14/14/0`. | exact component held; H64 blocked |
| 4 | E-008 causal H64 characterization | Retest E-007 with unchanged full-evaluator ensemble counts, first-failure distribution, and source-bound cause coverage; do not pair rebound indices. | Q1272, exact H64 T918113.406063; no source change from E-007. | `1053/776/0` passes 3-sigma non-inferiority; 64/64 exact sets classified with one result event. | non-inferior; held dirty |
| 4 | E-009 candidate result localization | Replay nonce `444000000042`, shot 3036 and adjacent control 3035 through balanced coordinate checkpoints. | No source or T change during localization. | First divergence is square `+2^56`; integer replay pins final C-half top reduction call 9/9. | localized; source unchanged |
| 4 | E-010 C-half LSBS57 | Widen only square top-reduction call 9/9 from 56 to 57 bits behind an opt-in. | Measured Q1272; square `+3` emitted / `+1.671` realized T. | Pinned pair passed, but exact miter moved fault to `+2^57` and had phase mask `0x0a`. | killed; source removed |
| 4 | E-011 explicit call-9 carry | Reuse the clean-ladder apex carry for low56 `+f`, then propagate it through high200 without shifting the boundary. | Q1272; measured square `+603` emitted / `+606.297` executed T, inside the 992-T allowance. | Pinned pair passed; all eight miter values were exact and dirty=0, but `z=2^57-f` left phase mask `0x10`. | value-supported; phase-killed |
| 4 | E-012 phase-clean call-9 carry | Attribute E-011 phase to an exact cleanup site, then correct only a complemented-AND measurement erasure with conditioned `NEG`. | No repair price: the admitted hypothesis was false. | All ladder/CINC HMR/CZ deltas were zero; phase appeared only in downstream `clear_overflow_phase`. | localized; hypothesis killed |
| 4 | E-013 pre-propagation overflow erasure | Run inherited overflow HMR/comparator before high200 mutation; temporarily restore its measured control for the live ladder reverse. | Focused Q515 / 817 emitted T; no arithmetic price over E-011. | All eight values exact and dirty=0, but repaired-seed phase remained `0x24`. | phase-killed; source removed |
| 4 | E-014 coherent high200 carry | Replace only E-011's vented high200 controlled increment with its complete CCX forward/inverse network. | Expected about +198 T over E-011, below 385.7 remaining; no new qubit. | Repaired-seed 8-lane phase/dirty first, then square64 and Q1272/live-T composition. | predeclared; final micro-repair |
| 5 | E-005 state-selective terminal tail | Detect nonterminal residuals and conditionally execute one exact extra walk/replay cell. | Prior fused selector shapes cost several thousand T; universal one-round repair is false for some states. | First enumerate residual-state coverage on a frozen corpus; no source port before that. | held |

E-001 and E-001b exposed the hidden multiply fold co-binder. E-001c changes the
premise by deleting a redundant stored selector, not by squeezing the schedule.

E-001c proved that composition and replay-density reduction, but its one exact
result fault fails the frozen acceptance rule. E-004 localized that event to
the final y-subtract and proved that a blanket window increase only moves the
lost carry. Do not search this stream or widen the boundary again.

E-008 replaced the non-causal index-subset comparison with a frozen
independent-ensemble gate. E-007 is statistically non-inferior to held fold55,
but not strictly superior, and remains dirty. E-009 then localized its sole
result event to the product-register square's final C-half top reduction. The
observed lost carry is exactly the first bit outside that site's 56-bit fold
window. E-010 proved that a one-site width shift cheaply fixes the pinned draw
but only moves the general fault to the next bit. A successor must encode the
carry state rather than choose a later truncation boundary.
