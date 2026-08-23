# Q1272 combined CPU negative-matrix receipt

Verdict: `PASS_23_OF_23_NEGATIVES / CPU_HANDOFF_GO / RANGE_DISABLED`.

The unchanged source-bound CPU binary accepted the exact operation stream and
checkpoint, then rejected every predeclared framing, identity, schedule,
command, nonce, and shot-index negative.  Every negative returned its expected
nonzero code, emitted exactly one required guard line, and left stdout empty.

## Bound model

- terminal D32 evidence commit: `8f8ba3af4bd792994154199bfec903dd6a72c88c`;
- target source / operations:
  `73422709ed70ba9725b3cb592770bcf197df4cdb` /
  `12,904,643` /
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`;
- model checkpoint: `e9b2d20ecd1169a8`;
- model / host / CPU source SHA-256:
  `0d4c9a812892b9dac598cb59a8345c443b9e21663ac29743578f4e651b39b92a` /
  `aa546788a823268cf311d88f028b80dd12826162fe220848ae46ec165b6190a2` /
  `dd05545d33911e7e0ab44b0e373f03a759ae8ee4b990f20f2cc40ca6ee2063af`;
- generated phase schedule SHA-256:
  `de37d6004427082c345004d1225d0f877abfe9597ac969df228b77eb915fe42f`;
- qualified CPU binary SHA-256:
  `47366b9d7d131639bb0ed9a8abc9cb87bd9c3b9aa5b746d0dcbc464ac9ba435c`.

The positive control reproduced checkpoint `e9b2d20ecd1169a8`.  It is the only
case in the receipt allowed to return zero or emit stdout.

## Negative coverage

The 23 fail-closed cases cover:

- bad operation magic, wrong declared operation count, same-count/wrong-SHA,
  wrong state digest, deliberately corrupted phase-family schedule, and a
  missing operation stream;
- scan mode, unknown mode, missing/extra mode arguments, and an extra argument
  to an identity command;
- empty, leading-zero, signed, 2^48, unsigned-overflow, and alphabetic nonces;
- missing, 9,024, leading-zero, signed, and alphabetic shot indices.

The wrong-count, wrong-SHA, bad-magic, wrong-state, and bad-schedule artifacts
and both deliberately invalid binaries are generated qualification artifacts
outside Git.  They cannot be mistaken for deployable binaries.

## Immutable receipts

- external root:
  `/Users/olifreuler/ecdsa-ops/q1272-live-phase-ea19759d/negatives/`;
- `receipt.tsv` SHA-256:
  `981eeacd629b31bc2f546d60d823c351f6538ecd02c1acd2bbffca824f233df3`;
- `IDENTITIES.sha256` SHA-256:
  `42216f35f053ad87d3c8ae75df26cb85ce8f042a65a28d8a0691dcc1e9e4c305`;
- transitive `MANIFEST.sha256` SHA-256:
  `3d63dcae8e7844a26f971794ab214275b7758b839691c1c19c6e4cec056d3ae0`;
- atomic terminal marker SHA-256:
  `27b9e5da16f0b3fed40bea9b7a242f867ed30f584980bb280498eab00098fd85`.

The committed model sources were byte-identical before and after the matrix,
and the worktree remained clean.  No operation stream, binary, log, mask,
fixture, or generated table is committed.

## Handoff boundary

The CPU combined contract is qualified on inherited + H64 + D32 complete
classical and conditional-phase masks, with deterministic repeats and all
loader/state negatives.  It is ready for an exact-source CUDA port and
CPU=CUDA fixture parity.  It is not authorization to scan a range, contact a
provider, launch a fleet, hunt a nonce, or submit.
