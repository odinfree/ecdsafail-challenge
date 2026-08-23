# b523 Q1276 missing-channel diagnosis

Date: 2026-08-23

## Verdict

`DIAGNOSIS_PASS`: the three count discrepancies are three exact
evaluator-only shots from one source family—the low-53/high-203 carry boundary
in the final coordinate shell.  There are no predictor-only shots in the
localized rows.

The product-register square, divide restore, and multiply restore are exact for
all three counterexamples.  Two shots first diverge in
`tlm_coord_y_sub_final`; one first diverges in `tlm_coord_rsub_final`.  Each
wrong coordinate is exactly `+2^53` above the field result.

## Exact shot sets

The trusted evaluator was instrumented only to emit every existing classical
mismatch shot index and to suppress result-file writes.  Circuit evaluation,
shot construction, and all validity checks were unchanged.

- temporary evaluator source SHA-256:
  `3c9cce35ae2f6feb6e090d90d62bdff4e70d743854c0b654a287f3c7be1b7890`;
- temporary evaluator binary SHA-256:
  `6978d4956d744b427c522c30dbffd2bba2736430482d2989dcff3bee57ff6803`;
- uninstrumented candidate builder binary SHA-256:
  `f35899e88731ee9f5121246b268cc06544cd6dd864fe874b731b209844d57466`.

| nonce | ops SHA-256 | evaluator | predictor | evaluator-only | predictor-only |
| ---: | --- | ---: | ---: | ---: | ---: |
| 444000000002 | `ca8c196bb524edf01299a70dfc47896ce8d4a475c0d133bf94b65fbd0bf36ebf` | 14 | 13 | 4731 | none |
| 444000000040 | `743593159ec590a0f4818e14f9915b60f438a8a50740ebad8314d344df2ef6a7` | 22 | 21 | 4800 | none |
| 444000000042 | `d3cef6607accda389788848fcb54ec11613b1fef7b92c0c88c40aee8e0e03410` | 20 | 19 | 4853 | none |

Every stream contains exactly `12,901,678` operations and measures Q1276 with
zero ancilla-garbage batches.  The complete 56-row union of evaluator and
predictor sets is `.lane/missing-channel-shotsets.tsv`, SHA-256
`af63be8ccf1523f4e14ceda81200c336e4e302be07afc0a7300c34b58532e1c5`.
It contains 53 shared shots, three evaluator-only shots, and zero
predictor-only shots.

## Boundary trace

A temporary source-bound profiler ran the three exact affine inputs through the
unchanged circuit at each of its 16 top-level phase boundaries.  The target
product-square subsystem was also exercised directly on the three exact
`(lambda, accumulator)` pairs.

- temporary product-square diagnostic source SHA-256:
  `8d2c7657579bcb15f62d1f023e8ad501eb08d9070bcfd0666f6e4bedc0114f61`;
- temporary phase-profiler source SHA-256:
  `a86f3f9d3df31f5e6bb611d9e99daa223573af08c2634d4513bde3f1dc861e38`;
- combined diagnostic builder binary SHA-256:
  `beb5d74304a544ae3f5a5f0d6938f62a77f3cdeb4b3462b60fcb4968cab624e8`.

The direct product-square output equals exact field subtraction for all three
inputs, with phase zero and all non-register qubits clean.  The complete affine
trace is exact through `pp_mul_restore` for all three shots.

| nonce / shot | first divergent phase | coordinate | circuit value | exact-model value | delta |
| --- | --- | --- | --- | --- | --- |
| 444000000002 / 4731 | `tlm_coord_y_sub_final` | y | `a49743152857dc122a260d5e524887cd7cbaeee7caa3f643c3ffffffb3567c55` | `a49743152857dc122a260d5e524887cd7cbaeee7caa3f643c3dfffffb3567c55` | `+2^53` |
| 444000000040 / 4800 | `tlm_coord_rsub_final` | x | `7a2a06040a0b7ba84a2ab7bf141531df2a1c8b07c4816de7d65fffff84effb47` | `7a2a06040a0b7ba84a2ab7bf141531df2a1c8b07c4816de7d63fffff84effb47` | `+2^53` |
| 444000000042 / 4853 | `tlm_coord_y_sub_final` | y | `ba33d4387b437767f7764b046fc07d8bfbd8168275705c1f6e9fffff1223818a` | `ba33d4387b437767f7764b046fc07d8bfbd8168275705c1f6e7fffff1223818a` | `+2^53` |

For the two y-subtraction shots, the full subtraction borrows (`anc=1`) and
the post-low-fold value is at or above the exact source threshold
`2^53 - (2^32 + 977) = 0x1ffffefffffc2f`.  The low-53 fold is value-correct,
but the carry/borrow crossing into the high 203 bits is dropped.  The fused
reverse-subtraction shot reaches the analogous lost-boundary state with
`anc=0`.  Replaying the source operations gives the phase-trace values above
without a nonce or shot special case.

## Frozen semantic correction

The single allowed correction is a coordinate-shell port:

1. implement the circuit's `mod_sub_vented` low-53 fold as a pure Rust value
   function;
2. implement the circuit's default fused `mod_rsub_vented_loaded` value
   function;
3. use those functions for coordinate subtraction and final reverse
   subtraction in both the fast and traced predictor paths.

This follows the source operations—256-bit complement/add, the real carry bit,
and the truncated `F = 2^32 + 977` fold.  It will not inspect a nonce, shot,
expected count, or corpus membership.  No circuit source changes are proposed.

The temporary evaluator, square, and phase-profiler instrumentation has been
removed byte-for-byte before this diagnosis is committed.  No generated
operation stream, binary, or raw log is retained in Git.

