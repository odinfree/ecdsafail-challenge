# Lane state — Q1271 selector composition

- phase: `STRUCTURAL_PASS / SCORE_MISS_12T / VALIDATION_DIRTY / HOLD`
- branch: `research/kimi-q1271-selector-binder`
- predeclaration commit: `341ebcb`
- target evidence/source: `41dd0b4` / `7342270`
- target operations: `12,904,643` / `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`
- prototype operation identity: `12,930,245` / `a9834ef57b1579c9e611f7ad95cbb5e226ab1281cfa7e6b35574fb04ff932ff6`
- prototype source hash: `2df7a2d3e2f25243bf3f72607fe6683a39dfd1cf3e86ba76e80fac1e60db8e89`
- prototype environment: selector eviction + doubled-out eviction +
  `PP_PEAK=1271` + `SQUARE_LADDER=241`
- exact full result: Q1271 / T915692.673 / rounded T915693 /
  score `1,163,845,803` / channels `17/17/0`
- live-beat ceiling: rounded T915681; prototype misses by 12 T and 14,464
  score points
- provider/range/hunt/submission: none

At `2026-08-23T12:09:14Z`, one first-party `kimi-code/k3` prompt attempt
failed before work began with the provider billing-cycle usage-limit response
(`403`). The two earlier CLI invocations failed locally at option parsing and
never called the model. No paid usage or source mutation occurred.

Root executed the predeclared one-family prototype locally after the Kimi
quota hold. The 64-lane profile, selector selftest, full ping-pong component,
and square component all reached Q1271 without a value, phase, or cleanup
failure. The unchanged 9,024-shot evaluator then measured the exact score and
failed only the intrinsic truncation channels above. The selector composition
is currently dominated by the simpler live-source Fable stream, which reaches
Q1271 at rounded T915686 and misses the same ceiling by only 5 T.

No nonce hunt opens on this stream. The next objective-advancing action is a
focused doubled-out boundary miter plus a tiny Toffoli reduction on the simpler
Q1271 stream, or a source-bound clean-nonce hunt only after it is score-positive
and the rolling spend gate reopens.
