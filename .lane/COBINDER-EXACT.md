# Exact co-binder experiments

Source anchor: `464ea805356a8d7bf06bc5c6c8f23e55683e76ba`

These experiments are independently gated.  Neither is a nonce candidate, and
they may be composed only after each primitive is value-, phase-, and
ancilla-exact and lowers its named local peak.  The dirty Q1277 composition is
architecture evidence only and is not searched.

## D-001: divide split-walk final-carry host

Hypothesis: in the high chunk of `signed_add_wrapping_sigma_split`, the carry
out of bit `n-2` has one semantic consumer: XOR into `target[n-1]`.  Instead of
allocating a clean final carry wire and then copying it, pre-XOR
`source[n-1]` into `target[n-1]` and compute the final majority directly into
that output.  Restore the bit-`n-2` operands before measurement-uncomputing the
earlier ladder.  This removes one high-ladder wire without changing an integer
width or truncating a carry.

Smallest falsifier, registered before source change:

1. Exhaust the Boolean identity for all `(a,b,carry,source_top,target_top)`:
   the hosted output must equal
   `target_top XOR source_top XOR majority(a,b,carry)`, and the lower source
   and sum bits must match the stock ladder.
2. Run the ping-pong primitive self-check with the gate both off and on.  Kill
   on any class, phase, or ancilla mismatch.
3. Trace the exact Q1277 divide owner.  Kill as a peak lever if the
   `pp_div_replay` local maximum does not fall by one.

Measured reveal after the first exact cut: the split-walk owner fell, but a
later replay cell became co-binding at Q1277.  Its frozen live set contains a
127-wire owned chunk ladder plus two replay boundaries.  D-001 therefore
survives as an exact component but cannot move the phase envelope alone.

## D-002: divide replay source-as-carry cell

Hypothesis: one owned carry in each replay chunk can occupy the source bit
that produced it.  A Cuccaro MAJ cell maps `(source, acc, carry_in)` to
`(carry_out, acc XOR source, carry_in XOR source)`; after higher carries are
retired, its UMA inverse restores `source` and `carry_in` and leaves
`acc XOR source XOR carry_in`.  This deletes one clean carry wire while
preserving the boundary for the caller's existing erase.

Smallest falsifier, registered before source change:

1. Exhaust all eight `(source, acc, carry_in)` states through MAJ then UMA.
   Kill unless source and carry-in are restored, the accumulator is the exact
   sum bit, and the hosted value between the cells is the majority carry.
2. Run the full ping-pong point-add self-check with D-002 alone and with D-001.
   Kill on any class, phase, or ancilla mismatch.
3. Census the replay-cell owner.  Kill unless its owned ladder drops from 127
   to 126, and kill the composition as a width lever unless D-001 plus D-002
   lowers the complete `pp_div_replay` envelope.

Measured reveal after D-001 plus D-002: both named allocations fell by one,
but a later 105-bit walk is an exact ladder fit and therefore uses the unsplit
sigma path.  Its 104 clean carries become the next Q1277 owner.  The D-001
Boolean identity applies unchanged to that ladder's final carry; extending the
same divide-only gate is killed if the 32-state miter, full self-check, or local
peak trace changes from the registered D-001 result.

## Frozen D-001/D-002 result on 464ea805

Both Boolean falsifiers passed: D-001 exhausted 32 states with zero mismatch;
D-002 exhausted eight MAJ/UMA states with zero mismatch.  The production
64-lane full point-add self-check passed with D-002 alone and with D-001 plus
D-002: all four ABI registers matched, phase was zero, and every non-ABI qubit
returned to zero.

On the frozen Q1277 architecture receipt, the final exact composition is:

```text
SUB4_SQUARE_TEDDY_SPARSE_TRI_CORR=1
SUB4_SQUARE_TEDDY_SPARSE_SPLIT=1
SUB4_PP_PEAK=1277
SUB4_PP_R1=342
SUB4_PP_R2=625
SUB4_PP_DIV_SPLIT_TOP_CARRY_HOST=1
SUB4_PP_DIV_REPLAY_SOURCE_CARRY=1
```

Its local envelope is `pp_div_replay` Q1276.  Global Q remains 1277 at
`pp_mul_walkback`; `pp_mul_replay` is Q1276.  The profile contains 12,910,210
semantic ops before the 96-op identity tail and 12,910,306 emitted ops after
it.  The last built stream SHA-256 is
`2f0d10347c18b866564cd1398d5aa08bc855f90be4639b8570bba4fc8cb2c9ee`.
Seed zero executed T919,766.53.  Sixteen independent 64-lane profile cohorts
were all `0/0/0` for class/phase/ancilla (1,024 lanes total).

This is a proved local divider cut, not a candidate.  It raises executed T
relative to the old dirty architecture receipt and leaves multiply at Q1277.
No nonce search or trusted candidate evaluation was run.

## M-001: multiply replay-boundary host or deletion

Hypothesis: one multiply walkback replay boundary may be hosted in a wire that
is clean at boundary creation and restored before its next semantic use, or
deleted if its exact producer state remains reconstructible at erase time.

Smallest falsifier, registered before source change:

1. Inventory allocation, first write, all reads, erase, and next use for the
   proposed host.  Kill if the host is not known clean at creation or is not
   restored exactly before its next use.
2. Exhaust the boundary primitive over the smallest complete producer chunk,
   including phase repair and all ancilla outputs.  Kill on any value, phase,
   or ancilla mismatch.
3. Trace `pp_mul_walkback`.  Kill as a peak lever if its Q1277 owner does not
   fall.  Separately trace `pp_mul_replay`, already Q1276, because moving only
   walkback cannot establish a global Q1275 stream.

## M-002: multiply transcript-state deletion

Hypothesis: one stored walkback decision is a deterministic function of the
remaining transcript and replay state at every later read and can be rebuilt
outside the binding instant.

Smallest falsifier, registered before source change:

1. Enumerate the smallest state slice containing one proposed deleted bit.
   Kill on two reachable histories with identical retained state and different
   deleted bits.
2. Require exact rebuild and erase with no co-resident replacement wire at the
   Q1277 instant; otherwise the live-set cut is zero.
3. Run value/phase/ancilla self-checks and trace both multiply phases as in
   M-001.

## Multiply outcome and live-frontier pivot

M-002 is killed: reachable retained replay/walk states collide with opposite
candidate transcript signs, so deletion is not a function of the retained
state.  An independently isolated M-001 MAJ/UMA source-host prototype exists,
but the live frontier pivot stopped it before compilation or simulation; it is
unverified and is not composed here.

During this experiment the public frontier advanced to exact source
`087cafaef46a4e339644a6191ff2df2e7031cb80`, Q1275, rounded T918972, score
1171689300.  Source `087cafa` is the accepted 940e34a-based four-default
co-binder cut, not a descendant of this lane.  The 464ea805 result is frozen as
transfer evidence only.  Any new measurement starts from an isolated exact
087cafa worktree and targets either a strict same-Q T beat or a real Q1274 cut.
