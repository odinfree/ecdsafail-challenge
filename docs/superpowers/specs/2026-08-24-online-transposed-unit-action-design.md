# Online Transposed Unit Action

Status: approved for local exact collision falsification on 2026-08-24.

## New premise

The static quotient compiler is closed because it stores the path and replays
it backwards. Ordinary Euclid also admits a forward, row-transposed action.
For each canonical quotient define

```text
E(q) = [[0, 1], [1, -q]].
```

If `B_T = E(q_0)...E(q_(s-1))`, then the row walk satisfies

```text
(p,T) B_T = (1,0).
```

After normalizing the product-column sign, its columns have the exact form

```text
B_T = [[-r_T, T], [k_T, -p]],
k_T*T - r_T*p = epsilon_T,  epsilon_T in {-1,+1}.
```

Therefore the coefficient row can consume each live quotient immediately:

```text
(lambda, 0) B_T = (-r_T*lambda, T*lambda) mod p.
```

The desired product appears without a reverse quotient tape. The remaining
question is whether the cofactor word can become the preserved multiplier
without hiding the same division in cleanup.

## First grammar

Allow the second seed component to be any function `h(T)` that is prepared
without using `lambda`. This is deliberately more generous than a constant or
low-degree seed. Modulo `p`, the online action produces

```text
g = -r_T*lambda + k_T*h(T)
z =  T*lambda.
```

For fixed `T`, varying `lambda` traces an affine line in `(g,z)` with direction
`(-r_T,T)`. The choice of `h(T)` moves the intercept but cannot change that
direction.

The complete two-register transducer must be injective on all nonzero `T` and
all `lambda`. Thus the `p-1` fixed-`T` lines would need to be pairwise disjoint.
In an affine plane over a field, two nonparallel lines intersect. The grammar
can survive only if every direction ratio `-r_T/T` is identical; equal or
coincident parallel lines must also receive distinct intercepts.

## Exact gate

At primes 31, 61, 127, and 251:

1. reconstruct `B_T` by the literal quotient row recurrence;
2. prove `(p,T)B_T=(epsilon_T,0)` and
   `k_T*T-r_T*p=epsilon_T` after product-sign normalization;
3. check `(lambda,0)B_T` yields the exact product for every `(T,lambda)`;
4. enumerate the direction ratios and exhibit two nonparallel fixed-`T`
   families;
5. independently replay intersections for representative seed families;
6. verify the alternative final-quotient expansion changes only the cofactor
   representative/sign and does not remove the line-intersection obstruction.

## Decision

- `HARD_NACK_ONLINE_TRANSPOSED_SEPARABLE_SEED` if two distinct direction
  ratios occur. That is an exact all-`h(T)` collision proof for this grammar.
- `ADMIT_ONLINE_TRANSPOSED_SEPARABLE_SEED` only if the directions are all
  parallel and a scalable distinct-intercept construction is explicit.

The NACK does not cover a seed `s(T)*lambda+h(T)`. Such a coupled seed can
rotate each line, but preparing the exact cancellation
`s(T)=r_T/k_T + constant*T/k_T` is itself a variable product with Euclidean
cofactors. That is the next grammar only if its production and cleanup are
specified without circularly assuming the desired in-place multiplier.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
