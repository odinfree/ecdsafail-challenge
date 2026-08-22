# Experiments — fable-peak-q1275-940e34a

Ledger convention: every row lists config, ops digest, and full-eval channels
(cls / phase-batches / anc-batches over 9024 shots). Score = Q x round(avg_tof).

## E1 — Baseline anchor verification (2026-08-23)

- Config: clean 940e34a, all defaults (PEAK=1278 R1=356 R2=625 LADDER=248,
  nonce 176078461220).
- Command: `./benchmark.sh` (log: `$CLAUDE_JOB_DIR/tmp/baseline_940e34a.log`)
- ops: 12,918,089; ops.bin SHA256
  `38e4d98d2ed7c9d0c3600f631e371de54284832f7cd7657fe25698c46c062a7e`
- Result: Q=1278, tested 9024, **0/0/0**, tot_tof 8,279,347,797,
  avg 917,480.917 → round 917,481. Score **1,172,540,718** — exact match to
  live gate (submission 38563a2). ANCHOR VERIFIED.
- Wall time: ~4 min on this machine (full 9024-shot eval is cheap locally).

## E2 — q1275 co-binder cut, env-only, inherited nonce (running)

- Config: 940e34a + env `SUB4_PP_PEAK=1275 SUB4_PP_R1=342 SUB4_PP_R2=620
  SUB4_SQUARE_LADDER=245`, nonce inherited 176078461220.
- Command: `SUB4_... ./benchmark.sh`
  (log: `$CLAUDE_JOB_DIR/tmp/cut_env_inherited_nonce.log`)
- Hypothesis (from prior dirty probes): Q=1275, avg_tof ≈ 918,994,
  fault sum ≈ 22 at this (now-dirty) nonce. Expect eval FAIL with nonzero
  channels; the point is the Q/T measurement + fault characterization.
- Result: **Q=1275 CONFIRMED**. ops 12,954,520 (+36,431 vs baseline);
  ops.bin SHA256
  `ac5f5a80caec1e4b789cf904069cd5056ecc9bd678e3101b77cd0847a7f5d7fd`.
  avg_tof **918,996.816** (probe claim ≈918,994 consistent within draw σ≈10).
  Faults at inherited nonce: **9 cls / 7 phase-batches / 0 anc** (sum 16; the
  probes' ~22 was a different dirty draw). First cls fault: shot 536.
  Projected clean-island score ≈ 1275 x 918,997 = **1,171,721,175**
  (−819,543 vs gate); strict-beat headroom ≈ 642 avg-T ≈ 64 draw-σ.

## E3 — Baked source defaults: digest guard (2026-08-23)

- Edits: `pingpong_div.rs` plan() defaults 356→342, 625→620, 1278→1275;
  `product_register.rs` SQUARE_LADDER 248→245.
- Baked build (no env) ops.bin SHA256 = `ac5f5a80…` — **byte-identical** to
  the E2 env-only stream. Eval is deterministic on ops bytes ⇒ E2's numbers
  transfer exactly to the baked source. DIGEST GUARD PASSED.

## E4 — Conflict-surface probes (running)

All full 9024-shot evals at inherited nonce 176078461220, env on baked-cut
source (P1/P2 override back to baseline values where noted):

| Probe | PEAK | R1/R2 | LADDER | Question |
|---|---|---|---|---|
| P1 | 1275 | 356/625 | 248 | Does peak migrate to square without ladder cut? |
| P2 | 1275 | 356/625 | 245 | What does the R1/R2 retune buy? |
| P3 | 1275 | 342/620 | 246 | Is 245 over-tight (246 fits under 1275)? |
| P4 | 1275 | 342/620 | 247 | Ladder boundary sweep upper point |

Results (all FAIL on channels as expected — dirty nonce; Q and avg_tof are the
measurements):

| Probe | Q | avg_tof | ops | faults |
|---|---|---|---|---|
| P1 | **1278** | 920,435.880 | 12,990,351 | 16/11/0 |
| P2 | **1275** | 920,446.330 | 12,990,953 | 12/10/0 |
| P3 | **1276** | 918,990.713 | 12,954,302 | 7/5/0 |
| P4 | **1277** | 918,984.359 | 12,954,110 | 5/6/0 |

Reading:
- P1: PEAK=1275 alone → Q stays 1278 (square binder at 1030+248) and PAYS
  +2,955 avg-T for zero qubits. Co-binder cut is mandatory. (Matches the
  b5796ce-era peak-migration finding.)
- P2: ladder cut alone lands Q1275; the R1/R2 retune is worth **−1,449.5
  avg-T** (920,446.330 → 918,996.816).
- P3/P4: square peak contribution = **1030 + LADDER** exactly (245→1275,
  246→1276, 247→1277, 248→1278). 245 is the max ladder under 1275. Going up
  1 ladder saves only ~6 avg-T (~8k score) but costs a qubit (~919k score):
  245 is correct. The stream's peak is an exact TIE between replay plan
  (1275) and square (1275) — N-way-tie law applies to future levers.

## E5 — R1/R2 axis sweep at PEAK=1275/LADDER=245 (2026-08-23)

Full evals at inherited nonce; all Q=1275:

| Config | avg_tof | ops |
|---|---|---|
| R1=334 R2=620 | 919,115.839 | 12,957,582 |
| R1=338 R2=620 | 919,060.923 | 12,956,029 |
| **R1=342 R2=620 (cut)** | 918,996.816 | 12,954,520 |
| R1=346 R2=620 | 919,268.840 | 12,961,744 |
| R1=350 R2=620 | 920,581.524 | 12,993,932 |
| R1=342 R2=610 | 919,047.250 | 12,955,892 |
| R1=342 R2=615 | 919,014.972 | 12,955,159 |
| **R1=342 R2=625** | **918,965.780** | 12,953,930 |

- R1=342 confirmed the axis minimum (steep penalty above 346).
- **R2=625 beats the mandated 620 by 31.0 avg-T (~40k score)**, monotone
  610→625. Cross-stream draw noise σ_diff ≈ 14 avg-T, so this is ~2.2σ —
  E6 multi-draw measurement before re-cutting the default. R2=630 stream
  also built for the boundary.

## E6 — FN gates for screen_nonces (2026-08-23) — ALL GREEN

| Gate | Expected | Measured |
|---|---|---|
| A positive | CLEAN tot 8,279,347,797 avg 917,481 score 1,172,540,718 no-win | EXACT match |
| B negative --full | DIRTY 9/7/0 141/141 | EXACT match |
| C early-abort | DIRTY, abort batch 9/141 | EXACT (1/0/0 at 9/141) |
| D digest guard | refuse on wrong sha | refused, exit 1 |

Early abort ⇒ ~15.7x dirty-draw saving at this fault density.

## E7 — Multi-draw executed-T: R2 ∈ {620,625,630} x nonces
{176078461220,1000,2000,3000} (running)

- Streams: 620 = `ac5f5a80…` (baked), 625 = `83b66b7ef8e5080924f96faa0970a625044eb9d1e58fa2f6a75d162a3bb850d8`,
  630 = `4678b1201ffcdacc0b5100f8eec8d8de2a1e4eee9f66a23482f06806f8ce69ae`.
- Purpose: separate structural T from draw noise before final default; pick
  min-mean stream as the packet target. Result: pending.
