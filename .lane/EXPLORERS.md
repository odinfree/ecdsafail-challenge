# Explorer board

Frozen before new measurement on 2026-08-23.

| rank | explorer | mechanism | expected price | falsifier | status |
|---:|---|---|---|---|---|
| 1 | E-001 replay-fold 55 | Keep one more low carry bit in both fused replay cells. | Measured +1329.01 same-seed diag T. | Exact profile measured Q1273 at multiply replay. | killed standalone |
| 1 | E-001b fold55 + peak1271 | Pay one bit less chunk allowance to host the widened fold inside global Q1272. | Measured +2251.20 same-seed diag T. | Still Q1273 at multiply fold. | killed |
| 1 | E-001c selector alias + fold55 | Eliminate materialized multiply `plus_2f` because its XOR factors are already live, then spend that wire on the wider fold. | Expected zero T and -1 Q for alias, plus E-001 fold price. | Exhaustive 8-state Boolean miter, Q/T profile, H/P, focused full-circuit gates. | selected |
| 2 | E-002 endpoint fold 21 | Keep one more carry position in terminal negation/seed helpers. | Unknown T; possible peak pressure at terminal loan. | Run only if E-001 closes cleanly and terminal remains binding. | queued |
| 3 | E-003 walkback fold 55 | Widen the sparse round-zero reverse fold. | Roughly one sparse controlled carry bit per traversal. | Needs an isolated source knob and exact reverse miter. | queued |
| 4 | E-004 square low-window +1 | Buy back product-register carry-drop errors. | Unknown, square co-binder risk. | Product-square selftest plus fixed shell/result census. | queued |
| 5 | E-005 state-selective terminal tail | Detect nonterminal residuals and conditionally execute one exact extra walk/replay cell. | Prior fused selector shapes cost several thousand T; universal one-round repair is false for some states. | First enumerate residual-state coverage on a frozen corpus; no source port before that. | held |

E-001 and E-001b exposed the hidden multiply fold co-binder. E-001c changes the
premise by deleting a redundant stored selector, not by squeezing the schedule.
