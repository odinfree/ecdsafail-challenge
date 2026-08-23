# Q1272 E007 Linux/CUDA parity result

Date: 2026-08-23

## Verdict

`PASS_FIXTURE_PARITY / HOLD_OVERCOUNT_BOUND / NO_SCAN`

The exact E007 packet passed its bounded Linux CPU/CUDA qualification on one
already-running, isolated RTX 4090 (`sm_89`) environment. The run executed
diagnostic fixtures and loader negatives only. Both binaries were compiled
with `PP_DISABLE_SCAN=1`; no range, calibration interval, hunt, provider
mutation, submission, or new spend occurred.

The first build attempt stopped before any fixture at the scan-disable marker
check because `strings | grep` returned 141 under `pipefail`. Commit
`da3f02c` replaced that pipeline with direct binary inspection and resealed
the stage hashes. The failed workspace was preserved separately; its binaries
are not evidence. The clean second attempt passed every gate.

## Exact identity and binaries

- circuit source: `ea93a131e2bc488bff6fa12010d1f3606c7771b0`;
- operation count: `12,943,345`;
- operation SHA-256:
  `4618d4af86c23c06cc72fef26f8a8e5986c7a9de5f804891541a8ce6eb189f37`;
- state digest: `963a662d2e392804`;
- Linux CPU binary:
  `eebd63c9218da15253d294824b410b5d404142c9c3a18e88fabbd2bb86a1f549`;
- CUDA `sm_89` binary:
  `54d1a5c5db58648aaaae4a0edb157ce0609f410e7e399618f375452e6f6bae53`;
- CUDA toolchain: `12.4` build `34097967_0`;
- C++ toolchain: Ubuntu g++ `11.4.0`.

Committed source and ledger hashes remained exactly those frozen in
`PARITY-STAGE.md`. Runtime receipt hashes:

| receipt | SHA-256 |
|---|---|
| `FINGERPRINTS` | `3b4a350229842166f5e3fd786636090b0371ab133eeb6a4f61919e813645a585` |
| `PARITY.complete` | `7e374d713bbba3f36a89e352d6be13b07ded5d92d3875c97fa470271161d1be0` |
| `DEDICATED.complete` | `a119c94965038413bb0a672e66e84c2eaf72724661b05b050b8416a4b39b95c9` |
| complete fixture-tree receipt | `41891cff49e541d40dde6be8623ee35e07c12f5783f854d45bbd1b910b8e87f4` |
| complete negative-tree receipt | `3d2c52bf68c0bd6deec17ad3d4925b890975c7ece9a1671edf6e6bb7c23956b3` |

Runtime binaries, outputs, negative artifacts, and logs remain outside Git.

## Positive parity

For every frozen row, Linux CPU, CUDA comb8, and CUDA comb16 emitted the same
complete breakdown byte-for-byte:

| nonce | pred cls | cause counts `walkD/replayD/walkM/replayM/result` | first |
|---:|---:|---:|---:|
| 251000962439 | 11 | `8/0/3/0/0` | 2582 |
| 0 | 14 | `6/2/6/0/0` | 151 |
| 7 | 19 | `10/2/6/1/0` | 90 |
| 2500069332 | 12 | `4/0/8/0/0` | 911 |

All ten CUDA diagnostic invocations printed state digest
`963a662d2e392804`. CPU, CUDA comb8, and CUDA comb16 also reproduced the
entire inherited 11-line ordered `index mask` ledger byte-for-byte.

## Negative parity

CPU and CUDA each rejected both temporary wrong streams with exit `2` before
corpus or kernel work:

- wrong count `12,943,344`: operation-count rejection;
- correct count but wrong exact SHA: runtime state digest
  `fdc72faec6f1490d`, rejected against `963a662d2e392804`.

The main packet independently required the full operation SHA before either
binary ran, so count, compact digest, and exact artifact identity were all
enforced.

## Protected-workspace audit

Before staging and again after completion, the protected Q1276 operation
artifact, four model sources, two binaries, three qualification receipts,
drain receipt, and four stage scripts matched their frozen hashes. Its
dedicated receipt and runs directory remained absent. The existing confirmer
kept the same process identity and start marker, with zero pending work and
zero active evaluations. GPU application count was zero before and after.
No protected file or process was changed or signalled.

The preserved Q1276 immutable hashes were:

| artifact | SHA-256 |
|---|---|
| operations | `d1461959eac52b19b644f1f97a3b44a3ea249a109f14a406d19e872cd17c5422` |
| `pp_host.h` | `257236aa61cafb8ba056271b7bd80d4144fb334bd31b11ae6b86405701c1c751` |
| `pp_model.h` | `4d3d748a3350851e263f9f3f180e6405b1240514dcff7a672b773751bbcf330e` |
| `ppcpu.cpp` | `8bbfad7fa8fa3efe0fa92805cf5ec7f41732edebceaa81ff2e8a7c9f05b9e6eb` |
| `ppgpu.cu` | `8fe6247eeb680ffad96423947909afc88321913bc039233dd85e18733b6a8fb3` |
| CPU binary | `73f09fb8f5d84bdd595c730e0be34a8a8abb5d78184c8f431987708b4d2cc61b` |
| CUDA binary | `672a47004f1f0a4a3ebc0d0a3e4a41e2dd903b1e1493bf493757fefed355cf2d` |
| `FINGERPRINTS` | `b78f07dc879a9eb6c1f5ef3248ced3a373b7d31d7a92d6d98ae741ed47964310` |
| `PARITY.complete` | `92f8ac280ecd0dd2710190a01e98e1fd59198d7e9142c567ff5acfa027a78cc1` |
| `BORROW.complete` | `b63248390e7e49a2d6a33782c3f457eefb5fdcdfe03a904cd6a25aa7e31d562f` |
| drain receipt | `0bd58d73f2252d0c459cbf055b9407215ca2416bb12ab3d95a6e5c087dfafb3b` |
| `build.sh` | `179e33f76c60ce6c99da12be026f0b8ffb19b8b479c3c9956aaada94ec33145c` |
| `calibrate.sh` | `5e60eed910d4c32831ab8ac8c2854f1a26162487aff4cab4fe4f76b21c117822` |
| `stage_verify.sh` | `1a4129387023bb3fbedde39c0d018dbba4f6043844db8997d1464514fd8051ef` |
| full-confirm path | `c252ffc8899926f9ffda1a31986c2b06f94cd8a06a9b3e83a00f2b65544068aa` |

## Remaining hold

GPU fixture parity is closed. Search readiness is not. Strict `pred_cls=0`
can discard a circuit-true zero because the fold55 restoration model may
conservatively count a benign wrapped overflow. The committed parity binaries
cannot scan, the borrowed path remains unarmed, and the tolerant pilot still
requires a global source-bound overcount proof `B <= 3`, a threshold
`max_faults >= B`, and a separately reviewed scan-enabled build. Every future
retained nonce still requires unchanged full 9,024-shot evaluation.

Independent E008 H64 evidence at commit `868a1b5` now matches the CPU model on
all 64 complete classical shot sets (`1053/1053` faults); its compact set
receipt is
`528df040a14c7d2ca8855500423cef5fdeae0f7ae83188ca2eb697e2706104a5`.
That closes a bounded corpus gate, not the global overcount proof.
