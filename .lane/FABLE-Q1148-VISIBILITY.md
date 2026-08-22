# Teddy Pender Q1148 visibility audit — Fable architecture lane

Updated: 2026-08-22T14:28:16Z

## Scope and source binding

Teddy Pender's Burn the House Down method set the question: protect the live leader, preserve the exact sparse-square component, and overturn the next load-bearing assumption instead of tuning a known saddle.

The read-only Fable lane audited the re-descent ancestor and the durable `7ca0559` tape/square evidence. Its live-score arithmetic has been rebased here to protected commit `36f6ca0`, Q1278/T919793, score1175495454. The ancestor uses a longer replay schedule than `36f6ca0`, so tape counts and raw replay widths below are architecture evidence, not a current-source measurement. Any implementation starts with a fresh live-source peak ledger.

## Verdict

- **HOLD** Teddy's exact sparse square. It lowers the standalone square from Q1278 to Q1148 and passes deterministic classical/phase/ancilla `0/0/0`.
- **KILL** Q1148 through any decoder that materializes the predecessor walk. The only concrete decoder family reintroduces about262 live walk qubits and raises the replay peak to roughly Q1290 on the measured ancestor.
- **HOLD as a reopen gate only** a reachable-set rank decoder that reconstructs signs without materializing the walk state. No target-field operator exists.
- **Next overturn:** change the cleanup contract so the reverse walk is unnecessary. If no reverse walk consumes the signs, the tape disappears instead of being encoded under another name.
- **PROMOTE nothing.** No composed source clears the live gate and trusted full9024 contract.

## Why tape removal is necessary

On the audited ancestor, replay keeps roughly703 sign decisions plus two required 256-bit data registers live. The two data registers carry the result and cannot simply be removed:

```text
~703 tape + 256 caller-y + 256 coefficient = ~1215 > Q1148
```

Current `36f6ca0` uses shorter divide/multiply schedules, but replay still owns the measured global Q1278 peak. A live-source peak trace must replace the ancestral count before construction; the qualitative necessity remains measured.

The tape exists because the walk is locally two-to-one. Both predecessor branches can map to the same post-state, so a reverse walk needs a sign per round unless a global invariant changes the cleanup contract.

## Measured component ledger from the audited ancestor

| phase | measured Q | status |
|---|---:|---|
| sparse product square | 1148 | exact component, `0/0/0` |
| value walk | 1057 | already below1148 |
| chunked replay | 1278 | global co-binder |
| full-ladder replay with raw tape | 1471 | T-efficient reference |
| ideal free tape deletion | 772 | information/economic lower bound only |
| add 256-bit source code | 1028 | code-only floor before decoder state |
| add known materializing decoder | about1290 | regression; KILL |

The code-only floor is not a construction. It excludes decoder workspace and decoder Toffoli.

## Current live economics

Fresh protected score:1175495454.

| target Q | strict T ceiling |
|---:|---:|
| 1278 | 919792 |
| 1148 | 1023950 |
| 1028 | 1143478 |
| 822 | 1430043 |
| 819 | 1435281 |

Using the ancestral full-ladder base T894782 and about985 T for the sparse-square composition, a Q1148 decoder has at most128183 added T and120 resident qubits beyond the Q1028 code-only floor. The plot-256 base T943810 leaves79155 added T and the same120-qubit resident budget. The known materializing decoder needs about262 resident qubits, more than twice the allowance.

These budgets are conservative architecture gates. They must be recomputed from an exact `36f6ca0` port before a candidate claim.

## Route ledger

### O1 — cleanup-contract overturn

Remove the need for `value_walk_back` through terminal canonicalization or a global sign-clearing invariant. This removes the tape rather than reconstructing it.

Cheapest falsifier:

1. On exact `36f6ca0`, list every consumer of the sign tape after coefficient replay.
2. Prove or refute that the final public result plus live coefficient state selects a unique terminal representative.
3. Build only a reduced-round exact map first.

`PASS` only if the reverse walk and tape can both be uncomputed without a new per-round carrier and with no phase or ancilla residue. `KILL` the proposed invariant on the first reachable collision with identical decoder-visible terminal state and different required cleanup action.

### O2 — reachable-set rank decoder

Represent each predecessor by the rank of its sign branch inside the globally reachable set. This is the only decoder shape that could avoid materializing the walk registers.

Reopen only with a target-field membership/rank operator whose resident scratch is at most120 qubits beyond the 256-bit code and whose added T is at most128183 at Q1148. A toy-field bijection is not enough.

### O3 — Bennett or streaming reconstruction

`KILL` under current semantics. The measured decoder holds about259 walk qubits plus external state, exceeding the resident budget; full recomputation adds roughly395k T on the audited ancestor.

Reopen only if signs are regenerated without resident predecessor registers.

### O4 — local prefix codec

`KILL` for Q1148. The measured law is `Q_pingpong(k)=1534-k`; even full coverage of the available first-traversal decisions bottoms nearQ1178, before the independent synthesis gap after decision8.

Reopen only with a global codec that removes more than256 raw decisions using less live state than it removes. A new tag per round is the tape renamed.

### O5 — coefficient absorption

`KILL` under current replay and cleanup semantics. The carry-aware census gives maximum sign fibers8 at k4 and128 at k8; hidden modular corrections depend on discarded high representatives.

Reopen only if changed replay semantics make the reverse-live coefficient state injective without another carrier.

## Next action

Port only O1's cheapest collision falsifier to exact live commit `36f6ca0`. Do not build a target-field rank decoder, launch a nonce hunt, or tune the killed materializing codecs first. Teddy's sparse square remains protected and ready to compose if replay falls to Q1148 or below.

## Credit

This direction exists because Teddy Pender explicitly told the campaign to attack or replace the tape and warned that low-Q components would not compose without another architectural change. The audit confirms that diagnosis: the missing piece is not another local tape gadget but a different cleanup contract.
