# Burn-the-House-Down: streaming ping-pong history — exact slice + collision falsifier

Source: `6b5c82c` (promoted, untouched). Date: 2026-08-22.
Worker: Claude Fable 5 (xhigh). Harness: `SUB4_PP_BURN_SLICE=1 ./target/release/build_circuit`.
Methodology: Teddy Pender's Burn-the-House-Down doctrine — overturn ledger,
cheapest-falsifier-first, grant-the-hypothesis-impossible-advantages,
map-every-co-binder, grind-last, attack-or-replace the sign tape.

## Overturn under test

Resident assumption: exact ping-pong replay requires one persistent sign qubit
per round, or a full walk/checkpoint state materialised at the replay peak.

Overturn condition (the win we were hunting): a bounded streaming
representation that reconstructs and clears the *next* replay symbol from state
already live at walkback, with **fixed scratch** and **no growth in retained
state across rounds**.

Kill trigger (from `.lane/STATE.md`): O(rounds) retained growth, or a full
256-bit checkpoint at the replay peak.

## Verdict: KILL the O(1)-retained streaming representation on `6b5c82c`

The retained sign tape is O(rounds) by direct measurement, and the sign is not
recoverable from the live walk state by any bounded (state-keyed) decoder
except in the fully-converged terminal tail. Sub-linear compression demands a
global reachable-set decoder holding ≥254 resident bits — the checkpoint route
already killed on width (Q1376 production splice, `9805dee`). This is not the
O(1) scratch the overturn requires. The convergent-tail region *is* locally
decodable (Teddy's shared-sign thesis) but that is a same-Q Toffoli lever, not
a peak-qubit cut, and it does not touch the O(rounds) bulk.

## What was built (exact, convergence-free, real modulus + width schedule)

A bounded slice on the live primitives (`value_walk`, `replay_halving`,
`replay_doubling_inverse`, `value_walk_back`), driven by a research-only gate
that never runs in a normal `build()`:

- **Exact anchor** — `value_walk(K)` ∘ `value_walk_back(K)`. The walk adder's
  boundary comparison is an identity (not a windowed approximation), so this is
  exact on ALL inputs with no convergence requirement. Asserted at K=4,6,8:
  EXACT restore of (u,v), `phase=0`, every ancilla clean, tape fully cleared.
  This carries walk restoration + phase repair + ancilla cleanup.
- **Full slice** — walk → forward replay → reverse replay → walk restoration,
  measured for peak Q and retained-state census. Carries forward replay
  (`replay_halving`) and reverse replay (`replay_doubling_inverse`).

Promoted-circuit safety: with the gate unset, `build()` is byte-for-byte
identical. `ops.bin` SHA256 with edits present, gate off:
`88706a40300b7f019202f65a0f28e86dbfe27fda65ad5ed33b0482ff9b14b7eb`, identical to
a pristine `git checkout` build of the two edited files. `PP_PROFILE=1` on the
promoted build: `peak_qubits=1278 peak_phase=pp_div_replay classical_mismatch=0
phase=0x0 dirty_qubits=0`.

### Retained-state census (the kill condition, measured)

| K | tape live at replay | active after walk | peak Q (slice) | emit CCX |
|---|---|---|---|---|
| 4 | 4 | 1032 | 1290 | 4274 |
| 6 | 6 | 1034 | 1291 | 6802 |
| 8 | 8 | 1036 | 1293 | 9330 |

Tape signs live through the replay = K exactly → **1 sign / round → O(rounds)
retained**, live continuously from the end of `value_walk` through
`value_walk_back`. (Slice peak is walk-dominated at these K because the width
schedule barely shrinks in ≤8 rounds; the production peak is the replay, see
co-binder note below.)

### Minimum decoder-visible state (mechanism)

`walk_back_round(r)` must supply `sign_r` to the reverse signed add, but
`sign_r = bit1(u_r) ⊕ bit1(v_r)` is only recomputable *after* the un-add
restores the pre-add state — a circular dependency. The forward walk step is
two-to-one (both `2z−a` and `2z+a` are odd and map to the same post-target `z`
under `sign = bit1(t) ⊕ bit1(a)`), so the post-round state does not determine
`sign_r`. Hence the sign must be stored: this is the tape. In the divide path
`b.free_vec(&coefficient)` runs *before* `value_walk_back`, so at the divide
walkback instant the only per-round-relevant live state is `(u_{r+1}, v_{r+1})`
— the streaming question there is exactly "is `sign_r` a function of
`(u_{r+1}, v_{r+1})`?"

## Decisive falsifier: reachability-aware collision search

For each round `r`, run the real walk of `r+1` rounds on 1,536 random nonzero
denominators, key on the live walk state `(u_{r+1}, v_{r+1})` at the scheduled
width, and look for a key observed with both `sign_r = 0` and `1` (a
reachable sign-disagreement). This is stronger than the generic two-to-one
argument: every state observed came from an actual walk.

Faithfulness of the key: the `width` column is exactly `value_width(r)` (a
source-level `assert_eq!` enforces `u.len() == value_width(r)`), and
`walk_back_round(r)` grows the registers to `value_width(r)` *before* it
consumes `sign_r` — so the key is the full decoder-visible state at that
walkback instant, not a truncation of a wider register. `value_width(600) = 46`.
Note the denominator cohort is drawn fresh per `(round, batch)` label, so each
row is an independent reachable sample of that round; the rows are not one walk
cohort tracked across rounds (no single-trajectory claim is made or needed).

| round | width | samples | distinct keys | sign-disagreements |
|---|---|---|---|---|
| 0 | 259 | 1536 | 1536 | 0 |
| 2 | 258 | 1536 | 1536 | 0 |
| 4 | 258 | 1536 | 1536 | 0 |
| 8 | 258 | 1536 | 1536 | 0 |
| 100 | 233 | 1536 | 1536 | 0 |
| 300 | 160 | 1536 | 1536 | 0 |
| 500 | 86 | 1536 | 1536 | 0 |
| **600** | **46** | **1536** | **1233** | **22** |
| 650 | 26 | 1536 | 115 | 8 |
| 680 | 13 | 1536 | 12 | 0 |
| 690 | 9 | 1536 | 7 | 0 |
| 693 | 8 | 1536 | 5 | 1 |

Reading of the three regimes:

1. **Wide bulk (rounds 0–~550, width 259→~86):** every state is distinct
   (birthday floor: 2^width ≫ 1536², so sampling exposes no merge). The
   two-to-one preimages `2z ± a` are *both* valid width-`w` odd numbers, so a
   decoder restricted to the live `(u,v)` cannot choose between them — the
   disambiguating information is the global reachable-set membership, i.e. the
   whole walk (≥254 resident bits, the §3e code-floor). A null here is NOT
   "streaming works"; it is "the ambiguity is not locally exposed."
2. **Transition zone (rounds ~600–650, width ~46–26):** the width schedule
   forces the representable state space below the reachable diversity, so
   merges appear — **22 reachable sign-disagreements at round 600 (width 46),
   8 at round 650.** (Most merged buckets still agree on the sign — the
   disagreements are the subset that kills the decoder.) Here a **bounded
   decoder keyed on the live walk state** *demonstrably* cannot regenerate
   `sign_r`: two reachable trajectories reach the same `(u_{601}, v_{601})`
   with opposite `sign_600`, so no function of that key produces the right
   sign for both. This falsifies the O(1)-retained, state-keyed streaming
   representation; it does not foreclose a decoder given *additional* resident
   inputs (that is the reopen gate, and it is exactly the ≥254-bit checkpoint
   the width floor kills). Tape required, reachability-demonstrated.
3. **Converged terminal tail (rounds ~680–693, width ≤13):** states collapse
   to the ±1 orbit (distinct keys 12→5), and `(u,v)` determines the sign
   (0 disagreements at 680/690). This is Teddy Pender's shared-sign tail:
   locally decodable, but it only covers the converged suffix (mean ~82 rounds)
   and is a same-Q Toffoli lever, not a peak-qubit reduction.

## Free-oracle (best-case) bound and the co-binder wall

Granting a zero-width, zero-cost sign oracle at the divide walkback removes the
divide tape but does not move the score: on `6b5c82c` the binding instant is
`pp_div_replay` at Q1278 (confirmed by `PP_PROFILE`), and the three-way
co-binder tie `{pp_div_replay, square_product_register, pp_mul_walkback}` at
Q1278 is prior-established on `a9af194` (`TEDDY-COBINDER-MAP-A9AF194.md`) and
architecturally inherited by `6b5c82c`. The N-way-tie law requires removing
resident state from ALL tied binders simultaneously; the multiply walkback
binder carries ~564 tape signs whose sign-disagreement wall is identical to the
one measured above. A divide-only streaming oracle is therefore insufficient
even at zero cost.

## Kill / continue / defer

- **KILL** — the O(1)-retained streaming representation of the replay history
  (bounded state-keyed decoder, fixed scratch, no per-round growth). Retained
  tape is O(rounds) (measured), and the sign is not locally decodable from live
  walk state in the bulk or transition zone (reachable disagreements at
  r600/r650). Sub-linear retained state needs a ≥254-bit global reachable-set
  decoder = the Q1376 checkpoint route (`9805dee`), not O(1) scratch.
- **DEFER (known, not a qubit cut)** — the converged terminal-tail shared-sign
  codec (Teddy) is locally decodable but reduces Toffoli at fixed Q, and the
  co-binder tie means it cannot cut peak Q alone.
- **Reopen gate** — a decoder that regenerates `sign_r` *without* a resident
  predecessor register, simultaneously across all three Q1278 co-binders. No
  such construction is exhibited; the transition-zone collisions are the
  precise obstruction any such construction must defeat.

## Citations (calibrated)

- Coefficient-absorption kill = `ad206c9`; the exact sparse-square lemma =
  `e004e5f` (do not swap these).
- History code-floor ≥254 bits and the two-to-one law: prior tape-representation
  audits (`redescent-teddy-*`, X004 `0d15561` — that ancestor is Q1266, NOT the
  promoted Q1278; its numbers are not transferable to `6b5c82c`).
- Retained full-word production splice → Q1376 (`9805dee`,
  `burn-retained-r3-9805dee`).
- Co-binder three-way Q1278 tie: `TEDDY-COBINDER-MAP-A9AF194.md`.
- 64-lane clean ≠ production-closed (Q1277 read `0/0x0` on 64 lanes, then
  10 classical + 8 phase-garbage batches at 9,024). All holds above are
  structural, on 64-lane / classical semantics, NOT production receipts.

## Reproduce

The harness was a temporary source-bound evaluator. After measurement the two
edited files were restored byte-for-byte to exact `6b5c82c`; the harness
survives in git history at commit `2b0bd4c` (`burn_slice_report` and helpers in
`src/point_add/pingpong_div.rs`, plus the read-only gate atop
`point_add::build`). To re-run it:

```
git checkout 2b0bd4c -- src/point_add/mod.rs src/point_add/pingpong_div.rs
cargo build --release --bin build_circuit
SUB4_PP_BURN_SLICE=1 ./target/release/build_circuit   # slice + collision table
PP_PROFILE=1 ./target/release/build_circuit           # promoted peak = pp_div_replay@1278
git checkout 6b5c82c -- src/point_add/mod.rs src/point_add/pingpong_div.rs   # restore
```

Current-source receipt (post-restore): normal gate-off build emits
12,950,916 operations, `ops.bin` SHA256
`88706a40300b7f019202f65a0f28e86dbfe27fda65ad5ed33b0482ff9b14b7eb` — identical
to the pristine `6b5c82c` artifact. (The 12,950,820 ops PP_PROFILE reports are
the pre-tail-nonce stream; the final artifact appends the 96 identity X-pairs.)
