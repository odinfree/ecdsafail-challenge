# Curve-Support Online Constant-Seed Gate

Status: approved for exact support-injectivity and decoder falsification on
2026-08-25.

## Changed premise

The all-field online Euclid row is collision-prone, but the affine-shell input
is supported on translates of `y^2=x^3+7`. For a fixed classical point
`C=(a,b)`, write the desired output point as `(X,Y)` and

```text
T      = a-X
lambda = (Y+b)/T
z      = T*lambda = Y+b.
```

Normalize the Euclid matrix to orientation `+1`:

```text
B_T = [[-r_T,T],[k_T,-p]],  k_T*T-r_T*p=1.
```

Applying it to the cheap seed row `(lambda,c)`, where `c` is a compile-time
field constant, gives

```text
g = -r_T*lambda+k_T*c
z = T*lambda-p*c = T*lambda mod p.
```

The second word is already the required product. The first word need only tag
the correct `T` on the exact curve support.

## Exact constant-seed certificate

For every classical curve point `C` at primes 31, 61, 127, 251, 509, 1021,
2039, and 4093:

1. enumerate every output curve point `(X,Y)` with `X != a`;
2. group rows by `z=Y+b`;
3. for every pair in a group, solve the single forbidden constant
   `g_i(c)=g_j(c)`;
4. reject an unavoidable collision if both affine functions are identical;
5. choose the first allowed constant in `0,+1,-1,+2,-2,...`;
6. replay the complete support map and require zero collisions and exact `z`.

For `p congruent 2 mod 3`, the cube map is a permutation, so each `z` has one
`X` and `c=0` must suffice. The `p congruent 1 mod 3` cases exercise the
three-root/endomorphism branch.

This admits only reduced-width support injection. It does not prove a bounded
production constant exists, provide an off-support permutation extension, or
decode `T` from `(g,z)`.

## Natural decoder A: affine postdecode

At the first classical point of every test field, solve exactly for

```text
T = A*g+B*z+C mod p.
```

No solution closes only a global affine postdecode.

## Natural decoder B: literal curve decompression

Because `Y=z-b`, recovering `X=a-T` requires a root of

```text
X^3 = Y^2-7.
```

For secp256k1, `p congruent 7 mod 9`. On the cubic-residue subgroup of order
`m=(p-1)/3`, a literal fixed-exponent root uses

```text
e = (m+1)/3,  3e = 1 mod m.
```

Binary exponentiation has 252 mandatory squarings before any non-square
multiply, branch tag, routing, or cleanup. Price those squarings with the
source-bound current square phase `T=54876.89`. If the squaring-only cost
exceeds the complete replacement ceiling `T=335738.86`, close this literal
decoder.

## Decisions

- `ADMIT_CURVE_SUPPORT_CONSTANT_SEED_INJECTIVITY_TOY_ONLY` if every exact
  support row is injective and has the exact second output.
- `HARD_NACK_AFFINE_CONSTANT_SEED_POSTDECODER` if no affine decoder exists.
- `HARD_NACK_CURRENT_SQUARE_CUBIC_DECOMPRESS` if the fixed-exponent
  squaring-only floor exceeds the replacement ceiling.
- Combined natural-decoder verdict:
  `HARD_NACK_CURVE_SUPPORT_CONSTANT_SEED_NATURAL_DECODERS`.

The next changed grammar is `GLV_TRIT_TAG_DECODER`: use the secp256k1 cube-root
endomorphism explicitly and ask whether the Euclid tag can select/transform a
root without first performing full exponentiation. A generic support lookup,
oracle root, or uncharged off-support extension does not qualify.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
