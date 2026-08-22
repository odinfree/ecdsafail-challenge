# Burn explorer: remove the replay passenger

Created: 2026-08-22
Source: `6b5c82c`
Branch: `research/kimi-burn-6b5c-passenger`
Status: both saddle falsifiers KILL; divide-replay peak census fully closed

Model: Kimi Code (k2/k3, high effort), multi-lane agent campaign.

## Protected leader

- Live source: `6b5c82c`.
- Trusted metrics: Q1278 / rounded T918358 / score1173661524.
- Reproduced locally this session: forced default build, 12,950,916 ops,
  ops.bin md5 `c0eddceaca5a76fc2307a68efc7a2aa1`, eval Q1278 / avg executed
  T918357.924 / score1173661524, classical/phase/ancilla 0/0/0 (9,024 shots).
- Objective: `round(avg_executed_toffoli) * peak_qubits`, strictly lower wins.
- Trusted contract: forced clean build, then unchanged 9,024-shot evaluator with
  classical/phase/ancilla all `0/0/0`.
- This explorer cannot hunt, spend provider credit, push, publish, or submit.

## Overturn 1 (KILLED): the caller-y replay passenger

Wall: the divide-replay peak holds a 256-qubit caller-y register that is idle at
the binding operation and survives only for the later EC-add shell.

Result: the premise is false on the exact ancestor and the falsity transfers
exactly to `6b5c82c`. Caller y IS the divide's numerator — an operand of every
replay round (`replay_halving_round`, parity alternation), written 803 ops
before the Q1278 binding instant, zero frees in the stream. The full source diff
9805dee→6b5c82c is rounds 698→694, endpoint window 20→26, and the tail nonce;
both are topology-neutral numeric windows. The three-way 1278 peak tie
(pp_div_replay / square_product_register / pp_mul_walkback) was re-measured on
6b5c82c and independently voids any div-replay-only shave.

Evidence: `.lane/KIMI-Y-TRANSFER-KILL-6B5C82C.md`, transferring Fable lane's
`e717062` census (`.lane/TEDDY-Y-PASSENGER-LIFETIME-9805DEE.md` on that branch).
Methodology credit: Teddy Pender's cheapest-falsifier-first discipline.

## Overturn 2 (KILLED): the 280 u/v compact reversible checkpoint

Wall: with y proven an active operand, the last open census component of the
divide-replay peak was the u/v walk-state pair frozen across the batch replay
of rounds 0..356: 2 × value_width(356) = 2 × 140 = 280 wires, idle-but-live at
the Q1278 binding instant.

Result: three independent exact kills on 6b5c82c, no prototype built.

1. Information floor: (u_356, v_356) is a bijective image of (const p, x), so
   any reversible checkpoint needs ≥256 wires. Max possible saving: 24 wires
   (the incumbent's shrink_to envelope is already near-floor).
2. T-kill: reaching the floor requires unwalk+rewalk of the prefix =
   2 × 71,756 = 143,512 executed T (pp_div_walk measured = exactly rounds
   0..355, fully unconditioned; per-round formula width(r)−3 cross-checks to
   the Toffoli). Budget for 24 wires at the exact gate: 17,247 T. Realized
   exchange 5,980 T/Q = 8.3× over break-even.
3. Q-kill: the mandatory rewalk before interleaved round 356 re-materializes
   u/v at the 2×259 round-0 envelope while tape copies (357), coefficient
   (256), and y (256) are live: floor 1,387 = +109 over the leader. Partial
   unwalks free nothing (the width schedule is non-increasing, so unwalking
   backward grows u/v).

Evidence: `.lane/KIMI-UV280-CHECKPOINT-KILL-6B5C82C.md`. Methodology credit:
Teddy Pender; sibling kills absorbed: r1 literal checkpoint (`a313b84`),
Bennett recomputation (`68bf16c` ledger).

## Divide-replay peak: final census (all components closed)

- sign tape (694): information-theoretically irreducible (`ad206c9`; the
  streaming-representation question is owned by the Fable stream lane).
- carry ladder: allowance cliff killed (`02a5836`).
- 256 numerator (y): active operand — overturn 1.
- 256 coefficient: second pair line, decoder-at-peak wall (`e717062`).
- 280 u/v walk slices: overturn 2.

## Target direction and saddle budget

- First invariant (overturn 1): remove the 256 caller-y wires from
  `pp_div_replay` — DISPROVEN (y is the numerator operand; tie voids shaves).
- Second invariant (overturn 2): hold the round-356 walk state below 280
  wires across the batch replay — DISPROVEN (24-wire floor, 8.3× T price,
  +109 Q rewalk peak).
- Composition target: combine with Teddy Pender's exact sparse-square component
  only after the replay peak independently falls below Q1148. Not reached.
- Current complete-circuit strict ceilings: Q1182 T<=992945; Q1148 T<=1022353.
- Budget: two dependency/liveness falsifiers plus one bounded circuit prototype,
  or four hours. Spent: two falsifiers, both kills; prototype not warranted
  (no dependency proof survived). No candidate was built; the normal path
  stands byte-for-byte (only `.lane/` evidence committed).

## Next action

None on this wall: the saddle is resolved — both named live-set invariants are
disproven by binding dependency falsifiers, and every census component of the
divide-replay peak is now closed by proof or measurement. Per the doctrine this
is a kill, not a saddle quit: the invariants resolved inside budget. Remaining
live direction at this frontier is the streaming sign-history representation,
already owned by the Fable stream lane (`68bf16c`); do not duplicate it. If
this lane continues, re-scope to a different wall (e.g. the square's 1278 tie
component) only with a fresh overturn ledger entry and a priced falsifier.
