# Exact constant-state structural-cut plan

Status: `ACTIVE / LOCAL / SUBMIT_CLOSED`

## Binding

- source commit/tree: `67524171baaf568dc3dc606f38515745f70804ff` / `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`
- baseline ops: `12,593,858`, SHA-256 `87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e`
- live frontier at phase entry: Q1267, rounded T911390, score `1,154,731,130`
- provider, nonce-grind, push, and submission gates: closed

## Claim under test

A fail-closed three-valued interpretation of the exact emitted program can
prove nonlinear gates to be identities from source semantics alone. Only the
four declared input registers begin unknown; every other qubit and bit begins
zero. The interpretation follows conditions, reset/HMR demolition, swaps, and
classical stores, and becomes unknown whenever the abstraction cannot prove a
state.

The frozen q775 witness is the RED fixture: after unconditional `R q775`, the
scanner must prove the later `CCX(q513,q775 -> q776)` dead. Any additional hit
must carry its exact operation index and tracked source site. HMR/R operations
are never proposed for deletion because they consume evaluator randomness.

## Phase gates

1. Unit-test the lattice and conditional transfer rules, including fail-closed
   behavior across unknown conditions and HMR.
2. Reproduce q775 on the exact promoted stream with no finite-shot evidence.
3. Group CCX/CCZ identities by source site and context; retain only a repeated
   family or another independently provable site.
4. Materialize at most one source-located deletion family behind a strict
   default-off gate. Require default byte identity and deletion-only stream
   proof before any evaluator run.
5. Run reduced-width/source selfchecks, then a 64-lane fixed profile. Admit a
   trusted 9,024-shot run only if the candidate is correct and has strict-live
   economics.

## Falsifiers

- The scanner does not reproduce q775.
- Every nonlinear hit except q775 disappears under conservative input,
  condition, HMR, and alias handling.
- A repeated hit cannot be mapped to one source callsite or cannot be removed
  without also changing non-target operations.
- Conservative score economics cannot strictly beat the refreshed frontier.

Elapsed time, missing novelty, and finite clean samples are not proofs.
