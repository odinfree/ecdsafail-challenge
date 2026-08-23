# Q1273 inherited-nonce CPU predictor gate

Verdict: `INHERITED_MASK_PASS / H64_UNOPENED`.

The source-bound CPU predictor exactly reproduces the complete classical
mismatch-shot set emitted by a minimally instrumented copy of the unchanged
9,024-shot evaluator. This checkpoint was sealed before any prediction or
evaluator result from the frozen H64 corpus was opened.

## Bound target

- circuit source commit: `093d85d64de87aa5006a94868172f642daacf136`;
- predictor predeclaration commit:
  `a8f7307f0a93ec78910444b2e4c18a78f70b9ae9`;
- predictor source commit:
  `9e9678471751993356b9a303dde6281fafd94937`;
- inherited nonce: `100000045835813`;
- operation count: `12,933,805`;
- operation SHA-256:
  `ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1`;
- checkpoint/tail-state digest: `2148e09f4c4293b2`;
- geometry: Q1273, divide/multiply rounds `698/696`, replay peak / square
  ladder `1273/243`.

## Predictor build and fail-closed gates

Final predictor binary SHA-256:
`93a9d9be4e542388457d802dd0a0832c527bfe3803efd8158a2d66e626ecd63c`.

The SHAKE256 known-answer test passed for both the empty string and `abc`.
The KAT stderr receipt SHA-256 is
`66706e32f25b0dc342a545c24d38801577c519bde87fe89ccca542d2de5a197b`.
The exact-stream `statedigest` command returned `2148e09f4c4293b2`; its stdout
and stderr SHA-256 values are respectively
`111d35d54a526d581ca8fe75b90f9a41ff359a0b56c95e7c22518680601e0cb6`
and
`a5f9fd1ddaea95a1b6874a20cb733e7a260aed6e66ef09baa9802d3d61d4177e`.

Three predeclared fail-closed gates passed:

- wrong operation count (`12,933,806`) exited 2 before model execution;
  artifact SHA-256
  `2a710e4069c79488a027cfd42cfec09b5d263af57fdfe725bbd6a55440ffe1f9`,
  stderr SHA-256
  `afc85c595ea71befb29a94b9d9b5a0794d2f6919bac624b701fa49375a31f898`;
- same count but wrong stream SHA exited 2 before model execution; artifact
  SHA-256
  `58a0de67b0d595b11a4a0e5f8a50098748dc4edf47e917744742d4a01bbd6458`,
  stderr SHA-256
  `03821fb3320319e6b65761946ec4fdf17d622d7f691b0210015b9fe6ffc31916`;
- CPU range-scan invocation exited 2 with scan mode disabled; stderr SHA-256
  `0884aeeee3b89a2362282832e9310ec56a2dddd5b652b771e95f698b78ca72c6`.

## Trusted evaluator instrumentation boundary

Only the following observability-only changes were applied to an external
copy of the exact evaluator source:

- retain classical mismatch shot indices in the per-seed report;
- print `CLASSICAL_SHOT <index>` when `EVAL_CLASSICAL_SHOTS=1`;
- suppress result/score writes when `EVAL_NO_WRITE=1`.

No circuit, simulator, seed, shot, or correctness logic changed.

- original evaluator source SHA-256:
  `b35314bc929ba6e6884304e70f926cd1a2cba7e316b01450349cc514701b83d2`;
- instrumented evaluator source SHA-256:
  `4e87d08dc10cb49ea46410c09796239601ba529deac87d0dc45d641337ede9fc`;
- instrumentation patch SHA-256:
  `15943baf5815f36188a8406b7a080c8b446f856a9337d8046eafe363752c6e4f`;
- instrumented evaluator binary SHA-256:
  `37081d949bf34f185023098e74393a9014b96853633646288a90f1538663580e`;
- `results.tsv` remained byte-identical before and after evaluation, SHA-256
  `eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`.

## Exact inherited result

The unchanged 9,024-shot evaluator reported Q1273, 12 classical mismatches,
12 phase-garbage batches, zero ancilla-garbage batches, and first classical
mismatch shot 93. The predictor reported 12 classical mismatches with the same
first shot. Its classified breakdown is:

- walk divide: 5;
- replay divide: 1;
- walk multiply: 4;
- replay multiply: 1;
- final-result channel: 1.

Both complete classical shot-index sets contain exactly:

`93, 2102, 2316, 4092, 4659, 5738, 5852, 5978, 6185, 7148, 8615, 8757`.

The evaluator and predictor index files are byte-identical, each SHA-256
`790f4f01966bfa2a886587a0af98c6d943c557a9cba71ef4dc4e463874e325ff`.
The full evaluator log SHA-256 is
`e693c27745575403be2bd39720ae2c1571239588f5d0323a8cd45f13c2b3d860`.
The predictor breakdown receipt SHA-256 is
`c76c19094b524de33e2bb71e0ae7bdff87cf7389cf70b53f4737b163044abb34`.

## Next gate

Open the already frozen H64 nonces `444000000000..444000000063`. For each
nonce, force-generate the candidate circuit, require the exact operation count,
Q1273, and zero ancilla-garbage batches, then compare complete evaluator and
predictor classical shot sets. Any mismatch is terminal for this port unless
localized as a source-semantic channel and validated on a separately frozen,
disjoint corpus. No range scan, provider work, hunt, or submission is allowed.
