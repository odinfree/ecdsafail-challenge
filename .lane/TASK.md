# Q1272 fused-fold selector-eviction implementation lane

Predeclared: 2026-08-23, before any candidate source edit, build, or output.

## Scope and identity

- Work only in this isolated worktree and branch.
- Exact base: `9e8c948e012ba92ccf2ab8cedfa77c6b8ead9f08`.
- Source model: hard-coded B1=24 inherited from `6f6da43`.
- Frozen geometry: `SUB4_PP_PEAK=1272`,
  `SUB4_SQUARE_LADDER=242`; all rounds, R1/R2, widths, slopes, BREAK_2,
  replay windows, and tape depth remain unchanged.
- Protected D1272 artifact: 12,904,991 operations, SHA-256
  `0ce4aac781957c12b2fb2217cb116a68fe77e74ad810a73cfd1a1f4450fa0e20`,
  measured Q1273/T914726.434 and 25/20/0.
- Live threshold frozen by dispatch for a Q1272 strict beat: rounded
  T <= 919105. Reopen live before any final score claim.

No predictor, nonce corpus, range, scan, hunt, provider action, submission,
public note, or incumbent edit. Exploratory source may be permissive, but every
reported result uses the exact gates below.

## Overturn ledger

| assumption | wall it creates | overturn observation | cheapest falsifier |
|---|---|---|---|
| The derived `sign_and_parity` selector must remain live from `plus_2f` construction through the complete 53-bit fused fold | terminal division replay is 1,214 fixed wires + 59 fold wires = Q1273 | erase that derived selector immediately after `plus_2f`, run the fold with 58 scratch wires, and reconstruct the selector only for `plus_2f` uncompute | one opt-in lifecycle edit plus focused selector/fold miter and allocator census |
| Long-lived replay/tape-derived state is cheaper to retain than to reconstruct | the tape/fold saddle cannot descend even though the selector is a two-CX function of still-live controls | exact recomputation preserves value, phase, and ancilla while exchanging a few Clifford gates for one peak qubit | compare protected opt-out identity, 64-lane exact component/point-add tests, then owner profile |

This is the single authorized family. Do not respond to a failure by changing
fold width, rounds, R1/R2, tape length, another selector, or arithmetic
semantics. Freeze the first failure and close the family.

## Frozen implementation

Add one default-off env opt-in, named
`SUB4_PP_FOLD_SELECTOR_EVICT=1`, only in
`signed_mod_add_pm_halve_fused`:

1. construct `sign_and_parity` and `plus_2f` exactly as protected;
2. immediately reverse the two CX operations that created
   `sign_and_parity`, prove/free the zero qubit, and enter
   `fused_fold_maskfree` without it live;
3. after the fold, allocate a zero qubit and reconstruct
   `sign_and_parity` from the same still-live controls;
4. use it to measurement-uncompute `plus_2f`, then reverse/free it exactly as
   protected cleanup already does;
5. change no Toffoli-bearing arithmetic and add no Hmr/CZ/R except the normal
   proven-zero allocator release required by the lifecycle.

The expected exchange is one peak qubit for zero executed Toffoli and a small
fixed Clifford increment. At T about 914.7k, one qubit is worth about 719 T at
constant product; the live Q1272 gate leaves about 4,379 rounded-T headroom.

## Gate order

Stop at the first failure.

1. Clean release build.
2. Protected opt-out reproduction: exact operation count/SHA above and Q1273.
3. Focused exact selector/fold falsifier covering all reachable control arms,
   including value equality, full phase mask 0, and every non-output ancilla 0.
   A new env-gated micro-selftest is allowed but must be durable only if useful.
4. Candidate operation count/SHA and allocator census. Required owner result:
   complete circuit Q1272, with `pp_div_replay` <=1272 and square/multiply
   owners <=1272. Record the exact source-line live set.
5. Existing product-square selftest and complete 64-lane point-add selftest:
   exact values, phase 0, ancilla 0, owner peaks Q1272.
6. Unchanged full 9,024-shot evaluator. Require ancilla 0 and rounded
   T <= 919105; record classical/phase counts and the first reported failure.
   A dirty architecture remains `HOLD_HUNT`, never a submission candidate.
7. Restore tracked generated files; exclude `ops.bin`, binaries, caches, logs,
   temporary evaluators, and generated result/score rows. Commit and push only
   durable source and evidence with a clean/upstream branch.

## Model lane

Implementation is assigned to Claude Fable 5 at high effort, with Opus as the
fallback model. The task must receive Matt/Teddy's structural direction:
remove or reconstruct live tape-derived state instead of narrowing another
ladder. Credit is provenance, not a substitute for the exact gates above.
