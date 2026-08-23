# Q1271 target0/sign-alias fail-closed qualification

Verdict: `PASS_23_OF_23_NEGATIVES / RANGE_DISABLED / FRESH_HOLDOUT_NEXT`.

The precommitted guard harness accepted the exact operation stream and
checkpoint, then rejected every fixed framing, identity, schedule, command,
nonce, and shot-index negative. All 23 negatives returned nonzero, emitted
their required guard exactly once, and left stdout empty. The positive control
alone returned zero and reproduced checkpoint `a05fe6ce236b1bfc`.

This receipt grants no provider, CUDA, scan, range, hunt, fleet, submission,
or public-note authority.

## Sealed inputs

- D32 evidence commit:
  `18bb4547c0889410440e9f3cb00df02819cb7327`;
- precommitted negative runner commit:
  `65a75467c5948d74a8de043d8ad68055f05f2211`;
- runner SHA-256:
  `d99a434f1aca8214e9851e4ea54c04d51f01c8b973e3953d7ff2fd2970c4da8e`;
- source / operation count / operation SHA-256:
  `a22090374a957d29a3331d6c876ad12ff45fea31` /
  `12,919,161` /
  `590cb55deb75af4ab9356fce97308b4ca4dc10ac031d4fd6d16464e8515972fa`;
- model / host / CPU source SHA-256:
  `46e227f7920f43e8d233791dfefd01858cff39c24807d17ed2b390befa0bb390` /
  `7d432431c1d27854f6dff6b0ff807da0241deabf3b3dccc63c53b09e8b7fee8b` /
  `0e10386e356f0a21e7a89bdf8445309d14641a94fe707fe788dd777727f796ba`;
- phase schedule / qualified CPU binary SHA-256:
  `49f82e4effec2c110fed73974df306cbcae9ac456043cb329bb15a7b5e97f4e8` /
  `5c2dc3f4c2be8df9a88d60448e17b65ae3073c285e68f41feaccec96f6f74021`.

The committed model source directory has a zero diff from terminal H64 commit
`08a9da2093bd5fececbaebc7569de55b12243d9f` after the matrix.

## Exact negative coverage

The 23 cases cover:

- bad operation magic, wrong declared operation count, same-count/wrong-SHA,
  wrong state digest, a deliberately corrupted phase-family schedule, and a
  missing operation stream;
- scan mode, range mode, an unknown mode, missing/extra mode arguments, and an
  extra identity argument;
- empty, leading-zero, signed, 2^48, unsigned-overflow, and alphabetic nonces;
- missing, 9,024, leading-zero, signed, and alphabetic shot indices.

The bad operation artifacts and deliberately invalid binaries are generated
qualification artifacts outside Git and cannot be mistaken for deployable
binaries.

## Immutable receipts

- external root:
  `/Users/olifreuler/ecdsa-ops/q1271-target0-sign-alias-590cb55d/negatives-v1`;
- `receipt.tsv` SHA-256:
  `9c2626f1f12ba1a7d64a25b7577a51967061f57bd5762cb35dc122f67eee8e80`;
- `IDENTITIES.sha256` SHA-256:
  `f2d909bf597eb94ed52ece9a161b5ec11de4e628eeda9dbc391d3419e1430656`;
- transitive `MANIFEST.sha256` SHA-256:
  `321e75062b447a13682d9e3b2aa4b9c0c9e0233987c4154869dd5785d96763b7`;
- atomic terminal marker SHA-256:
  `f140cc7529d3cc4a4e3676c58d7d7a10254fca4b44aaae1672e81b3762f22b7a`.

## Next gate

Freeze a genuinely fresh, domain-separated fixture list before producing any
oracle or model output. Then require exact complete classical and conditional-
phase masks, zero false negatives, zero false positives, and unchanged
identities on every row.
