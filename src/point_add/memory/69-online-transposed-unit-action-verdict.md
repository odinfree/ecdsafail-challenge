# Online Transposed Unit Action Verdict

Verdict: `HARD_NACK_ONLINE_TRANSPOSED_SEPARABLE_SEED`

The online row transposition is exact and removes reverse-order transcript
replay. Its separable cleanup grammar is not injective.

## Exact result

For the Euclid row matrix normalized to place a positive product in its second
component,

```text
B_T = [[-r_T, T], [k_T, -p]],
k_T*T-r_T*p = epsilon_T, epsilon_T in {-1,+1}.
```

The online row `(lambda,0)B_T` produced `T*lambda mod p` for all 83,342 pairs
over fields 31, 61, 127, and 251. Matrix reconstruction and product checks had
zero failures for both the canonical continued fraction and its alternate
final-one expansion.

## Exact collision proof

Giving the second seed the arbitrary value `h(T)` yields

```text
g = -r_T*lambda + k_T*h(T)
z =  T*lambda.
```

For each fixed `T`, this is an affine line in `(g,z)` whose direction is
`(-r_T,T)`. The seed function changes only the intercept. A full-field
two-register permutation would require all `p-1` lines to be disjoint, but any
two nonparallel affine lines over `F_p` intersect for every pair of intercepts.
The exact censuses found 22, 42, 85, and 158 distinct direction ratios at the
four increasing widths. Explicit intersections replayed for zero, one,
identity, and square seed families.

Thus no choice of separable `h(T)`, including an oracle-supplied one, repairs
this grammar. Changing the final continued-fraction expansion leaves the same
direction counts and obstruction.

## Boundary

This does not close a coupled seed `s(T)*lambda+h(T)`. Such a seed can rotate
the line directions, but the exact coefficient needed to align them contains
the Euclidean cofactors. The next gate must show how that coupled term is
produced and erased without assuming the desired variable multiplier, a
linear quotient history, or a dense division decoder.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
