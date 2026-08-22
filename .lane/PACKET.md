# Hunt packet — q1275 co-binder cut on 940e34a

Status: DRAFT until all FN gates recorded below are green. This packet is
target-bound: any screener/hunter consuming it MUST refuse to run on a stream
whose digest differs.

## 1. Target identity

| Field | Value |
|---|---|
| Base source | `940e34a` + lane commit (branch `research/fable-peak-q1275-940e34a`) |
| Config (baked defaults) | `SUB4_PP_PEAK=1275 SUB4_PP_R1=342 SUB4_PP_R2=620`, `SQUARE_LADDER=245` |
| Op count | 12,954,520 |
| ops.bin SHA-256 (at inherited nonce 176078461220) | `ac5f5a80caec1e4b789cf904069cd5056ecc9bd678e3101b77cd0847a7f5d7fd` |
| Qubits (peak) | **1275** |
| avg executed Toffoli (dirty draw @176078461220) | 918,996.816 |
| Current gate (live best 38563a2) | 1,172,540,718 = 1278 x 917,481 |

Regeneration: build `build_circuit` from the lane commit with no env overrides;
the produced ops.bin must hash to `ac5f5a80…` or the packet is void
(digest guard). Env-only equivalent on clean 940e34a:
`SUB4_PP_PEAK=1275 SUB4_PP_R1=342 SUB4_PP_R2=620 SUB4_SQUARE_LADDER=245`.

## 2. Objective (what a WIN is)

Find a 48-bit tail nonce `n` such that the patched stream passes the unchanged
9024-shot trusted eval with **0 classical / 0 phase / 0 ancilla** faults and

- `round(tot_tof / n_shots) <= 919,639`  (half-away-from-zero, Rust f64::round)
- equivalently at n_shots = 9024: `tot_tof <= 8,298,826,847`
- giving score `1275 * round(avg) <= 1,172,539,725 < 1,172,540,718` (strict).

Draw-to-draw executed-T σ ≈ 10 avg-T; the dirty-draw measurement sits ≈642
avg-T (≈64σ) below the bound, so effectively **every clean island is a WIN**
unless the live gate moves. If the live best drops below 1,171,721,175-ish,
re-derive the bound before hunting (`ecdsafail benchmark`).

## 3. Nonce patch spec (exact)

The stream's last 96 ops are X-gate identity pairs on qubit 0/1
(`apply_tail_nonce`, `src/point_add/mod.rs:1923`). For bit `b` in 0..48 of
nonce `n`, set `q_target` of ops `[len-96 + 2b]` and `[len-96 + 2b + 1]` to
qubit id `1` if bit set else `0`. In the decompressed 56-byte record layout,
`q_target` is the u64 LE at record offset 24. Patching only ever writes 0 or 1.
Guard: before patching, assert all 96 tail ops are `kind == X` with
`q_target <= 1`.

## 4. Draw derivation (exact eval semantics — any deviation is a false result)

1. Seed: SHAKE256 absorbing `b"quantum_ecc-fiat-shamir-v2"`, then
   `ops.len() as u64` LE, then per op: `kind as u8`, and `q_control2,
   q_control1, q_target, c_target, c_condition, r_target` each as u64 LE.
2. Test gen: 9024 iterations; each reads 2x32 bytes from the XOF → k1, k2 (LE);
   `t = k1*G`, `o = k2*G`; skip iteration (no retry) if `t.x == o.x` or either
   is (0,0); else expected = t + o. n_shots = surviving count (9024 in
   practice; handle < without asserting).
3. Simulator: `Simulator::new(total_qubits, num_bits, xof)` — the SAME XOF
   continues as the R/Hmr randomness stream. R/Hmr consume 8 XOF bytes on
   EVERY op occurrence regardless of condition mask.
4. Batches of 64 shots over `ceil(n/64)` batches, `clear_for_shot` per batch,
   registers 0-3 set per shot, then the full op stream applied once per batch.
   Channels per batch: per-shot classical compare on regs 0/1; `sim.phase &
   cond_mask != 0` → phase-garbage batch; after zeroing register qubits, any
   qubit with `& cond_mask != 0` → ancilla-garbage batch.
5. `tot_tof` = sim.stats.toffoli_gates after all batches (CCX/CCZ executed
   shots, condition-mask-weighted).

**Fleet optimization (validated by construction, not yet on GPU):** the SHAKE
prefix state over ops `[0, len-96)` is nonce-independent — absorb once, clone
the hasher per candidate, absorb the 96 patched tail records (5,376 bytes of
op fields). Cuts per-candidate seed hashing from ~723 MB to ~5 KB.
**Early abort** at the first dirty batch is verdict-safe (a fault is final);
it only shortens DIRTY candidates. Never early-accept: CLEAN requires all
batches.

## 5. Reference screener (this repo, lane branch)

`src/bin/screen_nonces.rs` — trusted-side clone of `eval_circuit` semantics
with digest guard, tail patching, early abort (`--full` disables), TSV output:

```
target/release/screen_nonces \
  --ops ops.bin \
  --expect-sha ac5f5a80caec1e4b789cf904069cd5056ecc9bd678e3101b77cd0847a7f5d7fd \
  --best-score 1172540718 \
  --start 0 --count 1000
```

Columns: `nonce status cls phase anc batches tot_tof avg_round score verdict`.

## 6. False-negative gates (must all be green before trusting any screen)

| Gate | Input | Expected | Measured (2026-08-23) |
|---|---|---|---|
| A: positive control | baseline stream `38e4d98d…` @ 176078461220 | CLEAN, tot_tof 8,279,347,797, avg 917,481, score 1,172,540,718, verdict no-win (strict-< check) | **EXACT match** |
| B: negative control (full) | cut stream @ 176078461220 `--full` | DIRTY 9/7/0, 141/141 batches | **EXACT match** |
| C: early-abort consistency | cut stream @ 176078461220 | DIRTY, aborts at batch 9/141 (first cls fault shot 536 ∈ batch 8, 0-indexed) | **DIRTY 1/0/0 at 9/141** ✓ |
| D: digest guard | wrong `--expect-sha` | refuses, exit 1 | **refused** ✓ |

ALL GATES GREEN. Screener is trusted for screening as of lane commit; re-run
gates after ANY screener or stream change.

Gate A also proves the screener's tot_tof/round/score pipeline against the
trusted eval's printed totals; B proves per-channel fault agreement; C proves
abort can't change a verdict, only truncate work.

## 7. Hunt sizing

- E2 fault sum 16 (9 cls / 7 phase-batches / 0 anc) at one draw. Poisson
  estimate: island density ≈ e^-16 ≈ 1.1e-7 → geometric-mean cost ≈ 8.9M
  candidates to first island. (Single-draw λ estimate — wide error bars;
  a few hundred screened nonces give a much better λ and per-channel split.)
- Local single-core cost ≈ 20-30 s per DIRTY candidate (test-gen + ~9 batches)
  → this is a fleet-scale hunt. NOT to be run to completion locally; local
  screening is for λ estimation and packet validation only.
- Every fleet survivor MUST be re-certified by the unchanged `./benchmark.sh`
  full run (0/0/0 + score) on the lane commit before any submission decision.

## 8. Boundary conditions

- The N-way tie law applies: this stream's peak is TIED between the replay
  plan (1275) and the square ladder (1030+245=1275). Any future lever that
  adds +1 anywhere at the peak instant un-lands Q1275 (P3/P4 evidence:
  LADDER 246→Q1276, 247→Q1277).
- R1/R2 axis sweep around (342,620) at PEAK=1275/LADDER=245: see EXPERIMENTS
  E5. If a lower-T neighbor exists, re-cut the packet (new digest) before
  hunting.
- No submission, provider creation/mutation, fleet deployment, or spend from
  this lane. The packet is a hand-off artifact.
