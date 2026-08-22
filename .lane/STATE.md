# Burn explorer: stream the ping-pong history

Created: 2026-08-22
Source: `6b5c82c`
Branch: `research/fable-burn-6b5c-stream`
Status: descent run to a measured KILL; protected leader untouched
Result: O(1)-retained streaming representation KILLED on `6b5c82c`. See
`.lane/EVIDENCE-BURN-SLICE-6B5C82C.md`.

Model: Kimi Code (k2/k3, high effort), multi-lane agent campaign.
Worker: Claude Fable 5, xhigh effort.

## Protected leader

- Live source: `6b5c82c`.
- Trusted metrics: Q1278 / rounded T918358 / score1173661524.
- Objective: `round(avg_executed_toffoli) * peak_qubits`, strictly lower wins.
- Trusted contract: forced clean build, then unchanged 9,024-shot evaluator with
  classical/phase/ancilla all `0/0/0`.
- This explorer cannot hunt, spend provider credit, push, publish, or submit.

## Overturn

Wall: replay carries a resident sign history plus restored walk state. Literal
full-word checkpoints, materializing decoders, and current-walk Bennett
recomputation are killed on measured width or Toffoli economics.

Assumption to overturn: exact replay requires one persistent sign qubit per
round, or a full walk/checkpoint state materialized at peak.

Overturn condition: a bounded streaming representation reconstructs and clears
the next replay symbol from state already live at walkback, with fixed scratch
and no growth in retained state across rounds.

Cheapest falsifier: build an exact 4-8-round nonzero-numerator reference slice
with forward replay, reverse replay, walk restoration, and phase/ancilla cleanup.
Measure retained-state growth before extrapolating. Kill any representation that
needs O(rounds) new state or a full 256-bit checkpoint at the replay peak.

## Target direction and saddle budget

- First invariant: max one reconstructed symbol live and fixed scratch across
  the bounded slice; reference/candidate continuation identical.
- Component target: Q<=1148 before composition with the sparse square.
- Current complete-circuit strict ceilings: Q1182 T<=992945; Q1148 T<=1022353.
- Budget: three different representation falsifiers or four hours. A failed
  low-five/full-word encoding does not kill other state representations.

## Outcome (2026-08-22)

Built an exact bounded slice on `6b5c82c` (walk round-trip verified EXACT at
K=4,6,8; full walk→replay→inv-replay→walkback measured) and ran a
reachability-aware collision search on the real walk. Findings:

- **Retained state is O(rounds)** — tape grows exactly 1 sign/round, live
  continuously from `value_walk` through `value_walk_back` (measured). This is
  the STATE kill trigger directly.
- **Minimum decoder-visible state = `(u_{r+1}, v_{r+1})`** at the walkback
  instant (divide frees the coefficient before walkback). `sign_r` is NOT a
  function of it: the walk step is two-to-one, and the un-add needs `sign_r`
  before it can be recomputed (circular).
- **Collision search:** wide bulk (rounds 0–~550) shows no local collision
  (birthday floor; ambiguity is global, not local); transition zone shows
  **22 reachable sign-disagreements at round 600 (width 46), 8 at round 650** —
  a bounded state-keyed decoder demonstrably cannot regenerate `sign_r`;
  converged tail (rounds ≥680) is locally decodable (Teddy's shared-sign,
  same-Q Toffoli lever only).
- **Free-oracle / co-binder wall:** promoted peak = `pp_div_replay`@Q1278
  (PP_PROFILE, on-`6b5c82c`); the three-way Q1278 co-binder tie (prior,
  `a9af194`) means a divide-only streaming oracle cannot cut peak Q even at
  zero cost.

**KILL** the O(1)-retained streaming representation. Sub-linear retained state
requires a ≥254-bit global reachable-set decoder = the Q1376 checkpoint route
already killed on width (`9805dee`), not the O(1) scratch the overturn demands.

## Reopen gate

A decoder that regenerates `sign_r` without a resident predecessor register,
simultaneously across all three Q1278 co-binders. The transition-zone
sign-disagreements (round 600, width 46) are the precise obstruction such a
construction must defeat. No such construction is exhibited here.

Harness lifecycle: the `SUB4_PP_BURN_SLICE` harness was a temporary
source-bound evaluator. After measurement it was REMOVED from working source —
`src/point_add/mod.rs` and `src/point_add/pingpong_div.rs` restored
byte-for-byte to exact `6b5c82c` (`git diff 6b5c82c -- src/` empty). The
harness is preserved in git history at commit `2b0bd4c`; reproduce
instructions live in `.lane/EVIDENCE-BURN-SLICE-6B5C82C.md`. Post-restore
receipt: gate-off build emits 12,950,916 operations, `ops.bin` SHA256
`88706a40300b7f019202f65a0f28e86dbfe27fda65ad5ed33b0482ff9b14b7eb`.
