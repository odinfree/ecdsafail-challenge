# Teddy retained-denominator round-3 receipt

Updated: 2026-08-23

Status: `EXACT_COMPONENT_HOLD`.

## Verdict

The frozen X007 semantic invariant survives. The retained-denominator
full-field divide-replay witness extends from production rounds `0..2` through
round `3` over all 4,096 predeclared denominators at the same Q1114 peak. The
same one local normalization flag is used around round 2 only. Round 3 is
flag-free: it reads canonical `y=0` as its add source and only halves the
`x in {0,p}` continuation target, so the production fused halve maps `p -> p`
without phase debt.

No kill gate fired. There is no second flag, growing carrier, unavailable
predecessor, dirty sign/scratch/flag, phase debt, or ancilla debt. This remains
a zero-seed component HOLD, not a whole divide replacement or score claim.

Teddy Pender receives the architectural credit: the retained-word route and
the bounded Burn-the-House-Down falsifier discipline are the reason this
component exists.

## Frozen identities and implementation isolation

- Worktree / branch:
  `/Users/olifreuler/Documents/Codex/2026-08-21/par/work/redescent-teddy-1270` /
  `research/redescent-teddy-1270`.
- Checked-out base before X007: `3370f66563966152040918cae97a964bacfcc427`,
  tree `fc60bb168d31a3b75ad2b42f44b06c4a332945ce`.
- Frozen predeclaration commit:
  `4b67b215442ff88dc32c011be26599783888ef40`.
- Burn doctrine SHA-256:
  `4b478d96237dc221cc9242250eb4232829e9050f01d0976d347f58d24f2a67a4`.
- Preserved production `src/point_add/pingpong_div.rs` SHA-256:
  `22c4820a9ba3b2356eb785d0d0d452b0939a643cb6c65241706554d19b7df376`.
- Exact rounds-`0..2` witness commit / source SHA-256:
  `384823f9c50c4bb450e03770f8451bd4f336674d` /
  `abe9176948afd7d9d41addda977f356f1fdb6b1d12c7ee14f90f82424c378550`.
- Isolated rounds-`0..3` module:
  `src/point_add/pingpong_retained_round3.rs`, SHA-256
  `13e8d210e85be9f9ad8397b411c302941ea00eadb4a971e2cd5232e4c3494680`.
- Its isolated diagnostic support module:
  `src/point_add/pp_profile.rs`, SHA-256
  `a16a91200b1b851340a10e05203b85c5c262ed7d1a4252023ddf17b4bb2fbd60`.
- Imported implementation provenance: local independent derivation
  `d5b53ff2b361f890608d210bc87342efeeda1a96`. It was inspected only after
  X007's source, corpus, limits, and kill gates were pushed. This lane compiled
  and reran every result below.
- Opt-in gate: `SUB4_TEDDY_RETAINED_ROUND3_SELFTEST=1`. With the gate absent,
  the checked-out production emitter still calls the original
  `pingpong_div::build_pingpong_point_add` path.

The ordinary release build before and after the isolated import emitted
exactly 15,730,117 operations. Both artifacts were 61,944,467 bytes and had
SHA-256
`843558da6f504e3f8f2f41cae1edeccdf0cfed9e0dc216f8e880ebc1752e7b75`.
The release self-test binary used below had SHA-256
`ae6810ed6201c4724d08f5b3f7c4a28e3778d71dcfcabcb0abf828f575ae5279`.
The generated binary and operation files are not committed.

## Frozen complete corpus

- Fixture: `.lane/fixtures/TEDDY-ROUND3-DENOMINATORS.hex`.
- Count / unique count: `4096 / 4096`.
- Layout: eight high prefixes times all 512 low-nine-bit residues, in the
  exact predeclared order.
- Fixture SHA-256:
  `9cbe05c8d2a2865318da958ce825163b9ac3052c142abd08c4026fff43076dbe`.
- Ordered base SHA-256:
  `307bdf64649d16c32e1c0ba89f4ed1806fa7a473f78b29507b551616eeaf3eab`.
- Generator SHA-256:
  `e354fef15e485a61986ffcface8fa7165c8aa32e67e725ca5596f661994b1b89`.

The candidate and reference independently consume the same formula frozen in
the fixture. The reference obtains signs 0 through 3 from the exact production
walk, runs the same production replay cells, and reverses the walk.

## Exact result

Command:

```text
SUB4_TEDDY_RETAINED_ROUND3_SELFTEST=1 target/release/build_circuit
```

Receipt:

```text
TEDDY_RETAINED_FULL_REPLAY_NORMALIZED PASS rounds=0..3
reconstructed_signs=1..3 lanes=4096 low_residues=512 high_prefixes=8
candidate_peak_q=1114 candidate_abi_q=768 candidate_extra_peak_q=346
candidate_total_q=1114 candidate_classical_bits=925
candidate_ops=13659 candidate_emitted_t=960
candidate_round_emitted_t=0:65,1:141,2:377,3:377
candidate_executed_t=894.054
reference_peak_q=1546 reference_abi_q=768 reference_total_q=1546
reference_classical_bits=2967 reference_ops=41110
reference_emitted_t=4010 reference_executed_t=3945.219
denominator_preserved=1 retained_word_preserved=1 replay_state_match=1
normalization_flag_peak=1 normalization_flag_final=0
normalization_flag_cleared_before_sign=1 concurrent_normalization_flags=0
normalization_toggle_rounds=2 round3_flag_free=1
phase=0 ancilla=0 persistent_carrier_bits=0 max_live_sign_bits=1
fixed_oracle_scratch_q=2
```

Every round checkpoint asserts the shared sign, both oracle scratch qubits,
the one flag, retained denominator, and phase. Toggle-in boundaries additionally
assert canonical replay registers. Terminal checking clears declared output
registers and proves every other qubit zero. Two direct reruns produced
byte-identical stdout/stderr receipts at SHA-256
`79c6d568e6a7a772aa3deb7696114421d9dff92fb1392a98e987d8bf2fe7a9e6`.

## Required negative and minimality control

Raw source-bound negative:

```text
SUB4_TEDDY_RETAINED_ROUND3_SELFTEST=1 \
SUB4_PP_RETAINED_FULL_REPLAY_PHASE_PROBE=1 \
target/release/build_circuit
```

It exits 101 at batch 0 after round 2 with nonzero phase
`220407001544196359`. This binds the round-2 sentinel normalization; the raw
`p` sentinel cannot be used as the fused-add source.

The same single flag was deliberately toggled around round 3 with
`SUB4_PP_R3_FORCE_TOGGLE=1`. It remains exact at Q1114/T960/T894.054 and all
cleanup counters stay zero, but candidate operations rise `13659 -> 14167`.
Those 508 extra linear operations buy no Q, T, or semantic improvement, so the
round-3 toggle is killed as unnecessary. This is not a second flag and never
overlaps the shared sign.

## Prototype debt and production binder

Relative to the frozen rounds-`0..2` witness:

| quantity | rounds 0..2 | rounds 0..3 | delta | frozen cap |
|---|---:|---:|---:|---:|
| peak Q | 1114 | 1114 | 0 | 1114 |
| emitted T | 583 | 960 | +377 | 1283 |
| average executed T | 550.247 | 894.054 | +343.807 | 1200.247 |
| operations | 8622 | 13659 | +5037 | diagnostic only |

The Q debt remains exactly 346 above ABI Q768: retained denominator 256,
shared sign 1, fixed oracle scratch 2, one local flag 1, and at most 86
transient replay qubits. Round 3 adds no retained state or peak width.

The cheapest named production divide-replay binder is the round-2
`replay_halving_round -> signed_mod_add_pm_halve_fused` cell: it first occupies
the 86 transient qubits that bind Q1114. The immediately following flag-free
round-3 cell reuses the same space and adds +377 emitted / +343.807 average
executed T at +0Q. Therefore the exact composition object bound by X007 is the
rounds-`0..3` zero-seed divide prefix with one atomic round-2 sentinel toggle;
there is no cheaper round-3 normalization variant.

## Scope boundary

This prefix initializes both coefficient registers to zero. It proves exact
sentinel bookkeeping, sign reconstruction, and production-cell cleanup on the
frozen complete census; it does not exercise a live nonzero numerator. The
final `{0,p}` branch assertion also passed the complete census but may encode a
corpus-specific identity. A production splice still requires exact nonzero-
numerator ABI closure before any global Q/T composition claim.

X007 stops here. No round 4, optimization sweep, nonce change, provider,
range, hunt, submission, or public note was opened.
