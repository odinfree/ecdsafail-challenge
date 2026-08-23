# Promoted Q1272 disjoint D32 predeclaration

Date: 2026-08-23

Status: `FROZEN_BEFORE_PREDICTION / EVALUATOR_UNOPENED`.

This 32-nonce holdout is frozen before running either the exact Rust predictor,
the shared CPU predictor, or the trusted evaluator on any member. It is
separate from the contiguous H64 corpus `444000000000..444000000063` and from
the inherited diagnostic nonce `65700024945645`.

The corpus was generated deterministically for indices `i = 0..31` as follows:

1. Compute `SHA256(b"q1272-promoted-d32-v1\\0" || LE32(i))`.
2. Interpret the first six digest bytes as an unsigned little-endian integer.
3. Sort the 32 resulting values numerically and require uniqueness.

The frozen corpus is `.lane/q1272-promoted-predictor/D32.nonces`, SHA-256
`45838602350ecabd4c95d900602d440692e57bffd2581160e1f151ccdb4cc79c`.
The predeclaration commit is the anti-adaptation boundary. No prediction or
trusted result may be consumed before that commit is pushed.

Terminal acceptance is exact 9024-bit classical-mask equality for all 32
nonces under structural source commit
`73422709ed70ba9725b3cb592770bcf197df4cdb`, operation count `12,904,643`,
operation SHA-256
`ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`,
and only this environment:

```
SUB4_PP_FOLD_SELECTOR_EVICT=1
SUB4_PP_PEAK=1272
SUB4_SQUARE_LADDER=242
```

Every other external `SUB4_*` variable is unset. Every trusted row must report
Q1272, 9024 shots, and zero ancilla-garbage batches. Phase is diagnostic here;
conditional-phase qualification is an independent source-bound gate. Provider
compute, scan ranges, nonce hunting, and submissions remain disabled.
