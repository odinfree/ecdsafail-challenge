# Q1266 binding-only source host: verdict

## Verdict

`HARD_NACK` at the predeclared fixed-64 economics gate.  The exact source host
does cut both live co-binders from Q1267 to Q1266 and remains value/phase/
ancilla clean, but it fires 1,665 times and spends far more T than one qubit is
worth.  No trusted 9,024-shot replay was admitted.

## Binding

- official parent commit:
  `67524171baaf568dc3dc606f38515745f70804ff`;
- official parent tree:
  `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`;
- prototype commit:
  `468fe54ca93fd2d9f712f8a0671f32daba6d992a`;
- prototype tree:
  `b613f21ab112cb512549a9c272978b79ffb99e0f`;
- exact revert commit:
  `b5c0c4b71330088633f3de7ddea7cfd6d0963c5b`;
- candidate compressed op SHA-256:
  `830a09b20e5a5d1fd750092cc7ed6815645b61a7a7c96fe1dc6665eb52a36f8f`;
- candidate canonical semantic op SHA-256:
  `2029d2470a2daa6af4505ac1e7e60084061d64b2274a5e5b40308ba390f3b625`.

The switch-off build reproduced the exact official 12,593,858 operations,
compressed SHA-256 `87371140...d05e`, and canonical semantic SHA-256
`bd3612b1...ad37` before the candidate was enabled.

## Candidate profile

The environment-gated candidate emitted 12,587,199 operations.  Its
fixed-64 profile was:

```text
peak Q:               1266
pp_div_replay peak:   1266
pp_mul_walkback peak: 1266
pp_mul_replay peak:   1264
square peak:          1153
executed T64:         913255.12
classical / phase / dirty: 0 / 0 / 0
```

The exact official fixed-64 control on the same rebuilt binary was
T911220.66 at Q1267 and 0/0/0.  The candidate delta is therefore +2,034.46
executed T on that population.

The emitted CCX count rises from 955,130 to 956,795: exactly 1,665 source-host
activations, consistent with the source host's one additional coherent CCX per
activation.  This is 946 activations beyond the full 719-T exchange budget
even before allowing for measurement-stream redistribution.

At Q1266 the strict live ceiling is rounded T912109.  The fixed-64 candidate
rounds to 913255, 1,146 T over that ceiling, for a diagnostic product
1,156,180,830.  That product is 1,449,700 worse than the live score.  A trusted
run cannot rescue a candidate that fails its registered prefilter by this
margin.

## Relationship to the earlier Q1266 saddle

This was not a rerun of the closed `1fca211` checkpoint saddle.  That route
changed `R1/R1_MUL/R2/PEAK` and failed its one trusted replay at 27/10/0.  The
source-host candidate left the schedule fixed and replaced one owned carry
only at the two current co-binders.  It independently fails on economics, so
the two closures are complementary.

## Reopen interface

Reopen source hosting only with one of:

1. an exact host cell whose incremental executed price is substantially below
   one T per activation;
2. a proof that at least 946 of the 1,665 activations can use a clean idle donor
   with Clifford-only restoration; or
3. an orthogonal exact T cut exceeding 1,146 on the same Q1266 stream before
   trusted replay.

Do not relabel checkpoint retuning, approximate boundary changes, or nonce
selection as a source-host improvement.

The production source is restored byte-for-byte.  No trusted replay, provider,
nonce grind, fleet, queue, push, public note, protected-instance, or submission
action was taken.
