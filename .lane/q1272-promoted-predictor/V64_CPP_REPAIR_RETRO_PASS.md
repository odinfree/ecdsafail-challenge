# Promoted Q1272 wrapped-restore C++ retrospective gate

Date: 2026-08-23

Verdict: `CPP_REPAIR_RETROSPECTIVE_PASS / NEW_HOLDOUT_REQUIRED / CUDA_HOLD`.

The implementation follows predeclaration `8078afc` exactly. Only the
overflow fallback in the shared CPU/CUDA classical model changed. It now
runs the fixed-width walk forward, reconstructs the source's canonical signed
terminal passengers, reverses rounds 695 through 1, applies the sparse round-0
inverse, and carries each restored denominator through the remaining point-add
shell. No phase data, width schedule, replay arithmetic, operation stream,
host generator, driver, range behavior, or trusted evaluator changed.

The only semantic donor was committed handoff
`83ad631e1a99db3db1c3886b4d61ff9ded94b0f5`, tree
`e96c542e73c8b265eadfe3c4bbcb71df1096a024`. Its complete model SHA-256 is
`0d4c9a812892b9dac598cb59a8345c443b9e21663ac29743578f4e651b39b92a`.
No uncommitted donor file was consumed.

## Repaired identities

- target structural commit:
  `73422709ed70ba9725b3cb592770bcf197df4cdb`;
- exact operation count: `12,904,643`;
- exact operation SHA-256:
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`;
- repaired shared model SHA-256:
  `d417865bcc119686dc2d9a3d45ca8e801332cf824c8ed95aefb5e0195f1318b2`;
- unchanged host SHA-256:
  `b635c95deb5bab2b89ea65de4dafdba22ea4184a647c82d4bb5680450f976435`;
- unchanged CPU driver SHA-256:
  `37550fe3d8d1f1130cdc03a746ed5b4ea6bdb619475eebcddaeb087342457352`;
- local arm64 qualification binary SHA-256:
  `0b1498cad4da581f30e7e69a6897afbaa7bc37c52513a4a0b52f348640935519`;
- reconstructed checkpoint/tail digest: `e9b2d20ecd1169a8`.

The SHAKE256 empty-string and `abc` KATs match their references.

## Targeted witness

On nonce `90522024612912`, shot `2544`, the repaired binary returns mask `4`
(`PP_F_WALK_MUL`). The full nonce now contains 18 faults, matching corrected
Rust and the trusted evaluator. Its cause totals are walk-divide 8,
walk-multiply 9, replay-multiply 1, and zero replay-divide/result faults.

## Complete-mask retrospective gates

- inherited target: all 23 trusted fault indices reproduced, including first
  shot 292;
- H64: 64/64 rows, 1,144/1,144 faults, byte-identical to corrected Rust,
  output SHA-256
  `6147c21129876a2193cd5813944b95d09ae1f149802c53ca731824a11be54adc`;
- spent D32: 32/32 rows, 559/559 faults, byte-identical to the corrected
  post-add3x Rust result, output SHA-256
  `f6684ce97550f8ff689061c34d7ea897db2f94ebd5da5419ddae911b5606c1f9`;
- revealed V64: 64/64 rows, 1,131/1,131 faults, byte-identical to corrected
  Rust and therefore to the trusted masks, output SHA-256
  `c3f5bf182ab37716e9dfaa03174de35ce703099ceb2c845a2c9e720b840ad862`.

All comparisons are complete 9,024-bit masks, not count-only checks. The raw
outputs and binary remain outside Git.

These are retrospective results on revealed corpora. The next gate is a new,
deterministic, disjoint holdout frozen before prediction or trusted evaluation.
CUDA compilation, provider compute, ranges, hunting, and submission remain
disabled.
