# Odd Power-of-Two Triangular Action Verdict

Verdict: `ADMIT_ODD_POW2_TRIANGULAR_SUBPRIMITIVE`

This admits one exact subprimitive.  It is not a full secp256k1 multiplier and
not a candidate.

## Binding

- Base commit/tree: `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f` /
  `eab2326ce33549eceeb5c10aa64eae33f148b0ac`.
- Protected default diagnostic: Q1266/T911367.14.
- A release rebuild after the default-off implementation emitted 12,596,439
  operations and reproduced compressed operation SHA-256
  `715257aeabdacc03c5a121bc4e1c9bbd563875198728211abbb1a40caeec3184`.
- Exact oracle receipt: `62-odd-pow2-triangular-action-receipt.json`, embedded
  SHA-256
  `c0258c70390014c13964c2bbea50529f4461b13ca9d2be618306e16909ffcd93`.

## Construction

For odd `M`, visit target controls from high to low.  At control `x_i`, add
`x_i * floor(M/2)` into `x[i+1:n]`.  Earlier steps cannot change a later
control before it is consumed, and the total full-word increment is

```text
(M-1) * sum_(i=0)^(n-2) x_i 2^i = (M-1)x mod 2^n.
```

The missing top-bit term vanishes because `M-1` is even.  The inverse visits
the controls low to high and subtracts the same suffixes.

Each suffix first computes clean `x_i AND M_j` sources, uses the existing fast
quantum add/subtract primitive, and measurement-uncomputes the sources.  No
product register is allocated.

## Exact evidence

The independent Python oracle exhausted every odd multiplier and every target
at widths 1 through 9: 174,762 input pairs, zero forward failures, zero inverse
failures, and zero multiplier-preservation failures.

The Rust implementation was exercised through the repository simulator for
every odd multiplier and every target at widths 1 through 7, both forward and
forward-plus-inverse.  Every batch had exact target value, preserved
multiplier, phase zero, and all non-input lanes zero.

The Rust operation census exactly matched these formulas at widths 1, 2, 3,
8, 16, 32, 64, 128, and 256:

```text
AND Toffolis    n(n-1)/2
adder Toffolis  (n-1)(n-2)/2
total Toffolis  (n-1)^2
peak Q          4n-2, n >= 2
```

At 256 bits the exact component price is Q1022/T65025, comfortably inside the
isolated Q1100/T335738.86 replacement envelope.

## Boundary and next obligation

The action computes `M*x mod 2^256`.  The odd lift encodes a nonzero field
element as `M=T` for odd `T` and `M=T-p` for even `T`; interpreting the power-
of-two product as `T*x mod p` still requires an exact reversible
pseudo-Mersenne fold.  Previous one-pass and half-summary receipts prove that
fold cannot be treated as a small causal correction.  The next grammar is an
explicit revisiting `PSEUDO_MERSENNE_NONLOCAL_FOLD`.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
