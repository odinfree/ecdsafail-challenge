# Predeclaration — in-place algebraic retained-word sign transducer

Written before the feasibility bound and before any semantic source edit.
Lane: `research/fable-2c79-retained-transducer`.
Frozen parent / promoted source: `2c79d2f4ef1f6fdc6f75024ef4ae50c6506e2208`
(Q1274, rounded T916526, score 1,167,654,124, full 9,024-shot `0/0/0`).
Tree: `d50e00b6ba06975de822e7184ca930d3542e255e`.

## One family, exactly

A single reversible in-place transducer state `C` (the "retained word") that
supplies the per-round divstep sign `sigma_r` to the coefficient replay for
**every** fused round of both traversals, replacing the resident sign tape
(`value_walk` -> `Vec<QubitId>`, 698 wide on Divide, 696 on Multiply), such that
the state never expands to a separately materialized raw `(u,v)` pair at the peak
instant `pp_div_replay` (nor at the tied `pp_mul_*` peak).

### Representation
`C` is at most a 256-bit code co-resident with the 768-qubit component ABI
(denominator + coefficient + numerator). It carries the denominator information
already present in the ABI; it introduces no second denominator-sized carrier and
no resident round tape.

### Forward / inverse update
Per replay epoch `r`, an update `C_{r+1} = F_r(C_r)` and its explicit inverse
`C_r = F_r^{-1}(C_{r+1})`, both in place, from which `sigma_r` is extracted into
one reused sign qubit and cleared, with a fixed O(1) scratch. No epoch may
materialize `(u,v)` of width `value_width(r)` beside `C`.

### Target peak owner
`pp_div_replay` at Q1274 and every co-binder tied within it (to be measured, not
assumed — the multiply replay is expected co-tied by construction,
`pingpong_div.rs:13-26`). A cut that drops only the divide tape is disqualified.

## Strict score ceilings (recomputed from live 1,167,654,124)
- Q1273: rounded T <= 917245 (`floor((1,167,654,124-1)/1273)`), i.e. total < 1,167,654,124.
- Q1272: rounded T <= 917967.
Recompute from freshly reopened live state before any measurement is trusted.

## Optimistic Q/T lower bound to derive (Gate 1, static, before code)
1. Counting bound on `|C|`: sign-sequence -> denominator is injective (walk is
   reversible to a canonical O(1)-bit terminal), so any code determining all
   signs is >= 256 bits.
2. Geometry bound: any epoch that regenerates `sigma_r` from a live full-width
   walk state co-resident with the ABI has peak >= 2*max_value_width + 512 + |C|.
3. Extraction bound: whether `sigma_r` is extractable from a code of size `|C|`
   without a live walk state, cheaply enough, at every round of both traversals.
If Q or T fails the live ceiling under the most optimistic assumptions, seal a
KILL and stop. No implementation opens unless the static bound survives.

## Miters and tests (only if the bound survives)
- Focused forward/inverse reachable-state miter: `C_{r+1}=F_r(C_r)`,
  `F_r^{-1}` restores `C_r`, extracted `sigma_r` equals the production tape sign
  on the frozen reachable corpus, sign qubit and scratch cleared, phase 0,
  ancilla 0, `persistent_carrier_bits=0`, over both Divide and Multiply.
- Instrument every Q1274 peak co-binder (measured tie set).
- Production affine + square selfchecks; exact peak Q; measured T.
- Protected default byte-identical with the family disarmed.

## Stop rules
- Static Q or T floor exceeds the live ceiling under optimistic assumptions: KILL.
- `sigma_r` not extractable past a bounded round without a live walk state or a
  second denominator-sized carrier: KILL (this is the adjacent lanes' wall).
- Any epoch materializes raw `(u,v)` at the peak: family violates its own charter.
- A cut drops only one tied binder: disqualified by the N-way-tie law.

## Hard exclusions (dispatch)
No nonce hunt, provider/cloud compute, `ecdsafail` submission, public note,
external communication, API-key access, or edit outside this worktree. At most
one inherited-nonce full 9,024-shot diagnostic, and only after all cheap gates
pass; a dirty result never authorizes a hunt or submission. `ops.bin`,
`results.tsv`, `target`, caches, logs, and generated artifacts are never committed.
