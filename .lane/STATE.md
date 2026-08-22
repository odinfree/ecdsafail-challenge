# Lane: fable-peak-q1275-940e34a

**Mandate:** Implement + validate the measured q1275 peak co-binder cut on exact
source 940e34a. Produce a target-bound screening/hunt packet gated on digest
guards, fixture agreement, and false-negative gates. NO submission, provider
creation/mutation, fleet deployment, or spend. Local bounded work only.

## Anchor (verified live via `ecdsafail benchmark` + `submissions --all`, 2026-08-23)

- Current best: submission `38563a2` (welttowelt), score **1,172,540,718**
  = 1278 qubits x 917,481 avg-T, commit `940e34a` — the exact commit this
  worktree sits on (clean).
- Score formula: `score = qubits * round(tot_tof / n_shots)` (round =
  half-away-from-zero, `src/bin/eval_circuit.rs:432-442`). Draw-dependent via
  Fiat-Shamir SHAKE256 over the exact op stream (`fiat_shamir_seed`).

## Target cut (this lane)

| Knob | Site | 940e34a default | Cut |
|---|---|---|---|
| `SUB4_PP_PEAK` | `src/point_add/pingpong_div.rs:1190` | 1278 | 1275 |
| `SUB4_PP_R1` | `src/point_add/pingpong_div.rs:1188` | 356 | 342 |
| `SUB4_PP_R2` | `src/point_add/pingpong_div.rs:1189` | 625 | 620 |
| `SUB4_SQUARE_LADDER` | `.../square/product_register.rs:28` (`SQUARE_LADDER`) | 248 | 245 |

Prior independent probes: ~Q1275/T918994, fault sum ~22 at inherited nonce,
projected 1275 x 918,994 = 1,171,717,350 (−823,368 vs gate). Probe nonces were
DIRTY — re-verify everything here.

## Strict-beat threshold at Q1275

score < 1,172,540,718 ⟺ round(avg_tof) <= 919,639
(1275 x 919,639 = 1,172,539,725; 1275 x 919,640 = 1,172,541,000).
With n_shots = 9024: avg < 919,639.5 ⟺ **tot_tof <= 8,298,826,847**
(919,639.5 x 9024 = 8,298,826,848). Verify n_shots == 9024 on every run —
rejected draws (k1==k2/infinity) would shift the denominator.

## Route facts (940e34a)

- Active route: pingpong (`SUB4_LEGACY_POINT_ADD` unset) —
  `src/point_add/mod.rs:2533-2548`. Tail nonce default `176078461220`
  (`SUB4_PINGPONG_TAIL_NONCE`), 48 bits in 96 identity X-pairs
  (`apply_tail_nonce`, mod.rs:1923) — function-identical, seed-only.
- Pingpong reuses trailmix symmetric in-place square ⇒ `SUB4_SQUARE_LADDER`
  is live in this stream; square's chunked wide adds are the peak co-binder.
- `plan()` knobs (r1/r2/peak) shape replay interleave chunking against the
  `peak` width budget (`allowance()`, pingpong_div.rs:1197-1199).
- PP_PROFILE=1 DOES write ops.bin (worktree-local; gitignored).
- Validation channels: classical mismatches / phase-garbage batches /
  ancilla-garbage batches, must be 0/0/0 over full 9024 shots.

## Status

- [x] Live anchor verified via CLI (score 1,172,540,718 @ 940e34a; rechecked
      after E7 — unchanged).
- [x] Local baseline verified: Q1278, avg 917,480.917, 0/0/0 (E1).
- [x] Cut measured + baked; digest guards passed (E2/E3).
- [x] Conflict surface mapped (E4): square peak = 1030+LADDER; co-binder cut
      mandatory (PEAK alone → Q stays 1278); R1/R2 retune −1,449.5 avg-T.
- [x] R1/R2 swept (E5) + multi-draw (E7): **final default R2=625** (30 avg-T
      better than mandated 620 at ~7σ on means; 630 flat). R1=342 confirmed.
- [x] screen_nonces screener: FN gates A/B/B'/C/C'/D ALL GREEN (E6).
- [x] PACKET.md FINAL on the 625 stream.
- [x] 100-nonce λ-refinement scan: 0 clean, dirty-batch λ ≈ 16.4, density
      ≈ 7.5e-8/nonce (geometric fit), early abort 16x (E8).
- [x] Cross-lane reconciliation with Einstein_Claude
      (~/ecdsa-ops/HUNT-PACKET-20260823-peakcut.md): their 10 fixtures
      verified **10/10 exact on both channels**; both lanes' stream hashes
      byte-identical; ceiling independently agreed. Reply sent (msg
      7f4d77eb…) recommending the 625 stream with the settled/unsettled
      split. LANE OBJECTIVE COMPLETE — remaining work (fleet hunt, final
      9024 certification of a survivor, submission) is out of this lane's
      mandate and handed off via .lane/PACKET.md.

## FINAL target identity (what the fleet should hunt)

- Config: PEAK=1275 R1=342 **R2=625** LADDER=245 (baked defaults, lane branch).
- Stream: 12,953,930 ops, SHA256
  `83b66b7ef8e5080924f96faa0970a625044eb9d1e58fa2f6a75d162a3bb850d8`.
- 4-draw avg_round 918,963-918,974 (mean 918,967.5); fault sums 25/12/15/23
  (λ ≈ 18.75, n=4).
- Strict beat at Q1275: round(avg_tof) <= 919,639 ⟺ tot_tof <= 8,298,826,847
  (n=9024). ~64σ headroom: ANY clean island wins.
- Projected winning score ≈ 1,171,682,925 (−857,793 vs gate).
- Einstein's negative (do not re-test): endpoint-fold widening does NOT
  transfer to this base (their EF 24/26/28 read fault 30/35/30 vs 22 at
  EF=20). Their q1274 alt (PEAK=1274/LADDER=244) exists but q1275 preferred.

## Hard rules

- Commit only clean source/state/tooling. Exclude ops.bin, target/, logs,
  results.tsv rows, generated artifacts. Push milestones to `odinfree`.
- Every candidate needs unchanged full 9024-shot 0/0/0 validation.
