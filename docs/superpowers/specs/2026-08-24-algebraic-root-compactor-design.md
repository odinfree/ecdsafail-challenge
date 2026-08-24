# Algebraic-Root Curve Compactor Gate

Status: approved by the autonomous structural-cut mandate; exact local proof
and cost falsifier only.

## Compactor hypothesis

The exact curve support shows at most two legal slopes per `T`. A proposed
one-word-plus-branch representation would compact

```text
(T, lambda) -> (T, branch)
```

and decode the standard output ordinate without performing the mixed product.
The decoder obligation must be stated explicitly.

## Algebraic identity

For the required output

```text
X = a - T
Y = T*lambda - b,
```

curve correctness gives

```text
Y^2 = (a-T)^3 + 7.
```

Thus the branch bit chooses one of the two square roots of the cubic radicand.
Conversely, for nonzero `T`, a selected root recovers

```text
lambda = (Y+b)/T.
```

A clean compactor/decompactor is therefore a point-decompression circuit, not
free entropy deletion.

## Rational obstruction

Over a symbolic field of characteristic other than 2, 3, or 7, the polynomial

```text
R(T) = (a-T)^3 + 7
```

has odd degree three and is squarefree: its derivative can share a root only at
`T=a`, where `R(a)=7` is nonzero. It is not a square in the rational function
field. No branch-selected rational function of `T` can therefore be a symbolic
square root on a Zariski-open curve family. Finite-field lookup interpolation
is outside this grammar.

## Addition-chain price gate

For secp256k1, `p mod 4 = 3`, so the standard root on quadratic residues is

```text
z^((p+1)/4).
```

The exponent has bit length 254. In any ordinary addition chain starting from
exponent one, one field multiplication can at most double the largest available
exponent, so at least 253 field multiplications are required. Price every one
at the current square cost T54876.89—an optimistic relaxation that treats all
general multiplications as squares and omits branch extraction, routing, and
cleanup.

## Binding

- Base commit/tree: `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f` /
  `eab2326ce33549eceeb5c10aa64eae33f148b0ac`.
- Current diagnostic: Q1266/T911367.14, operation SHA-256
  `715257aeabdacc03c5a121bc4e1c9bbd563875198728211abbb1a40caeec3184`.
- Current square: T54876.89.
- Conservative replacement ceiling: T335738.86.

## Exact path and controls

- Exhaustively verify the root identity, output equality, inverse slope
  recovery, and paired-root sign relation at p=31, 127, and 251.
- Verify the cubic is squarefree at every selected field.
- Verify the secp exponent, bit length, lower bound, relaxed T price, and budget
  ratio deterministically.
- Retain all support hashes and zero failure counts in one receipt.

## Falsifier

Issue `HARD_NACK_RATIONAL_ROOT_COMPACTOR` for the symbolic rational decoder and
`HARD_NACK_ADDITION_CHAIN_DECOMPRESS` if the optimistic addition-chain price
exceeds the replacement ceiling.

These verdicts do not prove a universal lower bound for every square-root
circuit. They close rational one-word decoding and ordinary monomial
addition-chain decompression using the current arithmetic cost floor.

## Authority

Local Python research only. Provider, nonce-grind, fleet, queue, push,
public-note, promotion, and submission authority remain false.
