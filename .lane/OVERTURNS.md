# Overturn ledger

Frozen before new measurement on 2026-08-23.

| id | inherited belief | existing evidence | smallest falsifier | state |
|---|---|---|---|---|
| O-001 | Width repair is the only practical density lever at Q1272. | Exact H64: fold55 composition lowers replay 126→65 and total classical 1135→1054. | Spend one bit of replay-fold precision and compare fixed-corpus replay and phase density at measured Q/T. | overturned; result gate still blocks |
| O-002 | Replay fold width 54 is still the right economic point after the Q1272 cut. | E-001c fits the T ceiling and lowers replay, but adds one exact result fault. | Fold `54 -> 55`, retaining `=54` opt-out. | held, not promoted |
| O-003 | One more fold bit must raise global peak Q. | E-001 measured Q1273 at `pp_mul_replay`; E-001c removes an exact redundant selector and returns to Q1272. | Compose fold55 with the multiply selector XOR alias. | overturned by composition |
| O-004 | Hard classical and phase density are separate taxes. | H64 changes classical 1135→1054 and phase 839→765 on the same fixed nonce block, though shots are SHA-bound ensembles. | Full unchanged simulation on the predeclared block; report joint counts without assuming independence. | co-movement observed; independence unclaimed |
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

E-001c passed its scoped 8/8 selector miter, Q1272 profile, focused square and
affine selftests, T ceiling, and complete ancilla gate. Exact H64 reduced replay
126→65, total classical 1135→1054, and phase batches 839→765. It still fails the
frozen rule because nonce `444000000032`, shot 7997 creates a result fault where
the base H block had none. The implementation remains opt-in and the protected
defaults remain unchanged.

The first fold55 predictor also missed three irreversible reverse-walk POP
faults. A scratch fail-closed correction obtained 64/64 exact count parity and
classifies them as one divide-walk and two multiply-walk faults. That repair is
not productionized here and cannot authorize a hunt.
