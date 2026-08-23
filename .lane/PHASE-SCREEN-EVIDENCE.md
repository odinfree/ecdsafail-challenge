# Q1274 source-bound fast phase screen

## Contract

The default-off CPU mode `ppcpu phasefaultshots NONCE` emits the complete,
sorted shot-index set

`clean_phase_mask = evaluator_phase_mask & ~exact_classical_mask`.

This is the hunt-sufficient contract. A nonce survives only when the exact
classical mask is zero **and** `clean_phase_mask` is zero. The implementation
does not claim raw phase parity on already-classical-dirty shots: the sibling
two-pass mirror proved those lanes can also contain bare-R vent contributions,
while every classical-clean phase fault in frozen evidence came from the three
modeled measured-boundary families.

## Source and schedule binding

- exact source operation count: `12,920,073`;
- exact `ops.bin` SHA-256:
  `4c68597468ed1dbb4f2e33042842227bf57c011c51f41e9cdaf13c73194b1f8c`;
- total R/Hmr words per 64-shot batch: `1,940,649`;
- modeled source sites: `3,961` = `2,571` chunk-boundary + `696` divide-flag
  + `694` multiply-flag Hmr sites;
- traced schedule TSV SHA-256:
  `5e4f8aa392b3de1628e252dc3bb2e3dea87cd15f315843c29ea69f320c1dedc0`.

The ordinary prefix loader already fails closed on operation count, file hash,
and checkpoint digest. Phase mode additionally requires exactly 9,024 corpus
shots, monotonically in-range schedule ordinals, the exact source-family order
for every classically clean shot, and consumption of every R/Hmr word before
the next batch.

## Oracle nonce-tail rule and negative

The source stream encodes the 48-bit nonce in its final 96 cancelling X
operations: two identical q0/q1 targets per little-endian nonce bit. A reusable
mirror must patch those 96 `q_target` fields **before both Fiat-Shamir hashing
and simulation**, exactly as `pp_nonce_shake` does. Execution remains unchanged
because every X occurs as an identical pair.

Negative reproduced: invoking the recovered raw mirror with the canary nonce
as a label but leaving the inherited tail unchanged repeated the inherited
receipt (`classical=22`, clean-phase shots `{4388,4629}`). After in-memory tail
patching, the canary returned its source-exact receipt (`classical=0`, shots
`{1753,5833}`). This negative prevents a label-only multi-nonce oracle.

## Frozen23 gate

PASS: `23/23` exact complete masked shot-index sets, compared byte-for-byte to
the corrected two-pass mirror. The durable count and SHA-256 ledger is
`.lane/stage-packet/PHASE_FIXTURES.tsv`; raw oracle rows remain scratch-only.
The two anchors were:

- inherited `251000962439`: classical `22`, clean phase `{4388,4629}`;
- canary `100000035106674`: classical `0`, clean phase `{1753,5833}`.

Host compile command:

```sh
clang++ -O3 -std=c++17 -pthread -o /tmp/ppcpu \
  .lane/stage-packet/src/ppcpu.cpp
```

The bundled `src/build.sh` has a pre-existing cwd bug (`cd src` followed by a
`src/ppcpu.cpp` path), so the direct command above is the actual build gate.
An arithmetic parity harness also matched the original square model on 100
deterministic inputs and both original replay models on 20 inputs, with exact
event counts `17/1972/1972` and the traced family sequence.

## Initial timing

Inherited nonce, same local host and exact stream:

- fast masked screen: `7.42s` wall, including prefix load and comb build;
- unchanged full evaluator receipt: `15.890s` wall (recovered prior run).

This clears the CPU economic gate provisionally. Frozen repeated timing follows
after disjoint32 and unchanged classical/negative regressions.
