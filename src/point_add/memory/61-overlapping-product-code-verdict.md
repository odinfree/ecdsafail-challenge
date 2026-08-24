# Overlapping Product-Code Verdict

Verdict: `HARD_NACK_OVERLAPPING_PRODUCT_CODE`

## Binding

- Base commit/tree: `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f` /
  `eab2326ce33549eceeb5c10aa64eae33f148b0ac`.
- Current diagnostic: Q1266/T911367.14, operation SHA-256
  `715257aeabdacc03c5a121bc4e1c9bbd563875198728211abbb1a40caeec3184`.
- Exact receipt: `60-overlapping-product-code-receipt.json`, embedded
  SHA-256
  `3c021250a61874392fddf6e4094aad6f2fb791ddd52227b8fc73994c220c427c`.

## Exact production result

The grammar allowed every overlapping conjunction-controlled constant factor:

```text
F(T) = C_empty * product_S C_S^AND(T_i for i in S) mod p.
```

On the exact secp256k1 subcube

```text
T = 2^255 + mask,  0 <= mask < 2^19,
```

all 524,288 values are nonzero and below `p`. Their unique multiplicative
Möbius transform has:

```text
nonempty coefficients       524287
nonidentity nonempty         524287
identity nonempty                 0
inverse reconstruction failures  0
```

The coefficient ledger SHA-256 is
`f628df3f922e4c3018f1216d77390bc81b5eb79044a263d69192ff42a2adcfe8`;
the input-value ledger SHA-256 is
`cb5431e1b881644ccf5d85ea80518f5a5a37b50be9b71b3c9393bc6b2d9ae2aa`.
The transform used one exact batch inversion per layer and its inverse zeta
transform reproduced every value.

## Controls

Toy subcubes at prime widths 5 through 11 all transformed and reconstructed
with zero failures. Separately generated sparse product codes recovered exactly
their declared nonidentity masks, ruling out a transform that merely reports
density for every input.

## Scope

The canonical expansion is unique. Therefore a literal factor-by-factor
schedule needs a nontrivial controlled constant for every nonempty subset of
these 19 active bits, even before the other 237 input bits are allowed to vary.
That is the exponential truth-table family excluded by the transducer
fingerprint.

This is deliberately not presented as a universal gate-count lower bound:
condition-stack execution weights and possible joint synthesis are different
questions. It closes only literal conjunction-factor execution. The next
grammar is `JOINT_ARITHMETIC_UNIT_ACTION`, which must realize many interactions
together through an explicit reversible arithmetic recurrence.

## Authority

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
