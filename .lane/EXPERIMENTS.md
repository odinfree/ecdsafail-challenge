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

- Result: pending.
