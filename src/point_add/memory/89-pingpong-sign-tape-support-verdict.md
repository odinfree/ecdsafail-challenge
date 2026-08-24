# Ping-Pong Sign-Tape Support Verdict

Exact local-codec verdict: `HARD_NACK_PINGPONG_FIXED_BLOCK_EXACT_CODEC`

Distributional observation: `ADMIT_TERMINAL_SUFFIX_BIAS_SAMPLE_ONLY`

## Circuit binding

The integer recurrence was compared against the actual 64-lane `value_walk`
simulator with exact widths and the approximate round-zero/round-one shortcuts
disabled. All 44,544 sign bits matched. The probe then exhaustively enumerated
the complete nonzero domains for seven primes from 5 through 12 bits.

## Exact local blocks miss the required cut

On the deterministic 100,000-input secp256k1 sample, independent partitions of
the 696-bit tape save at most 0, 1, 7, and 14 information bits for 4-, 8-, 12-,
and 16-bit blocks. This is below the 40-bit terminal floor before controls and
does not move the earlier Q1266 binding operation near round 335.

Larger sampled blocks cannot certify a saving because their observed rank is
capped by the sample count. The exact toy domains show the corresponding
terminal suffix support eventually saturating the full input domain, so the
decoder state grows with the field width rather than remaining a bounded local
code.

## Tail bias is real but is not a candidate

The last 56 bits have only 9,500 distinct words in the deterministic sample,
an observed 14-bit rank and 42-bit apparent saving. This is useful evidence of
late convergence, but it is neither an exhaustive support certificate nor a
decoder.

A cheap constant-tail implementation would need the walk to have reached its
`(+/-1,+/-1)` fixed point by round 656. The same sample leaves 5,595 of 100,000
walks nonterminal there, projecting about 505 bad walks in a 9,024-shot draw.
That is not a nonce-grindable approximation. The existing round-696 tail still
has 48 of 100,000 nonterminal walks, consistent with why the promoted stream
already requires nonce selection.

Experiment 2 is therefore not authorized under the predeclared gate. Reopen
only with a construction-independent support theorem and a reversible decoder,
or with a different equation whose natural state exposes at least 40 clean
wires before the round-335 peak.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
