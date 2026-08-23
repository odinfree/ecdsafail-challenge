# Teddy numerator-residual carrier X010 predeclaration

Predeclared: 2026-08-23

Status: `FROZEN_BEFORE_X010_CHARACTERIZATION_OR_SOURCE_EDIT`.

## One changed-premise saddle

X010 allows exactly one new 256-bit numerator-residual carrier to repair the
round-2 nonzero-ABI loss proved by X009. No second carrier, retained predecessor
word, second flag, growing transcript, or round-4 extension is allowed.

The experiment has two ordered stages:

1. characterize the exact round-2 residual on the complete frozen4,096-row
   corpus and determine whether it is a deterministic function of state already
   live at the correction and cleanup boundaries;
2. only if one clean reversible carrier is feasible, implement the smallest
   source-semantic compute/correct/uncompute oracle and rerun the complete
   rounds-`0..3` value, inverse, relative-phase, restoration, and cleanup gates.

This uses the research contract's prototype tolerance. Q may rise to1370 and T
may regress, but both debts must be measured exactly. A finite-corpus pass is a
component saddle only, never a full-circuit or score claim.

## Frozen source and evidence identities

- Branch: `research/redescent-teddy-1270`.
- X010 base HEAD:
  `6b8d50f246b96171989dcca39186ebb1ea656847`.
- X010 base tree:
  `a8962b7035d0753252e8b398313211444119fe10`.
- Preserved production `src/point_add/pingpong_div.rs` SHA-256:
  `22c4820a9ba3b2356eb785d0d0d452b0939a643cb6c65241706554d19b7df376`.
- X009 opt-in module SHA-256:
  `071699cc95dd3e09b95f9985f983d497399f17ec8c2efa527a073aa0510d66c5`.
- X009 env-gate source SHA-256:
  `d3cee3c036e1b4f83139a3fdd9da6b29f158cd9fc00a7dbe9567d34d1b8088df`.
- X009 amended predeclaration SHA-256:
  `d56243bf1c3139c9a51a1191d1ea017d96ff6667d32ee626705b12e1b6de7962`.
- X009 terminal receipt SHA-256:
  `a76756baa32ea86bd8fc8e71203365ae2598e0afa1b3be356caf252367e86565`.
- X009 normalized receipt SHA-256:
  `0563479d2663232a2e8291c0184a8be9d9ac414be69ff246042e321e83675591`.

Protected production remains untouched. X010 may add only opt-in
characterization/carrier selfchecks to the isolated retained module and its env
gate.

## Frozen corpus and authority

X010 reuses X008/X009's immutable denominator-major Cartesian corpus without a
row, order, or class change:

- 64 independent canonical denominators x64 unique canonical replay seeds =
  4,096 rows;
- seeds0..31: production ABI `(coefficient=0,numerator!=0)`;
- seeds32..63: strict transducer stress ABI
  `(coefficient!=0,numerator!=0)`;
- fixture SHA-256:
  `53b06714ffdf079be23b2d3e1d25706c0d2853ab08d13345588f9a505c9409b0`;
- ordered denominator SHA-256:
  `bd1c937e2aa188106bc156929b19f536f6b5933510221371e42d1cbaeedeea2d`;
- ordered seed SHA-256:
  `4a48e4569fd7ad7df277e9624f06a58b2b453cf8629c76eb07db24052d305d39`;
- generator SHA-256:
  `b23cb5665536738502a658228f9b0cb51d7b926b899abe381011f7a0c53a8f96`.

The unchanged raw production walk/replay remains the sole continuation and
finite-inverse authority. X009's source-event-bound stochastic coupling remains
frozen: raw uses the exact X008 SHAKE stream, candidate replay consumes the
corresponding post-walk `Hmr`/`R` words, and the first raw round-2 canary must be
`000000400000004f`.

## Stage A: exact residual characterization

For every row, record full 256-bit states at these boundaries:

```text
P1 = (d, c1, n1)                 raw/candidate exact after round1
C2 = (d, c2_candidate, n2_candidate)
R2 = (d, c2_raw,       n2_raw)
R3 = (d, c3_raw,       n3_raw)
```

Define both representations of the numerator residual:

```text
delta_field = (n2_raw - n2_candidate) mod p
delta_wrap  = n2_raw wrapping_sub n2_candidate in Z/(2^256)
```

Bit-exact raw continuation is the final gate; field equality alone is
insufficient. Record whether both residuals agree as ordinary subtraction on
canonical words and preserve both when they do not.

Test exact functional dependency by grouping identical keys and rejecting any
key fiber that contains more than one residual. The frozen ordered key menu is:

1. `d`;
2. `c1`; `n1`; `(d,c1)`; `(d,n1)`; `(c1,n1)`;
3. pre-correction full live key `P1=(d,c1,n1)`;
4. candidate correction-point subsets `c2_candidate`, `n2_candidate`,
   `(d,c2_candidate)`, `(d,n2_candidate)`,
   `(c2_candidate,n2_candidate)`;
5. correction-point full live key `C2`;
6. corrected-output full live key `R2`, for immediate carrier uncompute;
7. raw round-3 live key `R3`, only if immediate uncompute fails and the same
   carrier must survive one more round.

Select the earliest/smallest collision-free key in this order that also admits
a source-semantic reversible oracle. A unique full tuple on only the frozen
sample is not by itself a production formula.

Report carrier structure for the complete corpus and separately for production
and stress seed classes:

- distinct residual count and multiplicities;
- empirical Shannon entropy in bits and information lower bound
  `ceil(log2(distinct_count))`;
- all-one support mask, varying-bit mask relative to the first residual,
  highest active/varying bit, and naive fixed binary width;
- constant, retained-sign-conditioned, affine-XOR, or arithmetic-expression
  fits checked in that order;
- minimum live-key subset with no conflicting fiber and the largest fiber size
  for every rejected subset.

Stage A is observation only. It allocates no circuit carrier and makes no
correctness claim. Stop before construction if the residual is not a function
of an allowed live key, if exact correction needs two independent 256-bit
values, or if cleanup requires predecessor history no longer live.

## Stage B: one-carrier construction

Only a Stage-A-surviving mapping may be implemented. The carrier contract is:

- allocate exactly one 256-bit zero register `residual`; no second carrier;
- compute the exact residual from an allowed already-live key into `residual`;
- correct the candidate numerator bit-for-bit to raw round-2 continuation;
- clear `residual` either immediately from corrected live `R2`, or after round3
  from live `R3`; immediate cleanup is preferred and both choices must be
  declared in the receipt;
- never retain a predecessor copy of `c1`, `n1`, a sign transcript, or another
  256-bit word to make the inverse oracle work;
- retain X007/X009's one normalization flag, one shared sign, and two oracle
  scratch qubits; all are zero at their existing checkpoints;
- carrier and all scratch are zero before return; denominator and retained
  denominator are exact.

The frozen oracle-choice order is:

1. constant or retained-sign-conditioned linear toggle;
2. exact affine XOR of already-live bits;
3. direct reversible arithmetic expression using existing source primitives;
4. bounded-domain lookup only as an explicitly finite-corpus semantic witness.

A lookup-only witness cannot authorize a production formula or full-circuit
splice. No second construction, repair ladder, encoding sweep, or T
optimization is permitted after the first selected exact mapping.

## Frozen Q/T/state price

The X009 candidate base is Q1028:

```text
ABI768 + retained denominator256 + sign1 + scratch2 + flag1 = Q1028
```

One residual carrier raises the base to Q1284. The existing round-2 fused cell
uses at most86 transient qubits, so the absolute X010 cap is:

```text
Q1284 + transient86 = Q1370
```

No additional persistent qubit is allowed. Oracle scratch may use only the
same at-most86 transient envelope and must be cleared before the fused replay
cell binds. Q1371, a second flag, a 257th carrier bit, or a second 256-bit word
is an immediate KILL.

There is no score T ceiling for this first exact carrier prototype. Record
candidate operations, emitted T, average executed T over all4,096 rows,
per-stage T, and delta versus X009/X007. T is debt, not a score claim, and no
optimization follows inside X010.

## Exact pass and KILL gates

PASS requires all4,096 rows to satisfy:

- candidate/raw coefficient and numerator equality after rounds0,1,2,3;
- raw64-seed image injectivity and finite inverse for every denominator;
- candidate/raw complete phase-mask equality after every round and cleanup
  under the frozen event coupling;
- raw canary identity and walk/walkback phase preservation;
- denominator/retained preservation;
- sign/scratch/flag cleanup at every declared boundary;
- exactly one carrier, Q<=1370, no second flag/carrier/predecessor word;
- carrier zero at the declared immediate or post-round3 uncompute boundary and
  at return;
- all non-output quantum ancillas zero;
- byte-identical normalized receipt on a direct repeat.

Immediate KILL on the first ordered failure, including:

- `KILL_ONE_CARRIER_INSUFFICIENT` if two residual values or another full-width
  register are simultaneously required;
- `KILL_PREDECESSOR_HISTORY_REQUIRED` if the carrier cannot be cleared from
  `R2` or `R3` plus retained/live state;
- `KILL_RESIDUAL_ORACLE_NONFUNCTIONAL` for a conflicting allowed-key fiber;
- any value, finite-inverse, relative-phase, canary, restoration, cleanup,
  Q/state, or ancilla failure inherited from X009.

## Exact outcome boundary

An exact pass establishes only a Q<=1370 one-carrier rounds-`0..3` prototype
saddle on the frozen corpus. Its measured entropy/effective width names the
next re-descent target; it does not authorize round4, a whole-production splice,
full-circuit evaluation, score/promotion language, provider access, range scan,
hunt, submission, CUDA work, nonce change, or public note.
