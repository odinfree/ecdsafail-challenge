# Explorer board

Frozen before new measurement on 2026-08-23.

| rank | explorer | mechanism | expected price | falsifier | status |
|---:|---|---|---|---|---|
| 1 | E-001 replay-fold 55 | Keep one more low carry bit in both fused replay cells. | Measured +1329.01 same-seed diag T. | Exact profile measured Q1273 at multiply replay. | killed standalone |
| 1 | E-001b fold55 + peak1271 | Pay one bit less chunk allowance to host the widened fold inside global Q1272. | Unknown incremental T; total headroom 6362 same-seed diag. | Build/profile first; only then H/P and focused gates. | selected |
| 2 | E-002 endpoint fold 21 | Keep one more carry position in terminal negation/seed helpers. | Unknown T; possible peak pressure at terminal loan. | Run only if E-001 closes cleanly and terminal remains binding. | queued |
| 3 | E-003 walkback fold 55 | Widen the sparse round-zero reverse fold. | Roughly one sparse controlled carry bit per traversal. | Needs an isolated source knob and exact reverse miter. | queued |
| 4 | E-004 square low-window +1 | Buy back product-register carry-drop errors. | Unknown, square co-binder risk. | Product-square selftest plus fixed shell/result census. | queued |
| 5 | E-005 state-selective terminal tail | Detect nonterminal residuals and conditionally execute one exact extra walk/replay cell. | Prior fused selector shapes cost several thousand T; universal one-round repair is false for some states. | First enumerate residual-state coverage on a frozen corpus; no source port before that. | held |

E-001 was the smallest falsifiable change and exposed the hidden multiply
co-binder. E-001b is the smallest bounded composition: no new primitive, one
existing replay-budget knob, and the same fold-width mechanism.
