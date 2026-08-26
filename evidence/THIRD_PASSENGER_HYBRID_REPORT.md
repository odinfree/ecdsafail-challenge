# P1267/W1265 third-passenger hybrid

Date: 2026-08-26

Verdict: `ADMIT_TO_CONTROLLED_VALIDATION`. The construction has passed its
source-bound proof and 64-lane resource/correctness gate. It is not an official
score, clean-nonce result, provider authorization, or submission admission.

## Binding

- parent candidate: `9525e3271b19f17f218a9776e14f32a1baed52f2`
- parent tree: `f425ae5e144445f7aebb15ef022ebf23fbc05149`
- support certificate commit: `5782793` (cherry-picked here as `77dec0c`)
- constructed `src/point_add/pingpong_div.rs` SHA-256:
  `950997f008b472b14c7bf6d42f879014b71db166afd6e8094295e1bef86fb04d`
- exact candidate environment:
  `SUB4_SQUARE_B_LOCAL_K2=1 SUB4_PP_PEAK=1267`
  `SUB4_PP_WALK_PEAK=1265 SUB4_PP_THIRD_PASSENGER=1`
  `SUB4_PINGPONG_INPUT_AWARE_CONSTPROP=1 TLM_CASCADE_DISABLE=1`, with
  `TLM_CONSTPROP_STRADDLE` absent.

Only exact value `1` enables the construction. Absent, `0`, and invalid values
remain byte-identical under the P1267/W1266 baseline gate.

## Construction

At each nonterminal replay checkpoint, the existing clean loans `u[0]` and
`v[0]` gain one parity-selected passenger:

```text
even r: clear v[1] with u[2] XOR tape[1]
odd r:  clear u[1] with v[2] XOR tape[1]
```

The two controls remain live and stable across the replay cell. The passenger
is released clean, consumed by replay scratch, reacquired after that scratch is
clean, and restored with the two CX operations in reverse order. Prefix call
sites use `r1.saturating_sub(1)` so default-off custom schedules do not acquire
a new eager-underflow panic.

Coverage is 312 divide cells and 332 multiply cells, spanning post-round
checkpoints 314 through 645. The construction adds only Clifford operations;
its conditional executed-Toffoli value can nevertheless change because the
additional reusable wire changes intermediate measured-erasure paths.

## Proof gate

The construction-bound checker passes 9/9 tests and rejects source drift in
the flag, parity mapping, clear/restore sequence, four call sites, or two safe
prefix mappings. Its exact certificate remains:

- complete three-low-bit transition theorem: 16 rows, zero violations;
- reduced `p=2^6-9`: 2,106 checks, zero violations;
- production-width: 4,096 deterministic inputs x 332 rounds = 1,359,872
  checks, zero violations;
- input digest:
  `43b56f5f6eff8fc800c18a2c532923708bff44ec076f0abed98956d7b8cd8ed3`;
- checkpoint digest:
  `1da23ba23810716395dfbaaed376f88147a669cce5298087099a26ad73fe8d09`.

Independent review reproduced 9/9 tests against checker SHA-256
`a8ceae14bf09d94c1287b2b10216fa7c0788e70b029f5a607551aad37234b965`
and test SHA-256
`d5366ce33208e1020545420be1ea2f5e047f8ac27afdf642c63fa469a06d0d8d`.

## RED/GREEN resource gate

The first P1267/W1266 construction was a useful `HARD_NACK`: it stayed Q1265
because coefficient allocation binds before the prefix loan. Unsafe allocation
reorders were rejected because they alias passenger identities across the
subsequent value walk or recreate the same Q1265 simultaneous live set.

The bounded hybrid lowers only the walk cap to W1265 while retaining the
cheaper replay cap P1267. The third passenger then prevents replay from becoming
the replacement binder.

| arm | P/W | passenger | emitted ops | active/analyzed Q | profile T | final state |
|---|---|---|---:|---:|---:|---|
| baseline | 1267/1266 | absent | 12,520,960 | 1265/1265 | 906,701.56 | 0/0/0 |
| hybrid control | 1267/1265 | `0` | 12,524,600 | 1265/1265 | 906,890.14 | 0/0/0 |
| hybrid candidate | 1267/1265 | `1` | 12,527,189 | 1264/1264 | 906,924.45 | 0/0/0 |

`0/0/0` here means 64-lane profile classical mismatch, phase, and dirty-qubit
counts. It is not the trusted 9,024-shot challenge result.

Independent reconstruction counted exactly 644 loan cells and an exact raw
delta of `644 x 4 = 2,576` CX operations. The post-F21 emitted-op delta from
the W1265 control is 2,589 because the surrounding transformed stream and
finalization differ; no extra CCX or CCZ is introduced by the loan itself.

With custom `R1=0`, absent, `0`, and invalid flags produced the identical
artifact SHA-256
`934196db808c1d20d3c121efda4c6dfc2278fca51770a06d4c96149a76751508`.
Exact `1` failed closed at the `tape.len() >= 2` guard with no artifact.

Input-aware constprop removes 51 executed Toffolis in both the baseline and
hybrid candidate. Applying the evaluator's round-before-multiply rule to this
controlled profile gives:

```text
baseline: 1265 x round(906701.56 - 51) = 1,146,913,515
candidate:1264 x round(906924.45 - 51) = 1,146,287,472
profile product gain                         626,043
profile lead versus live source            4,586,286
```

The candidate pays 222.89 profile Toffolis for one qubit, well below the
approximately 717-Toffoli break-even. This is a larger local margin than the
Q1265 stack, but the populations differ and no official-score claim follows.

## Remaining gates

1. Independent three-arm 9,024 controlled-lane gate: current baseline A,
   P1267/W1265 passenger-off equivalence control H, and candidate C.
2. Independent code/diff review and a clean construction commit.
3. Generate a new source-bound checkpoint and CPU/CUDA model for the exact
   candidate artifact; previous Q1264 and Q1265 prefilters do not apply.
4. Device CPU/CUDA parity and an enforceable combined provider spend cap.
5. Bounded nonce search, untouched trusted 9,024-shot `0/0/0`, independent
   reproduction, live-source/score rebind, and submission gate.

## Provenance

The reduced-width direction was suggested by Justin Drake. Codex implemented
the N1 branch-B K2 and this third-passenger hybrid. The exact low-bit support
certificate was developed and independently scaled in the support-cert lane.
The F21 constprop implementation/checker is authored by `welttowelt`. Fable was
asked for read-only structural advice on cadence but returned only a quota
error; no Fable method is claimed. No provider, protected fleet, upstream
repository, or submission state was changed.
