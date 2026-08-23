# Q1271 target0/sign-alias combined-model H64 qualification

Verdict: `PASS_INHERITED_1_OF_1 / PASS_H64_64_OF_64 / MODEL_SEALED / D32_UNOPENED`.

The target-bound CPU model reproduces the complete trusted classical and
conditional-phase masks on the inherited fixture and every frozen H64 row.
There were no mask mismatches, geometry failures, nonzero ancillas, tolerant
matches, oracle lookups, or post-result source repairs.  This is a local
fixture-parity gate only and grants no provider, CUDA, scan, range, hunt,
submission, fleet, or public-note authority.

## Exact target and model identities

- source/evidence commit / tree:
  `a22090374a957d29a3331d6c876ad12ff45fea31` /
  `018eb52de8ab3e6337864338683821c0cbb574a2`;
- operations: `12,919,161`, SHA-256
  `590cb55deb75af4ab9356fce97308b4ca4dc10ac031d4fd6d16464e8515972fa`;
- operation checkpoint digest: `a05fe6ce236b1bfc`;
- model / host / CPU source SHA-256:
  `46e227f7920f43e8d233791dfefd01858cff39c24807d17ed2b390befa0bb390` /
  `7d432431c1d27854f6dff6b0ff807da0241deabf3b3dccc63c53b09e8b7fee8b` /
  `0e10386e356f0a21e7a89bdf8445309d14641a94fe707fe788dd777727f796ba`;
- locally compiled qualification binary SHA-256:
  `5c2dc3f4c2be8df9a88d60448e17b65ae3073c285e68f41feaccec96f6f74021`;
- H64 runner SHA-256:
  `d9b89336bbdb73fa0c8d664876fa244b870330c26b4012aabfacd3815dec59d3`.

The binary was rebuilt independently from the same source and generated
header and matched byte-for-byte.  SHAKE256 empty and `abc` test vectors also
matched their fixed references.

## Source-derived geometry

The target trace contains `12,919,065` source-attributed body operations plus
the exact 96-X nonce tail.  Joining it to the immutable operation stream gives
`1,941,386` R/Hmr words and 3,970 modeled measured-boundary sites:

- 2,579 chunk-carry predicates at `pingpong_div.rs:1577`;
- 694 divide-flag predicates at `pingpong_div.rs:1846`;
- 694 multiply-flag predicates at `pingpong_div.rs:2006`;
- three arithmetic-shell predicates at `arith.rs:1501`.

The phase-meta / generated-header SHA-256 values are
`665e64bb22d87ba629a133f7c67813c284a7fca47d1b6212914c83abe0f5fa1e` /
`49f82e4effec2c110fed73974df306cbcae9ac456043cb329bb15a7b5e97f4e8`.
An independent regeneration reproduced both files byte-for-byte.  The model
uses 696 divide rounds, 696 multiply rounds, Q1271 for divide replay, Q1272
for multiply replay, and square ladder 241, all derived from the frozen
target controls rather than inherited from the Q1272 donor.

## Complete-mask parity

Inherited nonce `65700024945645` matched exactly:

- classical: all `11/11` indices;
- conditional phase: all `4/4` indices
  `{2854,5626,8398,8828}`;
- ancilla: `0`;
- generated inherited artifact-manifest SHA-256:
  `5c68e3f88470ad6ec093aea85fa273c7ec44ae8b5646cf1abe24b081230591d3`.

Across H64, every complete mask matched exactly `64/64`:

- classical faults: `1,093 / 1,093`;
- raw phase faults retained as oracle context: `843`;
- conditional-phase faults: `298 / 298`;
- Q / shots / ancilla on every oracle row: `1271 / 9024 / 0`;
- model/oracle mismatches: `0`;
- compact generated `RESULTS.tsv` SHA-256:
  `3819de96a6d5351a53a8bd6b45371467cc2fa8f5ee7b5162fc34239391e2e6d7`.

The runner revalidated the frozen H64 canonical-oracle digest
`4ee3022cac1798c1d50e871db2518c7142750e6bd272e56b08e8b3bf05e1553e`
and its 192-row artifact-manifest digest
`0faa6512fc6240c71fd42c82ef8ddaf6c77f1990f0887604283e838e8b6c1072`
before executing any model row.

All generated masks, binaries, operation streams, phase tables, and raw logs
remain outside Git under
`/Users/olifreuler/ecdsa-ops/q1271-target0-sign-alias-590cb55d`.

## Next gate

Seal and push this exact model family.  Only then reveal the precommitted,
disjoint D32 list and compare the unchanged binary against trusted complete
masks once.  No source-semantic edit is permitted after D32 reveal; any mask
difference is terminal `HOLD`.
