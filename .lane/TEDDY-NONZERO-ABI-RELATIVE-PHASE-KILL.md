# Teddy retained replay relative-phase ABI X009 receipt

Date: 2026-08-23

Status: `KILL_NONZERO_NUMERATOR_ABI`; bounded experiment complete.

## Verdict

X009 stops at the first candidate value mismatch. The retained candidate and
unchanged raw production reference match coefficient/numerator continuation
and complete phase masks through rounds 0 and 1 in the first denominator
batch. After round 2, every one of the 64 frozen seed lanes has a value
mismatch (`mismatch_mask=ffffffffffffffff`). The first failing lane is the
narrow production entry ABI, not the stronger stress class:

```text
denominator_index  0
seed_index         0
seed_class         production
denominator        1
input coefficient  0
input numerator    1

candidate coefficient
bfffffffffffffffffffffffffffffffffffffffffffffffffefffff3ffffd23
reference coefficient
bfffffffffffffffffffffffffffffffffffffffffffffffffefffff3ffffd23

candidate numerator
2000000000000000000000000000000000000000000000000007fffedffffe86
reference numerator
6000000000000000000000000000000000000000000000000017ffff9ffffe92
```

The candidate coefficient is exact at the failing checkpoint, but its
numerator is not. This kills X007's `T;R2;T` sentinel normalization as a
nonzero-numerator production-ABI transducer. It was exact only on X007's frozen
all-zero replay seed.

Per the predeclared gate order, round-2 relative phase is not evaluated after a
value failure. Round 3, candidate terminal cleanup, the remaining 63
denominators, and a whole-production splice are not run and are not claimed.

## Frozen identities

- Original X009 predeclaration base:
  `85f52c9a9f1416542adf2084ef9b0a1b48c06f50`, tree
  `a4ebb1eb710980aa960a0557141df10490e95134`.
- Pre-semantic cleanup-reset amendment:
  `d0f51bf60bec127a80a225c9ee4eec37f72fcd84`, tree
  `037743a82001969bd35044bfca9cc9a48b87eab7`.
- Amended X009 predeclaration SHA-256:
  `d56243bf1c3139c9a51a1191d1ea017d96ff6667d32ee626705b12e1b6de7962`.
- Preserved production `src/point_add/pingpong_div.rs` SHA-256:
  `22c4820a9ba3b2356eb785d0d0d452b0939a643cb6c65241706554d19b7df376`.
- X009 opt-in source SHA-256 before this evidence file:
  `071699cc95dd3e09b95f9985f983d497399f17ec8c2efa527a073aa0510d66c5`.
- X009 env-gate source SHA-256 before this evidence file:
  `d3cee3c036e1b4f83139a3fdd9da6b29f158cd9fc00a7dbe9567d34d1b8088df`.
- Frozen corpus SHA-256:
  `53b06714ffdf079be23b2d3e1d25706c0d2853ab08d13345588f9a505c9409b0`.
- Ordered denominator/seed hashes:
  `bd1c937e2aa188106bc156929b19f536f6b5933510221371e42d1cbaeedeea2d` /
  `4a48e4569fd7ad7df277e9624f06a58b2b453cf8629c76eb07db24052d305d39`.
- Local release binary SHA-256:
  `5017438d446da0d7400970df5afa479490757099a70929b9fdfcb2c25d159ebc`.
- Toolchain: `rustc 1.93.0 (254b59607 2026-01-19) (Homebrew)`;
  `cargo 1.93.0 (Homebrew)`.

No binary or execution log is tracked. Protected production
`pingpong_div.rs` is unchanged.

## Exact gate coverage

Passed before the KILL:

- release compile;
- frozen corpus row count, Cartesian order, uniqueness, range, and seed-class
  checks;
- candidate Q1114 on ABI768, operations13,659, emitted T960 split
  `65/141/377/377`, round2 fused-cell binder, one flag, concurrent flags0,
  persistent carrier0;
- ordered candidate/reference stochastic replay structure: 1,866 shared
  `Hmr`/`R` events; exact inherited candidate cleanup sequence of 260 `R` and
  zero `Hmr`; reference walk stochastic prefix2,053 events;
- raw reference walk phase zero, exact X008 round-2 canary
  `000000400000004f`, raw rounds0..3 continuation for denominator0,
  collision-free64-seed forward image, finite inverse64/64, denominator
  restoration, cleanup phase preservation, and non-output ancilla cleanup;
- retained signs1 and2 equal raw walk signs; candidate denominator/retained
  word preserved; sign/scratch/flag zero through round2;
- candidate/reference coefficient/numerator and complete phase masks exact after
  rounds0 and1.

Failed:

- round2 coefficient/numerator continuation, all64/64 lanes in denominator0
  batch; first row is production seed0 `(d,c,n)=(1,0,1)`.

Not run:

- round2 phase comparison after the value failure;
- candidate round3 or terminal cleanup;
- denominators1..63, so no complete4,096-row candidate result;
- executed-T average, whole-production splice, round4, or full circuit.

## Commands and determinism

```text
cargo build --release --bin build_circuit
```

```text
SUB4_TEDDY_NONZERO_ABI_RELATIVE_SELFTEST=1 \
/Users/olifreuler/Documents/Codex/2026-08-21/par/work/redescent-teddy-1270/target/release/build_circuit
```

The compile exits 0 with three pre-existing unrelated warnings. The semantic
command exits101 at the declared round-2 value gate. Two direct reruns produced
byte-identical normalized `TEDDY_` lines, SHA-256:
`0563479d2663232a2e8291c0184a8be9d9ac414be69ff246042e321e83675591`.

## Scope closure

X009 authorizes no production splice. It performed no provider access, range
scan, hunt, submission, public note, CUDA work, nonce change, protected-source
mutation, round-4 extension, or full-circuit claim.
