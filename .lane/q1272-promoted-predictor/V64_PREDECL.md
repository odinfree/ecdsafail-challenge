# Promoted Q1272 post-repair V64 predeclaration

Date: 2026-08-23

Status: `FROZEN_BEFORE_PREDICTION / EVALUATOR_UNOPENED`.

This is the first fresh holdout after the add3x model correction at `3abf2af`.
It is frozen before the corrected Rust predictor, shared C++ predictor, or
trusted evaluator is run on any member.

The 64 nonces were generated deterministically for indices `i = 0..63`:

1. compute
   `SHA256(b"q1272-promoted-v64-after-add3x-v1\\0" || LE32(i))`;
2. interpret the first six digest bytes as an unsigned little-endian integer;
3. sort the 64 values numerically and require uniqueness.

The frozen corpus is `.lane/q1272-promoted-predictor/V64.nonces`, SHA-256
`9db8b3a0fc0f277f8cea77cac181cc6133a667c96d5e73a97397a7116a6ec1bd`.
It has zero overlap with the inherited nonce, H64, or spent D32.

The exact model and stream bindings are:

- corrected Rust source commit: `3abf2af`;
- corrected Rust source SHA-256:
  `39371fca9e77d7aab3cfda7111bdbc03c11d8cfc03966cd15b2ea77d79836e38`;
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

Terminal acceptance requires all 64 complete 9,024-bit classical masks to be
identical across the corrected Rust model, the unchanged shared C++ model, and
the trusted evaluator. Every trusted row must report Q1272, 9,024 shots, and
zero ancilla-garbage batches. Prediction must be sealed before the first
evaluator row is opened. Any difference fails the gate permanently; V64 then
becomes revealed evidence and cannot be relabeled as a fresh holdout.

Conditional phase remains an independently source-bound gate. CUDA, provider
compute, scan ranges, hunting, and submissions remain disabled.
