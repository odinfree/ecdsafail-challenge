# Burn explorer: stream the ping-pong history

Created: 2026-08-22
Source: `6b5c82c`
Branch: `research/fable-burn-6b5c-stream`
Status: structurally free descent; protected leader untouched

Model: Kimi Code (k2/k3, high effort), multi-lane agent campaign.
Worker: Claude Fable 5, xhigh effort.

## Protected leader

- Live source: `6b5c82c`.
- Trusted metrics: Q1278 / rounded T918358 / score1173661524.
- Objective: `round(avg_executed_toffoli) * peak_qubits`, strictly lower wins.
- Trusted contract: forced clean build, then unchanged 9,024-shot evaluator with
  classical/phase/ancilla all `0/0/0`.
- This explorer cannot hunt, spend provider credit, push, publish, or submit.

## Overturn

Wall: replay carries a resident sign history plus restored walk state. Literal
full-word checkpoints, materializing decoders, and current-walk Bennett
recomputation are killed on measured width or Toffoli economics.

Assumption to overturn: exact replay requires one persistent sign qubit per
round, or a full walk/checkpoint state materialized at peak.

Overturn condition: a bounded streaming representation reconstructs and clears
the next replay symbol from state already live at walkback, with fixed scratch
and no growth in retained state across rounds.

Cheapest falsifier: build an exact 4-8-round nonzero-numerator reference slice
with forward replay, reverse replay, walk restoration, and phase/ancilla cleanup.
Measure retained-state growth before extrapolating. Kill any representation that
needs O(rounds) new state or a full 256-bit checkpoint at the replay peak.

## Target direction and saddle budget

- First invariant: max one reconstructed symbol live and fixed scratch across
  the bounded slice; reference/candidate continuation identical.
- Component target: Q<=1148 before composition with the sparse square.
- Current complete-circuit strict ceilings: Q1182 T<=992945; Q1148 T<=1022353.
- Budget: three different representation falsifiers or four hours. A failed
  low-five/full-word encoding does not kill other state representations.

## Next action

Read the canonical Burn-the-House-Down doctrine and existing exact negatives as
evidence, not axioms. Start from a fresh nonzero-numerator reference slice on
`6b5c82c`; localize the minimal decoder-visible state before writing a full
builder. Do not tune rounds, carry windows, or nonces. Update this file and make
a clean durable commit for every measured hold or kill.
