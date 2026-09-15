# lane_refreeze status — Q792 refreeze + validation + submission

Owner: `/root/lane_refreeze` (deepseek-v4-pro, max, Codex). Route:
`lane_refreeze_submit` (composition) in `runtime/coordination.sqlite3`.

## Tree and configuration

- Worktree: `worktrees/lane_refreeze`, branch `codex/lane_refreeze`, base
  `6dfe5996` (4-hole Q792 whole-count), plus:
  - terminal coefficient-head fix: h0 = `work1[254]` under `four_hole()`
    (phase-1 head stays `work2[257]`). The w2[257]/w2[258] variant was
    falsified: 64/64 classical failures + phase=0xbdc9cb0a.. in two
    independent 64-shot streams (with and without the INV16 fix);
  - `q793_exit_low.rs` INV16 table fixed to the true mod-16 inverses
    (5->13, 13->5; the shipped table had 5->5, 13->11, breaking the reachable
    A=253(u=5)/A=252(u=13) forced-chart cases);
  - baked defaults `LOWQ_Q792_EEA=1`, `Q792_QUOTIENT_TOP_BORROW=1`
    (`src/point_add/mod.rs`);
  - refrozen `codex10h_resources()` -> `(1_296_419_964, 747_320_144)` for the
    four-hole+borrow combo (measured on the INV16-fixed whole-stream at
    laneT-reduce `37dff749`; the head retarget only moves CX operands and
    cannot change op counts); `candidate_configuration()` accepts exactly that
    combo (`q793_lifecycle_r03.rs`);
  - dev-only sentinel scans (sprint marker scan + `push_op` leak check) that
    are inert on the production emit path.
- Build: `target-lane-refreeze`, `cargo build --release --locked --offline
  --bin build_circuit` — PASSED at 12:44Z (w1[254]+INV16+refreeze).

## Gate chain (all run with NO environment flags set)

1. whole-count  -> PASSED 12:02Z on the pre-fix stream (w2 variant):
   `peak_qubits=792 ops=1369818684 structural_T=820699472` exact with NO env
   flags. The w1[254]+INV16 stream must now re-pin
   `peak=792 ops=1296419964 structural_T=747320144` via its own drift asserts
   (the stream prints the whole-resource census before asserting).
2. whole-stream (w1[254]+INV16) -> 64 shots, `classical_failures=0 phase=0x0
   dirty_ancillas=0`. STARTED 12:45Z. Log:
   `runtime/refreeze-q792-stream-w1inv16.log`.
3. whole-9024   -> all 9024 compact shots pass (only if time remains).
4. Freeze: commit source; hash src/point_add + artifact.
5. Submit under the shared `submission` lock; note at
   `runtime/q792-submission-note.md` (draft ready, 6.1 KiB).

## Live frontier (re-checked 11:19Z, 917 metric rows / 30 nondominated)

- Q792 `cf39122` T=893,988,754 (bulengerk) — candidate structural T=747,320,144
  dominates.
- Q793 `2dc9b2b` T=671,563,551 (welttowelt). No row at Q<=791.

## Coordination notes

- Heavy lock: held by `lane_refreeze build:refreeze-q792` since 11:34Z. NOTE:
  laneVerify-head reported the T_REDUCE job may still have been alive at
  11:37Z when I reconciled it at 11:33Z; my ps evidence was flawed. Flagged
  as a discipline error; no data was harmed (advisory lock only).
- Queue #13 = this lane's build.
- Deadline 13:35Z (window 2). If gates 2/3 cannot both complete in time, the
  frozen artifact + note + receipts are the handoff; do not submit past the
  deadline without a fresh user order.
