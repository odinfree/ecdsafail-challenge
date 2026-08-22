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
  min-mean stream as the packet target.
- Results (avg_round per draw; faults cls/phase/anc):

| Stream | @176078461220 | @1000 | @2000 | @3000 | mean avg | fault sums |
|---|---|---|---|---|---|---|
| R2=620 | 918,997 (9/7/0) | 918,988 (13/13/0) | 919,002 (12/11/0) | 919,003 (18/15/0) | 918,997.5 | 16/26/23/33 |
| **R2=625** | 918,966 (14/11/0) | 918,963 (9/3/0) | 918,967 (7/8/0) | 918,974 (10/13/0) | **918,967.5** | 25/12/15/23 |
| R2=630 | 918,971 (8/12/0) | 918,968 (13/13/0) | 918,972 (15/10/0) | 918,969 (15/13/0) | 918,970.0 | 20/26/25/28 |

- Draw σ(avg) ≈ 5-7. **625 beats 620 by 30.0 avg-T on means (~7σ) — settled.**
  630 vs 625: +2.5, flat. → FINAL default R2=625 (E8 re-cut; digest guard:
  baked build reproduces `83b66b7e…` exactly). Ancilla channel: 0 in all 12
  draws. Pooled fault mean 22.7 (n=12) — matches inherited "~22" claim; the
  625-vs-620 λ difference (18.75 vs 24.5, n=4 each) is ~1.7σ — suggestive,
  NOT settled.
- Cross-tool agreement: screener tot/9024 matches `eval_circuit`'s printed avg
  to all 3 decimals on both streams (620: 918,996.816; 625: 918,965.780), and
  fault counts match exactly (9/7/0 and 14/11/0).

## E8 — λ-refinement scan + Einstein fixture verification (2026-08-23, done)

- 100 nonces (4000-4099) early-abort on the FINAL 625 stream: **0 clean**
  (expected ~1e-5 P(≥1) at these densities), mean first-dirty-batch
  **8.61/141** → per-batch hazard ≈ 0.116 → dirty-batch λ ≈ 16.4, island
  density ≈ e^-16.4 ≈ 7.5e-8 (inferred — geometric fit, censored n=100) →
  ~13M candidates geometric-mean hunt. Early abort ≈ 16x dirty-draw saving.
- Reconciliation reply sent to Einstein_Claude lane (msg
  7f4d77eb-ca9a-484a-a59a-d27554ccfd92): fixtures verified 10/10, R2=625
  counter-finding with settled/unsettled split, density data, hand-off
  pointers.
- Einstein_Claude advisory packet (`~/ecdsa-ops/HUNT-PACKET-20260823-peakcut.md`)
  independently reproduces our 620 stream (SHA `ac5f5a80…` exact match, ops
  12,954,520 exact) and the 919,639 ceiling; their 10 calibration fixtures
  (nonces 101000000003…110000000027, cls/phase from stock eval) re-screened
  with screen_nonces --full.
- **Fixtures: 10/10 EXACT match on BOTH channels** (cls AND phase; anc 0
  everywhere, Q1275 everywhere). Channel means reproduce their 12.1/10.0 to
  the decimal. Their q1274 alt stream also reproduced byte-exact (MD5
  `5bfb54ea2651d97f87ba15f51c04c5ce`, ops 12,969,729, at
  PEAK=1274/LADDER=244/R1=342/R2=620) and their 620-stream MD5 `200fc84b…`
  matches our `ac5f5a80…` artifact. Joint toolchain calibration COMPLETE.
- Pooled 620-stream λ (their n=10 + our n=4): 22.8. 625-stream λ: 18.75
  (n=4). Difference ~1.6σ — suggestive only; T-advantage of 625 is the
  settled part (−30 avg-T, ~7σ).
- Fixture avg_rounds (620 stream, n=10): 918,976-919,004, mean 918,992.4 —
  consistent with their "918,994.37 (n=3)" and our 4-draw 918,997.5.
