# Q1272 combined unit-parity state

- status: `TERMINAL_KILL / CONDITIONAL_PHASE_MISMATCH / HOLD`;
- base: `f308df4f1ab054b204dec050bc8b9f452e7c49ee`;
- phase donor: `83ad631e1a99db3db1c3886b4d61ff9ded94b0f5`;
- checker: `d4cfb6b`;
- fresh corpus: `F32.nonces`, SHA-256
  `8d93cbf5e871f1ec8cab5768835c5c60a78a94fbc71611a96248a4248dc450ec`;
- complete classical equality: `193/193` rows;
- complete conditional-phase equality: `192/193` rows;
- failing fixture: D32 nonce `154123680082395`, evaluator-only clean-phase
  shot `8833`;
- post-corpus negative and deterministic-repeat gates: not reached after the
  fail-closed mismatch;
- terminal evidence: `TERMINAL_KILL.md`;
- next action: none in this lane.  No repair, rerun, CUDA, range, search,
  provider, network, or submission authority.
