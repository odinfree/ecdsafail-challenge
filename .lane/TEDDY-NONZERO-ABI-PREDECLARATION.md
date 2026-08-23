# Teddy retained replay nonzero-ABI predeclaration

Predeclared: 2026-08-23

Status: `FROZEN_BEFORE_X008_SOURCE_EDIT_OR_SEMANTIC_RESULT`.

## One bounded falsifier

Close or kill the named nonzero-numerator ABI gap in the exact retained-word
rounds-`0..3` divide-replay prefix. Do not extend the prefix to round 4.

The candidate reconstructs production signs 1 through 3 from one retained
denominator word, uses one shared sign, the existing two-qubit oracle scratch,
and the same single local normalization flag from X007. It must expose exactly
the same coefficient/numerator continuation as an unchanged production-walk
reference on a frozen nonzero-seed corpus. A separately built unchanged
production inverse must map that continuation back to the exact input ABI.

This is one semantic experiment. There is no second flag, persistent carrier,
extra retained word, width schedule change, arithmetic-window change, nonce
change, repair ladder, or optimization sweep.

## Frozen source and prior-result identities

- Branch: `research/redescent-teddy-1270`.
- X008 base HEAD:
  `21caaa1789b3a14c367aa574ee7ae0326ad6c5bc`.
- X008 base tree:
  `dc543da2bbf5861c5ca2a7e76cc60456f91454d6`.
- Preserved production `src/point_add/pingpong_div.rs` SHA-256:
  `22c4820a9ba3b2356eb785d0d0d452b0939a643cb6c65241706554d19b7df376`.
- Opt-in retained rounds-`0..3` module SHA-256:
  `13e8d210e85be9f9ad8397b411c302941ea00eadb4a971e2cd5232e4c3494680`.
- `src/point_add/mod.rs` SHA-256:
  `0398a3180ba153b9d685f3e6c2a8eb0d30cdd0052ef1f74cb6368204321aa975`.
- X007 receipt SHA-256:
  `f78309e7fdd444fa8a439cfb47ff6915f3c88936908b011b5c7e850af81d140d`.
- Default production artifact identity: 15,730,117 operations, 61,944,467
  compressed bytes, SHA-256
  `843558da6f504e3f8f2f41cae1edeccdf0cfed9e0dc216f8e880ebc1752e7b75`.

X007 proved only the all-zero coefficient/numerator seed. It is admissible as
setup evidence, not as a result for X008.

## Frozen independent denominator x seed corpus

The complete ordered corpus is the Cartesian product of 64 independently
generated denominators and 64 replay-register seed pairs, for 4,096 rows.
It does not reuse X007's structured denominator fixture.

- Fixture: `.lane/fixtures/TEDDY-NONZERO-ABI-CORPUS.tsv`.
- Row schema: 64-hex-digit `denominator`, `coefficient`, `numerator`, separated
  by tabs, with denominator-major then seed-major order.
- Denominators: 64 unique canonical field elements in `[1,p-1]`; SHA-256 of
  the ordered one-column encoding:
  `bd1c937e2aa188106bc156929b19f536f6b5933510221371e42d1cbaeedeea2d`.
- Seeds: 64 unique pairs; every numerator is nonzero. Seeds 0 through 31 are
  the production divide ABI (`coefficient=0`, `numerator!=0`). Seeds 32 through
  63 are the stronger transducer ABI (`coefficient!=0`, `numerator!=0`).
  Ordered seed encoding SHA-256:
  `4a48e4569fd7ad7df277e9624f06a58b2b453cf8629c76eb07db24052d305d39`.
- Complete 4,096-row fixture SHA-256:
  `53b06714ffdf079be23b2d3e1d25706c0d2853ab08d13345588f9a505c9409b0`.
- Generator SHA-256:
  `b23cb5665536738502a658228f9b0cb51d7b926b899abe381011f7a0c53a8f96`.
- Fixture size: 798,720 bytes.

The generator uses source-labelled SHAKE256 streams plus fixed edge values and
asserts counts, uniqueness, canonical range, seed classes, and all frozen
hashes. No row may be added, removed, reordered, or replaced after the
predeclaration commit.

## Explicit forward and inverse ABI

Let `d` be the denominator and `(c0,n0)` the coefficient/numerator seed. Let
`s1,s2,s3` be the exact first three nontrivial signs from the unchanged
production denominator walk. Let `Rr(sr)` be production
`replay_halving_round` at round `r`, and `Dr(sr)` its unchanged production
`replay_doubling_round` inverse.

The unchanged production forward mapping executes:

```text
(c0,n0) --R0--> --R1(s1)--> --R2(s2)--> --R3(s3)--> (c4,n4)
```

The independently seeded inverse mapping executes:

```text
(c4,n4) --D3(s3)--> --D2(s2)--> --D1(s1)--> --D0--> (c0,n0)
```

The retained candidate replaces each stored sign with compute/use/uncompute
from retained `d`. It retains X007's exact round-2 sequence:

```text
T(s1); R2(s2); T(s1)
```

where `T` reconstructs sign 1 into the one local flag, conditionally XORs `p`
into the coefficient register, then clears the flag through the same oracle.
Round 3 remains flag-free. The unchanged production reference does not apply
`T`; this is deliberate. Candidate continuation must equal the raw production
continuation after every round, so a zero-seed-only sentinel assumption cannot
hide behind a candidate/reference pair that shares the same modification.

The inverse circuit is a reference-side ABI miter, not added candidate state.
It is seeded from the measured forward continuation and must restore the exact
input coefficient/numerator pair for every row. Reference inverse failure is
reported separately and does not count as candidate parity.

## Exact pass and kill gates

X008 passes only if all 4,096 rows satisfy all of these:

- unchanged production forward and retained candidate coefficient/numerator
  continuations are equal after rounds 0, 1, 2, and 3;
- unchanged production inverse restores `(c0,n0)` exactly from `(c4,n4)`;
- denominator and retained denominator are preserved exactly;
- retained sign reconstruction matches production walk signs 1 through 3;
- one shared sign, two oracle scratch qubits, and the one normalization flag
  are zero at every declared cleanup checkpoint;
- normalization flags peak at one and never overlap another flag;
- persistent carrier bits remain zero;
- phase and non-output ancilla debt are zero in candidate, forward reference,
  and inverse reference;
- candidate peak Q is at most 1114 and the round-2
  `signed_mod_add_pm_halve_fused` cell remains the first Q binder.

Immediate `KILL_NONZERO_NUMERATOR_ABI` occurs if any seed 0 through 31 exposes
a continuation mismatch, proving the X007 mapping depended on both replay
registers starting zero. A mismatch only in seeds 32 through 63 is
`KILL_GENERAL_TRANSDUCER_ABI`; it preserves only the narrower production-entry
subspace. Any extra 256-bit carrier, second flag, Q>1114, unavailable
predecessor, dirty sign/scratch/flag, phase, or ancilla is also an immediate
KILL. If the unchanged inverse fails, report `KILL_REFERENCE_ABI_UNAVAILABLE`
instead of blaming the retained candidate. Stop on the first failing class; no
repair ladder is authorized.

## Frozen Q/T prototype price

The candidate ABI is Q768: denominator, coefficient, and numerator. Its fixed
debt is retained denominator256 + shared sign1 + oracle scratch2 + one local
flag1 =260, for base Q1028. The X007 round-2 fused cell uses at most86 transient
qubits, so X008's candidate cap is unchanged at Q1114. No extra inverse or
carrier register is charged to the candidate; forward and inverse references
are separate miters.

The forward candidate emits exactly the same structural rounds-`0..3` path as
X007: at most960 Toffoli, split65/141/377/377. Nonzero inputs may raise average
executed T, so the frozen executed ceiling is960. This prices a worst-case
+65.946 average executed T over X007's zero-seed894.054 receipt, with no Q or
emitted-T allowance. Reference forward/inverse costs are recorded separately
and are not a score claim.

## Exact outcome boundary

If all gates pass, name—but do not implement—the first whole-production splice:
the `PingPongDirection::Divide, Some(plan)` rounds-1-through-3 replay interval,
replacing stored tape controls with retained-word sign reconstruction while
keeping the live coefficient/numerator ABI and proving the existing terminal
conditional-negate/XOR coefficient cleanup. Do not extend to round 4.

No provider, range, hunt, submission, CUDA, public note, protected-leader
mutation, or whole-circuit promotion is in scope.
