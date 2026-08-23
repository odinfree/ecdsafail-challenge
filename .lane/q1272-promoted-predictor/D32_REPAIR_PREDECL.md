# Promoted Q1272 D32 causal-repair predeclaration

Date: 2026-08-23

Status: `FROZEN_BEFORE_MODEL_EDIT / SHOT_8729_CAUSE_ISOLATED`.

This correction is predeclared after the committed D32 reveal at `7dc45cc` and
before editing either classical predictor. It addresses only nonce
`66961008849867`, shot `8729`, the sole evaluator-only fault in D32.

## First divergent boundary

A diagnostic simulation of the unchanged exact operation stream and the
predictor's existing boundary trace agree through both coordinate subtractions
and the complete ping-pong divide. They first diverge at `tlm_coord_add3x`:

- restored x before add3x:
  `71845f69b5b1f63031b7bd01dab14f35109f1124cc50a511c82fe13a05e67c66`;
- offset x:
  `dce0860df8404328a9d13cc22c8ccfe6e077883abbb2cba1dadab4ebc7415169`;
- predictor after add3x:
  `0825f1939e72bfaa2f2b73486057bee9b205a9d4ff6907f758c000005baa7c14`;
- circuit after add3x:
  `0825f1939e72bfaa2f2b73486057bee9b205a9d4ff6907f758a000005baa7c14`;
- exact difference: predictor = circuit + `2^53`.

The current predictor uses field addition for this phase. The emitted circuit's
`mod_add_exact` instead performs a 256-bit wrapping add, then, on carry-out,
adds `F = 2^32 + 977` only inside the low 53-bit window. That low-window add
deliberately drops its outgoing carry. On this shot:

- reduced `3 * ox` is
  `96a19229e8c0c979fd73b64685a66fb4a16698b0331862e590901ec555c3fbdd`;
- the 256-bit add carries;
- wrapped low 53 bits are `0x1fffff5baa7843`;
- adding F yields `0x2000005baa7c14`, whose bit-53 carry is dropped.

This exactly explains the observed `2^53` divergence. Later boundary values
then differ transitively; they are not independent repair targets.

## Frozen correction

Add one source-local `coord_add3x_circuit(reg, coord)` value helper to both the
exact Rust model and shared C++ model. It must:

1. compute `3 * coord mod p` exactly;
2. compute `wrapped, carry = reg + reduced_3coord` over 256 bits;
3. if `carry == 1`, replace only bits 0..52 of `wrapped` with
   `(low53(wrapped) + F) mod 2^53`;
4. return every higher bit unchanged.

Replace only the existing field-add expression at `tlm_coord_add3x`. Do not
change the circuit source, width schedule, replay model, square model, Fiat-
Shamir checkpoint, operation count, operation hash, nonce framing, or trusted
evaluator.

## Acceptance gates

- targeted shot 8729 must become a predicted fault with exact circuit boundary
  value after add3x;
- inherited nonce must remain exact at 23/23 complete-mask equality;
- retrospective H64 must remain exact at 1,144/1,144 over all 64 masks;
- retrospective D32 must become exact at 559/559 over all 32 masks;
- shared C++ complete masks must equal the corrected Rust masks;
- a genuinely new, predeclared disjoint holdout must pass before CUDA GO.

D32 is revealed evidence, not a new holdout. Provider compute, scan ranges,
hunting, and submissions remain disabled.
