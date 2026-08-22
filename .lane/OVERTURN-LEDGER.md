# Exact-live sparse-square overturn

Updated: 2026-08-22

## O-003 — product-square zero pads are physical qubits

- Status: **OVERTURNED / HOLD FOR COMPOSITION**.
- Protected source: `6b5c82cbe723b33c296c8926876f14f1ac3307a8`.
- Protected score: `1278 * 918358 = 1173661524`, trusted `0/0/0`.
- Teddy Pender's tape re-descent exposed `square_product_register` as one of
  three independent Q1278 binders. The square's `tri_corr` path materialised
  two 129-wide layouts whose zero positions were represented by real qubits.
- Exact overturn: the env-gated sparse ripple accepts `Option<QubitId>`
  operands, so structural zeroes do not stay live across the carry peak. The
  measured boundary carry is erased by the existing exact comparator.
- Gate: `SUB4_SQUARE_TEDDY_SPARSE_TRI_CORR=1`.
- Transfer proof: the complete
  `src/point_add/trailmix_ludicrous/square/product_register.rs` file is
  byte-identical between ancestor `7ca0559` and exact source `6b5c82c` before
  this port.
- Exact-live standalone receipt: Q1278 to **Q1148**, emitted T
  `58879 -> 60693`, deterministic-64 executed T
  `58678.203 -> 59597.625`, value/phase/ancilla `0/0/0` on both paths.
- Exact-live full-affine diagnostic: global Q stays 1278 because replay still
  binds; emitted T `959995 -> 961809`, deterministic-64 executed T
  `918375.469 -> 919387.469`, value/phase/ancilla `0/0/0` on both paths.
- Default-path invariant: gate off emits `12950916` operations and preserves
  SHA-256 `88706a40300b7f019202f65a0f28e86dbfe27fda65ad5ed33b0482ff9b14b7eb`.
- Economics: at composed Q1148 the strict rounded-T ceiling is `1022353`; at
  the first global saddle Q1182 it is `992945`. The sparse route is not a
  current Q1278 score candidate, so no nonce hunt or full 9024-shot run is
  justified.
- Verdict: preserve the exact Q1148 component. Do not spend time on narrower
  approximate boundary compares before the replay family moves.
- Next saddle: combine this square with the compact 280-`u/v` checkpoint,
  fixed-scratch history stream, and symmetric multiply teardown. Re-profile
  `pp_div_replay`, `square_product_register`, `pp_mul_walkback`, and the Q1276
  `pp_mul_replay` near-binder; require complete-circuit Q<=1182 and rounded
  T<=992945 before any grind.

No provider, hunt, spend, submission, push, generated evaluator, `ops.bin`, or
build artifact belongs to this worktree.
