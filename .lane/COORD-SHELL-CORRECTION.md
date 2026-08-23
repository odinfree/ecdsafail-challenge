# Frozen b523 Q1276 coordinate-shell correction

Date: 2026-08-23

## Source change

The predictor now implements two source-semantic value cells:

- `coord_sub_circuit`: the 256-bit complemented add used by
  `mod_sub_vented`, followed by its conditional low-53 complemented `+F` fold;
- `coord_rsub_circuit`: the default fused `coord + 1 - reg` cell used by
  `mod_rsub_vented_loaded`, including the opposite carry branch and the same
  low-53 fold.

Both are pure arithmetic functions.  They inspect no nonce, shot, expected
count, or corpus membership.  They replace exact field subtraction at the
coordinate-subtraction and fused reverse-subtraction call sites in both the
fast and traced predictor paths.  No circuit source changed.

## Frozen identities

- parent diagnosis commit: `40e4792`;
- corrected model source SHA-256:
  `7a985f119df81b9be2150eea14480156bbf2da01652b2502eb02f861498ec115`;
- local corrected release binary SHA-256:
  `e460675947b48ff736fdfdbb218979bc952ae6cae02af81e00b007ae5c2320e9`;
- exact circuit operations: `12,901,678`;
- exact circuit operations SHA-256:
  `d460c3968659b6bbbf5615268d73df210df55f9cd4cbca330de1ef960c6dd4c0`.

The built-in SHAKE256/checkpoint/scalar/point self-test passes against the baked
circuit.

## Known-corpus result before commit

On the already-revealed fixed H64, corrected predictor counts match all 64
frozen full-evaluator counts exactly.  Aggregate predictor/evaluator counts are
both `1048`.

- corrected count TSV SHA-256:
  `ac1ffa6bbdc691de80d06cbe0e809670abc610353a5ca832e240bdca6c8987cd`;
- corrected verbose receipt SHA-256:
  `3160b1898b372c6711b43314b480bfb941dc38817f4f74517e0410a2a6630f06`.

The corrected predictor exact sets for the three diagnosed rows now include
shots `4731`, `4800`, and `4853`, respectively, and equal the trusted sets
recorded in `.lane/missing-channel-shotsets.tsv`.

This is not yet an exact-model promotion.  Complete trusted-evaluator shot sets
for all 64 H rows must be regenerated and compared after this source commit.
Only after 64/64 equality may the predeclared disjoint32 evaluator outcomes be
revealed.  Parity, range, scan, hunt, provider, and submission remain held.

