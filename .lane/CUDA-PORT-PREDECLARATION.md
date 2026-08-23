# Q1272 selector-stream CUDA predictor port

Date: 2026-08-23

## Frozen source

This implementation lane begins at Q1272 CPU audit commit `6d8a995`.  The
candidate circuit remains exact structural commit
`14608572e84daf89397768c43ac0d812c714c3bd` under:

```text
SUB4_PP_PEAK=1272
SUB4_SQUARE_LADDER=242
SUB4_PP_FOLD_SELECTOR_EVICT=1
```

Its identity is 12,908,488 emitted operations and operation SHA-256
`678c149f65ce00cd44caada6a534817e8b69f993913c509a8b396b6f526c22f0`.
The Rust predictor source SHA-256 is
`b2a4d44c89b5340c7cc7d2db8a11b8cebc9207537a0f6883445d9dd85799e9b4`.
It has independently matched 64/64 complete H64 classical masks and all
1,457/1,457 evaluator fault shots.

## Frozen CUDA parent and edit

Port the complete-mask CUDA predictor from exact B1 parity commit `ddfe396`:

```text
.lane/b1-24-parity/pingpong_filter.cu SHA-256
2986855fd6ad3334b448f296047d30851ba051dc2d2b9204fd8da08461856bae
```

Allowed semantic changes are limited to:

1. bind the checkpoint guard to 12,908,488 operations;
2. port the generic coordinate-subtraction, coordinate-reverse-subtraction,
   and product-square value-channel functions from the qualified Rust model;
3. route `point_add_classical` through those functions exactly as Rust does;
4. update source-binding comments and names.

The B1=24 walk, replay, Fiat-Shamir, elliptic-curve, complete-mask, early-exit,
and host orchestration code must otherwise remain unchanged.  The selector
lifecycle is classically exact and receives no CUDA exception.  No
nonce-specific repair, fixture lookup, accepted-mask table, or result-driven
branch is allowed.

## Execution gates

Implementation may proceed locally before the blinded CPU holdout is revealed,
but no GPU host or provider may start until that CPU holdout passes exactly.
After it passes, freeze source, archive, checkpoint, build-command, binary,
H64, and disjoint-set hashes before the first CUDA result.

Required remote gates, in order:

1. clean Linux CPU build reproduces the exact stream/checkpoint and complete
   CPU masks;
2. CUDA selftest passes;
3. Linux CPU and CUDA masks match byte-for-byte on all H64 rows;
4. Linux CPU and CUDA masks match byte-for-byte on the predeclared disjoint
   holdout after its CPU verdict is sealed;
5. wrong operation count, wrong checkpoint, and incomplete-screen-plus-mask
   negatives all fail closed;
6. protected host state is identical before and after, with no GPU process
   left running.

Any mismatch kills activation.  Passing parity still does not authorize a
range, hunt, provider fleet, submission, or public note.  Phase screening or
unchanged trusted confirmation and explicit score-economics gates remain
separate requirements.  Every promoted nonce still needs the unchanged full
9,024-shot evaluator at classical/phase/ancilla `0/0/0`.
