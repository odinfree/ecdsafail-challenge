# Q1272 repaired-model CPU to CUDA parity predeclaration

Date: 2026-08-23

Status: `PREDECLARED / NO CUDA RESULT / FIXED8 SEALED`.

This lane prepares one ordinary offline CPU-to-CUDA regression packet from
terminal local CPU GO commit
`32943c9589097312e78692122c72566f834355ef`. It may create reviewed source,
fixed fixtures, wrappers, and a content-addressed packet. It may not contact a
GPU host or provider, access an account, accept a nonce range, scan, search,
deploy, or submit.

## Exact inherited identities

- repaired source commit: `6cdcbedcb201bad289dd1381ae60429f0691d6fd`;
- terminal evidence commit: `32943c9589097312e78692122c72566f834355ef`;
- structural circuit source:
  `73422709ed70ba9725b3cb592770bcf197df4cdb`;
- operation count / SHA-256: `12,904,643` /
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`;
- checkpoint state digest: `e9b2d20ecd1169a8`;
- repaired shared model / host / CPU driver SHA-256:
  `9eab10bd8cf1c3510f4dcada4f08f8eb93d2efb749cc8496a88b7f68401bb90b`,
  `aa546788a823268cf311d88f028b80dd12826162fe220848ae46ec165b6190a2`,
  `71031a56d921056d41c845b4d933d5fcd020c563a98ec1d7f8407ab57c3962e1`;
- phase metadata / generated schedule SHA-256:
  `61e28111ff655bed39d5bc7dd8ccf0912274c112a34dfcc11ec01369725010b6`,
  `2135746c16dc4deb4e608cd2e7e1d9907fe167d76854ba2420279f6164efca82`;
- terminal CPU results / receipt SHA-256:
  `90ba8719ba2e082e6646726ac6a15a8ab19659d33de055d0ab5cd2faaa241fb9`,
  `21d5a7507335069b4b8c0999fe26356d9e449327b4f347390a2a341975248b14`.

The CUDA unit must compile the exact repaired `pp_model.h` as device code.
No stale scanner, hunt kernel, alternate arithmetic port, or fixture-specific
semantic branch may be imported.

## Frozen FIXED8 corpus

`FIXED8.nonces` SHA-256 is
`6830df61133fdd99ade11e4c2aa3b450f14dfe9331a7b64ae61817346e0a960c`.
The list is canonical, strictly increasing, unique, below 2^48, and contains
only fixtures already sealed by the 257-row CPU GO:

| nonce | source corpus | classical | raw phase | clean phase | sealed row manifest SHA-256 |
| ---: | --- | ---: | ---: | ---: | --- |
| 3306946714859 | V64 | 23 | 12 | 2 | `ece40af7879815732b5921db6091f78be1aacfd2b9abdec1e47ef2ae06c878ab` |
| 37754156253796 | F32 | 23 | 16 | 0 | `c317ec45b197f19228f1d89dc6215102764a6e9eda1f511e1f50f2617a0720d1` |
| 51170368051453 | V64 | 11 | 18 | 14 | `271b9b5bad81dc5e792909841f7cdb5053a2b559985d0b42b800044b05cd72df` |
| 65700024945645 | inherited | 23 | 8 | 1 | `ccf6e7a10c9b5f2b09d518f686fa25379f583d403e0c5c8e35c2efb8477c02a9` |
| 147428349223424 | R64 | 15 | 6 | 1 | `641c179728b86ded487dbda7ba838051f919a763ca41e07062f949f9a725f2a6` |
| 154123680082395 | D32 | 15 | 14 | 4 | `4879b59f065a25de2eb1dc86b2ddbfca41fa115999414b09618da30daef8947b` |
| 202374768790705 | F32 | 18 | 11 | 5 | `91f623e98dac6678003c332a6af6170bcc1638b33ff3b0e468e76dfae2909b2c` |
| 279811539530441 | R64 | 22 | 15 | 5 | `7b111a429095bc4b8f2bdb49cbdeffe055638dd239edf4d42eb08c89350bfffb` |

The packet builder must copy each sealed row's complete classical and
conditional-phase transcript from the terminal output tree, verify its row
manifest first, and content-address the resulting expected transcripts.

## Predeclared implementation boundary

The CUDA executable will expose one operation only: evaluate the eight
compile-time FIXED8 nonces. It accepts no nonce, start, count, range, file, or
submission argument. For each fixture it derives exactly 9,024 shots on the
host from the bound operation checkpoint, runs the exact repaired model on one
visible CUDA device, and emits canonical complete classical and conditional
phase transcripts.

The host may aggregate phase predicates using the same source-bound schedule;
all per-shot classical and predicate values must come from device execution.
The device width schedule, phase-family schedule, operation hash, operation
count, checkpoint digest, model hash, and fixture list are immutable packet
inputs.

The one-host wrapper must:

1. verify the complete packet manifest before compiling or executing;
2. require exactly one visible CUDA device and refuse comma-separated or
   empty device selections;
3. compile the bound CPU reference and fixed-only CUDA unit;
4. run both once over FIXED8, compare their canonical classical and clean
   phase transcripts byte-for-byte, and compare both against the sealed CPU
   transcripts;
5. run the fixed negative matrix; and
6. emit a terminal receipt only after the GPU is idle again.

The wrapper and CUDA executable must have no range or submission mode. They
must reject all positional arguments, missing or drifted packet files, wrong
operation hashes or counts, wrong checkpoint state, malformed/changed fixture
lists, unexpected output rows, CUDA schedule underfill or family mismatch,
multiple visible devices, and any CPU/CUDA/expected byte difference.

## Local completion and future execution boundary

This lane may finish `PACKET_READY / HOLD_CUDA_EXECUTION` after independent
local manifest verification, tamper rejection, source review, and confirmation
that no tracked or packaged executable exposes scanning or submission.

Actual CUDA compilation and execution are deliberately out of scope here.
Future CUDA PASS requires exact FIXED8 classical and clean-phase masks, Q1272,
9,024 shots per fixture, and all negatives. Even a PASS would authorize no
range, hunt, provider, deployment, submission, or promotion.
