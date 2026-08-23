# Lane state — tape/decoder (fable-burn-bdf4845)

Lane: Claude Fable architecture lane on exact promoted source **bdf4845**.
Objective: structurally different lower-Q route beating live leader; incumbent preserved in its own worktree.
Focus: the ping-pong walk **tape** (one sign qubit per round, ~698/696 rounds) — can it be
removed, checkpointed, streamed, dirtied, or replaced by recomputation so decoder-resident
walk state is not materialized at the peak? Value-exact live-range/representation change
preferred over truncation + nonce luck.

## Baseline (byte-exact, independently rebuilt in this worktree, 2026-08-23)

- Source: bdf4845 (promoted submission 792ac70, live leader).
- `./benchmark.sh` full run: **Q=1278, avg executed Toffoli=915,947.392, score=1,170,580,266**.
- 9024/9024 shots OK; 0 classical / 0 phase-garbage / 0 ancilla-garbage.
- Forced-rebuild `ops.bin` SHA256: `5b60d0a227b56f53abdc99b9588a80c1ff02838618ce4e7c3bf7cb22decdebb8`
  (50,893,170 bytes, 12,912,890 emitted ops).

## Exchange rate (live operating point)

Score = Q × T_avg. At Q=1278, T=915,947.392:
- **1 qubit ≡ 716.7 avg executed Toffoli** (break-even: dT = −T/Q · dQ).
- −1 qubit alone: −915,947 score. −1 avg Toffoli alone: −1,278 score.
- To beat leader need score < 1,170,580,266 → any (Q,T) with Q·T below that.

## Closed lanes (do NOT duplicate)

- Q1275 R1/peak/square-ladder transplant (PEAK=1275/R1=342/R2=625/LADDER=245), full inherited 17/8/0.
- Q1272 fold55 width-table lane.
- Knob-only SUB4_PP_PEAK / R1 / R2 sweeps (that is the incumbent's territory).

## Current status

- [x] Baseline byte-reproduced (E1).
- [x] Exchange rate computed (716.7 T/qubit).
- [x] Peak plateau inventory: 3-family plateau — pp_div_replay, pp_mul_walkback,
      square_product_register — all allowance-spenders at 1278 (E2, E3).
- [x] Falsifiers executed: A1 killed (information-forced, E4), A3 killed (arithmetic),
      A4 killed (exchange-rate, E5).
- [x] A2 killed (2026-08-23, exact — E6 sweep + E7 pricing): segment-matrix replay
      releases 0 tape bits (walk-back consumes signs as values), cannot compress
      (s ↦ M_seg injective, entries exactly k+1 bits), and application costs ≥ 2.3×
      baseline T while adding ≥ 3(k+1) qubits. Floor case Δscore ≥ +k·915,947.
- [x] A6 (tape-free escape outside ping-pong) killed by arithmetic: multiplication
      ladders cost ≥ 11× score whole-circuit and ≥ 14× at every hybrid margin (E7).
- **Lane verdict: EXHAUSTED. In-family Q1278 is exact-optimal (A1–A5), aggregate
  replay is net-positive-score by lower bound (A2), and the tape-free alternative
  loses ~10× on Toffoli (A6). No open architecture door remains in this lane;
  recommend concluding the burn and preserving bdf4845 as-is.**

## Key structural facts (from source read)

- `pingpong_div.rs`: walk records sign=src[1]⊕tgt[1] per round pre-add; tape live through
  coefficient replay AND needed as *value* (control) for walk-back. Signs are genuine
  1 bit/round of quantum data (both ± branches parity-consistent), not recomputable from
  post-state without the tape.
- Interleave Plan{r1=356, r2=625, peak=1278} already streams replay against the walk;
  `allowance = peak − (tape_len + 2N + 2·walk_width)` sizes the chunk ladder.
- Terminal state: all bits of u,v below sign are copies of sign; loan machinery frees them
  during terminal batch replay.
- Rounds: divide=698, multiply=696 (SUB4_PP_ROUNDS/_MUL).
