# Q1270 routed combined predictor state

- branch: `research/q1270-routed-combined-predictor`;
- circuit source: `90770b1` / tree `944593de...0c0d04`;
- full-run receipt: `953acb4`, SHA-256 `6dafe97e...589917`;
- operation stream: 12,953,636 / `ec4fadc0...eb63a`;
- inherited result: Q1270 / T916366.972 / `23/14/0`;
- inherited/H64/D32 hashes: `dabc1771...` / `87fb300f...` /
  `09941a91...`;
- D32: frozen private and unopened;
- target reproduction: 12,953,636 operations / `ec4fadc0...eb63a`, Q1270 /
  T916366.972 / `23/14/0`, PASS byte-exact;
- model status: no donor source, binary, table, checkpoint, or output imported;
- decision: `TARGET REBUILT / PHASE TRACE NEXT / NO HUNT`.

Next action: commit/push the rebuild receipt, then derive source-bound
operation checkpoint and phase geometry before constructing the trusted-mask
oracle.
