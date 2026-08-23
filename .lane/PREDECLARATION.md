# b523 Q1276 exact model qualification

Predeclared 2026-08-23 before circuit, model, or packet edits.

## Source and candidate identity

- protected source: `b523ecff127171013575bbcc3823e01996a79a34`;
- measured env-only candidate: `SUB4_PP_PEAK=1276` plus
  `SUB4_SQUARE_LADDER=246`;
- exact candidate artifact: 12,901,678 operations, SHA-256
  `d460c3968659b6bbbf5615268d73df210df55f9cd4cbca330de1ef960c6dd4c0`;
- exact geometry: Q1276, rounds divide/multiply `700/696`, replay fold
  window `53`, value-width break `30`, R1/R2 `298/613`;
- inherited full result: T915834.428, `17/16/0`;
- paired H64 candidate-row receipt:
  `84cdef5cc22bdde9c85210b28dab4dcfb767fec47463eadd7a21d761349febe2`.

The structural evidence is commit `e77ee12303a0ac898ba4042886df5d2efbd388ac`
on `research/b523-ladder-redescent`.

## Minimal bake

Change exactly two circuit defaults and no other circuit behavior:

1. replay peak `1278 -> 1276` in `pingpong_div.rs`;
2. square ladder `248 -> 246` in `product_register.rs`.

With the two environment variables unset, a forced clean build must reproduce
12,901,678 operations and SHA `d460c396...` byte-for-byte. A diff outside the
two defaults or an identity mismatch kills the bake.

## Upstream predictor port

Port the public `pingpong-prefilter` source at commit
`da0e5721f14f5d956aa703b38311f4087388a7b1`:

- Rust source SHA-256:
  `bc01d12729be766a2a385e65db1c36df31904ee2e9afd3772828e7c9cb9d1593`;
- CUDA source SHA-256:
  `2778a3de4359bcb74b20c16419ea914f571af880babcf25fa40f67923b8b32b1`;
- CUDA build-script SHA-256:
  `cf7284dd7a5c29db04bdd1d42504cca7c69d6e1f2d2e618aacc61544e198f7ef`.

The allowed semantic model delta is restricted to the exact b523 defaults:

- multiply rounds `rounds_div - 2 -> rounds_div - 4`;
- replay fold `54 -> 53`;
- `BREAK_1 40 -> 30`;
- validated operation count `13,324,385 -> 12,901,678`;
- source path/build integration and fail-closed identity text.

Do not tune the model after seeing calibration errors. With all model knobs
unset, predict classical mismatch counts for the complete frozen H64 candidate
block `444000000000..444000000063`. Every one of the 64 predictions must equal
the already frozen unchanged full-evaluator classical count. One mismatch is a
terminal `FAIL_MODEL`; count-only or aggregate equality is insufficient.

The model remains classical-only. Its optional phase ordering is not a
rejection gate and is outside this qualification.

## Frozen Linux/CUDA fixture set

If and only if all 64 CPU predictions match, freeze exactly the 32 even-index
H64 nonces:

```text
444000000000, 444000000002, ..., 444000000062
```

Each fixture records nonce, exact classical count, candidate operation count,
candidate operation SHA, and the CPU model's state/checkpoint identity. This
selection rule is nonce-index based and was fixed before predictor output.

Prepare a fail-closed Linux/CUDA parity packet that:

- refuses wrong operation count and wrong exact operation SHA;
- builds the Rust CPU oracle and CUDA source from frozen hashes;
- requires CPU = CUDA exact-count equality on all 32 fixtures;
- tests at least comb8 and comb16 where the CUDA implementation exposes those
  modes, otherwise records that the upstream kernel has one exact mode;
- emits a completion receipt only after every fixture and negative guard;
- has no range, screen, hunt, or calibration launch path in the parity stage.

This lane prepares and hands off the packet. It does not contact a provider or
run Linux/CUDA parity, scan a range, start a hunt, mutate a fleet, submit, or
spend. Generated operations, checkpoints, binaries, logs, and raw evaluator
artifacts stay outside Git.
