# Caller-y replay-passenger: exact transfer kill on 6b5c82c

Date: 2026-08-22. Lane: `research/kimi-burn-6b5c-passenger` @ e2619bb.
Methodology credit: Teddy Pender's Burn-the-House-Down discipline — cheapest
falsifier first, kill before building. Transferred evidence: Fable lane's
binding-lifetime census (`e717062`, `.lane/TEDDY-Y-PASSENGER-LIFETIME-9805DEE.md`,
itself Teddy-credited), measured at exact ancestor 9805dee.

## Verdict: KILL (transfer exact, tie re-measured)

The hypothesis under test (this lane's STATE.md): the 256-qubit caller-y
register is an idle passenger at the `pp_div_replay` peak, removable by
outer-shell rescheduling, reversible recomputation, or coordinate placement.

The ancestor census kills it: caller y IS the divide's numerator (wired by
`ec_add.rs:318` `divide(circ, xv, y2, true)`), an operand of every replay
round via parity alternation in `replay_halving_round`, written 803 ops
before the Q1278 binding instant, zero frees anywhere in the stream. The
stated kill condition "y is consumed during replay" is met.

## Transfer check: do rounds 694 / endpoint 26 alter the invariant?

The complete source diff 9805dee → 6b5c82c (`git diff 9805dee 6b5c82c -- src/`):

1. `pingpong_div.rs` `rounds()`: 698 → 694 (divide walk depth).
2. `pingpong_div.rs` `endpoint_fold_window()`: 20 → 26 (correction carry window).
3. `mod.rs`: tail nonce 68367898080254 → 1400958.

Nothing else. `replay_halving_round`, the shell callback wiring, the register
plan (`r1=356, r2=625, peak=1278`), and the width schedule are byte-identical.

- Rounds 698→694 changes the NUMBER of replay rounds, not the per-round
  register topology: every round still reads or writes numerator y. Invariant
  untouched.
- Endpoint 20→26 widens a pseudo-Mersenne correction carry chain inside
  `conditional_mod_negate` / `mod_halve_pm`; it does not change WHICH
  registers participate. Each fused replay round touches all 256 y wires via
  the sign-complement sweep plus the full-width chunked add regardless of the
  fold window. Invariant untouched.

## Re-measured on 6b5c82c (PP_PROFILE, 64-lane diagnostic, clean 0/0/0)

- Leader receipt reproduced first: forced default build, 12,950,916 emitted
  ops, ops.bin md5 `c0eddceaca5a76fc2307a68efc7a2aa1`, trusted eval
  Q1278 / avg executed T 918357.924 / score 1,173,661,524, classical/phase/
  ancilla `0/0/0` over 9,024 shots. Matches STATE.md's trusted metrics exactly.
- Global peak: 1278 at op 2,643,328, phase `pp_div_replay` (ancestor: op
  2,643,244 — the 84-op shift is the rounds/endpoint delta).
- Per-phase peak actives (PROFILE_ACTIVE_TIMELINE):

  ```text
  pp_div_replay            1278   <- global peak
  square_product_register  1278
  pp_mul_walkback          1278
  pp_mul_replay            1276
  pp_div_walk/walkback     1057
  everything else          <=1057
  ```

  The three-way 1278 tie (div replay / square / mul walkback) survives the
  698→694 / 20→26 transfer exactly, independently voiding any
  div-replay-only shave: a counterfactual free −256 at div replay still
  leaves square and mul walkback binding at 1278.

## Consequence for this lane

The replay peak's y component is closed: active operand, not reschedulable,
and single-phase moves are voided by the tie. No y-reschedule prototype was
built (per instruction: no duplicate of the ancestor's settled work). The
normal path is untouched — no source change, no eval beyond the leader
reproduction, results.tsv restored.

Reproduction (read-only):

```sh
cargo build --release --locked --offline --bin build_circuit --bin eval_circuit
./target/release/build_circuit && ./target/release/eval_circuit   # leader receipt
work=$(mktemp -d); cd "$work"
PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1 /ABS/target/release/build_circuit
git diff 9805dee 6b5c82c -- src/   # the full transfer surface
```
