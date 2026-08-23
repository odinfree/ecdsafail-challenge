# Teddy retained replay relative-phase ABI predeclaration

Predeclared: 2026-08-23

Status: `FROZEN_BEFORE_X009_SOURCE_EDIT_OR_SEMANTIC_RESULT`.

## One changed-premise falsifier

X009 asks whether the retained-denominator rounds-`0..3` divide replay is an
exact replacement for the unchanged raw production-forward replay **relative
to the current source**, even though that isolated raw reference is not
absolute-phase clean on arbitrary nonzero replay seeds.

The candidate and reference must have identical coefficient/numerator state
and identical complete phase masks after every replay round under one
source-event-bound measurement tape. Both sides may inherit the same nonzero
phase mask from the unchanged replay cells. The candidate may not introduce a
phase delta, new stochastic operation, new ancilla debt, or new retained state.

This is a prototype-equivalence experiment, not an absolute-phase proof. It
does not relax value, inverse, restoration, cleanup, width, or state gates. It
does not implement a production splice or extend to round 4.

## Why the premise changed

X008 stopped before candidate execution because the raw production reference
itself produced phase mask `000000400000004f` after round 2 for its first
64-seed batch. The complete mask covered seed indices `{0,1,2,3,6,38}`; the
first dirty row was production-ABI `(d,c,n)=(1,0,1)`.

Requiring that isolated reference to be phase zero cannot distinguish inherited
source debt from phase newly introduced by the retained replacement. X009
therefore compares candidate and raw-reference phase masks exactly. It records,
does not erase, the inherited reference debt. No X009 result may be restated as
raw-phase correctness or whole-circuit correctness.

## Frozen source and evidence identities

- Branch: `research/redescent-teddy-1270`.
- X009 base HEAD:
  `85f52c9a9f1416542adf2084ef9b0a1b48c06f50`.
- X009 base tree:
  `a4ebb1eb710980aa960a0557141df10490e95134`.
- Preserved production `src/point_add/pingpong_div.rs` SHA-256:
  `22c4820a9ba3b2356eb785d0d0d452b0939a643cb6c65241706554d19b7df376`.
- X008 opt-in module SHA-256:
  `fe6ca1a784291c50fb2a0d1a3ec67d6bb4fd785862e23214643bacee44767262`.
- X008 gate source `src/point_add/mod.rs` SHA-256:
  `d014064fdb557002f6c30574ed9a37fae9ca269f2df7416a497425d1cabcf0ff`.
- X008 absolute-phase KILL receipt SHA-256:
  `45ef2800c3fd9f1d5985e9b0a9c1ba34840fa8122d5455e4bab650439ff4fbc4`.
- X008 original predeclaration SHA-256:
  `89682e682625d24570908707c99713bc8f6f7c140cc6bf6553bd344976a8ad6a`.
- X007 exact zero-seed receipt SHA-256:
  `f78309e7fdd444fa8a439cfb47ff6915f3c88936908b011b5c7e850af81d140d`.

The protected production module and default build remain outside the X009
source edit. X009 may alter only the opt-in selfcheck and its env gate.

## Frozen corpus

X009 reuses X008's already-frozen complete Cartesian corpus without changing a
row, seed class, order, generator, or hash:

- 64 independent canonical denominators x 64 unique canonical seed pairs =
  4,096 ordered rows, denominator-major then seed-major.
- Seeds 0 through 31: production divide entry ABI
  `(coefficient=0,numerator!=0)`.
- Seeds 32 through 63: strict transducer stress ABI
  `(coefficient!=0,numerator!=0)`.
- Fixture `.lane/fixtures/TEDDY-NONZERO-ABI-CORPUS.tsv` SHA-256:
  `53b06714ffdf079be23b2d3e1d25706c0d2853ab08d13345588f9a505c9409b0`.
- Ordered denominator SHA-256:
  `bd1c937e2aa188106bc156929b19f536f6b5933510221371e42d1cbaeedeea2d`.
- Ordered seed-pair SHA-256:
  `4a48e4569fd7ad7df277e9624f06a58b2b453cf8629c76eb07db24052d305d39`.
- Generator SHA-256:
  `b23cb5665536738502a658228f9b0cb51d7b926b899abe381011f7a0c53a8f96`.

The harness must reassert row count, Cartesian order, uniqueness, canonical
range, numerator nonzero, and both seed classes before either simulator runs.

## Unchanged value and inverse ABI

For denominator `d`, raw production signs `s1,s2,s3`, and seed `(c0,n0)`,
the unchanged forward authority remains:

```text
(c0,n0) --R0--> --R1(s1)--> --R2(s2)--> --R3(s3)--> (c4,n4)
```

The retained candidate still computes/uses/uncomputes signs 1 through 3 from
one retained denominator word, uses X007's single sign1-keyed `T;R2;T`
normalization sequence, and keeps round3 flag-free. The raw reference never
shares `T`. Candidate and reference coefficient/numerator continuations must
match bit-for-bit after rounds 0, 1, 2, and 3.

For each denominator, all 64 raw round-3 output pairs must be unique. The exact
finite inverse remains the host table on that raw image:

```text
Fd^-1[Fd(c0,n0)] = (c0,n0)
```

No approximate production reverse cell is admitted as an arbitrary-seed
oracle. A collision or failed image lookup is an immediate KILL.

## Source-event-bound stochastic tape

Raw comparison of two independent SHAKE streams would test random-stream
alignment, not circuit equivalence. X009 freezes this coupling instead:

1. For each denominator batch, the reference consumes the exact X008 stream
   `SHAKE256("Teddy Pender X008 raw forward reference" ||
   denominator_index_le64)` across its unchanged full op order. This must
   reproduce the X008 first-batch round-2 canary mask
   `000000400000004f` before candidate comparison is accepted.
2. The harness records every 64-bit random word consumed by `Hmr` or `R` inside
   each unchanged reference replay range `R0`, `R1`, `R2`, and `R3`.
3. The candidate consumes those exact per-round words, in the exact same
   `Hmr`/`R` event order, for its corresponding unchanged replay cell. Extra
   reference walk/walkback events do not shift candidate replay randomness.
4. Candidate/reference replay ranges must have identical ordered `Hmr`/`R`
   kind sequences. The retained sign oracles, `T` toggles, and candidate
   cleanup must contain zero `Hmr` and zero `R`. Any extra stochastic event is
   `KILL_NEW_STOCHASTIC_DEBT`.
5. Reference walk phase must be zero before `R0`. Reference cleanup must not
   change the phase mask present after `R3`; candidate cleanup must likewise
   preserve its `R3` phase mask. Debt generated only by reference walk or
   walkback is `KILL_REFERENCE_AUX_PHASE_DEBT`, not inherited replay debt.

The complete 64-lane candidate and reference phase masks are compared after
each replay round and after cleanup. Equality includes every dirty and clean
lane; diff hunks or counts are insufficient. Nonzero equal masks are reported
verbatim as inherited raw-reference debt.

## Ordered gates and KILL classes

For each denominator batch, the harness applies this fixed order:

1. verify source/corpus identities and static resource/stochastic structure;
2. run raw walk and assert its phase is zero;
3. run raw rounds0..3, preserving complete state and phase masks, then prove
   collision-free finite-inverse closure and exact raw cleanup;
4. run candidate rounds0..3, asserting retained sign equality and local cleanup;
5. after each candidate round, compare denominator, retained denominator,
   coefficient, numerator, then the complete phase mask against raw authority;
6. run candidate cleanup and assert phase preservation and all non-output
   quantum ancillas zero;
7. repeat the full 4,096-row run and require byte-identical normalized receipt.

Immediate KILL classes:

- production seed0..31 value mismatch:
  `KILL_NONZERO_NUMERATOR_ABI`;
- only strict seed32..63 value mismatch:
  `KILL_GENERAL_TRANSDUCER_ABI`;
- any candidate/reference phase-mask difference:
  `KILL_RELATIVE_PHASE_MISMATCH`;
- raw forward collision or failed inverse lookup:
  `KILL_FORWARD_ABI_NONINJECTIVE`;
- X008 canary drift: `KILL_REFERENCE_CANARY_DRIFT`;
- extra candidate `Hmr`/`R`: `KILL_NEW_STOCHASTIC_DEBT`;
- walk/walkback-only phase change: `KILL_REFERENCE_AUX_PHASE_DEBT`;
- Q>1114, emitted T>960, a second/concurrent flag, extra 256-bit carrier,
  unavailable predecessor, dirty sign/scratch/flag, changed denominator or
  retained word, cleanup phase change, or non-output ancilla debt.

Stop on the first class in the ordered gate sequence. No correction or sweep is
authorized inside X009.

## Frozen Q/T/state price

The candidate price remains X007/X008's measured structure:

- ABI: denominator256 + coefficient256 + numerator256 = Q768.
- Persistent prototype debt: retained denominator256 + shared sign1 + fixed
  oracle scratch2 + one local normalization flag1 = Q260.
- Base: Q1028; maximum fused-cell transient: Q86; total cap: Q1114.
- Candidate operations: 13,659.
- Candidate emitted T cap: 960, split rounds `65/141/377/377`.
- Candidate executed T cap: 960 averaged over the frozen corpus.
- Flags peak1/concurrent0; persistent carrier0; max live sign1.

Host-side stochastic-tape extraction and the finite inverse allocate no circuit
qubits, bits, operations, or T gates. Reference resources are recorded
separately and are not score claims.

## Exact pass boundary

PASS requires complete 4,096/4,096 value, inverse, restoration, cleanup, and
per-round phase-mask equality, followed by a byte-identical repeat. A pass
proves only that the retained prefix introduces no additional phase or value
debt relative to the source-bound raw prefix under the frozen event coupling.

PASS may authorize a subsequent opt-in **prototype** of the first
whole-production splice: `PingPongDirection::Divide, Some(plan)` replay rounds
1 through 3 with retained-word sign reconstruction and the existing terminal
conditional-negate/XOR coefficient cleanup. X009 itself does not implement that
splice. No absolute-phase, raw-phase, trusted full-circuit, score, promotion,
provider, range, hunt, submission, CUDA, or public-note claim follows.
