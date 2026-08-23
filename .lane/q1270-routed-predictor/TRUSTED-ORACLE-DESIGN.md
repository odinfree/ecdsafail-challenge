# Q1270 trusted-mask oracle design gate

Decision: `IMPLEMENTED / UNRUN / NO MODEL IMPORTED`.

The source-bound oracle is `src/bin/q1270_trusted_masks.rs`. It is an
output-only executable over the exact frozen operation stream. It imports the
current `circuit`, `sim`, and reference-curve modules, but cannot import or call
the point-add builder or any predictor.

Its fail-closed contract is:

- use the trusted evaluator's bounded `QECCOPSZ` loader, per-operation
  validation, Fiat-Shamir transcript, secp256k1 reference addition, register
  ABI, and `Simulator`;
- require exactly 12,953,636 operations, Q1270, 961,070 classical bits, four
  256-bit registers, and a final 96-operation cancelling-X nonce image;
- change only the two equal X targets for each of the 48 nonce bits;
- execute two independent complete 9,024-shot passes from fresh Fiat-Shamir
  readers and compare every classical, raw-phase, clean-phase, and ancilla word
  plus the exact gate totals before emitting output;
- emit 141 canonical 64-bit words for each complete mask, exact shot and batch
  totals, and exact integer Toffoli and Clifford totals;
- reject malformed input, geometry drift, incomplete test sets, nonce-tail
  drift, any nondeterministic repeat, or any unexpected argument.

The next gate independently builds the oracle with `--locked --offline`, binds
the executable and current-core hashes, and requires the inherited output to
match the frozen 9,024-shot receipt. No donor source, model, binary, table,
fixture, checkpoint, or output has been imported.
