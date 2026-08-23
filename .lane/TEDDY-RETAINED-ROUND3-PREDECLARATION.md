# Teddy retained-denominator round-3 predeclaration

Predeclared: 2026-08-23

Status: `FROZEN_BEFORE_SOURCE_IMPORT_OR_RESULT`.

## One bounded experiment

Extend the exact retained-denominator full-field divide replay witness from
production rounds `0..2` through round `3`. The candidate may use the same one
local sentinel-normalization flag, one shared sign qubit, and the same fixed
two-qubit sign-oracle workspace. The flag must return to zero before it is
reused; there is no second flag, round-indexed carrier, growing transcript, or
retained predecessor state.

This experiment tests one semantic invariant only. It does not optimize widths,
compare windows, chunks, nonce, or score.

## Frozen identities

Checked-out lane before this predeclaration:

- branch: `research/redescent-teddy-1270`;
- HEAD: `3370f66563966152040918cae97a964bacfcc427`;
- tree: `fc60bb168d31a3b75ad2b42f44b06c4a332945ce`;
- current production `pingpong_div.rs` SHA-256:
  `22c4820a9ba3b2356eb785d0d0d452b0939a643cb6c65241706554d19b7df376`;
- current `point_add/mod.rs` SHA-256:
  `c99bd16b67b6716cbfe177227de2ba08db96d3f25b97a832538e6cbbfa3a38f0`;
- `Cargo.toml` / `Cargo.lock` SHA-256:
  `3c80178b08d29a158abb29a7dcb8eefc67c66f60f2c3bd14483b65eeca0740dc` /
  `42ff16919e551891ad1b21821329b116d133194245a0e0734a33573dfe598e07`.

The checked-out production file is the protected X004/clanker lineage. It is
not overwritten for this component experiment. The exact round-`0..2`
semantic witness will be imported as an isolated source module from:

- witness commit: `384823f9c50c4bb450e03770f8451bd4f336674d`;
- witness tree: `88bed584d45d9d0bcc74add7d0bbb070995c1a52`;
- witness parent: `d4f08d26444a5a6bed7dae28570f854e0f036995`;
- witness `pingpong_div.rs` SHA-256:
  `abe9176948afd7d9d41addda977f356f1fdb6b1d12c7ee14f90f82424c378550`;
- witness evidence SHA-256:
  `a21536fa7df0b86fb8ddd9446614dd4cf3732cb3c7f47528f1b74c6f4ed92b96`;
- promoted production source bound by the witness:
  `a9af194d737d0d7cf5c7e252e0cb5e59affbb10a`.

The imported module must remain opt-in and exit before production tail
construction. Default production circuit emission must remain byte-identical.

## Frozen 4,096-denominator corpus

The corpus is the exact round-`0..2` witness domain in the same order: eight
high prefixes, each followed by all 512 low-nine-bit residues. With
`p = 2^256 - 2^32 - 977`, `stride = p >> 4`, and `state = 0..7`:

```text
anchor[state] = wrapping_u256(stride * (state + 1))
base[state] = ((anchor[state] >> 12) << 12) + (state << 9)
denominator[state,residue] = base[state] + residue, residue = 0..511
```

- complete ordered fixture:
  `.lane/fixtures/TEDDY-ROUND3-DENOMINATORS.hex`;
- count / unique count: `4096 / 4096`;
- fixture SHA-256:
  `9cbe05c8d2a2865318da958ce825163b9ac3052c142abd08c4026fff43076dbe`;
- ordered eight-base SHA-256:
  `307bdf64649d16c32e1c0ba89f4ed1806fa7a473f78b29507b551616eeaf3eab`;
- generator SHA-256:
  `e354fef15e485a61986ffcface8fa7165c8aa32e67e725ca5596f661994b1b89`;
- first / last denominator:
  `0fffffffffffffffffffffffffffffffffffffffffffffffffffffffeffff000` /
  `7fffffffffffffffffffffffffffffffffffffffffffffffffffffff7fffffff`.

No denominator may be added, removed, reordered, or replaced after this commit.
The independent reference obtains signs `0..3` from the exact production walk,
applies the same production replay cells, and reverses the walk exactly.

## Frozen invariant and kill gates

The candidate passes only if all 4,096 denominators satisfy every condition:

- denominator and retained denominator are preserved exactly;
- candidate and independent production-walk reference replay states match after
  every declared round boundary and at the terminal checkpoint;
- at most one shared sign is live;
- the one normalization flag has peak count one, returns to zero between uses,
  and is zero at the terminal checkpoint;
- sign, two oracle scratch qubits, replay scratch, and normalization flag are
  zero at every declared cleanup checkpoint;
- persistent carrier bits remain zero and retained state does not grow with the
  round number;
- phase and ancilla debt are exactly zero.

Immediate `KILL` conditions are: any concurrent second normalization flag,
width or retained-state growth, an unavailable predecessor dependency, a dirty
sign/scratch/flag, nonzero phase, or nonzero ancilla. A failing case stops the
experiment; no repair ladder or second flag is authorized.

## Prototype Q/T debt price

The frozen round-`0..2` witness has ABI Q768, fixed base Q1028, candidate peak
Q1114, emitted T583, and average executed T550.247. Its explicit Q debt above
the ABI is 346: retained denominator256 + shared sign1 + fixed oracle scratch2
+ one local flag1 + at most86 transient replay qubits.

Round `3` receives no additional persistent-Q allowance: candidate peak must
remain at or below Q1114 and the replay transient must not exceed86. For the
bounded semantic prototype, one additional production cell plus sign-oracle and
normalization recomputation is priced at no more than +700 emitted T and +650
average executed T, for total ceilings T1283 emitted and T1200.247 executed.
These are research-debt ceilings, not a score or promotion gate.

If the semantic invariant passes, record exact per-round/cumulative T and name
the cheapest production divide-replay slice or composition that this result can
bind. Do not extend to round4, optimize, grind, hunt, or touch a provider.

## Commands and scope

The only authorized execution is a local CPU release build of the opt-in
component self-test plus a deliberate source-bound negative. No provider,
range, hunt, submission, CUDA, public note, or protected-leader mutation is in
scope.
