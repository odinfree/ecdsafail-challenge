# Online Cofactor Product Recurrence Gate

Status: approved for natural-cleanup falsification on 2026-08-25.

## Starting point

The online Euclid row `(lambda,0)` produces

```text
(-r_T*lambda, T*lambda).
```

The ideal coupled construction combines this row with `(0,T^2)`, whose online
image is `(T,0)`. Keeping both transformed rows would expose the desired cross
components `(T,T*lambda)` directly.

## Natural cleanup A: coherent dual row

The Euclid value row uses two 256-bit words. Each independent coefficient row
uses two more. Keeping the product row and the `T^2` cancellation row live
together therefore has the word floor

```text
2 value words + 2 product-row words + 2 cancellation-row words = 6n.
```

At `n=256`, Q1536 exceeds both the component cap Q1100 and the protected
whole-circuit peak Q1266 before quotient extraction, arithmetic carries,
orientation, zero-fiber logic, or cleanup.

## Natural cleanup B: measure the cofactor garbage

With only the product row, the unwanted word is `r_T*lambda`. In the surviving
output frame `(T,z=T*lambda)`, its phase-repair function is

```text
garbage(T,z) = r_T*z*T^-1 mod p.
```

The exact toy gate totalizes unsupported bit patterns to zero and computes the
GF(2) ANF of an alternating-bit parity of this word at adjacent widths. A dense
high-degree phase does not prove every measurement cleanup circuit impossible;
it closes literal ANF/kickmix-style correction and rebinding to the existing
generic in-place-multiply MBUC failure.

## Decision

- `HARD_NACK_COHERENT_DUAL_ROW_Q_FLOOR` from the exact six-word allocation.
- `HARD_NACK_ZERO_EXTENDED_COFACTOR_MBUC` if degree grows to `2n-O(1)` and
  density remains a constant fraction of the `2^(2n)` truth table.
- Combined verdict:
  `HARD_NACK_ONLINE_COFACTOR_NATURAL_CLEANUPS`.

This does not close every fused recurrence. The next grammar is
`BLOCKWISE_RESIDUAL_COFACTOR_COMPACTOR`: stop the online Euclid walk before its
residual pair collapses, and ask whether a bounded residual block can transfer
the missing multiplier information into the required output before the value
row is erased. The predeclared falsifiers are residual-state growth, a tail
transcript linear in `n`, or a cleanup map with the same dense division phase.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
