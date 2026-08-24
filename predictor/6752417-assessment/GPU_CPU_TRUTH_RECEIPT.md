# Q1266 GPU qualification CPU-truth reveal

Decision: `CPU_TRUTH_REVEALED_AFTER_FREEZE`

The GPU contract and six blind nonces were frozen at commit
`7ef751ce8cb47dbbe0bee67c8e1f364107f49786`. The unchanged qualified CPU
binary then emitted complete shot-index/fault-mask truth for calibration and
all blind fixtures. `gpu-cpu-fault-truth.tsv` records 121 exact lines: 15 on
calibration and 18, 16, 21, 15, 20, and 16 on blind-0 through blind-5.

`gpu-cpu-probe-truth.tsv` separately records the first 128 squeezed bytes and
all six Jacobian fields for calibration and blind-0. Every remote CUDA
configuration must match these machine-readable files exactly.

- fault truth SHA-256: `5f61199791475bd7d2ee88a4b6f13c09b18f96e68bf5e576e5a3443c19b7d8a5`
- probe truth SHA-256: `cb718f024626b3b97925eb7d5411de90ea6cdeed0ac65b15041c17d112f3fb81`
- local truth selfcheck: `PASS`, 7 fault fixtures and 4 probe groups

The CPU loader reported 12,596,439 operations for every fault fixture. No CUDA,
model, host, build, or fixture-source file changed between the pre-reveal freeze
and this reveal. A GPU disagreement is the contract falsifier; it does not
authorize model tuning.
