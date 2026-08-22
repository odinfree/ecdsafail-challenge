# Burn explorer: remove the replay passenger

Created: 2026-08-22
Source: `6b5c82c`
Branch: `research/kimi-burn-6b5c-passenger`
Status: structurally free descent; protected leader untouched

Model: Kimi Code (k2/k3, high effort), multi-lane agent campaign.

## Protected leader

- Live source: `6b5c82c`.
- Trusted metrics: Q1278 / rounded T918358 / score1173661524.
- Objective: `round(avg_executed_toffoli) * peak_qubits`, strictly lower wins.
- Trusted contract: forced clean build, then unchanged 9,024-shot evaluator with
  classical/phase/ancilla all `0/0/0`.
- This explorer cannot hunt, spend provider credit, push, publish, or submit.

## Overturn

Wall: the divide-replay peak holds a 256-qubit caller-y register that is idle at
the binding operation and survives only for the later EC-add shell.

Assumption to overturn: caller y must coexist with the full ping-pong divide
replay and walkback.

Overturn condition: an outer-shell schedule, reversible recomputation, or
coordinate placement keeps caller y out of the divide-replay live set while
restoring the exact point-add ABI and phase.

Cheapest falsifier: trace every read/write of caller y across
`build_pingpong_point_add`, prove its first post-replay consumer and last
pre-replay producer, then build an environment-gated liveness-only prototype.
Kill if y is consumed during replay or removing it necessarily creates another
256-qubit passenger at the same peak.

## Target direction and saddle budget

- First invariant: remove the 256 caller-y wires from `pp_div_replay`.
- Composition target: combine with Teddy Pender's exact sparse-square component
  only after the replay peak independently falls below Q1148.
- Current complete-circuit strict ceilings: Q1182 T<=992945; Q1148 T<=1022353.
- Budget: two dependency/liveness falsifiers plus one bounded circuit prototype,
  or four hours. Temporary score regression is allowed only while the named
  live-set invariant improves.

## Next action

Read the canonical Burn-the-House-Down doctrine and map caller-y ownership and
all co-binders on exact `6b5c82c`. Do not tune rounds, carry widths, endpoint
windows, or nonces. Produce either a measured liveness cut or a binding
dependency falsifier, update this file, and commit only durable source/evidence.
