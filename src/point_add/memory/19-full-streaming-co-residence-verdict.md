# Full-streaming replay: co-residence verdict

## Verdict

`HARD_NACK` for eliminating both replay batches by setting the existing
interleave plan to a fully streamed traversal on the bound source. The stream
removes terminal batch replay, but it does not remove sign history: divide must
retain every sign for its later reverse walk. The coefficient pair therefore
becomes co-live with the early walk carry ladder and the growing tape, producing
Q1309 rather than a lower-Q resource equation.

This verdict is scoped to the source-present fully streamed schedule. It is not
a lower bound against a new recurrence that erases or compresses history.

## Binding

- Official source commit:
  `67524171baaf568dc3dc606f38515745f70804ff`
- Official source tree:
  `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`
- Tested environment:

```text
SUB4_PP_R1=0
SUB4_PP_R1_MUL=0
SUB4_PP_R2=999
SUB4_PP_PEAK=1153
SUB4_PP_WALK_PEAK=1153
```

- Generated ops SHA256:
  `505f67b3d1076d1589f2830da9f6a0cc12e98ff1c8ffc570cf6ffd76549e8a7b`
- Fixed 64-lane profile transcript SHA256:
  `a1fa2a03be548e490ed0d47e3a1840590deb97009155a7d53ccdeed39348051f`
- B0 owner transcript SHA256:
  `15769dd9d7bf70d95aa7ed2e63d5bebd7af64bbc1db01d10664dc976570182f9`

## Exact measured equation

The full local profile reported:

```text
Q1309
T64=999247.98
ops=14729813
classical=0 phase=0x0 dirty=0
first peak phase=pp_div_replay op=669340
```

The exact live-owner census at the binding operation was:

```text
256  numerator/caller word
256  replay coefficient word
239  first walk limb
239  second walk limb
235  early walk carry ladder
 82  retained sign tape
  1  replay scalar
  1  replay scalar
----
1309
```

The multiply walkback independently reaches Q1309. The requested Q1153 cap is
not silently ignored: it controls replay and split-walk budgets, but the
source-present schedule has a 235-wire minimum early walk ladder while the
coefficient pair and 82 signs are resident. Lowering that cap cannot delete
these owners.

## Economics

Even before correctness qualification, the diagnostic product is
`1309 * round(999247.98) = 1,308,015,632`, well above the bound live score
`1,154,731,130`. The stream is therefore both wider and more expensive than
the promoted composition. A trusted 9,024-shot run is unwarranted.

## Changed-premise reopen

Reopen only with a mechanism that changes at least one of these terms rather
than selecting another plan coordinate:

1. consume or compress divide signs before reverse walk without losing phase;
2. replace the two-word coefficient recurrence;
3. replace the wide early walk adder while retaining exact inverse cleanup; or
4. fuse the affine shell so the complete multiply traversal disappears.

No provider, nonce, fleet, queue, push, public-note, or submission action was
taken.
