# Q1272 fixed CPU/CUDA parity packet

This lane packages the repaired Q1272 terminal CPU GO as a bounded CUDA
regression. The packet does not contain or import a scanner, range owner,
hunter, provider client, deployment helper, or submission client.

## Tracked components

- `FIXED8.nonces`: the sealed eight-fixture corpus;
- `src/ppcuda_fixed.cu`: a no-argument CUDA executable that compiles the exact
  repaired shared model and evaluates only the compile-time FIXED8 list;
- `packet/verify_packet.py`: complete manifest, identity, transcript, and
  interface verifier;
- `packet/run_one_gpu_parity.sh`: one-visible-GPU build and parity wrapper;
- `packet/selftest_failclosed.sh`: local packet tamper and interface negatives;
- `tools/build_packet.py`: offline content-addressed packet assembler.

The assembler copies the exact terminal CPU sources, operation stream, phase
schedule, and sealed expected transcripts into
`/Users/olifreuler/ecdsa-ops/q1272-cpu-cuda-parity-packet-32943c9/`.
Generated packet files remain outside Git.

## Current boundary

Local work may assemble and verify the packet and run the no-CUDA tamper
matrix. `run_one_gpu_parity.sh` is for a later explicitly authorized local or
isolated Linux CUDA execution. It accepts no arguments and requires exactly
one numeric `CUDA_VISIBLE_DEVICES` entry. Passing it proves only fixed-corpus
CPU/CUDA parity; it grants no range, hunt, provider, deployment, or submission
authority.
