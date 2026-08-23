# Exact prefilter for the frozen Q1276 stream

This is the g1000 CPU/CUDA classical-fault model rebound to the exact circuit
at commit `0b6ac181c46bd24ad6a5f8cd3d36b69bc040d73f`.

The circuit identity is fixed:

- 12,929,346 operations;
- `ops.bin` SHA-256
  `d1461959eac52b19b644f1f97a3b44a3ea249a109f14a406d19e872cd17c5422`;
- divide/multiply depths 698/696;
- R1/R2 356/625;
- g1000 width schedule;
- replay peak 1276 and square ladder 246.

The operation-count guard rejects every other stream. A run receipt must also
assert the state digest printed by `ppgpu`; the count alone is not a sufficient
stream identity.

`ppcpu counts NONCE...` evaluates complete 9,024-shot classical counts.
`ppgpu --breakdown NONCE` evaluates one complete nonce on CUDA. Scans default
to `--max-faults 0`; `--max-faults N` retains exact counts from zero through
`N` and early-exits only after the threshold is exceeded.

No output from this model is a valid circuit result. Every retained nonce must
still pass the unchanged full evaluator with classical, phase, and ancilla all
zero across 9,024 shots.

`stage_dedicated.sh` is the fail-closed path for a fresh dedicated GPU host. It
requires an idle GPU before and after CPU/CUDA parity and writes
`DEDICATED.complete`. `calibrate.sh` accepts exactly one host proof:
`BORROW.complete` xor `DEDICATED.complete`.

`build.sh` defaults to CUDA architecture 89. A Blackwell host must set
`PPGPU_CUDA_ARCH=120`; any other explicit architecture is rejected.
