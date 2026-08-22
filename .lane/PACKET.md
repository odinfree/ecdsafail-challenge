# Hunt packet — q1275 co-binder cut on 940e34a

Status: **FINAL** (all FN gates green; target re-cut to R2=625 after E7
multi-draw). This packet is target-bound: any screener/hunter consuming it
MUST refuse to run on a stream whose digest differs.

## 1. Target identity

| Field | Value |
|---|---|
| Base source | `940e34a` + lane commit (branch `research/fable-peak-q1275-940e34a`) |
| Config (baked defaults) | `SUB4_PP_PEAK=1275 SUB4_PP_R1=342 SUB4_PP_R2=625`, `SQUARE_LADDER=245` |
| Op count | 12,953,930 |
| ops.bin SHA-256 (at inherited nonce 176078461220) | `83b66b7ef8e5080924f96faa0970a625044eb9d1e58fa2f6a75d162a3bb850d8` |
| ops.bin MD5 (same stream, for MD5-keyed tooling) | `7464046369b46251d49e5ee03af881c5` |
| Qubits (peak) | **1275** |
| avg executed Toffoli (4 dirty draws) | 918,963-918,974, mean ≈ 918,967.5 |
| Projected clean score | ≈ 1275 x 918,967 = **1,171,682,925** (−857,793 vs gate) |
| Current gate (live best 38563a2, rechecked 2026-08-23) | 1,172,540,718 = 1278 x 917,481 |

Regeneration: build `build_circuit` from the lane commit with no env overrides;
the produced ops.bin must hash to `83b66b7e…` or the packet is void
(digest guard). Env-only equivalent on clean 940e34a:
`SUB4_PP_PEAK=1275 SUB4_PP_R1=342 SUB4_PP_R2=625 SUB4_SQUARE_LADDER=245`.
(An earlier draft targeted R2=620, stream `ac5f5a80…`, avg ≈918,997 — E7
measured 625 structurally 30 avg-T better at ~7σ on 4-draw means; 630 is flat
vs 625. Do not hunt the 620 stream.)

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
  --expect-sha 83b66b7ef8e5080924f96faa0970a625044eb9d1e58fa2f6a75d162a3bb850d8 \
  --best-score 1172540718 \
  --start 0 --count 1000
```

Columns: `nonce status cls phase anc batches tot_tof avg_round score verdict`.

## 6. False-negative gates (must all be green before trusting any screen)

| Gate | Input | Expected | Measured (2026-08-23) |
|---|---|---|---|
| A: positive control | baseline stream `38e4d98d…` @ 176078461220 | CLEAN, tot_tof 8,279,347,797, avg 917,481, score 1,172,540,718, verdict no-win (strict-< check) | **EXACT match** |
| B: negative control (full), 620 stream | `ac5f5a80…` @ 176078461220 `--full` | DIRTY 9/7/0, 141/141 batches (trusted eval E2) | **EXACT match** |
| B': negative control, FINAL 625 stream | `83b66b7e…` @ 176078461220 | trusted eval (E5): 14 cls / 11 phase / 0 anc, avg 918,965.780 | **screener --full: 14/11/0, tot 8,292,747,196 = avg 918,965.780 — EXACT** |
| C: early-abort consistency | `ac5f5a80…` @ 176078461220 | DIRTY, abort at batch 9/141 (first cls fault shot 536 ∈ batch 8, 0-indexed) | **DIRTY 1/0/0 at 9/141** ✓ |
| C': early-abort, FINAL stream | `83b66b7e…` @ 176078461220 | DIRTY, abort at first dirty batch | **DIRTY 1/1/0 at 27/141** ✓ |
| D: digest guard | wrong `--expect-sha` | refuses, exit 1 | **refused** ✓ |

ALL GATES GREEN. Screener is trusted for screening as of lane commit; re-run
gates after ANY screener or stream change.

Gate A also proves the screener's tot_tof/round/score pipeline against the
trusted eval's printed totals; B proves per-channel fault agreement; C proves
abort can't change a verdict, only truncate work.

## 7. Hunt sizing

- Fault sums on the FINAL 625 stream over 4 full draws: 25 / 12 / 15 / 23
  (cls+phase-batches; anc always 0 in all 12 E7 draws + 100 scanned nonces).
- **Density from the 100-nonce early-abort scan (nonces 4000-4099, 0 clean):**
  mean first-dirty-batch 8.61/141 → per-batch dirty hazard ≈ 0.116 →
  **dirty-batch λ ≈ 16.4, island density ≈ e^-16.4 ≈ 7.5e-8** (inferred —
  geometric fit on censored scan, better unit than raw fault sums because
  multiple faults share a batch) → geometric-mean cost ≈ **13M candidates**.
  Raw-fault-sum Poisson (λ≈18.75, n=4) gives the pessimistic bound 7.2e-9.
- Early abort measured: mean 8.61 of 141 batches on dirty draws → ≈16x
  throughput vs full eval. At-abort trigger split ≈ 50/50 cls/phase — a
  classical-only prefilter forfeits half the aborts.
- 620-stream λ for comparison: pooled 22.8 (Einstein n=10 fixtures + our
  n=4 full draws — fixture cross-check was 10/10 exact on both channels).
  625-vs-620 λ difference is ~1.6σ: suggestive, NOT settled.
- Nonce space: 48-bit (2.8e14) — density is the constraint, not the space.
- Local single-core cost ≈ 20-30 s per DIRTY candidate (test-gen + early
  abort) → fleet-scale hunt. NOT to be run to completion locally; local
  screening is for λ estimation and packet validation only.
- Every fleet survivor MUST be re-certified by the unchanged `./benchmark.sh`
  full run (0/0/0 + score) on the lane commit before any submission decision.

## 8. Boundary conditions

- The N-way tie law applies: this stream's peak is TIED between the replay
  plan (1275) and the square ladder (1030+245=1275). Any future lever that
  adds +1 anywhere at the peak instant un-lands Q1275 (P3/P4 evidence:
  LADDER 246→Q1276, 247→Q1277).
- R1/R2 tuning is settled: R1=342 is the axis minimum (E5, steep penalty
  above 346); R2=625 beats 620 by 30 avg-T at ~7σ on 4-draw means and 630 is
  flat vs 625 (E7). Any further re-cut voids this packet's digest.
- No submission, provider creation/mutation, fleet deployment, or spend from
  this lane. The packet is a hand-off artifact.
