# Q1272 CUDA port implementation checkpoint

Date: 2026-08-23
Status: `IMPLEMENTED_UNCOMPILED / HOLD_REMOTE`

The source-bound Q1272 classical predictor has been translated into
`.lane/q1272-cuda/pingpong_filter.cu` under the edit boundary frozen in
`CUDA-PORT-PREDECLARATION.md`.

Implemented changes:

- operation-count guard updated to `12,908,488`;
- circuit-exact coordinate subtraction and reverse subtraction ported from the
  qualified Rust predictor;
- six-limb product-square value channel ported from the same predictor;
- `point_add_classical` routed through those three circuit-exact functions;
- parent walk, replay, Fiat-Shamir, complete-mask, early-exit, and host control
  code otherwise left unchanged.

Source SHA-256:

```text
9f9f9c24539257a1e517323b2857798a7aedaee5e37aa3eb1c738f9c28d84c45
```

Local checks at this checkpoint:

- semantic diff against `ddfe396:.lane/b1-24-parity/pingpong_filter.cu`
  contains only the predeclared port surface;
- the translated functions were checked side by side against
  `src/bin/pingpong_filter.rs`;
- whitespace validation passes;
- this host has no `nvcc`, so the source has not been compiled or executed.

No GPU host, provider, range, hunt, or submission is authorized by this
checkpoint. Remote compilation remains blocked until the blinded D32 CPU mask
gate passes exactly. Once unblocked, the full Linux CPU/CUDA H64 and D32 mask
parity sequence and fail-closed negatives in the predeclaration remain
mandatory.
