# Predeclaration — retained-root bounded sign checkpoint/recompute

Written: 2026-08-23T09:22:19Z, before any implementation or production-source
edit.

## Frozen source and inherited exact evidence

- Worktree:
  `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/b523-sign-checkpoint-bound`
- Branch: `research/b523-sign-checkpoint-bound`
- Exact parent: `0e20bdd97df460121fc809d4ebeb6bab12a7a0ca`
- Parent tree: `91b2a9e2f55d9184f5a64521e714cabb04237760`
- `src/point_add/pingpong_div.rs` SHA256:
  `d6d964b1f403d7afc0b4ab4ab68dc0fe11e9ffb5e145813aac729c43569c09ba`
- `src/point_add/mod.rs` SHA256:
  `baa233216c412d526da6db3c8d7fa842773c124ddf9d7550fccc312dbc4cb8dd`
- `Cargo.lock` SHA256:
  `a898022e584c7bba293bc5c459c7a02bcd88c498e9b2013c1498ee66df5ab7e2`
- Protected absent-flag stream: 12,972,785 operations, 50,798,742 bytes,
  SHA256 `e33245d491a16192068ef7024a2c82375047c17af3c8f802c81066de0568cb0a`.
- Protected full control: Q1278, average executed T919785.268 (rounded
  T919785), full 9,024-shot classical/phase/ancilla `0/0/0`.

The two binding parent receipts are:

1. `.lane/KILL-FUSED-REACHABLE-INVERSE-B523.md`: the unchanged fused pair is
   exact on all 696 Divide and 694 Multiply production calls in P64/C64.
2. `.lane/KILL-RETAINED-SPLICE-CANONICAL-B523.md`: the retained-word splice is
   exact and clean for Divide rounds 2..7 at Q1114, but the frozen source has
   no sign source past round 7 and covers only 6/1390 fused calls.

No trajectory, inverse, retained-word prefix, or default-stream claim is
reopened here.

## Exactly one architecture

Price one **retained-root bounded sign checkpoint/recompute** architecture.
Keep the three 256-bit production words (denominator, coefficient, numerator),
one exact 256-bit retained denominator word, and both existing fused cells
unchanged. For each bounded chunk of missing production signs, reconstruct the
ordinary shipped ping-pong value walk from the retained root, copy at most `k`
signs, reversibly clear the materialized walk/checkpoint work, consume those
signs through the unchanged fused replay cells, then continue with the next
chunk. Conventional full `(u,v)` walk checkpoints may trade recomputation for
resident qubits and must be priced explicitly.

This family does **not** include a new direct ANF oracle, an arbitrary Boolean
sign synthesizer, a compressed reachable-set rank/unrank code, coefficient
absorption, a new inverse, changed cleanup semantics, a tape codec, arithmetic
window changes, or a second family. Such a representation would change the
predeclared checkpoint object rather than optimize this architecture.

All 696 Divide fused calls (rounds 2..697) and all 694 Multiply fused calls
(rounds 2..695) are required. The proven direct retained-word signs for rounds
2..7 may be granted at zero cost in the optimistic bound; the architecture
must cover every missing round 8 onward.

## Frozen qubit ledger

Use exact measured counts from the sealed splice, not an inferred cell size:

```text
three production words                 3 * 256 = 768 Q
one retained denominator word          1 * 256 = 256 Q
persistent base                                  = 1024 Q
fused-cell transient excluding sign             =   87 Q
```

The 87-Q cell transient is fixed by both sealed receipts: the candidate reaches
Q1114 with base1024 + one sign + two allocated oracle scratch + 87 cell wires,
and the independent tape-sign reference reaches Q606 from ABI518 + one working
sign + the same 87 wires.

For a `k`-sign chunk, first price:

```text
Q_cell(k) = 1024 + 87 + k = 1111 + k.
```

Then separately add every live source object:

- local sign tape and any duplicated output signs;
- ordinary walk state at the exact shipped `value_width(r)`;
- full boundary checkpoints (`u` plus `v`), including sign-extension wires;
- carry/borrow scratch and any recomputation pebble.

Give the architecture the optimistic in-place root reuse: the retained word may
serve as `v`, so materializing the ordinary walk needs only a new `u` word plus
the retained word's extension wires. No carry ladder or sign is charged in that
first source-state lower bound.

## Frozen Toffoli accounting

Use the exact static `WIDTH_SCHEDULE` in the frozen source. For every generic
round, the shipped `signed_add_wrapping_sigma` body contains exactly
`value_width(r) - 3` unconditional CCX gates in one walk direction. A
root-to-end-and-back reconstruction therefore costs at least

```text
2 * sum(value_width(r) - 3)
```

over the traversed generic rounds. This deliberately gives away round 0,
rounds 1..7, sign-copy gates, all checkpoint construction, all carry-boundary
repairs, every fused replay cell, the square, and the rest of point addition.
It is an absolute source-only lower bound, not an estimate of a complete
candidate.

If no conventional checkpoint can remain within Q1114, maximize `k` under the
cell ledger, partition the missing rounds into maximal chunks, place any short
remainder at the earliest rounds, and charge a fresh root-to-end-and-back
reconstruction for each chunk. Record the exact endpoint sets and integer sums.

For comparison, also record:

1. one ordinary forward/back pass over the same missing rounds;
2. the exact repeated-prefix excess over that pass; and
3. the Q1278 -> Q1114 exchange: rounded T headroom
   `1,049,462 - 919,785`, without assuming that the old walk remains in the
   candidate.

## Decision gate

Fresh leader: `1,169,101,620`. The strict target is:

```text
Q1114: T <= 1,049,462
1114 * 1,049,462 = 1,169,100,668  accepted
1114 * 1,049,463 = 1,169,101,782  losing
```

1. If the optimistic source-state lower bound exceeds Q1114, record that
   independently of the T result.
2. If the source-only Toffoli lower bound exceeds 1,049,462, or its repeated-
   prefix excess exceeds the entire Q-drop headroom, seal a terminal scoped
   `KILL` without implementation.
3. Only if both optimistic bounds pass may the lane write a
   `GO_IMPLEMENTATION` memo. That memo may specify only the smallest closure
   miter: one production-derived nonzero chunk spanning the first missing sign
   boundary (rounds 7..10), forward fused replay plus exact inverse cleanup,
   retained-root restoration, and value/phase/ancilla `0/0/0`. It may not edit
   production source in this turn.

## Authority and terminal hygiene

This is a no-spend analytic lane. Do not launch Claude or another paid model,
edit production source, build a candidate, alter defaults/nonces, use a
provider, hunt, submit, or publish. Commit and push only this predeclaration and
the compact terminal arithmetic/evidence memo. Exclude binaries, generated
operation streams, results rows, scores, traces, and logs. End clean.
