# SUB4 ladder overturn ledger

Updated: 2026-08-23T06:55:22+02:00

## Protected anchor

- Live source: `bdf4845afa4f911192e20b5260b9efbd67655cf9`.
- Live submission: `792ac703-febb-488d-ad24-3d1d13160014`.
- Live score at the audit refresh: `1,170,580,266 = 1278 * 915947`.
- Protected artifact: 12,912,890 ops, SHA-256
  `5b60d0a227b56f53abdc99b9588a80c1ff02838618ce4e7c3bf7cb22decdebb8`.
- Unchanged full evaluator: Q1278, average T915947.392, `0/0/0` over
  9,024 shots.

The incumbent remains untouched. This branch changes source defaults only for
an isolated structural candidate.

## Eight-commit source trace

`bdf4845~8` is `7ca0559`. The accepted-source path is:

| source | public Q/T | relevant source change |
|---|---:|---|
| `7ca0559` | 1278 / 921558 | divide698, multiply700, R1/R2 356/625, replay cap1278, square ladder248 |
| `36f6ca0` | 1278 / 919793 | multiply depth 700 -> 696; new nonce |
| `def24be` | 1278 / 919788 | nonce only |
| `a9af194` | 1278 / 919785 | nonce only |
| `9805dee` | 1278 / 919754 | dead-low constant-fold path plus nonce |
| `6b5c82c` | 1278 / 918358 | divide 698 -> 694 and endpoint window 20 -> 26; new nonce |
| `940e34a` | 1278 / 917481 | divide restored to 698, replay compare 22 -> 20, endpoint 26 -> 20; new nonce |
| `087cafa` | 1275 / 918972 | R1 356 -> 342, replay cap 1278 -> 1275, square ladder 248 -> 245; new nonce |
| `bdf4845` | 1278 / 915947 | g1000 width schedule, compare 20 -> 22, prior dead-low path removed; Q1275 cap/ladder reverted to 1278/248; new nonce |

The fresh chat observation is historically accurate: the current source pays
the convergence-risk cost of a four-round shorter multiply traversal than
`7ca0559`, while the square ladder is still 248. That does not make two global
qubits free on its own because the circuit has independent peak owners.

## Independent architectural corroboration

A later group-chat note tied the two-round freedom to tightening
`SUB4_SQUARE_LADDER` on an eight-commit-old baseline. Its author explicitly
retracted his initial current-source conclusion after noticing that baseline
gap. The note corroborates the ladder lever historically; it does not prove
the transfer to `bdf4845`. The current-source conclusion rests on this lane's
exact composition measurements: the replay peak cut alone leaves square at
Q1278, while pairing peak1276 with ladder246 lowers every named owner to Q1276.

The same note mentions an unpublished `v2Grinder` measurement near 16.2K
nonces per second. It has no shared source, protocol binding, or reproducible
receipt yet, so this lane does not rely on the rate and will not blindly
reimplement it.

## Assumptions and exact falsifiers

| load-bearing assumption | wall it creates | cheapest exact falsifier | result |
|---|---|---|---|
| Shorter multiply tape automatically lowers global Q | Square and divide replay can hide the gain | ladder248 -> 246 only | overturned: square falls to1276, global stays1278 at divide replay / multiply walkback |
| Tightening only the replay cap is enough | Square remains an independent peak | replay cap1278 -> 1276 only | overturned: replay families fall to1276, global stays1278 at square |
| The two cuts compose | A new taller owner could appear | enable cap1276 plus ladder246, keep R1/R2 356/625 | confirmed: all named owners form a Q1276 plateau |
| The existing Q1275 composition is the best product point | The third qubit may cost more T than it saves | compare unchanged full-shot Q1276 and Q1275 streams | overturned: Q1276 projected score is 16,671 lower |
| A structural pass implies a submission candidate | Tail-seeded graded faults may remain | unchanged full 9,024-shot evaluator | overturned at inherited nonce: Q1276 is `15/5/0`; Q1275 is `17/8/0` |

## Dependency ownership

The phase peaks below come from the same 64-lane seed and the detailed active
timeline profiler.

| composition | pp_div_replay | square | pp_mul_replay | pp_mul_walkback | global Q |
|---|---:|---:|---:|---:|---:|
| protected bdf | 1278 | 1278 | 1276 | 1278 | 1278 |
| ladder246 only | 1278 | 1276 | 1276 | 1278 | 1278 |
| replay cap1276 only | 1276 | 1278 | 1276 | 1276 | 1278 |
| cap1276 + ladder246 | 1276 | 1276 | 1276 | 1276 | 1276 |
| cap1275 + R1=342 + ladder245 | 1275 | 1275 | 1275 | 1275 | 1275 |

The square and replay cuts are independent lemmas; the pair is the width
theorem. The Q1275 branch subsumes the mechanism, but its third qubit costs
about +732.671 average T relative to Q1276. The local break-even is about
718.361 T per qubit, so that last step slightly loses on the product.

## Decision

- `GO`: exact predictor/model qualification for the Q1276 stream
  `d1461959...`; it is the cheapest current-head composition found here.
- `HOLD`: nonce hunting, fleet retarget, submission, and promotion. The baked
  inherited nonce is not clean.
