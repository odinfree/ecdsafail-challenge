# GLV Trit-Tag Decoder Gate

Status: approved for exact linear and linear-fractional decoder falsification
on 2026-08-25.

## Starting point

On exact curve support, an orientation-normalized online Euclid row with a
small constant seed produces an injective pair

```text
(g,z) = (-r_T*lambda+k_T*c,T*lambda).
```

For secp256k1, `p congruent 1 mod 3`. Fix a nontrivial cube root of unity
`beta`. Once `Y=z-b` is known, the possible X coordinates are one orbit

```text
X, beta*X, beta^2*X.
```

The Euclid word `g` is therefore a trit tag among at most three roots. A tag is
not a root carrier: a valid decoder must still create the selected X, hence
`T=a-X`, without the already-dead 252-square exponentiation.

## Gate A: every linear seed plus affine postdecode

Allow the stronger seed

```text
h = A*lambda+B*T+C.
```

Then

```text
g = -r*lambda + A*k*lambda + B*k*T + C*k.
```

If any affine postdecode `T=U*g+V*z+W` exists, then `T` lies in the field span
of

```text
-r*lambda, k*lambda, k*T, k, z, 1.
```

Treat the products `U*A`, `U*B`, and `U*C` as independent coefficients. This
strictly relaxes the actual construction. Exact inconsistency of the relaxed
linear system closes every linear seed with a global affine postdecode.

## Gate B: selected constant seed plus linear-fractional postdecode

For the exact smallest constant seed from the preceding gate, solve for a
nonzero coefficient vector in

```text
T = (A*g+B*z+C)/(D*g+E*z+F).
```

Cross multiplication is the homogeneous linear system with row

```text
(g,z,1,-T*g,-T*z,-T).
```

Full rank six closes every degree-one rational postdecode for that seed. This
does not close higher-degree rational maps or a different nonlinear seed.

## Gate C: GLV orbit identity

For every `p congruent 1 mod 3` test field and its first classical point:

1. find the least nontrivial cube root of unity `beta`;
2. group output curve points by Y;
3. verify every nonzero-X group is exactly closed under multiplication by
   `beta` and has at most three elements;
4. verify `T=a-X` on every tagged row.

This proves the trit interpretation but supplies no root carrier.

## Decision

- `HARD_NACK_LINEAR_SEED_AFFINE_POSTDECODER` if the relaxed feature system is
  inconsistent at every adjacent width.
- `HARD_NACK_CONSTANT_SEED_LINEAR_FRACTIONAL_POSTDECODER` if every selected
  seed system has rank six.
- `ADMIT_GLV_TRIT_INTERPRETATION_ONLY` if every orbit check passes.
- Combined verdict: `HARD_NACK_GLV_TRIT_LINEAR_TAG_DECODER`.

The next grammar is `RATIONAL_EUCLID_TAG_ROOT_CARRIER`: search bounded-degree
rational carriers that turn the Euclid tag itself into one cube root, before
branch selection. It must show a width-stable formula and a complete reversible
Q/T schedule; interpolation or an oracle root is not credit.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
