# Q1270 H64 trusted-mask receipt

Decision: `PASS 64/64 / MASKS SEALED / MODEL STILL UNOPENED`.

The frozen H64 `[770000000000,770000000064)` was exposed to the unchanged
current-source oracle only after the inherited gate was committed and pushed at
`b6c8b52f3b84eddb8b967be0520459dc3e5e8b2f`. The runner completed all 64
rows and atomically renamed the partial tree only after every identity,
geometry, two-pass equality, mask derivation, and ancilla guard passed.

## Corpus result

- exact rows: `64/64` in the frozen nonce order;
- geometry per row: Q1270 / 961,070 bits / 12,953,636 operations / 9,024 shots;
- aggregate classical failures: `1,177`, per-row range `11..27`;
- aggregate raw phase failures: `871` shots across `830` dirty batches,
  per-row shot range `4..21`;
- aggregate clean phase failures: `286`, per-row range `1..9`;
- aggregate ancilla failures: `0` shots / `0` batches;
- aggregate exact Toffoli total across all rows: `529,237,802,205`;
- aggregate exact Clifford total across all rows: `6,197,855,056,927`.

The final corpus identities are:

- `RESULTS.tsv` SHA-256:
  `da0ca6fed7a3e45433a1d997a0d6f0116d92748731256666731a4cdaa34e3a6e`;
- complete `SHA256SUMS` SHA-256:
  `07e4a19246681192735dcf4a68ca2c4095eb7caa7e746ce0336a0891436ba20a`;
- terminal `COMPLETE` SHA-256:
  `a5fcd33df7da08caae2b4348b6c5c91090b4984a2281abad7573cc11c4f28b31`.

An independent manifest check verified every sealed artifact. A second
independent parser then required all 64 canonical rows to be 4,892 bytes, have
the correct magic and 13-field summary, match their declared row SHA, contain
exactly four 141-word masks, satisfy `clean = raw & ~classical` word-for-word,
and reproduce every declared count. It passed `64/64`.

## Complete-mask digests

Concatenating each 141-word little-endian mask in ascending frozen nonce order
produces these corpus identities:

- classical:
  `61d45a196ca2c5e24823f008373dfa2866367a6ded3385690709350583bd49ac`;
- raw phase:
  `f121249a41f2c89a0b00a8d18c50b1c27a4d0267403e877bf9ddc019afaa0f5b`;
- clean phase:
  `3820bbeb4b3107ea15fa3f9b3eaddb671ce479f270cd86bb2480d6fb47c64ce2`;
- ancilla:
  `2e69ecb4f11d0e05bbb0dbb71590cf33cde3200ab1609cff3af60ab50ebc434f`.

The 64 complete `row.bin` records concatenated in the same order hash to
`88d324b7cca4a42a22c78915ca686f6ad98b2596460aa7ce11f9f785bfca71ef`.

Tracked `results.tsv`, `ops.bin`, evaluator, simulator, circuit, and structural
source hashes remain byte-exact. No donor source/model/binary/table/output and
no D32 value was opened during this gate. This receipt authorizes only a
separately predeclared, Q1270-source-bound model port; it grants no range,
search, provider, CUDA, hunt, submission, or public-note action.
