# Exact CPU-model qualification: b523 Q1276

Date: 2026-08-23

## Verdict

`EXACT_CPU_MODEL_PASS`; `HOLD_LINUX_CUDA_PARITY`; `HOLD_SCAN`;
`HOLD_HUNT`; `HOLD_PROVIDER`; `HOLD_SUBMIT`.

The frozen general low-53/high-203 coordinate-shell correction matches the
trusted evaluator's complete classical mismatch-shot sets on both the original
H64 and the precommitted blinded disjoint32.  This closes the bounded CPU-model
qualification gate.  It does not authorize a scan: the C/CUDA ports and their
source-bound parity/negative guards remain downstream.

## Source and executable identities

- correction commit before the blinded outcomes were revealed: `7204c6d`;
- corrected predictor source SHA-256:
  `7a985f119df81b9be2150eea14480156bbf2da01652b2502eb02f861498ec115`;
- corrected local predictor binary SHA-256:
  `e460675947b48ff736fdfdbb218979bc952ae6cae02af81e00b007ae5c2320e9`;
- uninstrumented trusted evaluator source SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`;
- temporary shot-index-only evaluator source SHA-256:
  `3c9cce35ae2f6feb6e090d90d62bdff4e70d743854c0b654a287f3c7be1b7890`;
- temporary trusted evaluator binary SHA-256:
  `6978d4956d744b427c522c30dbffd2bba2736430482d2989dcff3bee57ff6803`;
- untrusted circuit builder binary SHA-256:
  `f35899e88731ee9f5121246b268cc06544cd6dd864fe874b731b209844d57466`.

The temporary evaluator change only emitted the indices of already-detected
classical mismatches and suppressed result-file writes.  It did not alter the
simulation, seeds, expected points, shot count, or channel accounting.  The
instrumentation was removed byte-for-byte after qualification; no evaluator
change is committed.

## Circuit binding

- baked source: b523 with only `PP_PEAK=1276` and
  `SUB4_SQUARE_LADDER=246` hard-coded;
- operations per fixture: `12,901,678`;
- qubits per fixture: `1276`;
- inherited-candidate operations SHA-256:
  `d460c3968659b6bbbf5615268d73df210df55f9cd4cbca330de1ef960c6dd4c0`.

Each nonce bakes into its own operation stream because the tail nonce is part
of the circuit.  The raw receipt hashes below cover every per-nonce operations
SHA, op count, Q, channel count, and sorted classical shot list.

## Original H64 exact-set gate

- unchanged full evaluator: 64 fixtures x 9,024 shots;
- structural guards: 64/64 at Q1276, 12,901,678 operations, ancilla zero;
- evaluator totals: classical `1,048`, phase `883`, ancilla `0`;
- predictor/evaluator classical counts: 64/64 equal;
- predictor/evaluator complete classical shot sets: 64/64 equal;
- evaluator-only shots: `0`;
- predictor-only shots: `0`;
- raw bound rows receipt SHA-256:
  `90ec049539f89aa883f34676de2df92ea6de2221d664406072f16000cace4a9d`.

This includes the three previously missing shots: nonce `444000000002` shot
`4731`, nonce `444000000040` shot `4800`, and nonce `444000000042` shot
`4853`.

## Blinded disjoint32 exact-set gate

The nonce corpus was committed before diagnosis and before any evaluator
outcome was generated:

- corpus commit: `8948598`;
- corpus file SHA-256:
  `798bf6acc936215ff1f00487b1597833351c4ab9dbd1804ae15eba2515d914b4`;
- corrected predictor count receipt SHA-256, frozen before trusted evaluation:
  `ebdbfdf4c26b36a054e7ad93563fd92d9818fa147df52d816f01147fef5379cc`;
- corrected predictor verbose receipt SHA-256, frozen before trusted evaluation:
  `fea336e9dba9869f26cc050915a47bd36bfd73a1e985c1ac7efc9424626d3327`.

Results:

- unchanged full evaluator: 32 fixtures x 9,024 shots;
- structural guards: 32/32 at Q1276, 12,901,678 operations, ancilla zero;
- evaluator totals: classical `523`, phase `444`, ancilla `0`;
- predictor/evaluator classical counts: 32/32 equal;
- predictor/evaluator complete classical shot sets: 32/32 equal;
- evaluator-only shots: `0`;
- predictor-only shots: `0`;
- raw bound rows receipt SHA-256:
  `90e22fd7c5100ee058d4b3e9837d8d4a2ca83eddd5501fd24e230380a2ccf6f3`.

The compact per-fixture digest ledger is
`.lane/model-exact-set-qualification.tsv`, SHA-256
`a6358977fc9fe1d7f8701d0c28ffbab3fdab71e5792baf620ee88b9c9ffd802f`.
Every ledger digest is over the evaluator's canonical sorted classical-shot
CSV plus a trailing newline; the predictor set was required to be identical
before the row received `PASS`.

## Qualification boundary and next gate

This is exact empirical equality across 96 source-bound full-9,024-shot
fixtures, not a proof over every nonce.  No demonstrated predictor-only fault
remains in the qualified corpus.  Before any scan, port the same generic
coordinate subtraction and fused reverse-subtraction cells to the fail-closed
Linux/CUDA model, bind them to exact source/operation identities, and require
CPU = CUDA comb8 = CUDA comb16 on frozen fixtures plus wrong-count and
same-count/wrong-SHA rejection.  Until that closes, scan and provider work stay
disabled.
