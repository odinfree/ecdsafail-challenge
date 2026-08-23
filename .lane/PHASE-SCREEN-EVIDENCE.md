# Q1274 source-bound fast phase screen

## Contract

The default-off CPU mode `ppcpu phasefaultshots NONCE` emits the complete,
sorted shot-index set

`clean_phase_mask = evaluator_phase_mask & ~exact_classical_mask`.

This is the hunt-sufficient contract. A nonce survives only when the exact
classical mask is zero **and** `clean_phase_mask` is zero. The implementation
does not claim raw phase parity on already-classical-dirty shots: the sibling
two-pass mirror proved those lanes can also contain bare-R vent contributions,
while every reported clean-phase fault is bound to one of the modeled
measured-boundary predicates.

## Source and schedule binding

- exact source operation count: `12,920,073`;
- exact `ops.bin` SHA-256:
  `4c68597468ed1dbb4f2e33042842227bf57c011c51f41e9cdaf13c73194b1f8c`;
- total R/Hmr words per 64-shot batch: `1,940,649`;
- modeled source sites: `3,964` = `2,571` chunk-boundary + `696` divide-flag
  + `694` multiply-flag + `3` coordinate-shell subtraction Hmr sites;
- traced schedule TSV SHA-256:
  `613c9ec76668f0dd2eb3c5d334495ba11b3658dec060f06c3958e538e3011d10`.

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

## First disjoint32 falsifier and correction

The initial disjoint32 comparison stopped at its first mismatch, nonce
`700010000019`: the corrected-tail two-pass oracle emitted the complete sorted
set `{3102,3319,4324,4776,4784}` (SHA-256
`3d3005ca179826e81d9eb5c44e93b48196901bc3424a95369edd961ff48e14d7`),
while the pre-correction fast screen emitted
`{3319,4324,4776,4784}` (SHA-256
`69837836c80546f98b09add2c8c9cbecfe759f8d9b03196d881299bc7574198d`).
The missing shot `3102` first diverged at operation `12,906,665`,
`trailmix_ludicrous/arith.rs:1501`: the final coordinate-y
`mod_sub_vented` measured carry repair.

That source predicate is
`carry_anc XOR ((~coord_top19) < result_top19)`. It fits the same ordered trace
architecture and occurs exactly three times, at R/Hmr ordinals `623`, `1544`,
and `1,939,430`. After binding those sites, the corrected fast result is
byte-identical to the five-shot oracle set above. A fresh oracle rerun was also
byte-identical to the original full mirror log (SHA-256
`ff5e0911017f6421ff6d5724f23eaf764207a932ce8e23515d605f1cb350e223`).

## Frozen23 gate

PASS: `23/23` exact complete masked shot-index sets, rerun from the first nonce
after the shell-sub correction and compared byte-for-byte to the corrected
two-pass mirror. The durable complete sorted sets, per-set hashes, and counts
are in `.lane/stage-packet/PHASE_FIXTURES.tsv` (ledger SHA-256
`591cc3c5e1f7140dadbe192f5b98b3c971fb4725fd357752b7ef55bb3a03fe22`);
raw oracle rows remain scratch-only.
The two anchors were:

- inherited `251000962439`: classical `22`, clean phase `{4388,4629}`;
- canary `100000035106674`: classical `0`, clean phase `{1753,5833}`.

## Blinded disjoint32 gate

PASS: `32/32` exact complete masked shot-index sets after restarting at the
first declared nonce. The corpus is
`nonce[i] = 700000000000 + i * 10000019`, `0 <= i < 32`; its newline-delimited
nonce-list SHA-256 is
`6ec35ba16b516b8571c13c26ee503bf7de58af6a7f8d8aff37f3e37076db863a`.
It covers `288,768` shots and `146` clean-phase faults, including one exact
empty set. `.lane/stage-packet/PHASE_D32_FIXTURES.tsv` records every complete
sorted set plus its byte-level SHA-256; the ledger SHA-256 is
`fee237d38468963ec114bf722467886cd5b97b117211480c0cef9a1ccf9df2de`.

The gate took `203.6s` by the command runner, about `1,418` shots/s. Each of
the 32 standalone invocations reloaded the prefix and rebuilt the combination
table, so this is end-to-end gate throughput rather than a steady-state kernel
claim.

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

## Unchanged classical regression

PASS: the current phase-extended CPU source reproduced the unchanged
`fixtures.local.tsv` ledger exactly: `22/22` cases and `323/323` complete
per-shot rows set-equal. The fixture ledger SHA-256 is
`4889313f27a6f1daabd71f6b0c171459da8bf702424174923ec045e2990161e6`;
the sorted observed result SHA-256 is
`91bd3788228a5da40183688b0ae0d4bdaf2ea41a0c288076b0c993e13aeecb9`.
The mask histogram stayed `{1:136, 2:18, 4:148, 8:21}` with mask 16 absent.
Wall time was `54.823s` for all 22 standalone nonce invocations.

## Fail-closed stream and source binding

All negatives failed before evaluation:

- byte 0 framing mutation: SHA-256
  `f0a120ef246eac3c76123dc478522977cbc543a773ba540ae23c9d6adf30ecf1`,
  exit `1`;
- wrong-count header `12,921,096`: SHA-256
  `afb4eda48b819711710ae1e3f5eaf5fabdac2c1d19c2ffebe6a75d6e7d6abfeb`,
  exit `2`;
- same-count byte 16 mutation: SHA-256
  `4daf97cffbdfd19fdd6df22d0d8861af49d6b11e0d87f43cb50aafbc85a04e38`,
  exit `2`.

`MANIFEST.sha256` binds the current CPU phase sources, generated schedule, both
phase ledgers, and verification scripts. The ordinary loader independently
requires the exact operation count, full stream SHA-256, and checkpoint digest.
The corrected nonce-tail oracle rule above is the source-semantics negative.

## Terminal local timing and verdict

Three warm inherited-nonce phase runs completed in `6.84s`, `6.82s`, and
`6.64s`, each emitting the identical exact masked set (SHA-256
`832c1a0b584cb2775f6913bf3b950f36d28f51f80ffaa237f4ad539ccf210f53`).
The median is `6.82s`, or about `1,323` shots/s for all `9,024` shots, including
prefix load and combination-table construction. The classical breakdown median
was `2.26s` across `2.58s`, `2.26s`, and `2.26s`.

Against the recovered unchanged full-evaluator wall time of `15.890s`, the
terminal CPU phase screen is about `2.33x` faster. The earlier cold checkpoint
was `7.42s` versus the same `15.890s` reference. The blinded disjoint32 gate
sustained about `1,418` shots/s end to end across `288,768` shots.

This verdict is deliberately conditional-phase only: raw phase on
classically dirty shots is not represented and no raw-phase parity is claimed.
The only valid final clean predicate is
`classical_mask == 0 && clean_phase_mask == 0`. No CUDA phase implementation,
provider action, range scan, hunt, or submission occurred in this lane.
