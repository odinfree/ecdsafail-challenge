# Curve-Support Online Constant-Seed Verdict

Identity verdict:
`ADMIT_CURVE_SUPPORT_CONSTANT_SEED_INJECTIVITY_TOY_ONLY`

Natural-decoder verdict:
`HARD_NACK_CURVE_SUPPORT_CONSTANT_SEED_NATURAL_DECODERS`

## Exact support result

For orientation-normalized Euclid coefficients,

```text
B_T = [[-r_T,T],[k_T,-p]],  k_T*T-r_T*p=1,
(lambda,c)B_T = (-r_T*lambda+k_T*c,T*lambda mod p).
```

The second word is the required product for every constant seed. For each
classical curve point, collision of two support rows with the same second word
excludes at most one value of `c`, unless their first-word affine functions are
identical.

The exact gate enumerated all 8,210 classical points and 22,943,190 nonzero-T
support states over fields of widths 5 through 12. No unavoidable pair
occurred. The first allowed seed in `0,+1,-1,+2,-2,...` had magnitude at most
10, with zero replay or product failures.

When `p congruent 2 mod 3`, the cube map is a permutation, every output-Y fiber
has one X coordinate, and `c=0` works for every classical point. The tested
`p congruent 1 mod 3` fields have three-coordinate fibers and need the seed as
a branch tag.

This is a reduced-width support-injectivity theorem and a useful architecture
checkpoint. It is not yet a production seed certificate, a full-field
permutation, or a decoder.

## Closed natural decoders

At the first classical point of every field, no constants `A,B,C` satisfy

```text
T = A*g+B*z+C mod p
```

on the complete support. A global affine postdecode is therefore closed.

The literal nonlinear decoder reconstructs `Y=z-b` and a cube root of
`Y^2-7`. For secp256k1, `p congruent 7 mod 9`; inversion of cubing on the
cubic-residue subgroup uses a 253-bit exponent. Binary exponentiation requires
252 squarings. At the source-bound square price, squarings alone cost
T13,828,976.28, or 41.19 times the complete replacement budget, before
non-square multiplies, GLV branch selection, routing, off-support extension,
or cleanup.

## Next obligation

The only live support version is a `GLV_TRIT_TAG_DECODER`: exploit the three
secp256k1 cube-root endomorphism branches and make the Euclid tag select or
transform the correct root without performing the full exponentiation first.
It must also provide a bounded production seed certificate and a phase-clean
off-support permutation extension.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
