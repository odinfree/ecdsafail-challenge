# Teddy Pender unchanged-reference cleanup on `6b5c82c`

Created: 2026-08-22T20:39:31Z
Verdict: `OVERTURN_PREVIOUS_LIVE_NUMERATOR_ABI_KILL`
Candidate status: `HOLD_LOW5_UNJUDGED`

## Credit and question

Teddy Pender supplied the architecture, the exact low-five observation for
signs one through three, and the Burn-the-House-Down rule that an incumbent
reference must survive its own falsifier before that falsifier can judge a new
representation. His advice, not this instrumentation, reopened the buried tape
assumption.

The exact question was narrow: why did the unchanged four-round reference in
commit `34c1b50` fail reverse/cleanup on nonzero numerators, and was that a
reference-harness problem or evidence against Teddy's low-five candidate?

Model: Kimi Code (k2/k3, high effort), multi-lane agent campaign.

## Evidence provenance and shipping audit

The receipts below were produced by evidence commit `2bff9dc`. That commit's
568-line env-gated self-check was source-bound temporary instrumentation:

- it printed and assumed exact source `6b5c82c`;
- it imported the first nonzero corpus from experiment commit `34c1b50`;
- it encoded campaign-only forward/reverse checkpoints and two temporary
  schedules;
- it had no normal production callsite and did not establish a source-agnostic
  property suitable for permanent regression coverage.

PIP shipping review therefore removed the gate in a follow-up commit and
restored both edited production source files exactly to `6b5c82c`. The commands
and outputs remain here as immutable, commit-scoped evidence. They are not
commands supported by the shipping-clean lane HEAD.

## Isolation

- Exact promoted source:
  `6b5c82cbe723b33c296c8926876f14f1ac3307a8`.
- Imported evidence only: `34c1b50` and its parent experiment stack on
  `9805dee`.
- Historical evidence gate at `2bff9dc`:
  `SUB4_PP_BURN_REFERENCE_CLEANUP_SELFTEST=1`.
- Corpus: the first deterministic 64-lane nonzero batch from the old 4,096-case
  stress receipt.
- Candidate code: absent. Both tested circuits use only unchanged production
  walk/replay primitives.
- Schedules:
  - `historical_sentinels`: reproduces the old reference's four round-one
    sentinel toggles;
  - `production_faithful`: removes those diagnostic sentinels.
- The same SHAKE draw is used for both schedules.
- No nonce hunt, provider work, spend, push, post, publication, or submission.

The self-check records every matched forward/reverse boundary. At replay
boundaries it compares only the persistent coefficient and numerator registers,
plus phase. Simulator measurement-record bits are deliberately excluded: they
are transcript records, not logical state, and comparing them created a false
all-lane mismatch in the first draft of the falsifier.

## Falsifier 1: exact live replay geometry

Historical command at evidence commit `2bff9dc`:

```bash
SUB4_PP_BURN_REFERENCE_CLEANUP_SELFTEST=1 \
  ./target/release/build_circuit
```

The default source geometry is fold width 54, flag compare width 22, endpoint
width 26, fused inverse, and late-carry chunking.

### Historical-sentinel reference

```text
first_bad_replay_logical_stage=undo_replay_round_3
first_bad_replay_logical_lanes=20
final_classical=33
final_phase=23
final_ancilla=0
peak_q=1120
operations=54466
emitted_t=4960
executed_t=308706
```

### Production-faithful reference

```text
first_bad_replay_logical_stage=undo_replay_round_3
first_bad_replay_logical_lanes=22
final_classical=43
final_phase=27
final_ancilla=0
peak_q=1120
operations=52450
emitted_t=4960
executed_t=308706
```

The first logical divergence is the inverse round-three replay cell in both
schedules. Removing the historical sentinels does not repair the reference; it
increases final logical failures from 33 to 43 lanes on this paired corpus.
Therefore the old sentinels are not the root cause.

This also reproduces the old qualitative result on the new exact source: a
short arbitrary nonzero slice is dirty under the accepted source's deliberately
truncated and measured replay geometry. That source geometry already carries
modeled residual risk and was accepted only as a complete frozen circuit with
its exact tail nonce and trusted corpus.

## Falsifier 2: strict logical replay oracle

Historical command at evidence commit `2bff9dc`:

```bash
SUB4_PP_BURN_REFERENCE_CLEANUP_SELFTEST=1 \
SUB4_PP_REPLAY_FOLD_WINDOW=256 \
SUB4_PP_REPLAY_FLAG_COMPARE=256 \
SUB4_PP_ENDPOINT_FOLD_WINDOW=256 \
SUB4_PP_LEGACY_CHUNK_ORDER=1 \
SUB4_PINGPONG_UNFUSED_INVERSE=1 \
  ./target/release/build_circuit
```

This is intentionally wider and slower. It is a reference oracle, not a score
candidate.

### Historical-sentinel strict reference

```text
first_bad_replay_logical_stage=none
first_bad_replay_logical_lanes=0
final_classical=0
final_phase=24
final_ancilla=0
peak_q=1295
operations=83042
emitted_t=8030
executed_t=476200
```

### Production-faithful strict reference

```text
first_bad_replay_logical_stage=none
first_bad_replay_logical_lanes=0
final_classical=0
final_phase=33
final_ancilla=0
peak_q=1295
operations=81026
emitted_t=8030
executed_t=476200
```

The strict construction returns the persistent replay registers exactly at
every inverse boundary and returns denominator/numerator exactly at the final
ABI on all 64 lanes. This proves that the four-round reverse layout and caller
ABI are not structurally broken. The live logical dirt comes from the accepted
approximate replay geometry, not from Teddy's five-bit representation and not
from the sentinel harness.

The strict component's remaining phase masks are real diagnostic output, but
they are not a fixed-floor finding. This slice omits the complete affine
construction and the exact source-bound tail calibration. The protected
`6b5c82c` circuit itself independently passes the unchanged full 9,024-shot
trusted phase gate. A short arbitrary corpus cannot promote its raw phase count
into a production verdict.

## Normal-path identity

With the self-check gate absent:

```bash
./target/release/build_circuit
shasum -a 256 ops.bin
```

Observed:

```text
emitted operations: 12950916
88706a40300b7f019202f65a0f28e86dbfe27fda65ad5ed33b0482ff9b14b7eb  ops.bin
```

This exactly matches the protected clean `6b5c82c` stream receipt. After the
temporary self-check was removed, the two production source files also matched
`6b5c82c` byte-for-byte and the same normal stream hash was reverified. No
generated stream is retained in the lane.

## Decision

Overturn `KILL_LIVE_NUMERATOR_ABI_CLOSURE` as a judgment of Teddy's low-five
candidate. The old gate asked a residual approximate component to be an exact
oracle on an arbitrary nonzero corpus, then charged its own failure to the
candidate. The unchanged reference never earned that authority.

Do not promote the Q1123 low-five result. Its nonzero production status remains
unknown. Rejudge it with a paired two-level contract:

1. under the strict logical oracle, require exact midpoint equality, no replay
   logical divergence, and final classical/ancilla `0/0` relative to the clean
   reference;
2. under exact live geometry, require no new fixed residual above the paired
   reference, then defer phase and acceptance authority to a competitive,
   frozen whole-circuit candidate and the unchanged trusted 9,024-shot gate.

That is the next bounded saddle. It unblocks the Fable streamed-history lane's
logical test without authorizing grind-first statistics. Teddy gave us the map;
we merely stopped accusing the compass of the weather. The basement remains
haunted, but at least the ghost now has an exact operation index.
