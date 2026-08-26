# Ping-pong nonterminal third-passenger support certificate

Date: 2026-08-26

Verdict: `ADMIT_EXACT_THIRD_PASSENGER` for a bounded construction and pricing
phase. This is an exact support certificate, not a production change, score
claim, correctness admission, provider action, or submission authorization.

## Result

At every post-round walk state after round `r >= 1`, the parity-selected low
bit is an affine function of two stable live wires:

```text
r even: v[1] = u[2] XOR tape[1]
r odd:  u[1] = v[2] XOR tape[1]
```

Therefore the existing nonterminal loan of `u[0]` and `v[0]` can, in
principle, loan exactly one additional wire during the replay cell:

```text
r even: CX(u[2], v[1]); CX(tape[1], v[1]); release_clean(v[1])
r odd:  CX(v[2], u[1]); CX(tape[1], u[1]); release_clean(u[1])
```

Reacquire the clean passenger after replay and apply the same two CXs in
reverse order. The controls are not modified by the value walk while the
passenger is released. Replay may use a tape sign transiently, but restores
it before the passenger is reconstructed.

## Exact source binding

- Source checkout:
  `/Users/odin/Documents/coding with codin/ecdsafail-n1-f21-stack-codex`
- Commit: `9525e3271b19f17f218a9776e14f32a1baed52f2`
- Tree: `f425ae5e144445f7aebb15ef022ebf23fbc05149`
- `src/point_add/pingpong_div.rs` SHA-256:
  `67f6b692b1fed3641dad487b062ce0304958b312c4627355e772bc3954eea842`
- `src/point_add/mod.rs` SHA-256:
  `63f9568027fd4ce15523872d124fe374b3d1f1430ae08c62fb31d9ab2b2a3838`
- Exact defaults parsed by the checker: divide/multiply rounds `694/694`,
  divide `r1=335`, multiply `r1=315`, `r2=645`, `peak=1267`,
  `walk_peak=1267`, endpoint fold window `26`.
- At the first inspection the source checkout had one unrelated dirty file,
  `results.tsv`; this lane did not touch it. The source checkout was clean at
  seal, and no production circuit file was modified here.

The source parser also rejects a drifted current loan family: the bound source
must still loan only `u[0]` and `v[0]` before this certificate is applied.

## Exact proof

### Seed at fused round 1

Immediately before fused round 1, `u = p`, `u[1] = 1`, and both walk values
are odd. The source computes `tape[1] = u[1] XOR v[1]`, clears the classical
`u`, copies the arithmetic `v >> 1` into it, and complements by `tape[1]`.
At that point:

```text
u[1] = v[2] XOR tape[1].
```

The remaining fused corrections cannot alter bit 1. The low correction is
`ROUND1_H = 2^31 + 488`, which is `0 mod 4`, and the other correction starts
at bit 255. This proves the odd-round relation at the post-round-1 state. The
argument is unaffected by the truncated high borrow window because it uses
only the two exact low bits.

The `f mod 8` condition is material, not decorative. For secp256k1,
`p = 2^256 - f` with `f = 2^32 + 977 = 1 mod 8`, so
`ROUND1_H = (f - 1)/2 = 0 mod 4`. The reduced countermodel `f=5` changes the
proposed passenger at round 1 and is retained as a negative test.

### Generic-round induction

For any generic round `r >= 2`, call the unchanged operand `S` and the updated
operand `T`. Both are odd and the source sets `s = T[1] XOR S[1]`. Its
complement-sandwich adder computes `C = T + S` when `s=0` and `C = T - S`
when `s=1`, followed by an arithmetic right shift. Exhausting all 16 pairs of
odd three-bit inputs proves both low-bit identities:

```text
C[1] = 1
C[2] = T[2] XOR S[2] XOR S[1].
```

Thus the updated target remains odd and its post-shift bit 1 is
`S[2] XOR T[2] XOR S[1]`.

At the start of round 2, the seed gives the pre-round invariant
`T[2] XOR S[1] = v[2] XOR u[1] = tape[1]`. Consequently the updated target
satisfies `T'[1] = S[2] XOR tape[1]`. Swapping source and target roles for the
next round makes that post-round equality exactly the next pre-round
invariant. Induction proves the parity-switched relation for every `r >= 1`.

Schedule shrink/grow operations only remove or sign-extend top wires. They do
not touch bits 0, 1, or 2. All certified loan checkpoints retain at least 25
walk wires, so the three low wires are present throughout.

This algebra and the complete three-bit truth table are the certificate. The
full-width replay is a source-bound regression/falsifier, not the logical
basis for extrapolating from samples.

## Binder and lifetime coverage

The same post-round walk state is exposed in both directions:

- Divide prefix batch: after round `334`.
- Divide interleaved cells: after rounds `335..645`.
- Multiply interleaved cells: after rounds `645..315`, immediately before
  undoing the corresponding walk round.
- Multiply prefix batch: after round `314`.

That is 312 divide loan sites and 332 multiply loan sites, with 332 unique
round checkpoints `314..645`. Walk widths across those sites range from 154
down to 25 for multiply and 146 down to 25 for divide.

The relation is independent of the replay and walk peak budgets. It therefore
covers both explicitly requested binder configurations:

| configuration | `SUB4_PP_PEAK` | `SUB4_PP_WALK_PEAK` | local profiled Q |
|---|---:|---:|---:|
| current Q1265 | 1267 | 1266 | 1265 |
| exploratory Q1264 | 1266 | 1265 | 1264 |

Read-only local 64-lane profiles on the bound source were clean in both
configurations (`classical_mismatch=0`, `phase=0`, `dirty_qubits=0`). The
current configuration reached Q1265 in `pp_div_replay`; its phase peaks were
1265 (`pp_div_replay`), 1264 (`pp_mul_replay`), and 1265
(`pp_mul_walkback`). The exploratory configuration reached Q1264 in
`pp_div_replay`; all three corresponding phase peaks were 1264. These profiles
only bind the target lifetimes. They do not price the unimplemented third loan.

## Deterministic evidence

The canonical repro is
`pingpong_third_passenger_support.py`; its unit contract is
`test_pingpong_third_passenger_support.py`.

```text
9/9 unit tests PASS
16/16 odd low-bit transition rows, zero violations
scaled p=2^6-9: 54/54 nonzero inputs through 39 rounds
scaled checks: 2,106, zero violations
scaled state digest:
  40ecf35343cc7e39a9cfb34050172a2efdfb71944212890f37f18232b62d156e

production-width deterministic inputs: 4,096
loan rounds per input: 332 (314..645)
support checks: 1,359,872, zero violations
input digest:
  43b56f5f6eff8fc800c18a2c532923708bff44ec076f0abed98956d7b8cd8ed3
checkpoint digest:
  1da23ba23810716395dfbaaed376f88147a669cce5298087099a26ad73fe8d09
```

Deterministic denominators are `SHAKE256(domain || u64_be(index)) mod (p-1)
+ 1`, with domain `pingpong-third-passenger-v1`. The production-width model
executes the bound fused round-0 value map, fused round-1 corrections, exact
generic low-bit recurrence, parsed 694-round schedule/rescale/repair, and every
loan checkpoint. Since the claimed identity depends only on low bits 0..2,
high truncation and sign-extension behavior cannot enter the proof.

### Predeclared falsifier applied

The predeclared stop rule was: two reachable states with the same proposed
reconstructors and different passenger bits kill that relation. The weaker
family using only the other bit 1, current/adjacent tape signs, parity,
direction, and the already-known `u[0]=v[0]=1` is killed at every binder edge
tested:

| round | passenger | matching reconstructor tuple | sample indices | bits |
|---:|---|---|---|---|
| 314 | `v[1]` | `(0,1,0,0,0,1,1)` | 1 / 4 | 0 / 1 |
| 315 | `u[1]` | `(1,0,1,0,1,1,1)` | 0 / 9 | 1 / 0 |
| 334 | `v[1]` | `(1,0,1,0,0,1,1)` | 7 / 13 | 1 / 0 |
| 335 | `u[1]` | `(0,0,0,1,1,1,1)` | 2 / 3 | 0 / 1 |

Tuple order is `(other[1], tape[r-2], tape[r-1], tape[r], parity,
u[0], v[0])`. The repro deterministically emits the complete denominators and
walk-state witnesses. Adding the stable opposite register's bit 2 and using
`tape[1]`, rather than nearby signs, is exactly what resolves these collisions.

## Next bounded construction hypothesis (not implemented here)

Extend the interleaved loan helper with `after_round` and the stable
`tape[1]` control. Keep the existing `u[0]`/`v[0]` releases, then select
`v[1]` with control `u[2]` on even checkpoints or `u[1]` with control `v[2]`
on odd checkpoints. Pass `r1-1` at each prefix-batch call and `r` at each
interleaved call. Require `tape.len() >= 2` and walk width at least 3.

The construction gate should then, in order:

1. Prove RED/GREEN circuit-level clear/reacquire/restore equivalence for both
   parities and all four binder edges (`314`, `315`, `334`, `335`).
2. Confirm that the released wire is actually consumed by the intended replay
   ladder and does not merely become idle allocator headroom.
3. Price current P1267/W1266 and exploratory P1266/W1265 without changing any
   other flag, then test the one-step hypotheses P1268/W1267 and P1267/W1266
   respectively at fixed Q.
4. Run the normal full correctness and value gates before any score or
   submission claim.

No production circuit, provider, prefilter, remote repository, or submission
state was changed while producing this certificate. The unsafe blanket
`SUB4_PP_WALK_TOP_SKIP` path was not enabled or revisited.
