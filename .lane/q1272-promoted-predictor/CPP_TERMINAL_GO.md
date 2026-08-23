# Promoted Q1272 shared C++ terminal local-model gate

Date: 2026-08-23

Verdict: `LOCAL_CPP_CLASSICAL_GO / CUDA_HOLD / RANGE_HOLD`.

The V64 false negative at nonce `90522024612912`, shot `2544`, came from
substituting the ideal multiply denominator after a lossy fixed-width walk.
Commit `19de424` replaced that shortcut with the source-equivalent wrapped
forward transducer, canonical signed terminal reconstruction, walkback, sparse
round-zero inverse, and restored-denominator shell.  The targeted witness now
returns `PP_F_WALK_MUL` (`mask=4`).

## Fresh cross-implementation replay

A fresh arm64 build from the committed repaired sources reproduced state digest
`e9b2d20ecd1169a8`, passed the SHAKE256 empty-string and `abc` known-answer
tests, and was compared directly with a fresh run of the corrected Rust model.
Every comparison used the complete 141-word mask covering all 9,024 shots.

| corpus | nonces | classical faults | Rust/C++ complete masks | output SHA-256 |
| --- | ---: | ---: | --- | --- |
| inherited | 1 | 23 | exact | index set `c46041ff454200ba4d2ab3cffcefb2b118e4afd839f674431762b24da37f8848` |
| H64 | 64 | 1,144 | 64/64 exact | `6147c21129876a2193cd5813944b95d09ae1f149802c53ca731824a11be54adc` |
| spent D32 | 32 | 559 | 32/32 exact | `f6684ce97550f8ff689061c34d7ea897db2f94ebd5da5419ddae911b5606c1f9` |
| revealed V64 | 64 | 1,131 | 64/64 exact | `c3f5bf182ab37716e9dfaa03174de35ce703099ceb2c845a2c9e720b840ad862` |
| blind W64 | 64 | 1,138 | 64/64 exact | `0e395369f6b6e8d560e3693316f5dc59d93e0e009d5b7b559e712f62720b276d` |

That is `225` nonces, `2,030,400` modeled shots, and `3,995` fault bits with
zero Rust/C++ mask differences.  Inherited, H64, D32, and V64 are retrospective
corpora.  W64 is the new disjoint post-repair holdout and independently matches
the unchanged trusted evaluator on every complete mask, as sealed in
`W64_TRUSTED_PASS.md`.

## Fail-closed matrix

Twelve local negatives were rerun against the repaired source identity:

1. bad magic;
2. wrong operation count;
3. corrupted compressed body;
4. valid same-count but wrong checkpoint/tail state;
5. truncated operation stream;
6. missing operation stream;
7. disabled scan selector;
8. malformed nonce fixture;
9. empty nonce fixture;
10. missing nonce fixture;
11. extra fixture argument;
12. unknown selector.

Every rejection returned its predeclared nonzero status with empty stdout.  The
positive state control returned `e9b2d20ecd1169a8`.  The normalized negative
receipt SHA-256 is
`1eb7ea3b06970d900539c80b1a490e157cd15a791692a286aa95909685a8976d`.

## Boundary

This GO qualifies the committed shared C++ classical model for a separate,
source-bound handoff.  It does not inherit or grant conditional-phase, CUDA,
range, provider, hunt, or submission authority.  Those gates remain closed.
Generated binaries, operation streams, raw masks, evaluator logs, and negative
fixtures remain outside Git.
