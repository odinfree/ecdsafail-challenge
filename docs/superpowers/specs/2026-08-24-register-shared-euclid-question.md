# Register-Shared Euclid Architecture Question

Status: `HARD_NACK_DUPLICATE_LITERAL_ROUTE`; changed-premise variants only.

The anti-rot reconciliation in
`docs/superpowers/specs/2026-08-24-register-shared-euclid-reconciliation.md`
found that the literal question had already been answered on promoted ancestors.
Do not run the two-width experiment below unless a new row transition is first
specified that differs from both the current ping-pong recurrence and Luo et
al.'s register-sharing EEA.

## Question

Can a signed Euclid multiply row become injective on reachable state when
augmented only by `O(log n)` length/location metadata, allowing the branch to
be recomputed during reverse traversal without a linear sign tape?

## Required evidence

- Exhaustive reachable-state enumeration at prime widths 31 and 127.
- One width-parameterized metadata formula used unchanged at both widths.
- Every augmented post-row state has exactly one reachable predecessor.
- The reverse row computes its branch from the augmented state and queries no
  external oracle or table.
- A symbolic 256-bit Q/T equation includes metadata update, branch recovery,
  row arithmetic, inverse traversal, zero handling, and scratch cleanup.

## Continue condition

Continue only if every reachable forward row has one predecessor after adding
the declared metadata, the same metadata formula works at both widths, metadata
is `O(log n)`, and the conservative component projection is at most Q1100 and
T335738.86.

## Kill condition

Kill the exact metadata grammar if any collision requires metadata growing
linearly with row count or field width; any reverse row queries an omitted
oracle; any branch record accumulates across iterations; or the conservative
256-bit component exceeds Q1100 or T335738.86.

## Exclusions

- The killed 254-bit reachable-fiber rank and its exponential count oracle.
- The 796-scratch direct-centered sidecar and its 117-bit branch tail.
- The Q1150/T628k TrailMix lifecycle with a temporary word.
- Arbitrary QROM or truth-table synthesis.
- Production Rust work before the two-width injectivity result.

## Authority

Local reduced-width research only. Provider, nonce, push, public-note,
promotion, and submission gates remain closed.
