# E001 — selector composition with full split replay: KILL_Q

## Default-off control

With `SUB4_PP_MUL_REPLAY_PEAK` absent, the inherited Q1271 composition emitted
`12,930,245` operations with SHA-256
`a9834ef57b1579c9e611f7ad95cbb5e226ab1281cfa7e6b35574fb04ff932ff6b`,
byte-identical to its prior sealed result.

## Candidate result

The frozen selector + `doubled_out` + multiply-replay-1272 composition passed:

- selector lifecycle: 64/64 exact, all eight arms, phase 0, ancilla 0;
- full affine component: exact values, phase 0, ancilla 0;
- square component: Q1271 / T58738.531.

The full component nevertheless measured **Q1272**.  `PP_PROFILE=1`
reproduced Q1272 / diagnostic T915069.70, with the first binding allocation in
`pp_mul_replay`.  Trace counts also show the widened replay cells binding while
interleaved into `pp_mul_walkback`.  The Toffoli reduction is real, but the
post-add `doubled_out` loan begins too late to pay for the main add's wider
ladder.

At Q1272 this diagnostic is score-worse than the frozen live frontier, so the
trusted evaluator cannot change the verdict.

## Verdict

`KILL_Q`; stop before 9,024 shots.  No nonce, provider, range, hunt,
submission, or public-note action.  A pre-add alias of the redundant
`target[0] = sign` copy would be a distinct lifecycle family and requires a
new predeclaration.
