# Q1270 native complete-mask qualification HOLD

Date: 2026-08-23. Decision:
`HOLD / NO MASK COMPARISON / SEALED CORPORA UNOPENED BEYOND TRACKED INPUTS`.

This gate began from clean, pushed commit
`8bc5c5b13589fc404e84e47c04dab7a2adaf6af0` on
`research/q1270-routed-combined-predictor`. Local HEAD and
`odinfree/research/q1270-routed-combined-predictor` were identical. The
authorized task was to add a bounded complete-mask mode for only the tracked
inherited and H64 corpora, build it twice, and compare complete classical,
raw-phase, clean-phase, and ancilla masks against the sealed trusted rows.

The implementation was stopped before editing predictor source or producing a
model mask. The present native recurrence is a deterministic positive unit,
not a complete finite-width simulator: `NativeRecurrence::walk` and replay
return at the first width, parity, terminal, or cleanup fault. A complete
classical mask needs the exact circuit continuation after those faults rather
than an early dirty classification. A complete raw-phase mask additionally
needs exact per-batch Fiat-Shamir consumption for every R/Hmr ordinal and the
source-derived residual at each of the 4,658 qualified target sites. The sealed
schedule contains 3,267 chunk-carry, 694 divide-flag, 694 multiply-flag, and
three arithmetic-shell sites, but the current native model does not emit their
post-fault values or compose their measurement words.

Adding only corpus-selection CLI framing would therefore create an interface
that cannot satisfy the complete-mask contract. Filling the missing words from
the trusted rows, borrowing a donor implementation, treating an early dirty
classification as an output bit, or inferring raw phase from clean phase would
make the equality circular or unsound. No such fallback was added.

## Reverified frozen boundary

- starting predictor source hashes:
  - `src/q1270_pp_model.h`:
    `2e5e7542dda34d543d855b03a337fd466c5acaa61201bcf242346755c403f2a1`;
  - `src/q1270_pp_host.h`:
    `65a9f341d4f79c4a1c009a30e7f080cae06c7e6cc9fdb8a00116af7181db69db`;
  - `src/q1270_ppcpu.cpp`:
    `10c388c45da4cb064adae86d53227eb3980904ca9cf3dafe7f48e41561f89717`;
  - `src/q1270_square_boundary.h`:
    `5cda36dffc29fd8a19881214900e580d3a9c7cbed729dab8f4b6a731565aca52`;
- accepted tracked corpus identities remain:
  - inherited:
    `dabc177103443bede607625489337794ac828e25b60e787a67f7789bfa1627f1`;
  - H64:
    `87fb300f0f1aa12cb4c6e70c24f0cae7899313c1cc5bd6f92ab70c06848314bd`;
- target phase metadata / generated schedule remain
  `fba2270e4c4fed53db5625612c72b930dc821bb8c54c4ed43df5855f845bca0b` /
  `17720a6855002f12f0b90ce8598139bfa4f5d2ec0e1ed72d6579177da9a43d35`;
- trusted inherited row / H64 results remain
  `a2515e8989d873b721c59e9c58354f6b61d9754d0fb3291dd046ff9b6cc8f004` /
  `da0ca6fed7a3e45433a1d997a0d6f0116d92748731256666731a4cdaa34e3a6e`.

## Actions not taken

- no complete-mask predictor mode was compiled or run;
- no trusted-mask row was compared, partially compared, or used as model
  input;
- no operation stream was built;
- no official full evaluator was run;
- no range, scanner, provider, CUDA, hunt, submission, or external action was
  opened;
- the private D32 and future F16 were not read, generated, or opened;
- no temporary build, output, log, cache, or mask artifact was created.

The family stays frozen at the prior deterministic-unit and square-boundary
passes. A later gate must first implement and independently test exact
finite-width post-fault continuation plus source-bound phase-site emission;
only then may it make the one-shot inherited and unchanged H64 complete-mask
comparison. Until that implementation exists, the correct disposition is
`QUALIFICATION HOLD / NO HUNT`.
