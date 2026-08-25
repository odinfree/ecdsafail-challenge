# Generic round-two sign hosting at Q1263

Status: **source-baked structural candidate; diagnostic-only and not
admission-validated**. Submission remains **CLOSED**.

This result is bound to sealed source commit
`e793c38121451b7899e4a51730087041ff80f903`, tree
`3566f3cdc8d4b6555e32f8d356689e1f62c645c8`. The circuit-source diff over
`src/point_add/mod.rs` and `src/point_add/pingpong_div.rs` has SHA-256
`02862bb9783ab89af9da9771f8551d6a77f1597a1832bc71df9626af3b98a2aa`.

Reduced-width autoresearch direction suggested by Justin Drake.

## Invariant and implementation

In the alternating walk, the pre-round target at round `r` is the unchanged
source from round `r-1`. Therefore

```text
s_r = source_r[1] XOR source_(r-1)[1]
s_1 XOR ... XOR s_(R-1) = p[1] XOR old_operand[1]
```

The implementation omits only the generic round-two sign `s2`; it does not
reuse the separately falsified fused round-one candidate. Retained `s1` is
temporarily transformed into `s2` immediately around each consumer:

```text
local round two: s2 = s1 XOR p[1] XOR source_2[1]
checkpoint:      s2 = p[1] XOR old_operand[1] XOR all retained signs except s2
```

Both transforms are X/CX-only and are applied twice, restoring `s1`. The
retained path's two clean `s2` resets are reproduced on just-in-time clean
scratch wires at the same logical cell boundaries. That preserves the exact
global HMR/R random-event sequence without retaining `s2` across a peak.

The implementation and fail-closed opt-out live in
`pingpong_mod_mul_div_in_place`, `value_walk`, `value_walk_back`,
`toggle_local_s2_host`, `toggle_checkpoint_s2_host`,
`walk_round2_with_s1_host`, `walk_back_round2_with_s1_host`, and
`walk_back_round2_implicit_with_s1_host` in `pingpong_div.rs`.
`SUB4_PP_ELIDE_GENERIC_S2=0` selects the exact retained Q1264 path.

## Exact artifacts and resource result

| path | Q | emitted ops | compressed bytes | uncompressed bytes | SHA-256 |
|---|---:|---:|---:|---:|---|
| exact retained opt-out | 1264 | 12,548,734 | 45,649,871 | 702,729,120 | `f49c0d5d16bf41f0cb7a3eac0a74e5a097082f285cd3e0577d3023baa552c292` |
| zero-environment generic-s2 host | 1263 | 12,550,038 | 45,761,657 | 702,802,144 | `961049d362033b9d7168ce9d87de96f07e0aa675b68780aaf5a0fddd4421502d` |

The opt-out artifact is byte-identical to the independently clean-built sealed
Q1264 artifact. Two empty-circuit-control candidate builds were also
byte-identical to each other.

Both former binders fall exactly one wire:

- `pp_div_replay`: Q1264 to Q1263.
- `pp_mul_walkback`: Q1264 to Q1263.
- Complete active-allocation timeline: global maximum Q1263, with no transient
  Q1264 in another phase.

CCX remains `951,726` and CCZ remains `40`. The only static operation-count
changes are `+1,292 CX` and `+12 X`; R, HMR, and every other kind are exact.
Checkpoint parity materialization is 333 serial CX for divide and 313 for
multiply; applying each transform again to restore the host accounts for
`666 + 626 = 1,292` added CX. No T gate is added.

Paired 64-lane profiles at seeds 0, 1, and 2 matched in every phase row and in
total executed Toffoli: respectively `908680.36`, `908775.98`, and
`908598.69` for both candidate and retained paths.

## Correctness evidence and limits

`SUB4_PP_GENERIC_S2_SELFTEST=1` exhaustively checks widths 4 through 10,
every denominator in `1..p`, and `3*width` recurrence rounds, then asserts
that the production round-two tape slot owns no physical wire. Dedicated
Divide/Multiply and full 64-lane affine simulator gates passed with output,
phase, and ancilla cleanup exact at Q1263.

A coupled final-artifact differential used the same 64 valid affine lanes and
the same global logical random tape. It matched the random-event kind sequence
across `1,912,304` HMR/R events and every 64-bit classical execution mask for
all `951,766` logical CCX/CCZ gates. Its execution-mask SHA-256 was
`70e023bcabdc1a0a641fc61ca7f2bd80c8fc2b08711550861e8a30d99df8dae8`;
the complete trace log SHA-256 was
`69ce6d31416fb3086cb7118be20e7ff5ddf97e385964cb63735e0269c6383863`.

The inherited `82505456522172` tail nonce is only a negative control for this
new artifact. The untouched local trusted evaluator over 9,024 shots reported
28 classical mismatches, 12 phase-garbage batches, and zero ancilla-garbage
batches (diagnostic average executed Toffoli `908686.110`). This is not a
submission result and does not admit the artifact. A separately authorized
nonce search, exact artifact binding, clean trusted 9,024-shot validation,
independent reproduction, and refreshed-frontier comparison are all still
required before promotion or submission.
