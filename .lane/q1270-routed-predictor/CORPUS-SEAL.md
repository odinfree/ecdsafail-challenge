# Q1270 routed combined-predictor corpus seal

Date: 2026-08-23. Status: `SEALED / D32 UNOPENED`.

## New fixtures

| corpus | rows | visibility | SHA-256 |
|---|---:|---|---|
| inherited | 1 | tracked | `dabc177103443bede607625489337794ac828e25b60e787a67f7789bfa1627f1` |
| H64 | 64 | tracked, deterministic interval | `87fb300f0f1aa12cb4c6e70c24f0cae7899313c1cc5bd6f92ab70c06848314bd` |
| D32 | 32 | private, mode 0600, unopened | `09941a9174ee19346039a000ceb7f907a13aecaab0a47bf4f0d4b3272508240e` |

The private D32 is deterministic under a sealed 32-byte seed whose SHA-256 is
`2cf63b982a823ec4f145a443163c889f836f0ceea030eed9bdacdf0472f576a9`.
The generator is `tools/freeze_corpora.rb`, SHA-256
`def07bd9cdcc838a683c9bbf21a408d5b0c75040b1a763bc81c0148854c662e4`.
It enforces canonical decimal rows, uniqueness, range below 2^48, and zero
intersection without printing private nonce values.

## Prior-corpus exclusion identities

| prior object | SHA-256 |
|---|---|
| Q1271 live inherited-eight | `697dfcab8f33ab39c2f5ad706834c18d0440d4c76046b58f1df42fafe955111e` |
| Q1271 target0 inherited-one | `dabc177103443bede607625489337794ac828e25b60e787a67f7789bfa1627f1` |
| shared Q1271/Q1272 H64 | `17443162349d50e521b0c9a20904de5a0212a668e6f3ae7ea0e2702b2f79c4b9` |
| shared Q1271/Q1272 D32 | `62bca2420f684c718e52b516dc850f05d72c33f64798002fe2afd215642a0f90` |

The union contains 104 unique prior values. Automated set comparison returned
`overlap=0` for both new corpora.

## Reveal rule

The private D32 nonce file may not be read by a predictor process or used to
build an operation stream until all inherited and H64 trusted masks are sealed,
the donor model is source-bound, and exact H64 mask equality is committed and
pushed. Predictor output on D32 must then be hashed and committed before the
first D32 trusted evaluator run. Any post-reveal model edit invalidates D32.
