# b523ecf BREAK_1 counterbeat predeclaration

Written before semantic edits or variant measurements.

## Live anchor and decoded lever

- promoted source: `b523ecf`
- live score: `1,169,101,620`
- measured default: Q1278, T914789.886, full `0/0/0`
- default operation count/SHA: 12,876,472 /
  `4cb1787b181417c1e180ddf362fd7e44430ef2d422bb4184d73d7fe1924fdf7e`
- transferable lever: the linear value-width schedule's first breakpoint;
  `pingpong_div.rs.pre_ts` exposes the pre-sweep runtime knob with default 40,
  while the promoted source hard-codes the winning point 30
- non-transferable artifact: baked tail nonce `81327465284`

## Frozen sweep

Restore only the source-local `VW_BREAK1` runtime knob with promoted default
30. First prove that the unset build is byte-identical to promoted `b523ecf`.
Then evaluate these values in this order without adapting the set:

`20, 24, 26, 28, 29, 31, 32, 34, 36, 40`

For every point record operation count/SHA, Q, complete 9,024-shot
classical/phase/ancilla counts, exact average T from the isolated trusted
results row, rounded score, and first failure. The current baked nonce is only
a fixed diagnostic. A changed stream cannot inherit its cleanliness.

## Promotion gate

A variant advances only if Q<=1278, rounded T<=914789, ancilla=0, and its
measured counterfactual score is strictly below the live score. Dirtiness does
not kill a structurally cheaper point; it sends that exact stream to a new
source-bound predictor and nonce hunt. No adaptive neighbor, composition,
provider action, fleet retarget, hunt, submission, or public claim occurs in
this sweep. Generated ops, score/results rows, binaries, logs, and temp dirs
stay outside Git.
