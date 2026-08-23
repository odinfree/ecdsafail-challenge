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
- oracle design: current-core output-only two-pass complete-mask executable;
- deterministic build: two fresh release/locked/offline targets matched at
  `de84cf86...9acfd`;
- inherited masks: exact 141-word classical/raw/clean/ancilla row
  `a2515e89...8f004`, totals `23/15/4/0`, repeat byte-identical;
- H64 masks: `64/64` complete rows, results `da0ca6fe...e3a6e`, manifest
  `07e4a192...ba20a`, aggregate classical/raw/clean/ancilla
  `1177/871/286/0`;
- model family: `q1270_native_recurrence_v1`, empty implementation,
  predeclared at `4aaf5b8`;
- native derivation: phase/checkpoint byte-exact; 700/700 width rows and both
  696-round active schedules matched frozen source; widths
  `07e910b9...6f235`, active schedules `c49b95b0...a8bf5`, input seal
  `c226f964...003a8`;
- model status: no donor source, binary, table, checkpoint, or output imported;
- decision: `NATIVE DERIVATION PASS / EMPTY-FILE MODEL IMPLEMENTATION NEXT / NO HUNT`.

Next action: implement the recurrence from empty target files, build it twice,
and require complete inherited-mask equality. D32 remains unopened; F16 is
frozen only after inherited+H64 model equality.
