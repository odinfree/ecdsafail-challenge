# Burn explorer: remove the replay passenger

Created: 2026-08-22
Source: `6b5c82c`
Branch: `research/kimi-burn-6b5c-passenger`
Status: caller-y passenger KILLED by exact transfer; pivot to the 280 u/v checkpoint open

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

## Overturn 2 (OPEN): the 280 u/v compact reversible checkpoint

Wall: with y proven an active operand, the last open census component of the
divide-replay peak is the u/v walk-state pair frozen across the batch replay
of rounds 0..356: 2 × value_width(356) = 2 × 140 = 280 wires, idle-but-live at
the Q1278 binding instant.

Assumption to overturn: the batch-replay plateau must hold the 280-wire walk
state in raw pair form.

Overturn condition: a compact reversible checkpoint holds the round-356 walk
state below 280 wires across the batch replay and regenerates it for the
interleaved rounds, inside the exact Q/T gate.

Cheapest falsifier: information floor (the pair is a bijective image of
(const p, x) → ≥256 wires, max saving 24) plus the unwalk/rewalk T price
against the 24-wire budget, plus the rewalk co-live Q check. Kill if the
price exceeds 24 × 718.61 ≈ 17,247 executed T or the rewalk re-materializes
u/v while tape+coefficient+y are live.

## Target direction and saddle budget

- First invariant (overturn 1): remove the 256 caller-y wires from
  `pp_div_replay` — DISPROVEN (y is the numerator operand; tie voids shaves).
- Second invariant (overturn 2): hold the round-356 walk state below 280
  wires across the batch replay.
- Composition target: combine with Teddy Pender's exact sparse-square component
  only after the replay peak independently falls below Q1148. Not reached.
- Current complete-circuit strict ceilings: Q1182 T<=992945; Q1148 T<=1022353.
- Budget: two dependency/liveness falsifiers plus one bounded circuit prototype,
  or four hours. Spent: one falsifier (transfer kill). Temporary score
  regression is allowed only while a named live-set invariant improves; no
  candidate was built, so the normal path stands byte-for-byte.

## Next action

Run the overturn-2 falsifier: exact width/floor arithmetic on 6b5c82c plus the
measured prefix-walk price. Do not tune rounds, carry widths, endpoint windows,
or nonces. Produce either a measured liveness cut or a binding dependency
falsifier, update this file, and commit only durable source/evidence.
