# Claude Fable task — exact fast phase screen for Q1274 repair-r100

Work only in this isolated worktree and branch. Read the complete
`/Users/olifreuler/ecdsa-ops/skills/burn-the-house-down/SKILL.md`, this task,
this lane's `.lane/STATE.md`, and the complete sibling phase evidence at
`/Users/olifreuler/Documents/Codex/2026-08-21/par/work/fable-q1274-phase-redescent/.lane/STATE.md`.
Execute an implementation, not a read-only review.

## Frozen source and evidence

- source commit `fe0b7bac6348fb35b7680784d4295899e498d0e3`;
- operation SHA-256
  `4c68597468ed1dbb4f2e33042842227bf57c011c51f41e9cdaf13c73194b1f8c`;
- Q1274, diagnostic T916424.62, inherited unchanged full `22/11/0`;
- current branch HEAD `a7326a9` seals an exact 323/323 classical predictor
  ledger plus fail-closed identity guards;
- sibling commit `c08c7c4` proved 23/23 exact phase-mirror agreement and
  localized every classical-clean phase fault to truncated boundary erases at
  `pingpong_div.rs:1547`, `:1783`, and `:1898`.

The proven per-shot phase expression is the XOR, in exact Fiat-Shamir/Hmr
order, of `(true boundary carry XOR truncated comparison) & rng_bit` over the
three boundary-erase site families. The implementation must verify this
source-exactly; do not treat the prose formula as permission to skip RNG-order,
condition-stack, skip-shot, or identity checks.

## Frozen validation

Before inspecting any new oracle result, use:

1. the exact 23 nonces and deterministic dev/holdout split already frozen in
   the sibling phase state;
2. disjoint32 = `700000000000 + i*10000019` for `i=0..31`;
3. complete 9,024-shot phase-fault set equality for every nonce, never only
   counts;
4. unchanged classical 323/323 regression and both wrong-stream negatives.

## Bounded implementation family

Add one default-off/source-bound CPU phase-screen path to the sealed
`.lane/stage-packet` predictor. Preserve the existing classical output
contract byte-for-byte when phase screening is not requested. The new path may
use precomputed, source-bound schedule metadata, but must reproduce the exact
Fiat-Shamir seed and per-Hmr RNG ordering for each nonce and shot. Fail closed
on source, operation, checkpoint, schedule, or corpus mismatch.

Gate in this order:

1. rebuild/reproduce the sibling exact mirror on the frozen 23;
2. implement the CPU screen and require 23/23 complete phase-set equality;
3. reveal disjoint32 and require 32/32 complete phase-set equality;
4. rerun the existing 323/323 classical regression and negatives;
5. measure screen cost relative to the classical model. If it is not cheaper
   than unchanged full evaluation, report a terminal economic falsifier;
6. only if CPU is exact and economically useful, port the same contract to the
   vendored CUDA source and prove CPU/CUDA complete mask equality on a frozen
   local fixture set. No remote GPU is required or authorized.

No adaptive nonces, provider use, remote host, range, scan, hunt, submission,
public note, or `ecdsa-ops` mutation. Do not weaken final validity. Do not
commit ops.bin, result rows, generated binaries/logs, caches, mirror dumps, or
temporary artifacts. Apply critique -> fix -> verify. Do not commit or push;
Codex will inspect, record spend, and seal durable evidence.
