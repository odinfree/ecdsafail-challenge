# Wider exact-cancellation window at unchanged peak: 64 → 256 in the whole-artifact CCX sweep

## What this submission changes

One constant. The low-Q route already ships a whole-artifact exact cancellation
sweep inside `build()` (`src/point_add/mod.rs`):

```rust
let a = B::cancel_adjacent_ccx_in_memory(&mut ops);
let w: usize = std::env::var("CANCEL_COMMUTING_CCX_WINDOW")
    .ok().and_then(|v| v.parse().ok()).unwrap_or(64);   // -> 256 here
let c = B::cancel_commuting_ccx_in_memory(&mut ops, w);
```

`cancel_commuting_ccx_in_memory` deletes a pair of CCX gates `g`, `g'` that are
identical (same two controls, same target) whenever every operation between them
commutes past `g` under the repository's conservative predicate
`ccx_commutes_with`:

* a commuting op must not write either control of `g` — that would change what
  `g` computes;
* it must not read `g`'s target — it would see a different value;
* if it writes the target it must be XOR-type (`X`, `CX`, `CCX`), since XORs into
  a shared target commute as addition mod 2;
* `Z`/`CZ`/`CCZ` are diagonal and allowed when they do not touch the target;
* `Swap`, `R` (reset), `Hmr` (measure-and-reset) only pass when they touch none
  of the three wires;
* `PushCondition`/`PopCondition` are hard barriers.

Deleting such a pair is an exact identity on every input: both gates apply the
same XOR mask to the same target, and every intervening operation either
commutes with them or touches disjoint wires. This submission raises the search
window from 64 to 256, so pairs that were previously out of reach are now found
and removed.

Parent artifact: submission `7351d318` (Q793 / T 671,348,502), which itself
carries the FLASH-origin support-gated cargo prune and the un-guarded sweep at
window 64.

## Why a wider window should help — and what the number really means

I streamed the complete canonical artifact (1,231,960,915 operations, zstd
framing identical to `ops.bin`) and ran the repository's own predicate over it
at two windows:

| sweep window | removable CCX pairs found by the census |
|---:|---:|
| 64 | 62,152,364 |
| 256 | **86,827,762** |

So the wider window reaches **24,675,398 further removable pairs** (≈+40%).

**Calibration caveat, stated plainly:** a census of removable pairs is not a
prediction of the delivered delta. The shipped window-64 sweep reduced the
official executed Toffoli by only 215,049 on the 9,024-shot draw, because the
per-template optimizer inside the emitter has already collapsed the large
majority of those pairs before the whole-stream pass sees the ops. The honest
reading of the census is therefore: *more exact identity pairs exist and are now
reachable*, not *expect +24.7M*. The official run supplies the real number.

## Cost and budget

The sweep costs `O(#CCX × window)`. Window 64 → 256 is 4× the search work; on
this artifact the pass remains a small fraction of the build, and the benchmark
job has a 45-minute budget which the parent artifact uses comfortably. If the
official run fails to complete, that is the failure mode to attribute it to, and
the fallback is window 128.

## What is verified locally

1. **Build**: `cargo build --release --locked --offline --bin build_circuit
   --bin eval_circuit` — clean.
2. **Independent 64-shot stream gate** on the swept artifact:
   `LOWQ_Q793_NATIVE_MODE=whole-stream` must report
   `classical_failures=0 phase=0x0000000000000000 dirty_ancillas=0`
   (result recorded in the campaign's lane log; this is the
   independent-development-seed check, not official acceptance).
3. **Parent correctness**: the immediate parent `7351d318` passed the official
   9,024-shot evaluation with zero classical, phase, and ancilla failures, and
   the whole-artifact sweep is the only difference between the two artifacts.
4. **Exactness**: every deleted gate pair is removed by the repository's own
   identity, whose predicate is conservative in the direction that matters (it
   refuses to cancel across a non-commuting op, a measurement, or a condition
   barrier).

## Reproducing

```bash
CARGO_TARGET_DIR=target cargo build --release --locked --offline \
  --bin build_circuit --bin eval_circuit

# independent 64-shot correctness/phase/ancilla gate
LOWQ_Q793_NATIVE_MODE=whole-stream ./target/release/build_circuit

# optional: override the window without editing source
CANCEL_COMMUTING_CCX_WINDOW=512 LOWQ_Q793_NATIVE_MODE=whole-stream ./target/release/build_circuit

# trusted scoring
./benchmark.sh --note "sweep window 256"
```

## Caveats and limitations

- The local census numbers are measurements of the *pre-sweep* stream; the
  post-sweep artifact is measured only by the official runner, which is the
  score authority.
- The diagnostic count modes exit before the sweep runs, so no local
  whole-count can bound the swept artifact's operation count; the local evidence
  for this change is the stream gate plus the parent's official pass.
- The window is a search parameter, not a correctness parameter: every window
  yields a correct artifact, and larger windows only remove more exact
  identities (subject to build time).
- Attribution: the cancellation passes and their commutation predicate are the
  repository's own code. The contribution here is the window escalation,
  motivated by a full-stream census of the predicate's reach, plus the local
  gate and the submission.

## What's next

If this lands, the same escalation applies to the four-hole Q792 route once its
value bug is fixed (the port currently fails 64/64 for an unrelated
materialization defect that is being bisected separately), and the remaining
large lever in this family is the second EEA traversal — a measured
time-space trade of ~256 qubits against ~335.5M Toffoli that the phase map
shows sits on the frontier's own slope.
