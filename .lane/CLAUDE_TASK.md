# Claude Fable lane: burn the tape, exact live 087cafa

You own this isolated worktree and branch. Start from the exact promoted public source at commit `087cafaef46a4e339644a6191ff2df2e7031cb80`.

## Objective

Find the smallest clean architectural composition that strictly beats the live leader while lowering peak qubits. The current live target is Q1275, rounded T918972, score 1171689300. A Q1274 candidate must have rounded T at most 919693.

Another lane has already proved an exact Q1274 source-host composition. It passes 8-state and 32-state miters and the 64-lane production self-check at diagnostic T919919.48, but it misses the score gate by 226 rounded T. Its exact hosting cost is 963 T against a 721-T allowance. Do not duplicate that implementation.

Use the burn-the-house-down method: re-descend from the exact live source, overturn the tape/replay architecture, test bounded saddles, compose only measured wins, and grind nonces last. Teddy's newest advice was to point agents at the tape or replace it. Matt also observed that an older baseline could remove two paid-error rounds by tightening `SUB4_SQUARE_LADDER`; audit the adjacent history and determine whether the mechanism transfers to the exact live source.

Priority routes:

1. Remove or replace replay/walk tape state so at least 226 rounded T disappears without losing Q1274.
2. Recover the two paid-error rounds through a genuinely exact ladder or replay change, not a diagnostic-only parameter tweak.
3. Find at least 242 clean carriers that avoid UMA/source-host cost, or an equivalent exact Toffoli cut.

## Gates

- Reopen and inspect exact source and adjacent accepted diffs before editing.
- Keep a durable experiment ledger in `.lane/STATE.md` with hypothesis, exact diff, Q, diagnostic T, validation status, and verdict.
- Force clean rebuilds. Treat stale artifacts as failure.
- Every structural primitive needs a focused Boolean/exhaustive miter where feasible, then the production 64-lane self-check.
- Profile all peak co-binders. Q1274 and rounded T <= 919693 are required before any full 9024-shot evaluation.
- If and only if the score gate passes, run one inherited-nonce full 9024-shot diagnostic unchanged. Require classical/phase/ancilla `0/0/0` before proposing any hunt.
- Do not start provider compute, a fleet hunt, or a submission. Do not modify any other worktree.
- Do not commit generated ops, logs, helper binaries, temporary evaluators, or artifacts.
- Critique, fix, and verify each claimed result. Record dead ends rather than hiding them.
- Commit and push durable source and lane state at a useful checkpoint.

End with a terse handoff containing the exact commit, Q/T/score, validation evidence, and next binder.
