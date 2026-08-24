# Quotient-Euclid Unit Action

Status: approved for local exact recurrence and transcript-economics analysis on
2026-08-24.

## Question

The odd power-of-two action is cheap, but its pseudo-Mersenne conversion remains
nonlocal.  This route instead changes the exact field action itself.  The
current ping-pong multiplier factors a unimodular action into roughly 696
binary signed steps.  Ordinary Euclid gives a different factorization:

```text
(u, v) = (p, T)
(u, v) <- (v, u - q*v),  q = floor(u/v).
```

If the quotient transcript is `q_0, ..., q_(s-1)`, reverse it from coefficient
state `(lambda, 0)` using

```text
(a, b) <- (q*a + b, a) mod p.
```

The terminal Euclid state is `(1,0)`, so the final coefficient state is
`(p*lambda, T*lambda) = (0, T*lambda) mod p`.  This is an exact in-place field
unit action with a zero companion register; it does not need a power-of-two
fold.

## Why this is a different grammar

The quotient path has about 150 steps for a typical 256-bit denominator, not
696 binary rounds.  Its cost is moved into variable-width quotient digits and
their reversible transcript.  A useful implementation must therefore beat the
binary route after all of the following are priced:

- reversible quotient/remainder production and walk-back;
- a self-delimiting quantum transcript with a fixed production capacity;
- quantum routing between the alternating coefficient registers;
- multiply-add of a quantum quotient into a full field word;
- exact modular canonicalization, phase repair, and transcript cleanup.

No average trace count can substitute for this fixed-circuit accounting.

## Exact first gate

Implement an independent oracle that:

1. produces the canonical positive Euclid quotient list for every nonzero `T`;
2. reconstructs `(p,T)` exactly from terminal `(1,0)`;
3. applies the reverse coefficient recurrence and checks `(0,T*lambda mod p)`;
4. round-trips an Elias-gamma transcript exactly;
5. exhausts every `(T,lambda)` at prime widths 5 through 8;
6. censuses all `T` through width 14 and a deterministic 10,000-element secp
   sample for step count, quotient payload bits, gamma bits, and shifted-add
   area.

The final quotient of a canonical Euclid trace is at least two.  The quotient
payload is expected to stay below the general `2n` continuant envelope, while
the self-delimiting gamma stream is expected near `2.42n` rather than the 696-
bit binary tape at `n=256`.  These are transcript observations, not yet a
compiled circuit bound.

## Decision

- `HARD_NACK_QUOTIENT_EUCLID_RECURRENCE` on any reconstruction, multiplication,
  inverse, or transcript round-trip failure.
- `ADMIT_QUOTIENT_EUCLID_RECURRENCE_ONLY` if all exact checks pass and the
  production sample has fewer quotient steps and payload digits than the live
  696-round binary walk.
- A production circuit remains `HOLD` until a fixed schedule demonstrates its
  actual peak Q and executed T.  In particular, variable loop counts, average
  popcounts, and branch-dependent wire relabeling receive no credit.

The next falsifier is `STATIC_REVERSIBLE_TRANSCRIPT_COMPILER`: either compile a
fixed quotient codec/apply schedule below the Q/T target or show that quantum
routing and padding erase the recurrence advantage.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
