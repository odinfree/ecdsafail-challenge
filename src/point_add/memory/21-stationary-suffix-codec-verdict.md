# Stationary terminal-suffix codec: current-source verdict

## Verdict

`HARD_NACK` for replacing every sign after a fixed production cutoff with one
shared terminal-run sign. The transformation is exact only after the walk has
entered its `(+-1, +-1)` fixed-point orbit. Cutoff 631 is early enough to
remove 64 physical history qubits, but the fixed 64-lane source-bound selfcheck
found 27 classical mismatches. The operation stream changed and no fallback,
reset, or hidden postselection was present, so this is a direct falsification
of the assumed universal cutoff.

This verdict is scoped to a single fixed cutoff and shared run sign. It is not
a lower bound against a lossless variable-boundary suffix code or a different
walk recurrence.

## Binding and preserved artifact

- Official source commit:
  `67524171baaf568dc3dc606f38515745f70804ff`
- Official source tree:
  `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`
- Research parent: `6079d93`
- Prototype commit: `ffa9e377d4b48a23d216cd071a5b3c6009bc2324`
- Exact revert commit: `33197ff07b58eecc9d89e2b7dd5d4b237c25b1a8`
- Prototype source-diff SHA256:
  `ad60923e14600fa36b57272e8262c54e3e5316fb634dfc8ffcbee8b891179814`
- Activation: `SUB4_PP_TAIL_RUN_START=631`

With the codec disabled, the refactored prototype emitted the exact promoted
operation stream:

```text
ops SHA256 87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e
emitted ops 12593858
compressed bytes 45668102
```

That control rules out a stale binary or accidental baseline rewrite.

## Fixed-cutoff falsifier

The first and only structural cutoff was predeclared at round 631. All later
logical tape entries alias the round-631 sign; forward and inverse walk rounds
use it only as a control, coefficient replay retains every logical round, and
the one physical sign is cleared by the ordinary inverse of round 631.

The local build reported:

```text
ops SHA256 a96649488b88afaa61fffc0695843f50a3ef4e3c424f2796b26627df2277ff80
emitted ops 12531584
Q1267
T64 908758.02
classical mismatches 27
phase 0x1010101500000200
dirty qubits 0
```

Transcript SHA256 values:

- standard output:
  `321c1658a7ae9ab68b8f879ba43aeeb9c4a40f1de3677ea5928d0a446e805af0`
- profiler/selfcheck output:
  `c4adf9804e5df620868031753f0beb883252adaa676c24444e4ee395f7e96f2c`

The nonzero phase mask is downstream damage on failing lanes, not a clean
phase-only success. Since the classical gate already fails, no 9,024-shot
evaluator or nonce work is warranted.

## Co-binder falsifier

The raw allocation saving did not lower global Q. The existing planner uses
the freed history width to enlarge replay ladders and remains at Q1267. One
bounded count-shape check set both planner caps to 1209. It did not create a
Q1203 candidate: exact split geometry instead rose to Q1289/T64 957078.58 and
still had 27 classical mismatches plus phase garbage.

```text
ops SHA256 4bc0d049a20b6f4073010a7098aab91ae512ad0c8e23454ed50ed3ed9dcff5fc
stdout SHA256 5ae77b53bd7e57db6404c98caf594d93fb294b9a92869cd51c978016abe54b98
stderr SHA256 c3401fdea15f032437f27be34be0e330ebbe91f9e569e198cb93175f6ee41508
```

Thus the route fails both required premises: cutoff correctness and automatic
translation of nominal history savings into a lower global peak.

## Changed-premise reopen

Reopen this axis only with one of:

1. a source-bound proof that every admitted challenge lane reaches the terminal
   orbit before a cutoff that removes enough physical bits at both co-binders;
2. an explicit lossless variable-boundary suffix code, including reversible
   overflow handling and complete Q/T cleanup pricing; or
3. a different recurrence whose convergence certificate is stored more cheaply
   than the sign history it replaces.

The production source was restored byte-for-byte. No provider, nonce, fleet,
queue, push, public-note, protected-instance, or submission action was taken.
