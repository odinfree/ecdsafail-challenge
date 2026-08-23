# Live-4eb93cb Q1272 selector-eviction rebase predeclaration

Status: `PREDECLARED / NO SEMANTIC EDIT / NO CANDIDATE RESULT`.

## Live frontier and strict gate

Live benchmark and public submissions were reopened before this lane.  Current
SOTA is commit `4eb93cb33bbf6a93229fe166b8d511c5e52ee253`, Q1273,
rounded T914243, score `1,163,831,339`.

For Q1272 the largest rounded T that strictly beats live is:

```text
floor((1,163,831,339 - 1) / 1272) = 914,961
```

Rounded T914962 is score `1,163,831,664` and fails.  Kill this lane if the
candidate's unchanged full evaluation rounds above 914961.

## Exact base and archaeology

- branch: `research/q1272-promoted-selector-rebase`;
- base commit / tree:
  `4eb93cb33bbf6a93229fe166b8d511c5e52ee253` /
  `bb19b4018e418c19b4ac13a16c88a31a9d820299`;
- base `pingpong_div.rs` / `mod.rs` / square source SHA-256:
  `a247d6c7f31fd382b3041e4cb2f21d13d7870551fe68344e22615a02e11c0d20` /
  `da681f674c2bd0be2c507eafcc7785e045530d920fa343a52593aecf65619ba9` /
  `864d31454c5279632652cf48aeda038d481a504b09e4f7a8c0f266e10a24b81c`;
- adjacent promoted editable diff SHA-256:
  `2572579af54736886328c3465acc792598d4d2f4bd3062d1797b755d7d82321a`.

The promoted lever is independently verified as only: divide rounds
`698 -> 696`, sparse width repair off, replay peak `1274 -> 1273`, square
ladder `244 -> 243`, plus the baked nonce.  Multiply rounds stay 696.

The sole structural donor is commit
`14608572e84daf89397768c43ac0d812c714c3bd`, whose exact source delta against
its parent has SHA-256
`a70cc5bb135da45fafbc810070d2fd765560e178f47967a48fc1bef0fec2c525`.
Only its fused-fold selector lifecycle and focused 64-lane miter transfer;
none of its old rounds, width schedule, peak, square, nonce, fixtures, hashes,
or model artifacts transfer.

## One candidate family

Apply exactly one bounded composition:

1. transplant the donor's `fold_selector_evicted` opt-in, the two-CX erase and
   reconstruct lifecycle around `fused_fold_maskfree`, and its focused miter;
2. retain all promoted arithmetic and defaults except the candidate overrides;
3. measure with exactly:
   `SUB4_PP_FOLD_SELECTOR_EVICT=1`, `SUB4_PP_PEAK=1272`, and
   `SUB4_SQUARE_LADDER=242`;
4. leave rounds at promoted `696/696`, sparse width repair off, and every other
   `SUB4_*` control unset; retain inherited nonce `65700024945645`.

No second saddle, nonce change, repair resurrection, rescale transplant, R1/R2
change, or schedule edit is allowed in this gate.

## Frozen gates

Before pricing:

- the focused donor miter must pass 64/64 values for protected and evicted
  lifecycles, all eight selector arms, phase zero, ancilla zero, identical
  Toffoli, exactly `+4 CX +1 R`, and peak `-1`;
- product-square and full ping-pong component selftests must pass;
- forced release rebuild; no stale binary or `ops.bin` reuse.

Candidate measurement must record exact source commit/tree, env vector, loaded
operation count, full artifact SHA-256, Q, exact average executed T, rounded T,
score, and classical/phase/ancilla channels from the unchanged 9,024-shot
evaluator.  Generated artifacts remain outside Git.

Decision:

- if measured Q is not 1272 or rounded T exceeds 914961: terminal `KILL`;
- if Q1272 and rounded T is within the ceiling but any channel is nonzero:
  `SCORE_GO / VALIDATION_DIRTY`, hand source/op identity to a fresh predictor
  lane; no hunt here;
- only unchanged `0/0/0` could be submission-eligible, but submission is not
  authorized in this lane.

No provider, range, hunt, fleet action, or submission.
