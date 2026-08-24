# Interleaved odd-passenger loan plan

Status: `ACTIVE / STRUCTURAL / DEFAULT_OFF / SUBMIT_CLOSED`

## Invariant

Ping-pong's binary-GCD walk keeps both `u` and `v` odd. The low wires
`u[0]` and `v[0]` are therefore source-proven one at every replay checkpoint.
Replay reads only the sign tape and the two 256-bit coefficient registers; it
does not read the walk registers. The two low walk wires can be toggled to
zero, returned to the allocator for the replay cell, then reacquired and
toggled back to one before the next walk or walk-back round.

The terminal batch already implements the same passenger-loan principle over
the entire terminal walk state. This experiment extends it to the nonterminal
batch and interleaved cells that bind Q1267.

## Bound and gate

- exact parent source/tree: `67524171baaf568dc3dc606f38515745f70804ff` / `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`
- activation: strict `SUB4_PP_INTERLEAVED_ODD_LOAN=1`
- scope: only the divide batch/interleaved replay calls and multiply
  interleaved/lower-batch replay calls
- price: four X gates per loan interval; X is classically tracked and costs no
  evaluated Clifford or T
- no reset/HMR is added, so evaluator randomness consumption is unchanged
- allocator `reacquire` must prove both exact wire IDs are free after every
  replay cell

## Admission

1. Default-off build is byte-identical to official ops SHA-256
   `87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e`.
2. The full fixed-64 point-add profile is value/phase/ancilla `0/0/0`.
3. Both current replay owner phases fall below Q1267, and no other phase
   remains at Q1267.
4. Exact T is non-increasing; candidate score strictly beats the fresh live
   frontier under its actual Q.

First falsifier: either low bit is not restored, a replay cell retains one of
the borrowed IDs, or an independent owner keeps global Q at 1267. No trusted
9,024-shot, provider, nonce, or submission action occurs before these gates.
