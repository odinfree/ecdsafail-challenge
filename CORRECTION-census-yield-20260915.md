# Correction: the CCX-cancellation census is not a yield estimate

Written 2026-09-15T13:25Z by the root lane, after the submission
`7351d31` (Q793 / T671,348,502) was already on the public record.

## What was claimed

The commit message of `d726faf8`, a source comment in `src/point_add/mod.rs`,
the `probench-live-fix` patch, `lanes/laneRoot/streamtool`'s headline output,
and `ROOT-HANDOFF-20260915.md` §2 all carried the figure

> 62,152,364 removable CCX measured on the canonical Q793 stream

as if it were the effect of running the whole-artifact cancellation sweep.

## What was measured

| quantity | value | instrument |
|---|---:|---|
| official executed Toffoli delta for un-guarding the sweep | **−215,049** | trusted `eval_circuit`, submission `7351d31` |
| pass-faithful emitted CCX removals, window 64 | **223,188** | `streamtool/src/bin/passcount.rs` (new) |
| census-tool pair count, window 64 | 62,152,364 | `streamtool`, **different scan than the pass** |
| post-sweep structural (emitted) Toffoli | not measured | — |

The two numbers are not the same object, and the 289× gap is not explained by
"later passes had already removed them": the pass that ran removes pairs by the
repository's rule, and the census does not.

### Verification of this correction (measured 2026-09-15T15:35Z)

`passcount` replays the pass's decision procedure over the archived pre-sweep
stream (`/private/tmp/a24stream/ops-stream.bin`) without materializing it, using
the repository's exact `same_gate` and `ccx_commutes_with`. It reproduces the
stream's identity exactly — `read_ops = 1231960915`,
`ccx_total = 681079356`, `adjacent_identical_ccx_pairs = 11040`, all equal to
the campaign's recorded census — and its census mode reproduces the disputed
figure exactly (`31076182 pairs = 62152364 CCX`). On that same stream, the pass
removes **111,594 pairs = 223,188 CCX**:

| | pairs | CCX removed |
|---|---:|---:|
| census tool (loose scan) | 31,076,182 | 62,152,364 |
| `cancel_commuting_ccx_in_memory` (window 64) | 111,594 | 223,188 |

So the census over-counts the pass by **278×**. The internal consistency with
the official receipt is also there: the 111,594 pairs it removes include
conditional gates, and the official *executed* delta is −215,049, i.e. 96.4% of
the emitted removals — the same direction and rough size as the artifact's
measured 1.4% executed-vs-structural gap (671,348,502 / 681,079,356 = 98.6%
before the sweep).

Reproduce:

```bash
CARGO_TARGET_DIR=target-streamtool cargo build --release --offline
WINDOW=64 ./target-streamtool/release/passcount /private/tmp/a24stream/ops-stream.bin
```

Two corrections to the campaign's earlier reading of this tool:

1. The count disagreement is **not** evidence that the census is a valid upper
   bound. It is 278× above the true yield, so it cannot bound anything.
2. The census result is **not** evidence that window 64 and window 512 are
   equivalent on this artifact. That question is about the pass, and the pass's
   window sensitivity has to be measured with `passcount`. That run was started
   and **stopped** at 3.0e8/1.23e9 ops (about 25 minutes projected) to keep the
   host free for the lane's own jobs; the partial log is
   `runtime/passcount-pree-sweep-w512-INCOMPLETE.log` and carries no result. Do
   not quote the window-512 choice as measured until that run completes.

## Why the census over-counts

`lanes/laneRoot/streamtool/src/main.rs`, repository-predicate census block:

1. The **pass** (`cancel_commuting_ccx_in_memory`, `src/point_add/mod.rs`)
   scans forward from a gate and breaks at the first op that does not commute
   past it (`if !ccx_commutes_with(...) { break; }`).
2. The **census** keeps a set of pending gates, and on a non-commuting op marks
   only that gate dead (`first_dead`) while continuing to look for a match
   further along the window (`if pt == cur { hit = ...; break; }` is evaluated
   across all pending entries before the loop ends).

So the census pairs gates whose intervening stream does not commute through
every op in between — pairs the pass may not delete. The census's own sample
line for offsets 507..509 printed `unblocked=false` while still being counted in
the class census; the class is real, the count is not a yield.

## Standing rules

1. A pair census may identify a rewrite **class**. It may never be quoted as a
   yield, an expected delta, or a bound on what a pass will remove.
2. Only two numbers count for a pass: the pass's own removal count
   (`eprintln!("CANCEL adjacent={a} commuting={c}")` — record it when the build
   runs) and the trusted official delta.
3. A source comment, a commit subject, or a note may not present an
   instrument-model count as a measurement. If the instrument and the artifact
   differ in scan structure, the count is labelled as a class finder.
4. Any statement of the form "later optimizers already removed them" must come
   with the two counts that establish it, not with a reconstruction.

## Status of the submitted artifact

Unchanged and legitimate: `7351d31` is a real, official, nondominated Q793
point whose mechanism (removing the guard that skipped an exact
identity-cancellation pass) is sound. The correction concerns the headline
number attached to it in this campaign's records, not the artifact or the
receipt.
