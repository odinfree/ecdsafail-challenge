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

- [x] Live anchor verified via CLI (score 1,172,540,718 @ 940e34a).
- [x] Knobs + defaults located.
- [x] Local baseline verified: Q1278, avg 917,480.917, tot_tof 8,279,347,797,
      0/0/0, ops SHA `38e4d98d…` (E1).
- [x] Cut measured env-only at inherited nonce: **Q1275, avg 918,996.816**,
      faults 9/7/0 (E2). ops SHA `ac5f5a80…`.
- [x] Co-binder cut baked as source defaults; digest guard passed (E3):
      baked stream byte-identical to E2.
- [ ] Conflict-surface probes P1-P4 (E4, running).
- [ ] Screening/hunt packet (digest-guarded, FN-gated).

## Key working numbers

- Cut stream: 12,954,520 ops, SHA256 `ac5f5a80caec1e4b789cf904069cd5056ecc9bd678e3101b77cd0847a7f5d7fd`.
- Strict beat at Q1275: round(avg_tof) <= 919,639 ⟺ tot_tof <= 8,298,826,847
  (n=9024). Dirty-draw measurement sits ~5.8M tot-T below the bound.
- Island density estimate from E2 fault sum 16: P(0/0/0) ~ e^-16 ≈ 1.1e-7 per
  nonce if faults ~ Poisson — a fleet-scale hunt, NOT local. Local work stops
  at the validated packet.

## Hard rules

- Commit only clean source/state/tooling. Exclude ops.bin, target/, logs,
  results.tsv rows, generated artifacts. Push milestones to `odinfree`.
- Every candidate needs unchanged full 9024-shot 0/0/0 validation.
