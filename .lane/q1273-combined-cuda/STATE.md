# Q1273 combined CUDA handoff state

- branch: `research/q1273-combined-cuda-handoff`
- frozen base: `7b339f5d1fce6af6f3b3f360cb856b95326bb5ff`
- decision: `COMBINED_CPU_INTEGRATED / READY_LOCAL_PARITY / HOLD_CUDA / HOLD_RANGE`
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
- next gate: local source binding, CPU build/KAT/negative checks, then seal an
  immutable Linux/CUDA parity packet before requesting host activation
