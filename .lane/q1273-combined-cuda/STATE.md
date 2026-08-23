# Q1273 combined CUDA handoff state

- branch: `research/q1273-combined-cuda-handoff`
- frozen base: `7b339f5d1fce6af6f3b3f360cb856b95326bb5ff`
- decision: `TERMINAL_SCORE_DEAD / CUDA_NOT_RUN / PROVIDER_NOT_USED / RANGE_NOT_DECLARED`
- source identity: `093d85d / Q1273 / 12,933,805 / ee6448db...`
- checkpoint/tail state digest: `2148e09f4c4293b2`
- classical fixtures: inherited + H64 + D16 + blinded D32, `113/113`
- phase fixtures: inherited + D16, `17/17`
- allowed work: source-bound loader, scan-disabled parity binary, fixture
  packet verification, determinism, and fail-closed negatives
- forbidden work: uncommitted sibling intake, provider action, range, hunt,
  submission, API-key access, or semantics copied from Q1272/Q1274 by label
- combined CPU GO: `3c1a49cdde48f804c4e35bd0501d7d8d7f46f15e`, tree
  `70ab3c0196b85abd74835399094642aeb828b323`
- combined source hashes: host `bc2df218...`, model `14fc9230...`, CPU
  `1d93d468...`
- local handoff seal: commit `80ba329`; CUDA source SHA-256
  `7233b102f16df943f96b4900941ec845f946f3d3159e1bd6eece6b4c8f1b8900`
- stop reason: promoted source `4eb93cb` is Q1273/T914243 with score
  `1,163,831,339`; this Q1273 family can no longer strictly beat the board
- terminal boundary: preserve the scan-disabled scaffold; do not compile on a
  provider, declare a range, hunt, or resume this port without a new score case
