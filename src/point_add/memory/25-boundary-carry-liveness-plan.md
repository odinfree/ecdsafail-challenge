# Boundary carry and output-host liveness: bounded mission order

## Ball owner and changed equation

The single owner is the lifetime of one replay chunk boundary at the actual
Q1267 divide-replay peak.  The candidate combines Justin Drake's exact
window-entry-carry observation with the older exact source/output host cells:

> Can the carry entering the retained comparison window be kept in an existing
> source or output wire until the chunk boundary is consumed, then restored
> without another clean qubit, a co-resident prefix ladder, or replay of the
> omitted prefix?

This is a liveness/information question, not another window sweep.  The exact
Boolean identity is already established on remote research artifacts; this
phase must close the reversible schedule and the production score equation.

## Source and prior-art binding

- official source commit:
  `67524171baaf568dc3dc606f38515745f70804ff`;
- official source tree:
  `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`;
- Justin controller artifact:
  `e06c1810f17c97d5b0ee964ee63f62b8a05d83e9`;
- reduced-width circuit harness:
  `e0322f5eddb5fb169ed89a8430a269a36dbc58e0`;
- Pareto sweep:
  `d76c426f7ad568355ecdb29be946a2a455226ecb`;
- earlier exact carry-host composition:
  `8d261ea9449bcd37c9a6d9a1d981a90761ec7b57`.

The prior artifacts already prove that supplying the exact window-entry carry
removes the truncated phase error.  They do not prove that the entry carry can
be restored cheaply at the production peak.

## Current owner census

The zero-environment official stream was rebuilt locally:

```text
operations: 12,593,858
ops SHA-256: 87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e
Q: 1267
fixed-64 executed T: 911220.66
value / phase / ancilla: 0 / 0 / 0
```

The built-in allocation census at operation 913,421 in `pp_div_replay` is:

```text
335 sign-tape wires
256 coefficient wires
256 numerator wires
292 walk-limb wires
126 owned chunk carries
  2 live chunk boundaries
--------------------------------
1267 live qubits
```

The two apparent one-wire rows in the raw census are the specialized round-0
and round-1 signs and are included in the 335-bit tape total.  Every listed
family is semantically live; no clean anonymous donor exists.

At the binding allocation, 126 owned carries plus an external carry-out means
a 127-bit chunk.  The retained comparison window is 21 bits, so its exact
entry carry is `c106`.

## Executable falsifiers

The certificate must exhaustively show:

1. fixed-width `(accumulator, carry_in) -> (sum, carry_out)` is not injective
   for a fixed addend, so the incoming boundary cannot be coherently erased
   from next-chunk outputs alone;
2. the MAJ source-host cell is exactly reversible when its predecessor carry
   is retained, but loses one bit of information without that predecessor;
3. a top-window phase oracle without the entry carry has exact collision
   witnesses even when the original chunk carry-in is supplied; and
4. restoring a hosted `c106` by the MAJ/UMA dependency chain requires
   `c105..c0`, or else recomputation/replay of that omitted 106-bit prefix.

## Admission and hard falsifier

`ADMIT` requires one explicit schedule that restores every host and phase with:

- Q at most 1267, or Q1268 with at least 719 rounded executed-T saved;
- no co-resident carry prefix and no full omitted-prefix replay;
- exact forward/inverse value and phase semantics; and
- a live donor named by role at the operation-913,421 owner.

`HARD_NACK` the one-entry-carry/output-host family if output assimilation is
non-injective and source-host restoration recursively requires the omitted
prefix.  A phase-exact but wider/slower repair is correctness defense, not a
leadership candidate.  Do not port it into production Rust or run a trusted
9,024-shot evaluation under this structural label.

Provider, nonce, fleet, queue, push, public-note, protected-instance, and
submission authority remain closed.
