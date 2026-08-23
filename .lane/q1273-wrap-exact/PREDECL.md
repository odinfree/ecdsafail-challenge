# Q1273 wrapped-register predictor repair predeclaration

Status: `FROZEN / RESULTS UNOPENED`.

This lane starts from terminal predictor hold
`41df51a37e0489b5e801faec9b3db588b2037c6a` and the exact structural source
`093d85d64de87aa5006a94868172f642daacf136`.  It remains bound to Q1273,
`12,933,805` operations, and operation SHA-256
`ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1`.

The unchanged predictor inputs are:

- `pp_host.h` SHA-256
  `7a7e477082c240278c36eabfca227b8266d638ae5ab30e5ac6ea2a7dd34f42bb`;
- `pp_model.h` SHA-256
  `8e97b9b94d313e05bbe7fb844a53381b17c9c3fbd027a744feb41edaa993976d`;
- `ppcpu.cpp` SHA-256
  `0fde4f34365e352b272e138d450d9321fff9a1366d38fbd7213dda35b58fa4a8`;
- qualified CPU binary SHA-256
  `93a9d9be4e542388457d802dd0a0832c527bfe3803efd8158a2d66e626ecd63c`;
- inherited full-evaluator receipt: nonce `100000045835813`, complete classical
  mask with `12` shots, phase `12`, ancilla `0`.

## One allowed semantic family

The only allowed repair family is a **terminal-canonicalized finite-width
register transducer** copied from the source circuit's logical state changes:

1. Each `shrink_to` retains the low `w` two's-complement bits of both walk
   registers.  Each walk add and arithmetic shift then runs modulo that exact
   scheduled width; it never substitutes an ideal unbounded-GCD value.
2. The sign tape is the tape produced by those wrapped registers.  At the
   terminal passenger loan, each register is canonicalized exactly as the
   circuit does: bit 0 becomes one and interior bits become copies of the
   retained sign, yielding `+1` or `-1` at the current width even when the
   preceding walk did not converge mathematically.
3. Replay consumes that exact tape with the already source-bound fold/carry
   model.  Walkback starts from the circuit-canonicalized terminal registers,
   grows by sign extension, reverses every fixed-width add/shift, and applies
   the source's truncated sparse round-zero inverse fold.  The recovered low
   256 denominator bits, rather than the ideal original denominator, feed the
   remaining point-add shell.
4. The final classical verdict is the complete circuit-derived coordinate
   comparison.  The implementation may retain the existing fast path when no
   scheduled-width overflow occurs, but the overflow path may not use
   `overflow => fault`, `overflow => clean`, an ideal full-output fallback, a
   nonce/shot exception, or a corpus-derived threshold.

This is one source-semantic family.  If it cannot preserve both bound witnesses
and the blinded holdout, the lane stops `HOLD`; no second repair family may be
tuned in this lane.

## Bound revealed regressions

- Divide false positive to remove: nonce `730140001442`, shot `6329`, original
  mask `PP_F_WALK_DIV`; unchanged evaluator says clean.  First ideal overflow:
  post-round 602, scheduled width 44.  Oracle artifact SHA-256
  `233c7b5333bd197d1985a7dd6582f438111b90eb5dd6c601552012568d0a51fb`.
- Multiply false negative that must remain a fault: nonce `730070000721`, shot
  `2493`, original and evaluator mask `PP_F_WALK_MUL`.  First ideal overflow:
  pre-round 503, scheduled width 83.  Oracle artifact SHA-256
  `2bc767c89b97cb294a218489f21f72924cd08d9902596bc965761d0fc5986d19`.
- Inherited plus H64 exact-mask regression: 65/65 complete sets; H64 fixture
  ledger SHA-256
  `7918937a30d562a2dd26cf59374cdb702c11ce0f08d42789f9ef42da8264b5f4`;
  evaluator concatenated index-mask SHA-256
  `9c1c9cfb0dc7057e8ea1aafbd55c42382e9c4eeabab0d13fe80d18d98c899f46`.
- Revealed inherited plus D16 oracle ledger SHA-256
  `e148f24d99ae45b3c6930a33d49173fd31b2c236593d98375956077b3feb4d1b`.

## Newly frozen disjoint D32

The 32 nonces in `D32.nonces` were frozen before any evaluator or repaired
predictor result was opened.  Their SHA-256 is
`62bca2420f684c718e52b516dc850f05d72c33f64798002fe2afd215642a0f90`.
Each row is the unsigned integer represented by the first 12 hexadecimal
characters of:

```text
SHA256("ecdsa.fail|q1273-wrap-register-v1|093d85d64de87aa5006a94868172f642daacf136|41df51a37e0489b5e801faec9b3db588b2037c6a|d32|%02d")
```

for indices 00 through 31.  The list has 32 unique values and no collision
with the inherited nonce, H64 range, or either fixed witness.  D32 remains
blinded until implementation and all revealed regressions pass.

## Frozen gate order

1. Commit this predeclaration before semantic edits.
2. Implement only the family above and commit the implementation before
   qualification.
3. Require exact complete-mask equality for the two witnesses, inherited,
   H64, and D16 in that order.
4. Only after those pass, generate unchanged-evaluator D32 masks and compare all
   32 complete masks.  Repeat the full predictor corpus and require byte-exact
   determinism.
5. Re-run wrong operation-count, same-count/wrong-SHA, wrong-state-digest, bad
   framing/magic, missing fixture, malformed nonce, and scan-disabled gates.
6. Prepare a CUDA handoff packet only after every CPU gate passes.  No CUDA
   build, provider, range, hunt, incumbent mutation, or submission is allowed
   in this lane.

Generated operations, evaluator output, raw masks, binaries, logs, and scratch
instrumentation remain outside Git.  Git may contain only source, nonce lists,
hash ledgers, and concise terminal evidence.
