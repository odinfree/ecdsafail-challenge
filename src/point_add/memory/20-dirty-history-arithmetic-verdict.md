# Dirty-history arithmetic: exact but economically dominated

## Verdict

`HARD_NACK` for the tested vented dirty-history arithmetic architecture on the
bound source.  Already-live sign-history qubits can replace clean carry ladders
without changing value, phase, or ancilla semantics, but restoring arbitrary
dirty history costs far more Toffoli than the score ceiling permits.  After the
carry ladders move, the raw 694-sign history beside the two 256-bit coefficient
words is itself the next wall.

This closes the tested `iadd_dirty_2clean_*` composition.  It is not a lower
bound against a new dirty-workspace cell or a history representation shorter
than the raw sign tape.

## Binding

- Official source commit:
  `67524171baaf568dc3dc606f38515745f70804ff`
- Official source tree:
  `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`
- Research parent before prototype: `bc5cd33e02940885e963200f9c202cf08b00fca5`
- Prototype commit: `3a00a61` (`research: prototype dirty-history arithmetic`)
- Prototype source-diff SHA256:
  `3ffc6ce0d01336b98da737dd747ad7f29ec2cd95d5d8d1d8e89ea532d23aad2f`
- Revert commit: `255b9dd` (`Revert "research: prototype dirty-history arithmetic"`)
- Activation environment: `SUB4_PP_DIRTY_HISTORY_ARITH=1`

The prototype used the existing exact vented quantum-offset and controlled
constant cells.  Every borrower received raw tape wires excluding the sign
currently used as a control, and every borrowed bit was required to return
bit-for-bit with phase zero.

## Exact results

The unrestricted exact composition completed the 64-lane full point-add
selfcheck:

```text
Q1233
T64=2271655.83
classical=0
phase=0x0
dirty=0
```

Transcript SHA256:
`6eaa25639187a6d12548eb9bfa45f8a986d78a15aa40f61a97e2aab2bb233662`.

A second implementation pass activated dirty borrowing only when the projected
clean allocation would exceed Q1233.  It also completed the full selfcheck:

```text
Q1234
T64=1871482.19
classical=0
phase=0x0
dirty=0
```

Transcript SHA256:
`2e51c24ab3719035adf37cbc30c0b79852a2f9bfd8ddeb1986853fba06f2a5ca`.

At Q1234 the live score permits at most T935762.  The targeted prototype is
therefore over the live-score T ceiling by 935720 and has diagnostic product
`1234 * 1871482 = 2309408788`.  A trusted 9,024-shot evaluator is unwarranted.

## Next owner equation after clean carries disappear

The unrestricted B0 censuses exposed the new wall.

Division terminal replay:

```text
694 raw history
256 numerator
256 coefficient
 21 phase-comparison carry
  6 endpoint/ABI flags
----
1233
```

Multiply terminal replay has the same 694 raw history and 512 coefficient/ABI
words; its sampled exact peak is Q1230.  Thus even a hypothetical zero-cost,
zero-width replacement for the main add ladders leaves 1206 semantic qubits
before correction flags.  The earlier Q1203 admission target cannot be reached
by carry borrowing alone.

## Changed-premise reopen

Reopen only with at least one of:

1. a lossless state-conditioned history representation that removes raw signs
   while decoded scratch is live;
2. a coefficient recurrence that does not co-reside as two full field words;
3. an exact dirty arithmetic cell whose complete circuit delta fits the Q/T
   ceiling, not merely its allocation count; or
4. a fused affine/multiply architecture that removes this terminal replay.

No provider, nonce, fleet, queue, push, public-note, or submission action was
taken.
