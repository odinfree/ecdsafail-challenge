# Overlapping Product-Code Gate

Status: approved for local exact falsification on 2026-08-24.

## Question

Independent digit windows are closed. The next controlled-constant grammar
allows overlapping conjunctions of `T` bits:

```text
F(T) = C_empty * product_(nonempty S) C_S ^ AND(T_i for i in S) mod p.
```

The direct action would apply the corresponding fixed in-place constant
multiplier whenever conjunction `S` is true. This is the canonical
multiplicative Boolean expansion; overlaps and controls of every order are
allowed. The question is whether the exact secp multiplier has a sparse
expansion on even a small production subcube.

## Unique coefficient transform

On an `m`-bit Boolean cube, every nonzero function has a unique expansion of
this form. If `f(U)` denotes the value at mask `U`, its coefficients are the
multiplicative Mobius transform

```text
C_S = product_(U subseteq S) f(U)^((-1)^(|S|-|U|)) mod p.
```

Equivalently, start with the complete value table and, for every bit, divide
each set entry by the corresponding unset entry. Re-zeta-transforming the
coefficients must reproduce every original value.

## Production subcube

Fix context `b=2^255` and let the lowest 19 bits vary:

```text
f(mask) = b + mask,  0 <= mask < 2^19.
```

Every value is nonzero and below secp256k1 `p`. Compute the exact 524,288-entry
Mobius transform using one batch inversion per transform layer. Record every
coefficient, the nonidentity count, a canonical digest, and an exact inverse
zeta reconstruction check.

The predeclared falsifier is 524,287 nonidentity coefficients on nonempty
subsets. That forces the literal controlled-factor grammar to carry an
exponential family already on 19 input bits, violating the transducer's
no-exponential-table fingerprint before circuit pricing. This is not converted
into an executed-Toffoli lower bound: condition-stack probabilities and
cross-factor circuit synthesis are deliberately not assumed.

## Controls

At toy widths, test context plus every available low bit and require exact
forward/inverse transforms. A sparse synthetic product with a declared set of
nonidentity coefficients must recover exactly that set after transform. The
production transform must be deterministic under repeated execution.

## Decision

- `HARD_NACK_OVERLAPPING_PRODUCT_CODE` if the production subcube has all
  524,287 nonempty coefficients nonidentity, reconstructs exactly, and all
  toy and sparse controls pass.
- Otherwise `INCONCLUSIVE`.

This closes the literal factor-by-factor multiplicative Mobius grammar. It
does not reject arithmetic synthesis that jointly realizes many coefficients,
a non-Boolean representation of `T`, or the original Euclidean unit action.
No provider, nonce, fleet, queue, push, public-note, candidate, or submission
authority is created.
