# Claude Fable lane: repair the Q1274 rescaled schedule

You own only this isolated worktree and branch. The exact starting checkpoint is
`82a742b19fb28d641e3993c3ef18abd0191544ee` (source change `94616482...`). It is
already a measured Q1274 candidate: 64-lane diagnostic T915905.50, artifact
SHA-256 `60b6fe451b0cea31c2deffee907c74a1327e175f1adbe9dd41d6e9d76e6ea933`,
12,913,879 loaded ops, production self-check clean, inherited full result
18/10/0. The live leader remains Q1275/T918972/score 1171689300.

## Objective

Keep Q1274 and the large score win, but reduce the compressed width schedule's
classical-fault density before the nonce hunt. The prior `940e34a` rescale lane
estimated roughly +3.2 classical lambda from a handful of overly narrow rounds.
Find the smallest targeted repair: preferably add one bit only to the roughly six
narrowest/highest-exposure rescaled rounds, not a uniform schedule widening.

Use burn-the-house-down doctrine: inspect the actual old lane and exact source,
test bounded schedule saddles, compose only measured wins, and leave grinding to
the separately qualified prefilter lane.

## Routes, in order

1. Recover the exact `SUB4_PP_WSCHED_FILE` or equivalent per-round tooling from
   `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/fable-width-rescale-940e34a`.
   Import only durable source changes, never artifacts or logs.
2. Identify which rescaled rounds actually create width violations and test
   sparse +1-bit repair sets. Minimize added Toffoli and preserve every Q1274
   co-binder.
3. Measure several bounded repair sets with clean rebuilds. Freeze the best one
   only if diagnostic T remains comfortably below the Q1274 ceiling 919693 and
   production self-check/selftest stay clean.
4. Secondary clue only after route 1-3: Matt noted that an eight-commit-old
   baseline could make two rounds/qubits free by tightening
   `SUB4_SQUARE_LADDER`. Determine whether the current 245->244 cut already
   exhausts that transfer. Do not claim another cut without binder evidence and
   exact tests.

## Evidence and gates

- Keep `.lane/STATE.md` append-only from this checkpoint: hypothesis, exact
  configuration/diff, Q, diagnostic T, fault-density evidence, validation, and
  verdict for every tested set.
- Force clean rebuilds; stale artifacts invalidate a result.
- Reproduce the starting candidate before editing.
- Run focused schedule/width checks, all available point-add selftests, the
  production 64-lane self-check, and profile every peak co-binder.
- Do not run a nonce scan, provider compute, fleet action, or submission.
- A single inherited-nonce full 9024 diagnostic is allowed only after Q/T and
  structural gates pass. A dirty inherited draw does not kill a density repair.
- Do not modify any other worktree. Do not commit `results.tsv`, generated ops,
  logs, helper binaries, temporary evaluators, or generated artifacts.
- Critique, fix, and verify each claimed result. Record dead ends.
- Commit and push useful durable source/state checkpoints.

End with the exact commit, Q/T/estimated score, measured density change, tests,
and the next binder.
