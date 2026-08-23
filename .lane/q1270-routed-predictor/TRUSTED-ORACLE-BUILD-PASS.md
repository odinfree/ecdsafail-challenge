# Q1270 trusted-mask oracle build receipt

Decision: `BUILD PASS / INHERITED CALIBRATION NEXT / MODEL UNOPENED`.

The oracle design at commit `24d22930cdc07994793400e34c0653bfc5090ca9`
was compiled twice from two fresh target directories with release optimization,
`--locked`, and `--offline`. Both binaries are byte-identical:

- oracle source SHA-256:
  `4059969b3cca026a637e7fc735acc8c214d23a5172344d25463dff0ecf128b60`;
- independent binary A SHA-256:
  `de84cf864bd80b7acf934259fa5435e4103d9b387167456091d85ca34ce9acfd`;
- independent binary B SHA-256:
  `de84cf864bd80b7acf934259fa5435e4103d9b387167456091d85ca34ce9acfd`;
- binary comparison: exact byte equality.
- fail-closed freeze runner SHA-256:
  `bdcc89367d9a183de036d7ef817a02e6cf7d9f8b8389308fb502be90cbdcd472`.

The committed freeze runner binds both binaries, the exact Q1270 operation
stream, checkpoint, schedule, oracle source, unchanged trusted evaluator,
current simulator/circuit/reference-curve core, structural source files, and
the selected corpus before executing. It rejects the private D32 corpus by
construction: its only accepted corpora are `inherited` and `h64`.

Each successful row is a canonical little-endian binary record containing the
full source, receipt, operation, nonce-transform, checkpoint, schedule,
evaluator, oracle-source, and oracle-binary identities; exact geometry and gate
totals; and 141 words each for classical, raw-phase, clean-phase, and ancilla
masks. Inherited calibration runs the already-two-pass oracle twice more and
requires byte-identical output, the frozen `23/14/0` validity counts, first
classical shot 373, and the exact displayed Toffoli and Clifford averages.

No donor source, model, binary, fixture, table, checkpoint, or output has been
opened or imported. No D32 value has been opened.
