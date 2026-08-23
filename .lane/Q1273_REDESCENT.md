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

Pending.

### Near-gate calibration addendum

Predeclared after the seed-0 result, before revealing any seed-1 measurement:
because seed 0 leaves less than 100 T of projected ceiling headroom, run exactly
one quiet paired remeasurement at `PP_PROFILE_SEED=1`. The candidate and the
runtime-restored Q1274 ancestor use the same inputs and simulator randomness.
Both paired deltas must be <= +719 T; disagreement closes the route as HOLD
rather than inviting another seed or parameter change.
