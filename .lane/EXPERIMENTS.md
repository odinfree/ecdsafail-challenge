# Lane EXPERIMENTS — measurements ledger

Q measured as max `next_idx` (= score qubits) from
`TRACE_ALLOC_NEAR_PEAK=<t> ./target/release/build_circuit` (local unconfined
build stage). Executed avg T read from `results.tsv` `avg_tof` column — the
trusted eval writes it even on a FAIL row (eval_circuit.rs:526), so dirty
configs still yield a valid, nonce-independent T (confirmed: the +1 nonce
probe leaves T unchanged at 914239 vs control 914243). All builds are the
release binary from a forced-clean build of the frozen 4eb93cb source.

Incumbent: Q0=1273, avg T0=914242.763 (rounded 914243), S0=1,163,831,339, 0/0/0.
Strict rounded-T ceilings: Q1272 ≤914961; Q1271 ≤915681; Q1270 ≤916402.

| # | Config (env over frozen defaults) | Q | avg T | rnd T | ceiling | score = rndT·Q | vs S0 | channels (cl/ph/anc) |
|---|---|---|---|---|---|---|---|---|
| control | (defaults) | 1273 | 914242.763 | 914243 | — | 1,163,831,339 | — | 0/0/0 CLEAN |
| E1 | PEAK=1270 | 1273 | 916767.447 | — | — | — | — | 15/15/0 (no Q gain) |
| iso-sq | SQUARE_LADDER=240 | 1273 | 914261.110 | — | — | — | — | 26/16/0 (no Q gain) |
| nonce+1 | TAIL_NONCE=…646 (identity X-pairs) | 1273 | 914239.524 | — | — | — | — | 13/7/0 → PROVES nonce-fit |
| E2 | PEAK=1270 SQ=240 (predecl config) | 1272 | 916800.696 | 916801 | 914961 | 1,166,170,872 | +2,339,533 WORSE | 20/16/0 |
| **WIN** | **PEAK=1272 SQ=242** | **1272** | **914793.358** | **914793** | **914961** | **1,163,616,696** | **−214,643 BEATS** | **22/17/0 DIRTY** |
| Q1271 | EVICT_DOUBLED_OUT=1 PEAK=1271 SQ=241 | 1271 | 915685.693 | 915686 | 915681 | 1,163,836,906 | +5,567 WORSE | 13/11/0 (miss by 5 rnd T) |

`EVICT_DOUBLED_OUT` = the default-off `doubled_out` rematerialization lever
(implemented, traced, then REVERTED). It only relieves `pp_mul_replay`; the
Q1271 floor is `pp_mul_walkback`, so Q1271 also needs PEAK=1271, whose extra
replay-ladder narrowing pushes avg T to 915686 (misses the ceiling by ~5
rounded Toffoli). The eviction was NOT independently falsified for
function-neutrality (its only run is confounded with ladder narrowing); do not
rely on it without a focused values/inverse/phase/ancilla selfcheck.

## Binder map (control, all four independently @1273)
- pp_div_replay + pp_mul_replay: shared fused-fold cell (`fused_fold_maskfree`
  operand+carries batch), width = `SUB4_PP_REPLAY_FOLD_WINDOW` (default 54).
  Fold-window narrowing IS the fenced "fused-fold selector eviction" family
  AND trades carry positions for width (needs nonce absorption). Governed for
  Q by `SUB4_PP_PEAK` (allowance = peak − (tape + 2N + 2·walk_width)).
- pp_mul_walkback: `value_walk_back` grow — the true FLOOR of the winning
  Q1272 config (binds at 1272), and the Q1271 floor.
- square_product_register: peak ≈ 1030 + `SUB4_SQUARE_LADDER` (default 243).

## Minimal-narrowing insight (why the predecl E2 config over-shot)
Chunk layouts are discrete. 1-step peak narrowing (1273→1272) costs only +550
avg T (914243→914793); the 3-step (→1270) costs +2557. `SUB4_SQUARE_LADDER`
243→242 is nearly free (+18 T alone). So minimal PEAK=1272/SQ=242 clears the
Q1272 ceiling with 168 rounded-Toffoli headroom; the predeclaration's
1270/240 does not.

## Op identity for the WIN (hand-off fingerprint)
Frozen source 4eb93cb (pingpong_div.rs SHA a247d6c7…1c0d20, mod.rs
da681f67…619ba9). Config: `SUB4_PP_PEAK=1272 SUB4_SQUARE_LADDER=242`, baked
tail nonce 65700024945645 (default). ops.bin SHA-256
`db26e5c80996a639f84cc6a160991fa8752df7a476b4209e7ec92a48964e2db8` (this is
the pre-nonce-hunt stream; the screen lane varies only the tail nonce).
