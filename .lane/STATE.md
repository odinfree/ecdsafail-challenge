# Lane state: bdf4845 SUB4 ladder history and Q1276 composition

Updated: 2026-08-23T07:38:09+02:00

## Decision

`STOP_OLD_STREAM / ZERO_MODEL_GATE_PASS`

The historical square-ladder observation is real, but `SUB4_SQUARE_LADDER`
cannot lower the global peak alone. On exact live source `bdf4845`, the
smallest useful composition changes only:

```text
SUB4_PP_PEAK:       1278 -> 1276
SUB4_SQUARE_LADDER:  248 -> 246
```

R1/R2 stay 356/625, divide/multiply depths stay 698/696, the g1000 schedule
and nonce stay unchanged. The two defaults remain runtime-overridable.

## Exact measurements

All structural rows use the same deterministic 64-lane diagnostic. Full rows
use the unchanged trusted 9,024-shot evaluator.

| route | ops | ops SHA-256 | Q | diagnostic T | diagnostic cls/phase/anc |
|---|---:|---|---:|---:|---:|
| protected bdf | 12,912,890 | `5b60d0a227b56f53abdc99b9588a80c1ff02838618ce4e7c3bf7cb22decdebb8` | 1278 | 915994.83 | 0/0/0 |
| ladder246 only | 12,913,274 | `88d992ef9d81fef23545e309dba9145222c1d04e1f1f96fd8846de857d46b21f` | 1278 | 916021.14 | 0/0/0 |
| replay cap1276 only | 12,928,962 | `ba6cc62dc1a678fdb75918712ea88d013006d08cdf41d8661405c7c8841b80a6` | 1278 | 916569.22 | 0/0/0 |
| Q1276 pair | 12,929,346 | `d1461959eac52b19b644f1f97a3b44a3ea249a109f14a406d19e872cd17c5422` | 1276 | 916718.89 | 0/0/0 |
| prior Q1275 package | 12,947,403 | `059a249a8d2934aa83f508280f508821a92fb0b7ce5de5045d00acd0fa8e5e02` | 1275 | 917331.19 | 0/0/0 |

Full-shot receipts:

| route | average T | rounded score | classical/phase/ancilla | verdict |
|---|---:|---:|---:|---|
| protected bdf | 915947.392 | 1,170,580,266 | 0/0/0 | protected incumbent |
| Q1276 pair | 916628.572 | 1,169,618,604 | 15/5/0 | dirty; no submit |
| prior Q1275 package | 917361.243 | 1,169,635,275 | 17/8/0 | dirty; no submit |

The score entries for dirty routes are counterfactual products used only to
rank structures. They are not valid submission claims. Q1276 would clear the
refreshed live score by 961,662 if a full-clean nonce existed. It is 16,671
better than the Q1275 package on the product and has the lower inherited fault
fingerprint.

Q1276 artifact identity:

- compressed bytes: 51,271,953;
- MD5: `db4645d14ff62f009a3571f49aa69211`;
- first classical mismatch: shot 32;
- `pingpong_div.rs` SHA-256:
  `ef9dd2d570c5826f0739509c45a082927985f68109c4dcbc53c36d9add2bb6d6`;
- `product_register.rs` SHA-256:
  `d2ee51194594123d982be3f135fbc087d24bf1cd645d8346c986f8d5dce3724d`;
- `build_circuit` SHA-256:
  `e1e7fb0e305d45bdd20fdcf9189d70d9f898d015f3b5e8fd66e4b15931b2e55e`;
- unchanged `eval_circuit` SHA-256:
  `00c6e5971bb510e32ddc42bfcf6542f5af8e394e8284a9820d1ae794c4e805a7`.

## Source and focused gates

- Clean locked release build: pass; only three pre-existing warnings in
  untouched multiply/dirtyscan code.
- Baked no-environment Q1276 build: byte-identical to the env-only candidate,
  SHA `d1461959...`.
- `SUB4_PRODUCT_SQUARE_SELFTEST=1`: exit 0.
- `SUB4_PINGPONG_POINT_ADD_SELFTEST=1`: exit 0.
- Detailed peak trace: balanced Q1276 plateau at divide replay, square,
  multiply replay, and multiply walkback.
- Same-seed 64-lane gate: `0/0/0`.
- Unchanged full evaluator: `15/5/0`, so the inherited nonce is falsified.
- `git diff --check`: pass.

The full evaluator's generated `results.tsv` rows, `ops.bin`, release binaries,
temporary profiles, and score output were not retained in Git.

## Exact-model qualification checkpoint

- CPU equals the unchanged full evaluator on the inherited nonce and three
  ordinary fixtures, including first classical failure.
- Isolated and dedicated CUDA gates both give CPU = comb8 = comb16 on all four
  fixtures with state digest `5a0a4564563a201a`.
- The dedicated native-architecture binaries are bound as CUDA `6347cff0...`
  and CPU `bb5b5f0b...`.
- Source-build equals tail-patch byte-for-byte on all four fixtures. The
  unchanged reserved full-confirm path closed receipt
  `b09d29a129f61e02a95152da747e7fbe675375bbe23e945e597f9c6c88d927ee`.
- The predeclared zero calibration retained two rows. GPU, CPU, and unchanged
  full evaluation agreed at classical zero on both; the final results were
  `0/8/0` and `0/1/0`. Receipt `0ed3e932...` closes the observed zero edge.
- Neither retained row is a valid island. The separate low-3 interval was not
  run because a stronger promoted-source Q1276 composition superseded this
  stream. Canary launch, fleet retarget, and submission were cancelled.

## Scope and next action

No nonce hunt, fleet retarget, submission, or incumbent change occurred. The
only range activity was the fixed qualification interval.

This stream is frozen with its terminal receipts. Do not run its fixed low-3
interval or launch its canary. Reuse the validated parity and confirmation
doctrine only after binding it to the stronger promoted-source composition.
Final acceptance remains full 9,024-shot `0/0/0`.
