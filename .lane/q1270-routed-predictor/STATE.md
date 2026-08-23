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
- phase geometry: 4,658 sites / 1,947,720 R/Hmr; metadata
  `fba2270e...bca0b`; schedule `17720a68...43d35`;
- Fiat-Shamir checkpoint: 5,064 bytes / `75deeae0...b937f`, 4,096-byte
  trusted-XOF selfcheck PASS;
- model status: no donor source, binary, table, checkpoint, or output imported;
- decision: `PHASE GEOMETRY SEALED / TRUSTED MASKS NEXT / NO HUNT`.

Next action: commit/push phase geometry, then build the current-core two-pass
trusted oracle and seal inherited plus H64 complete masks before any donor
model import.
