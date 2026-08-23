# Claude Fable lane: Q1272 density overturn

You own only this isolated worktree and branch. Start from the exact audited
Q1272 source at commit `091abce0c0ac73f5e1965034fa976fa14c855594`.
The frozen artifact is 12,901,167 loaded operations, SHA-256
`ecc3d9f0bb1dd4e68e6d337e39c4cdb66cfbfe83928a81fec28e22797fca4cfd`,
Q1272, diagnostic T914748.17, and inherited full result 17/16/0 with exact
average T914792.720. Live is Q1275/T918972/score 1171689300. At Q1272 a clean
rounded T must be <=921139, leaving roughly 6.3k T of density-repair room.

## Objective

Minimize expected time to a clean Q1272 nonce while retaining a strict score
beat. Re-descend on this exact 696/696 stream; do not assume the Q1274 density
frontier transfers. First price the transfer exactly, then attack the hard
terminal/replay/tape channels if schedule widening saturates.

Use the completed Q1274 repair lane only as evidence and tooling:
`/Users/olifreuler/Documents/Codex/2026-08-21/par/work/fable-rescale-repair-82a742b`
at source commit `fe0b7ba` and evidence commit `d793aa2`. Its 100-index repair
measured about -0.95 held-out classical lambda for +519 diagnostic T, but it
uses the 698-round map `floor(r*703/697)`. This lane uses the distinct
696-round map `floor(r*703/695)` and must refit on its own stream.

## Routes

1. Reproduce the Q1272 artifact byte-for-byte before editing. Port only the
   byte-neutral schedule dump/override and deficit-census tooling from the
   Q1274 lane. Never import generated artifacts or logs.
2. Predeclare training and held-out nonce corpora before observation. Measure
   the Q1272 fault decomposition and evaluate direct Q1274 r100/r200 transfer
   as controls, then refit sparse +1 and bounded +2 repairs on Q1272.
3. Price the measured Pareto frontier in diagnostic T, Q, held-out classical
   fault density, and remaining strict-beat margin. Prefer the best expected
   search-economics knee, not the lowest T in isolation.
4. If width repair saturates, isolate schedule-independent terminal, replay,
   walkback, and tape channels. Test the smallest bounded architectural
   overturn with focused exact miters. Do not claim a tape cut from a parameter
   change alone.
5. Audit Matt's old-baseline `SUB4_SQUARE_LADDER` clue only against current
   binders. The present Q1272 cut is replay ladder 130->128 plus square ladder
   244->242; another cut needs measured co-binder and exact-test evidence.

## Gates

- Keep `.lane/STATE.md` append-only from this checkpoint with hypotheses,
  exact diffs/configs, corpus commitments, Q/T/density measurements, tests,
  verdicts, and next binder.
- Force clean rebuilds. Stale artifacts invalidate results.
- Use held-out data and report uncertainty. A single inherited draw is not a
  density estimate.
- Every frozen candidate must keep all peak co-binders at Q1272, pass focused
  square and affine selftests, production 64-lane selfcheck, and `git diff
  --check`.
- One inherited 9,024-shot full diagnostic is allowed only after the Q/T and
  structural gates pass. A dirty inherited draw does not kill a density repair.
- Do not run a nonce scan, provider compute, fleet mutation, submission, or
  public communication. Do not modify any other worktree.
- Do not commit `ops.bin`, `results.tsv`, score files, logs, helper binaries,
  temporary evaluators, generated tables, or other artifacts.
- Critique, fix, and verify every claimed result. Commit and push durable
  source/state checkpoints when useful.

End with exact commits, Q/T/estimated strict-beat score, held-out density
change, validation evidence, and the next binder.
