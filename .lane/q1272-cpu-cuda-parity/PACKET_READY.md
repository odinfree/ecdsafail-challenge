# Q1272 repaired-model fixed CPU/CUDA parity packet

Date: 2026-08-23

Verdict: `PACKET_READY / OFFLINE_VERIFIED / HOLD_CUDA_EXECUTION`.

The bounded packet from terminal CPU GO `32943c9` is assembled,
content-addressed, independently re-extracted, and locally verified. No CUDA
compiler or GPU is present on this host, so the CUDA source remains uncompiled
and unexecuted. No provider, account, instance, network, range, search,
deployment, or submission action occurred.

## Packet receipt

```text
packet directory
/Users/olifreuler/ecdsa-ops/q1272-cpu-cuda-parity-packet-32943c9

archive
/Users/olifreuler/ecdsa-ops/q1272-cpu-cuda-parity-packet-32943c9.tar.gz

implementation commit
1390a1464dd0a05d6d8b89edfc43df14bb7c9620

packet files including MANIFEST.sha256
14

archive bytes
49,682,830

archive SHA-256
0d984dec387940836e45145cc2960a36edbc4cdbc813b91acaf71ca1d3f04705

MANIFEST.sha256 SHA-256
5a016d0591024c71f20d5480084c0df1454bb8fb3bd4a947d5877e05565f9904

PACKET.meta SHA-256
097ba603415259bd4e1a8fa9bf08b6d5f63efa32669baa6c3fe81213e45a5c13
```

The packet directory is owner-only and write-protected. A clean archive
extraction independently emitted:

```text
Q1272_FIXED8_PACKET_OK fixtures=8 shots=72192 classical_rows=150 clean_phase_rows=32 cuda_execution=not-performed
```

## Bound implementation

The CUDA source SHA-256 is
`23791a4aa69d3f88303bf64f8437a001f7f736721452490bc26b700ce908b072`.
It imports the exact repaired shared model rather than an earlier scanner or
parallel arithmetic implementation. The packet binds:

- circuit source `73422709ed70ba9725b3cb592770bcf197df4cdb`;
- 12,904,643 operations, SHA-256
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`;
- checkpoint state digest `e9b2d20ecd1169a8`;
- repaired model SHA-256
  `9eab10bd8cf1c3510f4dcada4f08f8eb93d2efb749cc8496a88b7f68401bb90b`;
- phase metadata SHA-256
  `61e28111ff655bed39d5bc7dd8ccf0912274c112a34dfcc11ec01369725010b6`;
- phase schedule SHA-256
  `2135746c16dc4deb4e608cd2e7e1d9907fe167d76854ba2420279f6164efca82`;
- FIXED8 SHA-256
  `6830df61133fdd99ade11e4c2aa3b450f14dfe9331a7b64ae61817346e0a960c`.

The device kernel produces every per-shot classical cause and source-bound
phase predicate. Host code performs only the already-qualified corpus
derivation and phase-RNG aggregation. The CUDA executable hardcodes the eight
nonces, accepts no arguments, reads only the packet's exact `ops.bin`, and
requires exactly one visible CUDA device.

## Fixed expected outputs

FIXED8 spans inherited, D32, V64, F32, and the fresh R64 holdout. It includes
the repaired D32 shot-8833 row, a zero-clean-phase row, and a 14-clean-phase
row. Across 72,192 shots, the sealed expected transcripts contain:

- 150 complete classical cause rows, SHA-256
  `b37aebb01c90a89490d2f5c545ec9f7dd6b77d9952699b7d31757f17ddf9ea91`;
- 32 complete conditional-phase rows, SHA-256
  `a33b9abd86414551e1280d250c2a2e121a5e230f8d9a4a0066280937daa906f4`.

After packet assembly, a fresh local CPU binary was rebuilt from the packaged
sources and recomputed all eight fixtures. Its two transcripts matched the
packet byte-for-byte and reproduced those same hashes. The rebuilt binary
SHA-256 is
`c49aa0b174d75d36cb1081bdfe6d35baf57a15bc9985800eaa02a4ee834af243`.

## Offline guards

Python syntax, shell syntax, Git whitespace, source hashes, and immutable
input checks passed. The local packet selftest passed four cases without CUDA:

1. changed `PACKET.meta` rejected with empty stdout;
2. wrapper positional argument rejected;
3. comma-separated multiple-device selector rejected;
4. explicitly empty device selector rejected.

The future one-GPU wrapper additionally encodes missing/truncated operation
stream, forced bad phase family, schedule underfill, CPU/CUDA mismatch,
CPU/expected mismatch, GPU/expected mismatch, multiple visible devices, and
non-idle GPU failures. Those CUDA-dependent negatives remain unexecuted.

## Execution boundary

`run_one_gpu_parity.sh` performs exactly one fixed sequence: verify packet,
compile the bound CPU and CUDA units, recompute FIXED8, compare all complete
classical and conditional-phase transcripts, execute the fixed negative
matrix, confirm the sole GPU is idle again, and emit `PARITY.complete`.

This packet readiness receipt is not CUDA parity. A future CUDA mismatch is
terminal HOLD. A future exact PASS still grants no range, hunt, provider,
deployment, submission, or promotion authority.
