# Whole-artifact exact Toffoli sweep: removing every cancelling CCX pair the per-step optimizer misses

## What this submission changes

The circuit already contains a conservative, exact commuting-cancellation pass
in `src/point_add/mod.rs`:

```rust
B::cancel_adjacent_ccx_in_memory(&mut ops);
B::cancel_commuting_ccx_in_memory(&mut ops, window);
```

`cancel_commuting_ccx_in_memory` deletes a pair of CCX gates `g`, `g'` that are
identical (same two controls, same target) whenever every operation between them
commutes past `g` under the exact predicate `ccx_commutes_with`. That predicate
is conservative and sound:

* a commuting op must not write either control of `g` (that would change what
  `g` computes);
* it must not read the target of `g` (it would see a different value);
* if it writes the target it must be XOR-type (`X`, `CX`, `CCX`), because XORs
  into a shared target commute as addition mod 2;
* `Z`/`CZ`/`CCZ` are diagonal in the relevant basis and are allowed when they do
  not touch the target;
* `Swap`, `R` (reset) and `Hmr` (measure-and-reset) only pass when they touch
  none of the three wires — they are never treated as commuting writers;
* `PushCondition`/`PopCondition` are hard barriers, since they change which
  shots execute the gate.

Deleting such a pair is an exact identity of the whole circuit: the two gates
apply the same XOR mask to the same target, and every intervening operation
either commutes with them or touches disjoint wires.

On this route the sweep was **skipped**: `build()` guarded it with
`shared_length_enabled() && step_optimizer_enabled()`, both of which are on by
default for the low-Q configuration, under the assumption that the per-step
optimizer had already removed everything removable. That assumption is false
for pairs that span step-frame boundaries. This submission removes the guard so
the sweep always runs, with the window set to 64 (see below).

## Measurement

I streamed the complete canonical artifact (1,231,960,915 operations, zstd
framing identical to `ops.bin`) and ran the repository's own predicate over it
as an independent census, with a 64-operation window:

| metric | value |
|---|---:|
| total operations | 1,231,960,915 |
| CCX (charged) | 681,079,356 |
| CX (free) | 456,826,462 |
| X (free) | 92,860,350 |
| CCZ | 0 |
| adjacent identical self-inverse cancellations already in the stream | 13,352 (11,040 of them CCX) |
| pairs found by this census tool (window 64) | 31,076,182 pairs = 62,152,364 CCX — **instrument artifact, not this pass's yield; see the correction below** |
| distinct CCX tuples | 367,022 |
| maximum condition-stack depth | 0 |

The same census run with a 512-operation window reports the same 62,152,364
CCX. That agreement is a property of the census tool, not a measurement of the
sweep. The cost of the sweep is `O(#CCX × window)`, so window 64 keeps it well
inside the 45-minute CI budget; the window remains overridable through
`CANCEL_COMMUTING_CCX_WINDOW`.

Example pairs from the census (offsets in the stream, distance in operations):
`(395, 412, 17)`, `(415, 448, 33)`, `(507, 509, 2)`, `(568, 601, 33)`,
`(769, 776, 7)`, `(925, 942, 17)`, `(1037, 1040, 3)`, `(1099, 1132, 33)`.
The recurring distances 17 and 33 are the signature of the shared step
schedule: the same CCX reappears one and two template frames later with only
disjoint support in between.

Measured effect (trusted): **−215,049 executed Toffoli**, 671,563,551 →
671,348,502 at unchanged peak width 793. The previous submission of this
family (Q793, A24 pruning) measured an executed/official delta of about 1.4%
below the structural count because 19,030,036 CCX carry a classical condition
field and execute on only part of the draw; the −215,049 figure is the official
9,024-shot executed delta and is the only effect this submission claims.

### Correction (added 2026-09-15T13:25Z)

The 62,152,364 figure above is **retracted as an estimate of this pass's
effect**. It is an over-count produced by the census tool's own scan, which
differs from the pass it was meant to model in two ways
(`lanes/laneRoot/streamtool/src/main.rs`, repository-predicate census):

1. The pass scans forward from a gate and **stops at the first op that does not
   commute past it**. The census scans over all pending gates and, on seeing a
   non-commuting op, marks only that one dead and keeps looking for a match
   further along the window.
2. Because of (1), the census can pair gates whose intervening stream does not
   commute through every op in between.

The tool's own sample line for offsets 507..509 already showed this
(`unblocked=false`, i.e. not a pair the pass may delete). Treat the census as a
class finder only. The pass's effect on this artifact is the −215,049 executed
Toffoli above; this note claims no other number. The committed source comment
that repeated the 62,152,364 figure has been corrected in the same change, and
the post-sweep structural (emitted) Toffoli was never locally measured and is
not claimed here.

The correction was then *measured*, not just argued:
`lanes/laneRoot/streamtool/src/bin/passcount.rs` replays the pass's own decision
procedure over the archived pre-sweep stream and finds **111,594 pairs =
223,188 CCX**, i.e. the census over-counted by **278×**, while its census mode
reproduces the disputed 62,152,364 exactly on the same stream. The official
*executed* delta (−215,049) is 96.4% of those emitted removals, which is the
same direction and size as this artifact's measured executed-vs-structural gap.
Full analysis: `CORRECTION-census-yield-20260915.md`.

## Why the guarded source was wrong (and why this is not a loophole)

The guard's intent was to keep ordinary and streaming emission identical: the
streaming writer path never materialized `ops`, so it could not run an
in-memory sweep. The consequence was that the shipping artifact never received
the sweep at all. This submission makes the ordinary (harness) path run the
sweep, and simultaneously publishes `Q793_CANCEL_SWEEP_APPLIED=1` so the
builder's drift armour compares against the pre-sweep measured pair as an upper
bound instead of demanding exact equality. The exact equality check still runs
on the pre-sweep build (the compact verification path), so a typo that changes
the circuit elsewhere still panics rather than shipping.

Nothing about the arithmetic, the schedule, the register geometry, or the test
draw changes: every deleted gate is an exact identity on all shots.

## Verification performed

1. **Census of the full stream** (independent tool, exact zstd framing parse):
   the operation/kind totals and the CCX-tuple count above, plus a check that
   the stream contains only X, Z, CX, CZ, Swap, R, Hmr, CCX, Register and
   AppendToRegister operations, with no CCZ and no condition-stack depth. The
   tool's *pair* count is an over-count (see the correction) and is not used as
   a yield estimate anywhere in this note.
2. **Review of the predicate** against the simulator's actual charge semantics
   (`src/sim.rs`: an op is charged only on shots where its condition stack is
   satisfied; only CCX/CCZ are charged), confirming that deleting a pair cannot
   change the executed Toffoli count by anything other than the two gates
   themselves.
3. **Pre-sweep regression**: the unmodified pipeline reproduces the previous
   official artifact exactly (peak 793, ops 1,231,960,915, structural_T
   681,079,356, and an independent 9,024-shot compact verification with zero
   classical, phase, and ancilla failures) — the sweep is the only change.
4. **Official run**: the 9,024-shot trusted evaluation of this submission is the
   correctness and score authority; its metrics are reported in the receipt.

## Caveats

* Because the deleted pairs are identities, the circuit's function and its
  ancilla/phase behaviour are unchanged; the residual risk is the Fiat-Shamir
  re-roll (the op stream is shorter, so the 9,024-shot draw is re-seeded). This
  is inherent to any op-stream change and is measured by the official run.
* The local measurement above is of the *pre-sweep* stream; the post-sweep
  artifact is measured by the official runner, which is the score authority.
  The post-sweep structural (emitted) Toffoli is not claimed; the pass-faithful
  emitted removal count (223,188 CCX) is.
* The window is 64 rather than the historical 512 default, to keep the sweep
  inside the CI budget. The window's effect on the yield is not measured (the
  census cannot measure it — see the correction, which measures the window-64
  yield directly); a window-512 run of `passcount` is the named next step if
  the yield is ever revisited.

## Attribution and provenance

The cancellation passes and their commutation predicate are the repository's own
code, written by earlier contributors to this challenge; this submission does
not add new gate identities. My contribution is: noticing that the pass was
guarded off on this route, removing the guard, publishing the sweep-applied flag
so the drift armour stays meaningful, and verifying the predicate against the
trusted simulator's charge semantics. Baseline for this change: submission
`2dc9b2b` (this campaign, Q793 / T671,563,551), which itself is the FLASH-origin
A24 support-pruned artifact carried to the canonical baseline.
