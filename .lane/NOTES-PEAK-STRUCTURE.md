# Peak structure (measured on this worktree, source 2c79d2f)

## Trusted score
- Q = `max referenced qubit id + 1` over the whole op stream (`src/circuit.rs:348-387`,
  `analyze_ops`), consumed `src/bin/eval_circuit.rs:469`, scored `:432-442`
  (`score = round(avg_tof) * qubits`). Only CCX/CCZ charged (`src/sim.rs:82-99`).
- Live receipt: Q1274, rounded T916526, score 1,167,654,124 (verified 1274*916526).
- On the pingpong route the builder's `b.peak_qubits` == trusted Q exactly (LIFO
  allocator, every id referenced via its `R` free, no op-deleting post-passes — the
  pingpong branch returns at `mod.rs:2539-2555` before all strip/fanout passes).

## Peak-binding instant (measured)
- `TRACE_EACH_PEAK=1`: peak Q1274 binds in phase `pp_div_replay` at ops_idx 2528381
  (terminal batch replay). Prior shoulder 1271 at ops_idx ~929878.
- `B0_WIN_LO=2400000 B0_WIN_HI=2600000` census at best_active=1274, best_ops=2528381,
  phase=pp_div_replay, n_live=1274, 9 owner groups:
  - 339 @ pp_div_walk  pingpong_div.rs:1150  (walk_round sign alloc — tape)
  - 256 @ init         pingpong_div.rs:2056  (numerator/y, ABI)
  - 256 @ pp_div_replay pingpong_div.rs:268  (coefficient)
  - 145 @ init         pingpong_div.rs:2055  (denominator/x base, ABI)
  - 145 @ tlm_inverse  arith/adder.rs:341    (recycled pool wires)
  - 130 @ pp_div_replay pingpong_div.rs:838  (chunk carry ladder, split adder)
  -   1 @ ...:797, 1 @ ...:1150, 1 @ pp_div_walk:604
  (Owner attribution is by ORIGIN site; wires are recycled via the LIFO pool, so
   e.g. the 339+130+... reflect where currently-live ids were first minted, not a
   clean register partition. The clean co-binder decomposition below is the
   authority.)

## Co-binder decomposition (1274, from budget identity)
`allowance = peak - (tape_len + 2*N + 2*walk_width)`, `N=256`.
- tape (one sign qubit/round): 698 (divide)  <- DOMINANT, 55% of Q
- coefficient: 256 (ABI)
- numerator:   256 (ABI)
- loaned u,v sign wires: 2
- chunk carry ladder: 62
- TOTAL: 1274

## THE N-WAY TIE (critical) — MEASURED three-way
`PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1` per-phase active maxima:
- pp_div_replay    1274  <- binder
- pp_mul_replay    1274  <- binder
- pp_mul_walkback  1274  <- binder
- pp_div_walk / pp_div_walkback / pp_mul_walk  1057
`peak_phase` only updates on strict `>`, so TRACE reports pp_div_replay alone — a
reporting artifact. A lever must drop ALL THREE tied binders (or be provably
sole-binder) to lower global Q. Divide and multiply carry independent tapes
(698 / 696), so a divide-only transducer leaves Q=1274.

## Geometry constants (live; NOT the memory-doc values)
`SUB4_PP_PEAK=1274` (pingpong_div.rs:1263, an INPUT to chunk-layout search),
R1=340 (:1261), R2=628 (:1262), ROUNDS(divide)=698 (:34), ROUNDS_MUL=696 (:23),
VALUE_WIDTH=259 (:7), N=256.

## Score gates (recomputed from live 1,167,654,124)
- Q1273: strict rounded T <= 917245 (headroom +719 over 916526)
- Q1272: strict rounded T <= 917967 (headroom +1441)

## Sign / tape mechanism (walk)
- Round r update: `target <- (target + (-1)^sigma * source)/2`, arithmetic, width
  `value_width(r)` (258 at r=8, shrinking to 8 by r~689). source untouched.
- `sigma_r = target[1] XOR source[1]` — 2 bits of the CURRENT (u,v) state.
- source/target swap by parity (the "pingpong"): even r: u->v; odd: v->u.
- tape = one sigma qubit/round, FULLY LIVE across the coefficient replay; freed only
  in value_walk_back at the very end. Replay consumes signs 0..697 (increasing),
  walk_back consumes 697..0 (decreasing) -> every sign needed both early and late ->
  all 698 simultaneously live at the terminal replay. That is the 698.
- walk_back_round is PASSED sigma_r (drives reverse add), then recomputes sigma from
  restored operands to zero+free the wire. It does NOT self-generate sigma.

## Prior KILLs (evidence, adjacent lanes)
- KILL-RETAINED-SPLICE-CANONICAL: retained 256-bit denominator word gives exact
  sigma for rounds 1..7 only; ANF of sigma_r vs ORIGINAL denominator explodes
  (2,2,5,11,25,57,115,244,481,1001,2013,4041,8177,16433 terms through sign 14).
  6/696 divide, 0/694 multiply. No sign source past round 7.
- KILL-SIGN-CHECKPOINT-BOUND: conventional checkpoint/recompute materializes (u,v);
  first missing sign at round 8 needs walk width 258 -> Q1284 floor (>1114 target,
  and >1274). Counterfactual no-persistent-checkpoint k=3 replay = 57,027,954 T.
- Both name the SAME next family: an in-place algebraic retained-word transducer
  whose state never expands to raw (u,v) and whose per-epoch inverse is explicit.
  That is THIS lane's objective.
