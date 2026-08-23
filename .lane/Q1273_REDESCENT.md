# Q1273 one-saddle re-descent

Predeclared: 2026-08-23, before any semantic edit or Q1273 measurement.

## Protected leader and live contract

- Explorer ancestor: `2d09ccc3266daabdaf6776554f2936055161bd98`.
- Protected leader source is not edited by this lane.
- Fresh live benchmark: score `1,167,654,124`, Q1274, rounded T916526,
  promoted source `2c79d2f`.
- Strict Q1273 ceiling: rounded T <= `917245`, because
  `1273 * 917245 = 1,167,652,885 < 1,167,654,124`.
- Marginal allowance from the protected full result: at most `+719` rounded
  executed Toffoli for the one-qubit cut.
- Correctness contract: focused structural/selftests first. No nonce scan,
  provider action, full evaluator, or submission is authorized here.

## Overturn ledger

Wall: the Q1274 architecture is at a narrow width plateau. The prior lane
priced an unrepaired Q1273 pair near the score boundary, but the final r100
source and clean-tail stream have not been independently traced and priced as
one immutable descent.

Load-bearing assumption: lowering only the replay budget or only the square
ladder leaves another peak owner at Q1274. The smallest plausible theorem is
the coordinated one-notch pair:

- `SUB4_PP_PEAK`: default 1274 -> 1273;
- `SUB4_SQUARE_LADDER`: default 244 -> 243.

All other defaults, including R1=340, R2=628, the r100 width repair, the
compressed width schedule, and tail nonce `100000045835813`, remain frozen.
No R1/R2 grid or repair-table tuning is permitted in this experiment.

## Frozen procedure and kill rule

1. Forced-release build the untouched ancestor. Require the known base ops
   identity and record exact op count/SHA.
2. With `PP_PROFILE_SEED=0`, record the complete Q1274 peak-owner table,
   fixed-64 executed T, and classical/phase/dirty channels.
3. Bake only the coordinated pair above and force rebuild.
4. Require Q1273 and re-trace every peak owner. Run the production ping-pong
   simulator selfcheck and focused relevant Rust tests.
5. Compare same-seed fixed-64 candidate T against the ancestor. If marginal
   T exceeds `+719`, kill immediately: no extra saddle, full-9024 evaluation,
   model port, or search.
6. If the marginal gate passes, project rounded full T as `916526 + delta`
   and preserve the candidate for an independently authorized validation
   lane. This lane still does not scan or submit.

Saddle budget: exactly one coordinated pair and its forced base/candidate
measurements. The invariant is a real Q1274 -> Q1273 global peak cut without a
new Q1274 co-binder.

## Results

### Ancestor reproduction and exact plateau

Forced release rebuild of untouched `2d09ccc`:

- emitted ops: `12,920,073` (`12,919,977` before the 96-op tail);
- `ops.bin` SHA-256:
  `2974f70668476c5a635bc16680b3d6a4ca90cb3b93c0f59a1660774a3bbb8ee2`;
- fixed-64 seed 0: Q1274, T916424.62, classical/phase/dirty `0/0/0`.

`PROFILE_ACTIVE_TIMELINE=1` identifies four exact Q1274 co-binders:

| phase | peak | dominant B0 live groups |
|---|---:|---|
| `pp_div_replay` | 1274 | tape 339; output 256; coefficient 256; walk 145+145; ladder 130; 3 singles |
| `square_product_register` | 1274 | square 258; output 256; carry ladder 243; square blocks 129+129; restored/walk passengers |
| `pp_mul_replay` | 1274 | tape 695; output 256; coefficient 256; carry ladder 61; 6 miscellaneous wires |
| `pp_mul_walkback` | 1274 | tape 628; output 256; coefficient 256; carry ladder 62; walk 26+26; replay passengers |

The first global peak is `pp_div_replay` at op index 2,528,381. The square
notch alone cannot lower the replay families, and the replay budget alone
cannot lower the independent square family; the coordinated pair was therefore
the minimum complete saddle.

### One bounded saddle

Only these source defaults changed:

- `SUB4_PP_PEAK`: 1274 -> 1273;
- `SUB4_SQUARE_LADDER`: 244 -> 243.

All predeclared frozen defaults remained unchanged. Forced candidate rebuild:

- emitted ops: `12,933,805` (`12,933,709` before the tail);
- `ops.bin` SHA-256:
  `ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1`;
- Q1273, with all four former binders now exactly Q1273;
- fixed-64 seed 0: T917056.48, `0/0/0`;
- fixed-64 seed 1: T917090.25, `0/0/0`.

Paired same-seed economics:

| seed | Q1274 T | Q1273 T | marginal T | +719 gate |
|---:|---:|---:|---:|---|
| 0 | 916424.62 | 917056.48 | +631.86 | PASS by 87.14 |
| 1 | 916591.53 | 917090.25 | +498.72 | PASS by 220.28 |

Using the worse paired delta conservatively against live rounded T916526 gives
projected rounded full T <= 917158, projected score <= `1,167,542,134`, and
strict-beat margin >= `111,990`. This is an estimate, not a full evaluator
receipt; the exact live Q1273 ceiling remains T917245.

### Cheap correctness gates

- Release build: PASS.
- Runtime opt-out identity: PASS; `SUB4_PP_PEAK=1274` plus
  `SUB4_SQUARE_LADDER=244` reproduces ancestor SHA-256 `2974f706...` exactly,
  while the default rebuild reproduces candidate SHA-256 `ee6448db...`.
- Production 64-lane affine selfcheck: PASS, Q1273, T917188.359.
- Product-register square selfcheck: PASS, Q1273, T58726.125.
- Both fixed-64 profiles: classical/phase/dirty `0/0/0`.
- Focused Rust test target: BLOCKED before test execution by 165 inherited
  test-only compile errors (missing old direct-centered symbols and obsolete
  simulator methods). The production binary and both env-gated selfchecks
  compile and pass; the candidate changes touch neither failing test surface.

At structural commit seal, no full-9024 evaluation, nonce scan, model port,
provider action, or submission had been run.

### Authorized inherited-nonce full gate

After structural source/evidence commit
`093d85d64de87aa5006a94868172f642daacf136` was pushed, the parent lane
authorized exactly one unchanged 9,024-shot evaluation on the inherited nonce.
The candidate `ops.bin` and the unchanged trusted evaluator were staged outside
Git at `/Users/olifreuler/ecdsa-ops/q1273-redescent-093d85d-full9024`.

- source tree: `f6fd9d8b151a84fd886835ff3a818d3c1c9ef072`;
- emitted ops: `12,933,805`;
- ops SHA-256:
  `ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1`;
- trusted evaluator source SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`;
- trusted evaluator binary SHA-256:
  `a082c8449897081a0822fcf8866346a90cd4d37dfcdd3660ab64768ffb542436`;
- measured Q/T: Q1273 / T917103.815, rounded T917104;
- hypothetical rounded product: `1,167,473,392`, which clears live score
  `1,167,654,124` by `180,732` and clears the Q1273 T ceiling by `141`;
- classical/phase/ancilla: `12/12/0`;
- first mismatch: shot 93;
- evaluator log SHA-256:
  `bf93954845fcb8e13a38f108f4a7d28332ed29ce357d7f633a47794a2bf38400`;
- evaluator result-row SHA-256:
  `dc515b01994fc32eeba8485990910972bf0bbf908ff69092515a6973d718bd64`.
- external receipt SHA-256:
  `f65aad34d8392d2c273349aa06f50beb8a8cc0a01c04892e801455081840ce17`;
- verified artifact-manifest SHA-256:
  `59e1d3b3d7de85765777695ad60ddd090713b34dc710d3365506de4b63b82dff`.

The unchanged evaluator correctly emitted no canonical `score.json` for the
failed correctness gate. The result row's `5c6404f` short commit is an unrelated
enclosing-worktree metadata lookup from the external archive; the exact source
commit/tree and byte hashes above are authoritative.

### Verdict and next binder

`SCORE PASS / CORRECTNESS FAIL / MODEL-QUALIFICATION HANDOFF`. The pair is a
real global Q1274 -> Q1273 cut and its measured T clears the live product
ceiling, but the inherited nonce is dirty at `12/12/0`. It is not a submission
candidate and no hunt is authorized. Its exact source/ops identity is suitable
for a separately predeclared predictor qualification if the campaign chooses
to price the dirty stream.

The next plateau is still the same four phase families at Q1273. The marginal
seed-0 cost is concentrated in replay geometry: division replay +296.30 T,
multiplication walkback +204.26 T, multiplication replay +116.40 T, versus
only +12.20 T in the square. The next structural binder is therefore the
replay/walkback boundary-carry ladder and its long tape passengers, not another
square-only notch. Any future Q1272 attempt should first remove replay carry or
tape co-residence; blindly applying another peak/ladder notch repeats the
expensive side of the saddle.

Candidate B0 confirms the one-wire movement at each reducible limb: division
replay ladder 130 -> 129, square carry ladder 243 -> 242, multiplication replay
ladder 61 -> 60, and multiplication walkback ladder 62 -> 61. The large tape,
output, coefficient, and walk-passenger populations remain co-resident.

### Near-gate calibration addendum

Predeclared after the seed-0 result, before revealing any seed-1 measurement:
because seed 0 leaves less than 100 T of projected ceiling headroom, run exactly
one quiet paired remeasurement at `PP_PROFILE_SEED=1`. The candidate and the
runtime-restored Q1274 ancestor use the same inputs and simulator randomness.
Both paired deltas must be <= +719 T; disagreement closes the route as HOLD
rather than inviting another seed or parameter change.
