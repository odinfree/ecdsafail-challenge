# Q1272 fused-fold selector eviction — implementation result

Updated: 2026-08-23. Implementation lane per `.lane/TASK.md` (predeclared
`SUB4_PP_FOLD_SELECTOR_EVICT` lifecycle family). Model: Claude Fable 5, high
effort. Claude delivered the source uncommitted; Codex independently
reproduced and seals it below.

## Decision

`GO_Q1272 / ALL_GATES_PASS / HOLD_HUNT / LIVE_REOPEN_CONFIRMED`

The predeclared selector eviction lands Q1272 on the complete circuit with
zero Toffoli change. All frozen measurement gates passed in order; no gate failure, no
rescue tuning, no other selector/window/round/R1/R2/width/arithmetic change.
The architecture inherits the dirty nonce (18/13/0), so it is `HOLD_HUNT`,
never a submission candidate. Codex reopened the benchmark at
2026-08-23T07:00Z: live remains source `b523ecf`, score 1,169,101,620, so the
strict Q1272 rounded-T ceiling remains 919,105. No provider, hunt, or
submission action was taken.

## Source change (exact)

Only two files changed (+227 lines, all default-off-gated or selftest):

- `src/point_add/pingpong_div.rs`
  (`de5e347383a9bab4d76a2776b3bcee4bebda4fecb65beb3dd1ad4c1cbf4c1095`):
  - `fold_selector_evicted()` — reads `SUB4_PP_FOLD_SELECTOR_EVICT=1` per
    call, default off;
  - in `signed_mod_add_pm_halve_fused` only: after `plus_2f` is created
    exactly as protected, reverse the two CX that created `sign_and_parity`,
    `free` the proven zero (one allocator R), run `fused_fold_maskfree`
    without it live, then re-allocate and reconstruct it from the still-live
    `parity`/`not_sign_and_parity` controls; protected cleanup then runs
    unchanged. Per call: +4 CX +1 R, 0 Toffoli, 0 Hmr/CZ;
  - `fold_selector_evict_selftest()` — focused exact falsifier (gate 3).
- `src/point_add/mod.rs`
  (`3106691965fbd0002fc0dc427e07f28f30654be49b748beb08d93b30c21db490`):
  env hook `SUB4_PP_FOLD_SELECTOR_EVICT_SELFTEST=1` next to the existing
  pingpong selftest hooks; no-op otherwise.

Protected path is bit-identical when the flag is off (gate 2 SHA proof).
Unchanged evaluator source: `src/bin/eval_circuit.rs`
`b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`; lib
`sim.rs`/`circuit.rs`/`lib.rs`/`weierstrass_elliptic_curve.rs` untouched.

## Gate log (frozen order, all PASS)

Base `9e8c948` + predeclaration `71a5aae`; worktree clean except the two
source files above. All artifact builds used
`SUB4_PP_PEAK=1272 SUB4_SQUARE_LADDER=242` and (candidate only)
`SUB4_PP_FOLD_SELECTOR_EVICT=1`.

1. **Clean release build** (`cargo clean` then
   `cargo build --release --locked --offline --bin build_circuit --bin
   eval_circuit`):
   `build_circuit`
   `982cad04f614297c00c4ee70f5750e975e4e43bf979c03d4e42ae7a01b2f46eb`,
   `eval_circuit`
   `25f14502ab636fd5647a0e7118a2106b50c29bc421f1fb99cbbeb6db0282bc98`
   (binary hash differs from the prior lane's only via worktree path
   embedding; evaluator SOURCE hash matches the protected identity above).
2. **Protected opt-out reproduction**: 12,904,991 ops, `ops.bin` SHA-256
   `0ce4aac781957c12b2fb2217cb116a68fe77e74ad810a73cfd1a1f4450fa0e20`
   (byte-exact vs the protected D1272 artifact), unchanged evaluator header
   Q1273; full 9,024-shot run reproduced 25/20/0 and T914726.434 exactly.
3. **Focused falsifier** (`SUB4_PP_FOLD_SELECTOR_EVICT_SELFTEST=1`): builds
   the standalone fused-halve cell protected and evicted under the
   terminal-replay ladder budget 58; PASS — 64/64 lane values exact against
   the classical `((t±s)/2) mod p` model AND lane-for-lane between the two
   lifecycles, phase mask 0 and every non-input ancilla 0 on both streams,
   all 8 reachable (sign, overflow, parity) selector arms exercised
   (greedily sign-assigned generic lanes; coverage asserted), Toffoli
   emitted identical, delta exactly +4 CX +1 R, standalone peak 572 → 571.
4. **Candidate artifact + census**: 12,908,488 ops, `ops.bin` SHA-256
   `678c149f65ce00cd44caada6a534817e8b69f993913c509a8b396b6f526c22f0`.
   Owner profile (`PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1`): complete
   circuit Q1272 (peak at ops idx 2,232,972, phase `pp_div_replay`);
   `pp_div_replay` 1272, `square_product_register` 1272, `pp_mul_replay`
   1272, `pp_mul_walkback` 1272; profile composition 64/64 exact, phase 0,
   dirty 0. Emitted Toffoli bit-identical to protected: 956,626 CCX +
   28 CCZ. Exact source-line live set at the peak
   (`B0_WIN_LO=2232900 B0_WIN_HI=2233050`), rows sum to 1,272:

   | live | owner | role |
   |---:|---|---|
   | 297 | `pingpong_div.rs:1067` (pp_div_walk) | pre-replay walk signs |
   | 1 | `pingpong_div.rs:1067` (pp_div_replay) | interleaved walk sign |
   | 1 | `pingpong_div.rs:519` | fused round-zero sign |
   | 256 | `pingpong_div.rs:2005` | caller numerator register |
   | 256 | `pingpong_div.rs:261` | replay coefficient register |
   | 163 | `pingpong_div.rs:2004` | walk register u (width 163) |
   | 163 | `arith/adder.rs:341` | walk register v (width 163) |
   | 134 | `pingpong_div.rs:753` | split walk-add high-chunk carries |
   | 1 | `pingpong_div.rs:712` | split walk-add boundary carry |

   The binding instant moved from the terminal fused fold (protected: base
   1,214 + 59 = 1,273 at idx 4,257,060) to the `Plan::peak`-budgeted
   interleaved walk-split region at exactly the requested 1,272; the fold
   cell now holds 58 scratch wires. Op delta fully attributed: 698 divide
   replay fused calls × 5 lifecycle ops = 3,490, plus 7 Clifford ops in
   `pp_div_restore` (1,141 → 1,148; the allocator free-pool order shifts
   `restore_wire_layout`'s exact swap sequence), total +3,497, +0 Toffoli.
5. **Existing selftests under candidate env**: product-square PASS, 64/64
   exact, phase 0, ancilla 0, 58,980 emitted / 58,721.141 executed T, peak
   Q1272; complete 64-lane affine point-add PASS, 64/64 exact, phase 0,
   ancilla 0, 956,654 emitted / 914,816.203 executed T, Q1272.
6. **Unchanged full 9,024-shot evaluator** on the candidate `ops.bin`:
   Q1272; classical 18, phase 13, **ancilla 0**; avg T 914,727.660 →
   rounded 914,728 ≤ frozen 919,105 (headroom 4,377). First reported
   failure: `PHASE GARBAGE: global_phase = 0x0040000000000000 across 64
   live shots` (inherited dirty nonce; expected; `HOLD_HUNT`). Receipt row
   captured then `results.tsv` restored to protected SHA
   `eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`.
7. **Cleanup**: `ops.bin`, `score.json`, and result rows removed/restored;
   no binaries, caches, temporary evaluators, or logs in the tree; nothing
   staged.

## Independent Codex reproduction and provenance seal

At 2026-08-23T07:00Z Codex discarded the prior build products with
`cargo clean`, rebuilt `build_circuit` and `eval_circuit` with
`--release --locked --offline`, and independently reran the frozen gates from
the source diff. The protected artifact reproduced byte-exact at 12,904,991
operations / `0ce4aac781957c12b2fb2217cb116a68fe77e74ad810a73cfd1a1f4450fa0e20`,
Q1273/T914726.434, 25/20/0. The candidate reproduced byte-exact at 12,908,488
operations / `678c149f65ce00cd44caada6a534817e8b69f993913c509a8b396b6f526c22f0`,
Q1272/T914727.660, 18/13/0. The selector miter, square selftest, point-add
selftest, complete owner profile, and nine-group peak census all reproduced
the results above. Release binary hashes were
`982cad04f614297c00c4ee70f5750e975e4e43bf979c03d4e42ae7a01b2f46eb`
(`build_circuit`) and
`25f14502ab636fd5647a0e7118a2106b50c29bc421f1fb99cbbeb6db0282bc98`
(`eval_circuit`); evaluator source remained protected at
`b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`.

Provenance verdict: acceptable with the adaptive corpus repair disclosed, not
silently treated as byte-identical predeclaration. The first adversarial
`p-2` corpus made the protected approximate arithmetic phase-dirty before any
candidate simulation or full-evaluator result existed. It was replaced once
with a deterministic SHAKE-labelled generic corpus whose eight selector arms
are asserted. The candidate was not measured before that repair, and no
result-conditioned lane selection or rescue source edit followed it. The
frozen protected SHA, candidate SHA, unchanged evaluator, independent rerun,
and exact focused parity therefore support the structural conclusion; the
upcoming source-bound H64 gate must still characterize density independently.

## Pricing

At constant product, one qubit ≈ 719 T here. Candidate vs protected D1272:
−1 qubit for +1.226 average executed T (input-drift only; zero emitted
Toffoli change). Score at measured Q: 914,728 × 1,272 = 1,163,534,016 —
252,768 below the D1273 structural row (1,163,786,784) and 5,567,604 below
the freshly reopened live best (1,169,101,620 at 2026-08-23T07:00Z).

## Critique–fix–verify audit

- **Critique 1**: first falsifier draft used adversarially degenerate crafted
  lanes (`p−2`-style operands, tied 20-bit top windows) to force selector
  arms; the truncated measured-erasure repairs are only exact on generic
  values, so the PROTECTED stream itself showed phase garbage (mask 200,
  shots 3/6/7 — the o=1 crafted lanes). **Fix**: derive arm coverage from
  generic pseudorandom lanes with greedy sign assignment; coverage asserted,
  not assumed. **Verify**: falsifier passes with all 8 arms and phase 0 on
  both lifecycles.
- **Critique 2**: a `#[cfg(test)]` harness entry was unusable — the repo's
  `cargo test` target has ~165 pre-existing compile errors in stale tests.
  **Fix**: wired the selftest through the established env-gated hook in
  `build()` instead. **Verify**: hook is a no-op unless set; protected SHA
  reproduction (gate 2) proves stream identity with the hook present.
- **Critique 3**: op-count delta (+3,497) was not the naive 698×5 = 3,490.
  **Fix/verify**: attributed exactly — +7 Clifford ops in `pp_div_restore`
  from the shifted free-pool order; per-phase profile confirms Toffoli
  bit-identical and the composition selftests prove the restore is exact.
- **Critique 4**: standalone-cell peak would not expose the eviction (the
  default 96-wide chunk ladder dominates the fold). **Fix**: falsifier pins
  `set_ladder(58)`, the terminal-replay allowance, making the fold the
  binding allocation. **Verify**: peak 572 → 571 asserted.

## First blocker

None. No frozen gate failed; no failed source experiment remains in the tree.
