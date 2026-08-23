# Q1272 omitted phase-cleanup repair state

- status: `PREDECLARED / NO REPAIR MODEL OUTPUT / R64 SEALED`;
- base HOLD: `12c4a723ae5a06e056f152b8bca33abe848f265d`;
- mismatch: D32 nonce `154123680082395`, evaluator-only clean-phase shot
  `8833`;
- cause: the phase extractor omits both source-bound
  `trailmix_ludicrous/arith.rs:1471` R/Hmr sites;
- exact phase locations: `tlm_coord_add3x` and `tlm_coord_rsub_final`;
- permitted edit: the two predicates frozen in `PREDECL.md`, with classical
  arithmetic unchanged;
- fresh holdout: `R64.nonces`, SHA-256
  `c0253a53113952659308bdc32c0245160b30093fc3ef4e7925cfbd02332a186b`;
- next gate: commit this predeclaration before model edits, then rerun all 257
  local rows and fail-closed guards.
