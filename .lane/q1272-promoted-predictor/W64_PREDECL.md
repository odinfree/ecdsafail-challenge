# Promoted Q1272 post-wrapped-repair W64 predeclaration

Date: 2026-08-23

Status: `FROZEN_BEFORE_PREDICTION / EVALUATOR_UNOPENED`.

This is the first fresh holdout after the shared C++ wrapped-state repair at
`19de424`. It is frozen before the corrected Rust predictor, repaired C++
predictor, or trusted evaluator is run on any member.

The 64 nonces were generated deterministically for indices `i = 0..63`:

1. compute
   `SHA256(b"q1272-promoted-w64-after-wrapped-restore-v1\0" || LE32(i))`;
2. interpret the first six digest bytes as an unsigned little-endian integer;
3. sort the 64 values numerically and require uniqueness.

The frozen corpus is `.lane/q1272-promoted-predictor/W64.nonces`, SHA-256
`db43f935ec97561cdab7f1e0c86d11ea439f9b75f0da815a7a92b999bc5575a0`.
Deterministic regeneration is exact. It has zero overlap with inherited,
H64, spent D32, or revealed V64.

The exact model and stream bindings are:

- corrected Rust source commit: `3abf2af`;
- corrected Rust source SHA-256:
  `39371fca9e77d7aab3cfda7111bdbc03c11d8cfc03966cd15b2ea77d79836e38`;
- repaired shared C++ source commit: `19de424`;
- repaired shared model SHA-256:
  `d417865bcc119686dc2d9a3d45ca8e801332cf824c8ed95aefb5e0195f1318b2`;
- structural source commit:
  `73422709ed70ba9725b3cb592770bcf197df4cdb`;
- operation count: `12,904,643`;
- operation SHA-256:
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`;
- checkpoint/tail state digest: `e9b2d20ecd1169a8`;
- exact external environment:

```
SUB4_PP_FOLD_SELECTOR_EVICT=1
SUB4_PP_PEAK=1272
SUB4_SQUARE_LADDER=242
```

Every other external `SUB4_*` variable is unset.

Prediction order is Rust first, repaired C++ second, then an immutable seal
before the first trusted evaluator row is opened. Terminal acceptance requires
all 64 complete 9,024-bit classical masks to be identical across both models
and the unchanged trusted evaluator. Every trusted row must report Q1272,
9,024 shots, and zero ancilla-garbage batches. Any difference fails this gate
permanently.

Conditional phase remains independently owned. CUDA, provider compute, scan
ranges, hunting, and submissions remain disabled.
