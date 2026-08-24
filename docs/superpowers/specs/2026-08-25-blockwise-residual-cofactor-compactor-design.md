# Blockwise Residual Cofactor Compactor Gate

Status: approved for exact identity and natural-codec falsification on
2026-08-25.

## New premise

Let a Euclid prefix have matrix `B` with determinant `epsilon in {+1,-1}`.
Transform the value row and a seed row by the same prefix:

```text
(p,T) B = (u,v)
(lambda,h(T)) B = (x,y).
```

The cross determinant is prefix-invariant:

```text
u*y-v*x = epsilon*(p*h(T)-T*lambda)
        = -epsilon*T*lambda mod p.
```

This is materially different from the repository's older half-GCD checkpoint:
the prefix matrix itself need not be retained or applied to obtain the product.
At residual width `w`, the two determinant products are rectangular `n by w`
rather than full `n by n` products.

The missing obligations are preserving `T`, making the adaptive prefix
reversible, and erasing every residual/code word.

## Natural compiler A: stored prefix

Keep the two-word seed row, shrink the two-word value row to its exact residual,
store the prefix quotients, and allocate one field word for the preserved `T`
before replaying the prefix into the seed row. Grant this compiler impossible
advantages:

- concatenate raw quotient binary payloads with free boundaries and parsing;
- charge no quotient arithmetic, controls, carries, orientation, determinant,
  or cleanup;
- use the exact residual bit lengths, not `2w`.

Its optimistic checkpoint floor is

```text
Q = 3n + bitlen(u) + bitlen(v) + sum(bitlen(q_i)).
```

For all cut widths `w=1..256`, scan the deterministic 10,000-denominator
secp256k1 sample already bound by the quotient-Euclid receipt. The route is
closed if the minimum over cut widths of the worst sampled floor exceeds Q1100.
Elias-gamma is recorded only as a decodable control; it cannot rescue raw.

## Natural compiler B: no prefix code

Apply each adaptive quotient to both rows immediately and keep no code. This is
only a reversible support map if distinct `(T,lambda)` inputs never reach the
same four-word checkpoint.

Exhaustively enumerate all legal inputs for primes 31, 61, 127, and 251 at
every residual cut. Use the cheapest affine seed `h(T)=T`, which also gives the
smallest observed collision count among degree-at-most-eight monomial seeds at
the material cuts. Record exact collisions. A collision closes the literal
code-free adaptive-prefix map; it does not close a map carrying a sidecar.

## Natural compiler C: minimum fiber rank

For each residual key `(u,v,epsilon)`, sort its compatible multipliers and store
the multiplier's rank in that fiber. This uses only
`ceil(log2(max_fiber_size))` sidecar bits and is therefore the strongest natural
replacement for the raw prefix.

At widths 5 through 12, cut at `floor(n/2)`, zero-extend the exact decoder

```text
(u,v,epsilon,rank) -> T
```

to the surrounding binary cube and compute the GF(2) ANF of an alternating-bit
parity of `T`. Degree within one of the input count and constant-fraction
density closes only a literal table/ANF/kickmix decoder and cleanup. It is not a
general circuit lower bound.

## Anti-rot boundary

Prior commits `6232c5e` and `7067522` already found that a half-GCD matrix plus
residual/tail exceeded scratch and that generic measurement cleanup was dense.
The later endpoint/rank series through `3d3c288` tested block support, local
DP horizons, rank payloads, and slot envelopes. This gate earns novelty only
from deleting matrix application via the cross determinant. It must not claim
that continued-fraction rank decoding in general is newly closed.

## Decisions

- Admit `PREFIX_CROSS_DETERMINANT_PRODUCT_IDENTITY` only if every exact product
  check passes.
- `HARD_NACK_STORED_PREFIX_Q_FLOOR` if even the free-parser raw floor exceeds
  Q1100.
- `HARD_NACK_QUOTIENT_FREE_PREFIX_COLLISION` if the code-free checkpoint map
  collides on exact legal inputs.
- `HARD_NACK_ZERO_EXTENDED_RESIDUAL_RANK_DECODER` if the canonical minimum-rank
  decoder has the predeclared dense, high-degree profile.
- Combined verdict:
  `HARD_NACK_BLOCKWISE_RESIDUAL_COFACTOR_COMPACTOR_NATURAL_CODECS`.

The reopen condition is a specific algorithmic residual codec that fits the
Q1100 whole-component envelope, has a phase-clean reversible decoder, and is
priced below the T335738.86 replacement ceiling. Generic lookup, raw history,
and an oracle-supplied rank do not qualify.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
