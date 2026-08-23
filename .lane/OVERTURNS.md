# Overturn ledger

Frozen before new measurement on 2026-08-23.

| id | inherited belief | existing evidence | smallest falsifier | state |
|---|---|---|---|---|
| O-001 | Width repair is the only practical density lever at Q1272. | The exact Q1272 census attributes a substantial floor to schedule-independent terminal/replay/walkback/shell channels; widening cannot remove it. | Spend one bit of replay-fold precision and compare fixed-corpus replay and phase density at measured Q/T. | open |
| O-002 | Replay fold width 54 is still the right economic point after the Q1272 cut. | Width 54 was tuned on an older score saddle; Q1272 has `6346.28` full-T headroom below the strict-beat ceiling. | Default `54 -> 55`, retaining `=54` opt-out. | bounded hold: T affordable, but standalone Q1273 |
| O-003 | One more fold bit must raise global peak Q. | E-001 measured Q1273 at `pp_mul_replay`; diag T916106.31 versus same-seed base914777.30. | Contract replay budget `1272 -> 1271` while widening fold `54 -> 55`. | overturned for standalone; composition open |
| O-004 | Hard classical and phase density are separate taxes. | Prior fixed-corpus work found strong co-variation, but not on the widened Q1272 stream. | Full unchanged simulation on the predeclared phase block; report joint counts without assuming independence. | open |
| O-005 | A local replay improvement is enough to claim a candidate. | Terminal, walkback, square, and result channels can remain, and all Q1272 co-binders must stay at or below 1272. | Require complete cause census, focused selftests, base/live opt-outs, and full channel reporting. | protected |

Kill conditions for the first experiment: Q above 1272; rounded full T above
921139; either protected SHA fails; a focused miter/selfcheck fails; or the
predeclared corpus shows no replay-density reduction. A dirty inherited draw
is evidence about that draw only and is not a kill condition.

E-001 hit its Q kill gate before density work: 12,923,378 ops, SHA
`f3915652770187b4200ac6bf424ee3034b54e859b06717bf912fef562f72ed00`,
Q1273, same-seed diag T916106.31, diagnostic `0/0/0`. The source default was
restored to 54. Per the bounded-saddle rule, E-001b is now predeclared as the
same fold55 cell plus `SUB4_PP_PEAK=1271`; it advances only if global Q returns
to 1272 and rounded full T remains within the same ceiling.

E-001b also hit Q1273: 12,945,334 ops, SHA
`65d7cb17bb9ede12e28f2d1a354b003a79a7b47ebc1ebb80cca2a8b9b4741d90`,
same-seed diag T917028.50, diagnostic `0/0/0`. The exact B0 census identifies
the peak as 695 tape + 256 input + 256 coefficient + 53 fold carries + thirteen
singletons at multiply replay. Budget contraction lowers other phases but does
not remove the fold cell's own extra wire.

E-001c is frozen before measurement: the multiply cell currently materializes
`plus_2f = routed XOR minus_f`, although the fold consumes that selector only
through linear CX toggles. Keep it as the two-wire XOR alias
`[routed, minus_f]`, removing one live selector qubit, and compose with fold55.
The scoped exhaustive miter is all `(routed, sign, operand)` states with
`minus_f = routed AND sign`; it must prove both the selector value and every
operand toggle identical. The implementation is opt-in until all gates close.
