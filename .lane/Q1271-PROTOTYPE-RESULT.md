# Q1271 selector-plus-binder prototype result

Verdict: `STRUCTURAL_PASS / SCORE_MISS / VALIDATION_DIRTY / NO HUNT`.

## Frozen composition

- parent evidence: `41dd0b4508527081b8d24255adf0579389f02453`
- parent structural source: `73422709ed70ba9725b3cb592770bcf197df4cdb`
- source change: one default-off clear/free/rematerialize lifecycle for
  `doubled_out` across the fused fold
- environment: `SUB4_PP_FOLD_SELECTOR_EVICT=1`,
  `SUB4_PP_EVICT_DOUBLED_OUT=1`, `SUB4_PP_PEAK=1271`,
  `SUB4_SQUARE_LADDER=241`; every other external `SUB4_*` variable absent
- source SHA-256:
  `2df7a2d3e2f25243bf3f72607fe6683a39dfd1cf3e86ba76e80fac1e60db8e89`
- operation count: `12,930,245`
- operation SHA-256:
  `a9834ef57b1579c9e611f7ad95cbb5e226ab1281cfa7e6b35574fb04ff932ff6`

The parent selector stream was rebuilt first at exactly 12,904,643 operations
and SHA-256 `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`.

## Structural checks

- fixed-seed 64-lane profile: Q1271, T915640.33, classical/phase/dirty
  `0/0/0`
- selector lifecycle selftest: PASS 64/64, all eight selector arms, phase 0,
  ancilla 0, identical Toffoli, local peak 573 -> 572
- full ping-pong affine component: exit 0, Q1271, 957,797 emitted and
  915643.234 executed Toffoli
- product-register square component: exit 0, Q1271, 58,997 emitted and
  58,738.531 executed Toffoli

These checks establish a useful prototype, not a complete local proof of the
new lifecycle: the dedicated doubled-out boundary-value forward/inverse miter
from the predeclaration remains to be written.

## Unchanged full evaluator

- Q: 1271
- exact average executed Toffoli: 915692.673
- rounded T: 915693
- rounded score: `1,163,845,803`
- live score at measurement: `1,163,831,339`
- strict Q1271 rounded-T ceiling: 915681
- score miss: 14,464 points; 12 rounded Toffoli
- classical / phase / ancilla: `17/17/0`
- first mismatch: classical shot 11

The full result supersedes the optimistic 64-lane T estimate. Because this
stream is both score-negative and dirty, no predictor port, range declaration,
provider action, nonce hunt, submission, or public note is authorized.

## Next

Prioritize the simpler live-source Q1271 stream at rounded T915686, which is
only 5 T over the ceiling. Validate the doubled-out lifecycle independently,
then remove at least 5 rounded T without increasing Q. Grinding remains last.
