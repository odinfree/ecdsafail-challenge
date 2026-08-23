# Teddy retained replay nonzero-ABI X008 receipt

Date: 2026-08-23

Status: `KILL_PHASE_DEBT_REFERENCE`; bounded experiment complete.

## Verdict

X008 stops at its first authority gate. The unchanged raw production-forward
reference is not absolute-phase clean on the frozen nonzero replay ABI. In the
first 64-seed SIMD batch, phase becomes nonzero after production replay round 2:

```text
TEDDY_NONZERO_ABI FAIL class=KILL_PHASE_DEBT_REFERENCE stage=round2
denominator_index=0 seed_index=0 denominator=1 coefficient=0 numerator=1
phase_mask=000000400000004f
```

The complete observed phase mask in that first batch covers seed indices
`{0,1,2,3,6,38}`. Seed 0 belongs to the production entry class
`coefficient=0,numerator!=0`, so this is not confined to the stronger
nonzero-coefficient stress class.

The predeclared contract required the isolated raw reference to have phase
zero. Therefore the finite-inverse table and retained-candidate comparison were
not run. There is no candidate parity result, no rounds-1-through-3 production
splice claim, and no repair ladder.

This does not overturn X007's exact all-zero-seed result. It kills only X008's
stronger absolute-phase nonzero-ABI closure. A future relative-phase experiment
must be separately predeclared and must compare the complete candidate and raw
reference phase masks exactly while disclosing this inherited raw phase debt.

## Frozen identities

- X008 implementation base before semantic source edits:
  `d3ec4604bb9e135f8054b5509ebd8514410ebb94`.
- Base tree: `fbe0685113cbfd7a516be3817227dfa7e918f50b`.
- Preserved production `src/point_add/pingpong_div.rs` SHA-256:
  `22c4820a9ba3b2356eb785d0d0d452b0939a643cb6c65241706554d19b7df376`.
- Frozen predeclaration SHA-256:
  `89682e682625d24570908707c99713bc8f6f7c140cc6bf6553bd344976a8ad6a`.
- Frozen 4,096-row corpus SHA-256:
  `53b06714ffdf079be23b2d3e1d25706c0d2853ab08d13345588f9a505c9409b0`.
- Ordered denominator SHA-256:
  `bd1c937e2aa188106bc156929b19f536f6b5933510221371e42d1cbaeedeea2d`.
- Ordered seed-pair SHA-256:
  `4a48e4569fd7ad7df277e9624f06a58b2b453cf8629c76eb07db24052d305d39`.
- Corpus generator SHA-256:
  `b23cb5665536738502a658228f9b0cb51d7b926b899abe381011f7a0c53a8f96`.
- X008 opt-in source SHA-256 before this evidence file:
  `fe6ca1a784291c50fb2a0d1a3ec67d6bb4fd785862e23214643bacee44767262`.
- X008 gate source `src/point_add/mod.rs` SHA-256 before this evidence file:
  `d014064fdb557002f6c30574ed9a37fae9ca269f2df7416a497425d1cabcf0ff`.
- Local release `build_circuit` binary SHA-256:
  `c0d2bd907332ee083dde40bd80d5c1cdd0302d195761f7ae04f93aeae54179b4`.
- Toolchain: `rustc 1.93.0 (254b59607 2026-01-19) (Homebrew)`;
  `cargo 1.93.0 (Homebrew)`.

No binary or execution log is tracked. The opt-in gate leaves
`src/point_add/pingpong_div.rs` untouched and returns before default artifact
emission.

## Prototype price before the semantic gate

The miter builds both sides before simulation, so the candidate debt is known
even though parity is blocked:

```text
candidate ABI Q       768
candidate peak Q      1114
candidate extra Q     346
candidate peak phase  teddy_nonzero_round2_signed_mod_add_pm_halve_fused
candidate operations  13659
candidate emitted T   960
round emitted T       0:65, 1:141, 2:377, 3:377
normalization flags   1
concurrent flags      0
persistent carriers   0

reference ABI Q       768
reference peak Q      1546
reference operations  40605
reference emitted T   4010
```

Candidate executed T is intentionally unreported: no candidate batch ran.
The round-2 fused replay cell remains the candidate Q1114 binder, and the
frozen Q/emitted-T caps pass.

## Exact commands and deterministic receipt

Release compile:

```text
cargo build --release --bin build_circuit
```

It exits 0 with three pre-existing warnings in unrelated source.

Semantic command, run from a fresh temporary directory so its ignored
`ops.bin` cannot touch the worktree:

```text
SUB4_TEDDY_NONZERO_ABI_SELFTEST=1 \
/Users/olifreuler/Documents/Codex/2026-08-21/par/work/redescent-teddy-1270/target/release/build_circuit
```

It exits 101 at the declared phase gate after raw reference round 2. Two direct
reruns produced identical `TEDDY_` receipt lines, each SHA-256:
`46762dce4f3c7a907e6e2277dc4254e108bb6cc79e5802b1d944fa2d01ed9878`.

## Scope closure

X008 performed no provider access, range scan, hunt, submission, public note,
nonce change, CUDA work, protected-source mutation, round-4 extension, or
whole-circuit claim.
