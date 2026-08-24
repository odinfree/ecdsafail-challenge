# Ping-Pong Sign-Tape Codec / Regeneration Gate

Status: approved for two bounded experiments. No circuit integration is
authorized until both gates admit.

## Objective

Remove at least 40 resident bits, plus codec controls, from the 696-bit
division sign tape while preserving the exact shipped walk/replay map. The
first useful tier is Q1169 with diagnostic `T <= 888324`; the campaign target
is score at most 1,038,451,438.

## Exact recurrence under test

Let `p = 2^256 - 2^32 - 977` and let the input denominator be `a`.
The fused first round records `a0 = a mod 2`, leaves `u = p`, and maps `v` to

```text
floor(a/2) - p + a1*p + a0*(p+1)/2,
```

where `a1 = floor(a/2) mod 2`. Every later round alternates the target register,
records `s = target[1] XOR source[1]`, and maps

```text
target <- (target + (-1)^s * source) / 2.
```

All integers are represented in the scheduled signed two's-complement width.
The production model is admissible only after its tape matches the real
gate-level simulator bit-for-bit on deterministic lanes, including both input
parities and marginal width cases.

## Experiment 1: reachability and information gate

1. Add a default-off diagnostic that extracts the real `value_walk` tape from
   the 64-lane simulator without changing the shipped stream.
2. Cross-check the recurrence above against every extracted bit.
3. Exhaust complete toy domains for odd primes of widths 5 through 12.
4. Measure deterministic secp256k1 samples at fixed block positions for block
   widths 4, 8, 12, and 16, plus terminal suffixes through width 32.
5. Report distinct support, `ceil(log2 support)`, input collisions, and the
   best possible resident saving before decoder gates.

Admit only if an exact support proof, or a production construction independent
of sample coverage, saves at least 40 resident bits. Sample-only missing words
are evidence for selecting a grammar, never an exact codec certificate.

Falsifier: full support at every fixed local block, or an information lower
bound above 656 bits for every tested streaming partition, closes the local
block codec family.

## Experiment 2: reversible decode and timing gate

For an admitted support, synthesize or explicitly construct forward and inverse
maps, prove injectivity on the complete reachable support, and schedule decode
so the raw signs do not coexist with the full code at the terminal peak.
Measure:

- maximum simultaneously resident code, raw, control, and scratch bits;
- emitted and executed Toffoli delta on the actual call count;
- exact forward/inverse state, phase, and ancilla cleanup;
- diagnostic Q/T and score against the untouched baseline.

Admit only if the measured stream clears a target tier. A lookup table, an
unpriced oracle, or a decoder whose code and raw block coexist above Q1266 is a
hard NACK.

## Anti-rot stop rule

There are exactly two experiments. After reachability and decode timing, the
lane must end in `ADMIT`, `COMPLETE`, or `HARD_NACK`. A new grammar requires a
new design receipt and may not silently extend this search.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
