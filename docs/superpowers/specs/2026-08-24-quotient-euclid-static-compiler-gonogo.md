# Quotient-Euclid Static Compiler Go/No-Go

Status: `NO_GO_RAW_OR_SELF_DELIMITING_TRANSCRIPT` on 2026-08-24.

## Current gate

The direct transducer admits at most Q1100 total, including its two 256-bit
inputs, and T335738.86. It also forbids a branch, quotient, or path transcript
whose size grows linearly with the arithmetic path.

The exact recurrence receipt observes, among 10,000 deterministic secp256k1
denominators:

```text
max quotient payload = 355 bits
max gamma stream     = 548 bits
max quotient count   = 186
```

A replay partner is a mandatory 256-bit field word. Even granting zero parser
ancilla and letting every trace use the observed rather than proven worst
case, the two direct layouts peak at:

```text
inputs + partner + raw payload   = 512 + 256 + 355 = Q1123
inputs + partner + gamma stream  = 512 + 256 + 548 = Q1316
```

Both exceed Q1100. Both are also linear path transcripts, independently
violating the structural fingerprint.

## Historical rebinding

Repository history already charged the standard objections against an older,
looser scratch-600 / 3M-Toffoli campaign:

- `f6fc46c465bef21aa157ad9f54917f2b2f07fc8e`: ordinary quotient payload plus
  one partner reached 616 scratch qubits before self-delimiting parsing;
- `ec4d5d0`: empirical prefix-code history reached about 518 bits before its
  partner and decoder;
- `13fe1be`: replay by recomputing Euclid prefixes from the live input had an
  optimistic mean weight above 8.7 million;
- `192bc54`: a rank decoder for raw centered quotient concatenation was dense;
- `0721c17`: a fixed 256-shift scan per quotient was gate-dead even at one
  Toffoli per bit trial;
- `c1aea55`: the remaining packed extractor margin could not afford a generic
  alignment barrel;
- `6232c5e` and `7067522`: half-GCD checkpoint state plus its tail exceeded
  scratch, while measuring the checkpoint induced a dense phase function.

Those commits are archaeological evidence, not current candidate receipts.
Their assumptions are conservative for this gate: the current route gets one
Q1100/T335738.86 component, not a relaxed Q2800/3M point-add envelope.

## Decision

`HARD_NACK_QUOTIENT_EUCLID_STATIC_TRANSCRIPT_COMPILER` applies to:

- a raw concatenated quotient tape;
- Elias-gamma or another self-delimiting linear tape;
- a fixed scan over every quotient position;
- naive prefix recomputation;
- the already-tested rank-decoder, MBUC, and half-GCD checkpoint escapes.

The exact recurrence remains mathematically admitted, but no longer owns the
implementation ball. Reviving it requires a new premise: an online
transposition that absorbs quotient information into the two output words and
cleans it without a linear tape, dense decoder, or third persistent field
word.

Provider, nonce-grind, fleet, queue, push, public-note, promotion, and
submission authority remain false.
