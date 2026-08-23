# Q1273 combined CUDA handoff state

- branch: `research/q1273-combined-cuda-handoff`
- frozen base: `7b339f5d1fce6af6f3b3f360cb856b95326bb5ff`
- decision: `PREDECLARED / HOLD_COMBINED_CPU / HOLD_CUDA / HOLD_RANGE`
- source identity: `093d85d / Q1273 / 12,933,805 / ee6448db...`
- checkpoint/tail state digest: `2148e09f4c4293b2`
- classical fixtures: inherited + H64 + D16 + blinded D32, `113/113`
- phase fixtures: inherited + D16, `17/17`
- allowed work: source-bound loader, scan-disabled parity binary, fixture
  packet verification, determinism, and fail-closed negatives
- forbidden work: uncommitted sibling intake, provider action, range, hunt,
  submission, API-key access, or semantics copied from Q1272/Q1274 by label
- next gate: commit and push this predeclaration, then implement the mechanical
  range-disabled parity scaffold while waiting for terminal combined CPU GO
