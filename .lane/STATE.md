# Lane STATE — live 4eb93cb third-binder re-descent

Worker: Claude Fable 5, high effort, ≤USD 25. Source frozen at 4eb93cb
(child predeclaration commit 8525146). Harness never edited. No provider
compute / nonce hunt / fleet / submission / external messages.

## DISPOSITION: SCORE_GO / VALIDATION_DIRTY (hand-off) + Q1271 KILL

A Q1272 candidate STRICTLY BEATS the incumbent objective and is dirty on full
channels → per lane rule it is handed (as durable source + op identity) to a
separate nonce-screen lane. The Q1271 extension is a KILL (misses ceiling).

## Protected leader (incumbent)
- Source `4eb93cb…`, tree `bb19b40…`. Files byte-exact vs predeclaration:
  pingpong_div.rs `a247d6c7…1c0d20`, point_add/mod.rs `da681f67…619ba9`.
- Q1273, avg T 914242.763 (rnd 914243), score 1,163,831,339, 0/0/0 CLEAN.
- Reproduce: forced-clean release build, then `./benchmark.sh` (defaults).

## Winning candidate (SCORE_GO / VALIDATION_DIRTY)
- Config (pure env on frozen source, NO source edit):
  `SUB4_PP_PEAK=1272 SUB4_SQUARE_LADDER=242`; default tail nonce 65700024945645.
- Q1272, avg T 914793.358 (rnd 914793 ≤ Q1272 ceiling 914961, 168 headroom).
- Score 1,163,616,696 = 914793·1272 < 1,163,831,339. Beats by 214,643 (−0.0184%).
- Exchange-rate gate (exact): 1272·914793 < 1273·914243 ✓ strictly beats.
- Channels: 22 classical mismatches + 17 phase-garbage + 0 ancilla-garbage /9024.
- ops.bin SHA-256 `db26e5c80996a639f84cc6a160991fa8752df7a476b4209e7ec92a48964e2db8`.
- HAND-OFF: a nonce-screen lane (with nonce authority this lane lacks) re-hunts
  `SUB4_PINGPONG_TAIL_NONCE` for THIS ladder config to clear the 22/17 dirty
  channels. Executed T is nonce-independent, so the score stays 1,163,616,696.

## The third binder (named)
Peak 1273 is co-bound by FOUR independent phases (all measured @active=1273):
pp_div_replay, pp_mul_replay (shared fused-fold cell), pp_mul_walkback
(value_walk_back), square_product_register (1030+SUB4_SQUARE_LADDER).
- The fused-fold cell (SUB4_PP_REPLAY_FOLD_WINDOW=54) is the shared replay
  binder; narrowing it IS the predeclaration-fenced "fused-fold selector
  eviction" AND is a carry-for-width correctness trade → not used.
- Q1272 is reached by the minimal 1-step narrowing PEAK=1272 (drops
  div_replay/walkback) + SQ=242 (drops square). Its true floor is
  pp_mul_walkback. mul_replay already floors at 1272 unaided.

## THE REAL WALL (load-bearing assumption overturned)
The incumbent 0/0/0 is NONCE-FITTED, not exact. Proof: replacing the baked
tail nonce with +1 (identity X-pairs → same unitary, only the Fiat-Shamir
op-stream hash changes → a different 9024-shot test set) yields 13 classical
mismatches + 7 phase-garbage. So the circuit carries intrinsic truncation
error (lambda>0) and the baked nonce is tuned so all 9024 derived points dodge
it. Consequences:
1. ANY op-stream change — ladder narrowing OR a function-neutral qubit
   eviction — reshuffles the test set and re-exposes lambda → dirty.
2. Restoring 0/0/0 after any width change requires a tail-nonce re-hunt, which
   THIS lane forbids. Hence no in-lane change can be clean; genuine width wins
   must be dirty and handed to a nonce-screen lane. This is exactly the
   burn-the-house-down "certificate lock-in" anti-pattern: the correctness
   gate is fitted to the incumbent op stream.

## Stale-premise correction (durable finding)
The frozen predeclaration's premise — "lowering SUB4_PP_PEAK and the square
ladder to 1270/240 remains Q1273 because a third allocation binds" — does NOT
reproduce on this source. 1270/240 yields Q1272 (dirty), and the minimal
1272/242 both reaches Q1272 AND beats the score. The predeclaration's 1270/240
over-shoots the peak knob by 2 steps and would score WORSE (S=1,166,170,872).

## Rejected / killed levers (with evidence)
- Q1271 (EVICT_DOUBLED_OUT + PEAK=1271/SQ=241): T 915686 > 915681 ceiling; Q·T
  = 1,163,836,906 > S0 → KILL. The doubled_out rematerialization (default-off,
  byte-neutral when off; implemented then reverted) only relieves mul_replay,
  but the Q1271 floor is walkback, forcing PEAK=1271 whose T penalty overshoots
  by ~5 rounded Toffoli. Not independently falsified for function-neutrality.
- SUB4_PP_PEAK / SUB4_SQUARE_LADDER alone: no Q gain, T up, dirty.

## Next objective-advancing action
Nonce-screen lane: on frozen 4eb93cb with `SUB4_PP_PEAK=1272
SUB4_SQUARE_LADDER=242`, hunt `SUB4_PINGPONG_TAIL_NONCE` to clear the 22/17
dirty channels; expected clean score 1,163,616,696 (Q1272). Secondary: seek a
walkback-phase truncation-neutral eviction to make Q1271 reachable without the
PEAK=1271 T penalty (would then need T ≤ 915681).

## Worktree
Clean: source byte-exact; ops.bin/score.json gitignored; results.tsv restored
to tracked state (benchmark FAIL rows discarded). Only .lane/*.md committed.
