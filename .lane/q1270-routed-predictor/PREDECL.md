# Q1270 routed source-bound combined predictor predeclaration

Date: 2026-08-23. Decision: `FROZEN / TRUSTED MASKS FIRST / MODEL UNOPENED`.

This lane qualifies a source-bound classical plus conditional-phase CPU screen
for the exact Q1270 routed-control stream. The circuit source stays rooted at
`90770b1`; the terminal full-run evidence is referenced from `953acb4`. This
lane grants no circuit edit, CUDA, provider, range, hunt, submission, or
public-note authority.

## Structural, artifact, and full-run binding

- exact circuit source commit / tree:
  `90770b10664fc89065b1d05ac792370efed4c629` /
  `944593de97d412f8b4c7242f7d0aff98002c0d04`;
- terminal full-run evidence commit / tree:
  `953acb44fbcbb32ab097a52be31ae365db41bd92` /
  `5ef28c48221cd3bd3e63018a9faead791b3a79cc`;
- terminal receipt SHA-256:
  `6dafe97e6d9a7ed38ed4009e150a2c1b8661375eb6af1690136e33cf12589917`;
- `src/point_add/pingpong_div.rs` SHA-256:
  `9b1e5e8540a01584e1238c27328481ba67db3b167aa199db4113e846f1eb6295`;
- `src/point_add/mod.rs` SHA-256:
  `3fbe6baa8bb4638217f7416b858f4ddd57906fdaaecc500d860f1ca96f1ed60f`;
- unchanged evaluator source SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`;
- exact operation count / compressed SHA-256:
  `12,953,636` /
  `ec4fadc0b5cd1c26ee5d81001b7a72692678b61a94c4091032dd93b8b62eb63a`;
- Q / bits: `1270 / 961,070`;
- inherited full result: exact displayed T `916366.972`, rounded T `916367`,
  score `1,163,786,090`, classical / conditional-phase / ancilla `23/14/0`,
  first classical mismatch shot `373`.

The exact circuit environment is:

```text
SUB4_PP_FOLD_SELECTOR_EVICT=1
SUB4_PP_EVICT_DOUBLED_OUT=1
SUB4_PP_ALIAS_TARGET0_SIGN=1
SUB4_PP_EVICT_SIGN_XOR_ADD=1
SUB4_PP_PEAK=1270
SUB4_PP_MUL_REPLAY_PEAK=1271
SUB4_SQUARE_LADDER=240
SUB4_PINGPONG_TAIL_NONCE=<fixture nonce>
```

No other `SUB4_*` variable is permitted.

## Frozen corpora

- inherited nonce list: one row, `65700024945645`, SHA-256
  `dabc177103443bede607625489337794ac828e25b60e787a67f7789bfa1627f1`;
- public deterministic H64: `[770000000000, 770000000064)`, SHA-256
  `87fb300f0f1aa12cb4c6e70c24f0cae7899313c1cc5bd6f92ab70c06848314bd`;
- private unopened D32 SHA-256:
  `09941a9174ee19346039a000ceb7f907a13aecaab0a47bf4f0d4b3272508240e`;
- private seed SHA-256:
  `2cf63b982a823ec4f145a443163c889f836f0ceea030eed9bdacdf0472f576a9`;
- deterministic freeze tool SHA-256:
  `def07bd9cdcc838a683c9bbf21a408d5b0c75040b1a763bc81c0148854c662e4`.

The D32 values and seed live mode-0600 outside Git at
`/Users/olifreuler/ecdsa-ops/q1270-routed-combined-ec4fadc0/private/`.
Generation printed only hashes and counts; no nonce values were opened, no
operation stream was built for them, and no evaluator or predictor saw them.

Disjointness was checked against 104 unique values spanning both prior Q1271
inherited corpora, the shared prior Q1271/Q1272 H64, and the prior Q1271/Q1272
D32 object. The new H64 and D32 have zero intersection with those values, with
each other, and with the inherited Q1270 nonce. `CORPUS-SEAL.md` binds the
prior identities and reveal rule.

## Mandatory order

1. Commit and push this predeclaration before target reconstruction.
2. Rebuild from an empty target using `--locked --offline`; require exact
   source hashes, operation count/SHA, Q, bits, and inherited full receipt.
3. Derive the operation checkpoint, nonce-tail shape, R/Hmr count,
   source-site trace, conditional-phase family table, schedule, and ordinals
   anew from `90770b1`.
4. Build a current-source output-only trusted oracle by auditable
   instrumentation of the unchanged evaluator. It may emit complete masks and
   integer metrics only; simulation, comparisons, RNG, accounting, and exit
   status remain unchanged.
5. Before importing, compiling, or running any donor predictor code, seal
   complete trusted inherited and H64 masks outside Git and push their hashes
   and aggregate receipts.
6. Only then predeclare and port one donor recurrence semantically. No Q1271 or
   Q1272 fixture, checkpoint, schedule, ordinal, operation digest, or generated
   table may transfer.
7. Require complete 9,024-bit classical-mask equality and complete
   `raw_phase_mask & ~classical_mask` equality for the inherited row, then for
   all 64 H64 rows in one frozen reveal. Any mismatch kills the family.
8. Only after the H64 equality commit is pushed may the D32 nonce file be
   opened to the frozen predictor. Seal predictions before any D32 operation
   build or trusted evaluator result, then reveal the evaluator once without a
   post-reveal model edit.

## Exact mask and guard contract

For every nonce, retain outside Git and hash a canonical row containing:

- nonce, source/operation/checkpoint/schedule identities;
- Q1270, 961,070 bits, 12,953,636 operations, and 9,024 shots;
- 141 little-endian 64-bit words for the complete classical mask;
- 141 words for the complete raw conditional-phase mask;
- 141 words for `raw_phase & ~classical`;
- exact classical, raw-phase, clean-phase, and ancilla totals;
- exact integer Toffoli/Clifford totals and deterministic row digest.

Every row requires ancilla zero, canonical unique shot indices in `[0,9024)`,
deterministic byte-identical repeats on the calibration row, no abort or
partial output, and fail-closed identity checks. Count-only agreement is not
predictor evidence.

Generated operation streams, binaries, traces, checkpoints, schedules, raw
masks, evaluator output, and logs remain outside Git. Commits contain only
source, runners, hash manifests, and evidence summaries.
