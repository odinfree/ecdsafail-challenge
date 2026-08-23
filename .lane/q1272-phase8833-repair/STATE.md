# Q1272 omitted phase-cleanup repair state

- status: `TERMINAL_GO / LOCAL_CPU_REGRESSION_PASS`;
- base HOLD: `12c4a723ae5a06e056f152b8bca33abe848f265d`;
- mismatch: D32 nonce `154123680082395`, evaluator-only clean-phase shot
  `8833`;
- cause: the phase extractor omits both source-bound
  `trailmix_ludicrous/arith.rs:1471` R/Hmr sites;
- exact phase locations: `tlm_coord_add3x` and `tlm_coord_rsub_final`;
- repair commit: `6cdcbedcb201bad289dd1381ae60429f0691d6fd`;
- applied edit: exactly the two predicates frozen in `PREDECL.md`, with
  classical arithmetic unchanged;
- fresh holdout: `R64.nonces`, SHA-256
  `c0253a53113952659308bdc32c0245160b30093fc3ef4e7925cfbd02332a186b`;
- complete equality: `257/257` classical masks and `257/257` conditional-phase
  masks, covering 2,319,168 shots with Q1272 and ancilla zero;
- guard matrix: 11/11 rejected fail-closed;
- deterministic repeats: inherited, F32, repaired D32, and fresh R64 exact;
- results SHA-256:
  `90ba8719ba2e082e6646726ac6a15a8ab19659d33de055d0ab5cd2faaa241fb9`;
- terminal evidence: `TERMINAL_PASS.md`;
- next action: none in this offline lane. No CUDA, range, search, provider,
  network, account, deployment, or submission authority is inferred.
