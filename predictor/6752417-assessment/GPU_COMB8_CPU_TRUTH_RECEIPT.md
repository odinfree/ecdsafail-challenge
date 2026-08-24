# Q1266 comb8-only GPU qualification CPU-truth reveal

Decision: `CPU_TRUTH_REVEALED_AFTER_COMB8_FREEZE`

The comb8-only source and eight new blind nonces were frozen at commit
`b0d035ae6223e7eba25789f882d6379319a2935a`. The unchanged qualified CPU
binary then emitted complete shot-index/fault-mask truth for calibration and
all eight blind fixtures.

`gpu-comb8-cpu-fault-truth.tsv` records 165 exact lines: 15 on calibration and
20, 13, 19, 22, 21, 15, 18, and 22 on blind-0 through blind-7.
`gpu-comb8-cpu-probe-truth.tsv` records the first 128 squeezed bytes and all six
Jacobian fields for calibration, blind-0, and blind-7.

- fault truth SHA-256: `de01b7d59032cbc9cc60b66443841ed3973f20777115833e37ab997b9c61d880`
- probe truth SHA-256: `1a92b34c0a8dc288872575c661f5309ca14cbe9fc988279f099bc63599b8ec1b`
- local truth selfcheck: `PASS`, 9 fault fixtures / 165 lines / 6 probe groups

Every remote thread-width configuration must match these files exactly. The
CPU loader reported 12,596,439 operations throughout. No CUDA, model, host,
build, or fixture-source file changed between freeze and reveal; any GPU
disagreement is terminal for this fresh artifact.
