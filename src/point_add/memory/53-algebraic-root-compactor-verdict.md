# Algebraic-Root Curve Compactor Verdict

Verdict: `HARD_NACK_ALGEBRAIC_ROOT_COMPACTOR`

## Binding

- Base commit/tree: `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f` /
  `eab2326ce33549eceeb5c10aa64eae33f148b0ac`.
- Current diagnostic: Q1266/T911367.14, operation SHA-256
  `715257aeabdacc03c5a121bc4e1c9bbd563875198728211abbb1a40caeec3184`.
- Current square: T54876.89.
- Conservative replacement ceiling: T335738.86.
- Exact receipt: `52-algebraic-root-compactor-receipt.json`, embedded
  SHA-256
  `f73eea6d80e7737dbea2d718207689aa1d773d9b9feb5e52e15a1b18f91e0156`.

## Exact equivalence

On all 391 enumerated curve-supported states at p=31, 127, and 251, the
required product output satisfies

```text
X = a-T
Y = T*lambda-b
Y^2 = X^3+7 = (a-T)^3+7.
```

Root identity, output equality, inverse slope recovery for nonzero `T`, and
paired-root sign checks all have zero failures. Each `T` has at most two output
roots. A one-word-plus-branch compactor is therefore exactly a point
decompressor: the branch selects one of the two square roots, and the inverse
recovers `lambda=(Y+b)/T`.

## Rational decoder

The cubic `(a-T)^3+7` is squarefree in the tested characteristics and has odd
degree three. It is not a square in the rational function field, so a symbolic
branch-selected rational function of `T` cannot decode the ordinate on an open
curve family.

Verdict: `HARD_NACK_RATIONAL_ROOT_COMPACTOR`.

## Addition-chain decoder

For secp256k1, the ordinary root exponent `(p+1)/4` has bit length 254. Any
addition chain from exponent one needs at least 253 field multiplications.
Pricing every multiplication as the cheaper current square—and omitting all
branch extraction, routing, general products, and cleanup—already costs
T13883853.17, 41.353 times the entire replacement ceiling.

Verdict: `HARD_NACK_ADDITION_CHAIN_DECOMPRESS`.

This is not a universal square-root circuit lower bound. It closes rational
one-word decoding and monomial addition-chain decompression with the current
arithmetic floor.

## Next grammar

The only remaining affine-shell grammar is `DIRECT_UNIT_ACTION`: implement the
destructive permutation `lambda <- T*lambda mod p` itself with no third field
word and no linear history. Further curve-support feature fitting is closed as
autoresearcher rot.

## Authority

Provider, nonce-grind, push, public-note, promotion, and submission authority
remain false.
