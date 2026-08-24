# Odd-Lift Half-Word Summary Gate

Status: approved for local exact falsification on 2026-08-24.

## Question

The one-pass odd-lift correction is closed. The next narrow construction is a
two-pass fold: inspect one half of the odd-lifted word `w`, retain a small clean
summary, then overwrite that half while emitting the other half of
`y=T*lambda mod p`.

At a balanced cut, a deterministic clean transducer state must distinguish all
different required output halves compatible with the same `T` and the same
visible half of `w`. The base-two logarithm of that diversity is therefore a
state lower bound for this exact two-pass grammar. This is a communication
bound on the named schedule, not an ancilla lower bound for arbitrary nonlocal
circuits.

## Exact toy census

For every nonzero `T` and every field `lambda`, compute the odd lift and target
exactly as in `2026-08-24-odd-lift-prefix-stream-design.md`. At cut
`k=floor(n/2)`, report:

```text
D_low  = max |{ y mod 2^k : fixed (T, w mod 2^k) }|
D_high = max |{ floor(y/2^k) : fixed (T, floor(w/2^k)) }|.
```

The required summary sizes are `ceil(log2 D_low)` and
`ceil(log2 D_high)`. The unreduced identity target `y=w` is the positive
control and must require zero summary bits. Widths 5 through 11 are required.

## Exact secp256k1 certificate

Let

```text
R = 2^256
B = 2^128
c = R-p = 2^32+977
T = B.
```

Because `T` is even, its odd signed lift has word `M=B+c`. Write
`lambda=l+B*h`, with `0<=l,h<B`.

### High half to low output

Choose `l=0` and all `h` in `[0,B)`. Every `lambda=B*h` is below `p` because
`B>c`. Then

```text
w mod B = 0
y mod B = c*h mod B.
```

Since `c` is odd, multiplication by `c` permutes all `B` low-half words.
Therefore `D_low=B` and any summary needs at least 128 bits.

### Low half to high output

For every `l`, put `q=floor(c*l/B)` and choose the unique

```text
h = -c^-1*(l+q) mod B.
```

Expanding `(B+c)*(l+B*h) mod B^2` shows `floor(w/B)=0`. At most `c` of these
`B` pairs lie in the excluded interval `[p,R)`, leaving at least `B-c` legal
field inputs.

For a legal pair, write `j=floor(c*h/B)`, so `0<=j<c`. Before the single
possible pseudo-Mersenne correction, the high half of `B*lambda` is `l+j`.
Subtracting `p=B^2-c`, when required, subtracts `B` from that high half and can
add at most one carry from adding `c` to the low half. Thus for every final
high word `H`,

```text
H = l+j+delta mod B,  0<=j<c, delta in {0,1}.
```

Each `H` has at most `c+1` compatible values of `l`. Hence

```text
D_high >= ceil((B-c)/(c+1)),
summary_high >= ceil(log2 D_high) = 96 bits.
```

The executable certificate must recompute all constants, inequalities, and
bit bounds with integer arithmetic; no enumeration of the production domain
is required or permitted.

## Decision

- `HARD_NACK_ODD_LIFT_HALF_SUMMARY` if the positive controls pass, the exact
  toy census reaches the balanced-half ceiling in both directions at every
  tested width, and the production certificate proves bounds 128 and at least
  96 bits.
- Otherwise `INCONCLUSIVE`.

This rejects a sublinear retained summary for the named two-pass half-word
overwrite. It does not reject circuits that keep both halves live, revisit
them nonlocally, or use a different arithmetic factorization. No provider,
nonce, fleet, queue, push, public-note, candidate, or submission authority is
created.
