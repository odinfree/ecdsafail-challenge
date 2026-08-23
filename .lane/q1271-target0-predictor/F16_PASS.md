# Q1271 target0/sign-alias fresh F16 qualification

Verdict: `PASS_FRESH_F16_16_OF_16 / ZERO_FN_ZERO_FP / CPU_PREDICTOR_GO`.

The domain-separated F16 list and one-shot runner were committed and pushed
before either local program produced output. The unchanged source-bound model
then reproduced every complete trusted classical and conditional-phase mask
on all 16 unseen rows. The inherited fixture and final fresh row also repeated
byte-for-byte.

This is terminal local unit-test parity for the combined CPU predictor. It
grants no CUDA, provider, scan, range, hunt, fleet, submission, or public-note
authority.

## Freeze and identity boundary

- negative-matrix evidence commit:
  `2cfdd9e5be17a73d08eccdc10a1dc9becf201abd`;
- pushed fresh-list / runner commit and tree:
  `52d884a0997e63f9ce0dad2d3963d6ab2dfe2886` /
  `8e382ca9395982d7904c28fc4d85d05da89ffba4`;
- frozen `F16.nonces` SHA-256:
  `bbfdbf0372f73855519c100bd5aa52c39f5f1fe5e6f966e7726b2a43c008819e`;
- one-shot runner SHA-256:
  `8b1551a9e480d7a5979d824b687def9f952044c0a370fe0ac9ad6d2040badc79`;
- domain seed-material SHA-256:
  `2f523d2176f634223f8b6c173771b59e6f49ae2a9c50c5dd12c07999153b8d19`.

The runner independently regenerated the first 16 domain-separated values and
proved they were canonical, unique, below 2^48, and disjoint from inherited,
H64, and D32. Exactly 16 counters were consumed; no fixture was selected from
an observed mask or score.

Exact source identities remained:

- source / operation count / operation SHA-256:
  `a22090374a957d29a3331d6c876ad12ff45fea31` /
  `12,919,161` /
  `590cb55deb75af4ab9356fce97308b4ca4dc10ac031d4fd6d16464e8515972fa`;
- checkpoint: `a05fe6ce236b1bfc`;
- model / host / CPU source SHA-256:
  `46e227f7920f43e8d233791dfefd01858cff39c24807d17ed2b390befa0bb390` /
  `7d432431c1d27854f6dff6b0ff807da0241deabf3b3dccc63c53b09e8b7fee8b` /
  `0e10386e356f0a21e7a89bdf8445309d14641a94fe707fe788dd777727f796ba`;
- phase schedule / CPU binary / trusted-oracle binary SHA-256:
  `49f82e4effec2c110fed73974df306cbcae9ac456043cb329bb15a7b5e97f4e8` /
  `5c2dc3f4c2be8df9a88d60448e17b65ae3073c285e68f41feaccec96f6f74021` /
  `90e4db8669c03b259c13b259018134b754faa94adfbc1e491a601f1052cd6402`.

The model source directory still has a zero diff from terminal H64 commit
`08a9da2093bd5fececbaebc7569de55b12243d9f`.

## Fresh exact result

Across 16 unchanged 9,024-shot trusted rows:

- complete classical masks: exact `16/16`, faults `256/256`;
- complete conditional-phase masks: exact `16/16`, faults `62/62`;
- raw phase faults retained as trusted context: `184`;
- classical false negatives / false positives: `0 / 0`;
- conditional-phase false negatives / false positives: `0 / 0`;
- per-row classical range: `11..21`;
- per-row raw-phase range: `7..18`;
- per-row conditional-phase range: `2..9`;
- Q / shots / ancilla on every row: `1271 / 9024 / 0`.

The inherited fixture and ordered final F16 row were rebuilt and evaluated
again. Oracle attribution/output and both model channels were byte-identical.

## Complete local corpus

The immutable model is exact on inherited + H64 + D32 + fresh F16:

- rows: `1 + 64 + 32 + 16 = 113/113`;
- classical faults: `1,925/1,925`;
- raw phase faults retained as oracle context: `1,472`;
- conditional-phase faults: `519/519`;
- complete-mask false negatives / false positives: `0 / 0`;
- trusted ancilla failures: `0`;
- fail-closed guards: `23/23`.

## Immutable fresh receipts

- external root:
  `/Users/olifreuler/ecdsa-ops/q1271-target0-sign-alias-590cb55d/fresh-f16-v1`;
- `RESULTS.tsv` SHA-256:
  `dda73db98d89d0e82de9c264ebbf965948ec44c318d4a222ea09121639ddc829`;
- transitive repeat-manifest SHA-256:
  `24a98255cad6878716adbd80684832dea119a0b15b016968b96cbea09e872246`;
- immutable-input manifest SHA-256:
  `af7b23a3ffd1cbb055c3b8da8384a1dc9316a4da6fcaf5641cc13f54c738bad8`;
- terminal marker SHA-256:
  `f8df2e9813acc3c7ef8cafb6afba724f7401c0816470c50f059027b3511a66e4`.

All operation streams, generated schedules, binaries, masks, attribution, and
logs remain outside Git. The local Q1271 combined predictor qualification is
terminal `GO` under the assigned boundary.
