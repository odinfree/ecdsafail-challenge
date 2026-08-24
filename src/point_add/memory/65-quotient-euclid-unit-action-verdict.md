# Quotient-Euclid Unit Action Verdict

Verdict: `ADMIT_QUOTIENT_EUCLID_RECURRENCE_ONLY`

This admits an exact field-action recurrence and its classical transcript
codec. It is not a compiled reversible circuit and not a candidate.

## Binding

- Frozen base commit/tree: `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f` /
  `eab2326ce33549eceeb5c10aa64eae33f148b0ac`.
- Oracle implementation commit/tree:
  `e843705a64728ae8d5b103888eed24a704089882` /
  `160d80b019aa23b8db2ee5ab2486f707e07b3f7e`.
- Full reproducible gate payload SHA-256:
  `1e54f3a15f98d56c71db2c92d39e5b0043a65e5834c90f037bb292844a975910`.
- Summary receipt: `64-quotient-euclid-unit-action-receipt.json`.

## Exact construction

Ordinary Euclid maps `(p,T)` to `(1,0)` with positive quotients `q_i`:

```text
(u,v) <- (v, u-q_i*v).
```

Starting from `(lambda,0)`, visit those quotients in reverse and apply

```text
(a,b) <- (q_i*a+b, a) mod p.
```

The continuant recurrence reconstructs `(p,T)`, so the final state is exactly
`(p*lambda,T*lambda) = (0,T*lambda) mod p`. Applying
`(A,B) -> (B,A-q_i*B)` in forward quotient order recovers `(lambda,0)`.

## Exact evidence

The independent oracle exhausted 83,342 `(T,lambda)` pairs across prime fields
31, 61, 127, and 251. Forward value, inverse value, and zero-companion checks
all had zero failures. Every denominator at widths 5 through 14 reconstructed
its inputs exactly, ended with a quotient at least two, and round-tripped the
Elias-gamma codec with zero failures.

On a deterministic 10,000-element secp256k1 sample:

```text
metric                    min       mean       p95       max
quotient steps            113     150.0185     166       186
quotient payload bits     319     337.4212     345       355
gamma transcript bits     499     524.8239     534       548
shifted-add terms         195     224.5499     238       259
```

All observed maxima are below the live binary walk's 696 rounds. These are
transcript measurements, not static circuit prices and not universal bounds.

## Boundary and next obligation

The decisive problem is now `STATIC_REVERSIBLE_TRANSCRIPT_COMPILER`. A scored
circuit must provision a fixed worst-case tape, produce and erase each quantum
quotient reversibly, route the alternating coefficient pair without free
branch-dependent relabeling, and execute the multiply-adds at a fixed charged
cost. Average step count, quotient popcount, and classical variable loops earn
no score credit.

The route advances only if that complete schedule fits the isolated
Q1100/T335738.86 replacement envelope and preserves exact value, zero phase,
and clean non-input lanes. Otherwise it closes with a compiler-level
`HARD_NACK`.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
