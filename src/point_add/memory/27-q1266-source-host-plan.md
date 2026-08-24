# Q1266 binding-only source host: bounded prototype order

## Changed premise

The prior exact source-host composition at commit
`8d261ea9449bcd37c9a6d9a1d981a90761ec7b57` fired 963 times across four
Q1275 co-binders and missed the Q1274 T ceiling by 242.  The current official
source has a different peak equation:

```text
pp_div_replay:   Q1267
pp_mul_walkback: Q1267
pp_mul_replay:   Q1264
square:          Q1153
```

Only two phases must be cut.  The old activation price therefore cannot be
reused.  This is distinct from the closed Q1266 checkpoint saddle at
`1fca21126db62276e23f0704f45c2955c4749f75`, which changed only interleave
coordinates and failed the trusted gate at 27/10/0.

## Prototype

Port the already-proved Cuccaro MAJ/UMA source host into the current generic
`chunk_add`, default off behind:

```text
SUB4_BINDING_SOURCE_CARRY_Q1266=1
```

It may fire only when:

```text
phase in {pp_div_replay, pp_mul_walkback}
active_qubits + owned_carries > 1266.
```

Replace exactly one clean owned carry with an addend wire.  When the chunk has
no incoming carry, host position one rather than zero so the MAJ cell has the
required predecessor.  Restore the addend and predecessor with the exact UMA
cell before lower measured carries unwind.

## Predeclared gates

1. The existing exhaustive eight-case MAJ/UMA certificate in
   `pp_boundary_liveness.py` remains the primitive positive control.
2. With the switch absent, emitted operations and SHA-256 must reproduce the
   official 12,593,858 / `87371140...d05e` artifact.
3. With the switch enabled, the full source must build at Q at most 1266 and
   both former Q1267 phases must fall.
4. The fixed-64 profile must report exact ABI value, zero phase, and clean
   ancillas.
5. The strict live frontier permits T at most 912,109 at Q1266.  Relative to
   live rounded T911390, the host may spend at most 719 T.  The activation
   count and measured T delta must fit that budget; a count-only Q cut is not
   admission.
6. Only after gates 1-5 may an unchanged trusted 9,024-shot run be considered.
   No nonce search is authorized, and any inherited-stream failure closes the
   route.

## Hard falsifiers

`HARD_NACK` without trusted replay if any of these occurs:

- Q remains 1267 because a co-binder was missed;
- the host fires more than the 719-T exchange budget or fixed-64 pricing
  exceeds the strict ceiling;
- value, phase, ancilla, or disabled-artifact reproduction fails; or
- another exact wire is required at a binding activation.

Preserve the prototype and exact revert if it fails.  Provider, nonce grind,
fleet, queue, push, public-note, protected-instance, and submission authority
remain closed.
