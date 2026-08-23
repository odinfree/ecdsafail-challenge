# b523ecf balanced ladder re-descent

Predeclared 2026-08-23 before any candidate build or measurement.

## Live and historical anchors

- live refresh: source `b523ecf`, score `1,169,101,620 = 1278 * 914790`;
- promoted full result: Q1278, exact average T `914789.886`, `0/0/0`;
- promoted artifact: 12,876,472 operations, SHA-256
  `4cb1787b181417c1e180ddf362fd7e44430ef2d422bb4184d73d7fe1924fdf7e`;
- current defaults: divide/multiply rounds `700/696`, replay peak `1278`,
  square ladder `248`, replay window `298/613`;
- accepted `087cafa` is the exact historical accepted source with the tighter
  square ladder: peak/ladder `1275/245`, Q1275/T918972;
- the later source-bound `bdf4845` saddle audit measured the adjacent
  peak/ladder `1276/246` pair at Q1276. Its full T delta over its protected
  parent was `+681.180`, but that transfer is only a projection here.

The group-chat recollection of an approximately eight-commit-old baseline is
supporting direction, not an exact source claim. Source inspection, rather
than the recollected distance, selects the already measured coordinated
peak/ladder pair.

## Smallest clean transplant

Keep `b523ecf` byte-source-identical and change only existing runtime opt-ins:

```text
SUB4_PP_PEAK=1276
SUB4_SQUARE_LADDER=246
```

All other defaults remain those of `b523ecf`, including rounds `700/696`,
R1/R2 `298/613`, width break `30`, and tail nonce `81327465284`. This tests
whether the promoted stream can realize a two-qubit descent by lowering both
known co-binders without paying the separate correctness cost of deleting two
divide rounds.

No semantic source edit, default change, adaptive neighbor, or grid is
authorized. A one-knob build may be used only as a cheap co-binder falsifier;
it cannot advance.

## Frozen measurement order

1. With both knobs unset, force a clean build and require the promoted count
   and operation SHA above.
2. Force a fresh candidate build. Record exact operation count/SHA, Q, fixed
   64-lane profile T and all three channels using `PP_PROFILE_SEED=0`.
3. Continue only if Q is at most 1276 and rounded T is at most 916223, the
   exact Q1276 strict-beat ceiling against the refreshed live score.
4. Run the product-square selftest and the complete point-add selftest under
   the exact candidate knobs. Require zero ancilla and affine/selftest pass.
5. Run the unchanged trusted evaluator for all 9,024 shots at inherited nonce
   `81327465284`; record exact T and classical/phase/ancilla channels.
6. If the structural score gate and ancilla gate still pass, run the complete
   fixed H64 nonce block `444000000000..444000000063`, in order, for both the
   unset protected source and the candidate. Every row uses a fresh operation
   artifact and the unchanged full 9,024-shot evaluator. Finish all 64 rows in
   each stream even if an intermediate row is dirty. Record aggregate channel
   counts, exact average T, and a sorted row-ledger SHA for each stream.

Changed operation streams do not inherit the promoted nonce's `0/0/0` result.
No H64 row is a hunt survivor and the corpus cannot authorize scanning.

## Verdict gate

`GO_MODEL` requires Q<=1276, rounded T<=916223, all selftests green, ancilla
zero in the inherited full run and all H64 rows, and no catastrophic increase
in either classical or phase H64 density relative to the unset source. Exact
CPU/GPU predictor qualification would remain a separate later gate.

This lane does not authorize a nonce hunt, provider action, fleet mutation,
submission, incumbent edit, or spend. Generated artifacts, binaries, logs,
and evaluator rows stay outside Git; only durable hashes and transcribed
evidence may be committed.
