# Final-Add Carry-to-Fold Handoff — Terminal Report

## Verdict

`HARD_NACK_CARRY_HANDOFF_FAMILY`

Every permitted route crosses one of two checked walls. Below the retained-rank
threshold, exact cleanup of the final-carry HMR phase cannot save enough
nonlinear work. At or above that threshold, even a deliberately optimistic
lifetime relaxation exceeds Q1266 before dirty-host conversion or any other
added nonlinear cost is charged.

This verdict is scoped only to rewrites of the final-chunk carry publication
and its selector/fold/cleanup interface in
`signed_mod_add_pm_halve_fused` and
`signed_mod_double_add_pm_fused`. It does not rule out schedule, window, round,
configuration, frame, or other structural changes, all of which were outside
this contract.

## Exact binding and receipts

| Item | Bound value |
|---|---|
| Source commit | `522d00296ab014b0f4d128915b53851516f17f4d` |
| Source tree | `eab2326ce33549eceeb5c10aa64eae33f148b0ac` |
| Active `pingpong_div.rs` blob | `f4399563b1fe8c4beee568027ebf52df252e7555` |
| Candidate runtime | `SUB4_PP_ROUNDS=694`, `SUB4_PP_ROUNDS_MUL=693` |
| Calls | 692 divide + 691 multiply = 1,383 cells |
| Fold geometry | divide 54 / multiply 53; fold-carry wires 51 / 50 |
| Exact baseline operation artifact | 12,553,305 ops; 45,725,252 bytes; SHA-256 `a4995dc4be4b7b314853d379941141b3b5753110412c07e8a2bc5d097d218ed1` |
| Baseline peak | Q1266 at op 2,423,219 in `pp_div_replay` |
| B0 log | SHA-256 `4df1efc63e9c4a0dedb2bb6dcf2367a615d2a2bde0286a9153f93703c6fb95a5` |
| Static census log | SHA-256 `6a66c3af15cdc21a455cbc7068c4810dfb4f3b9a9ca037ee47c355cdd241a4fc` |
| Census build stdout | SHA-256 `b8ad87415fdce89362a035e5d415afd4b2e0934cd68c08b197352bfeb51280fa` |

The env-gated static-census patch contains only active-count reads and
diagnostic output and emits zero builder operations. Its generated operation
artifact exactly matches the bound reference hash above. The patch is retained
only as a reproducibility artifact; it applies cleanly to the exact source, and
the active Rust source has been restored byte-for-byte.

## Route closure

| Route | Status | Strongest checked falsifier |
|---|---|---|
| R1: retained top-carry suffix | KILLED | The exact-local retained-chain candidate is value-, phase-, ancilla-, and inverse-clean, but literal retention fits 0/1,383 cells. Its minimum exact peak is Q1288 and maximum Q1320. At the three-CCX economic threshold, the perfect-host relaxation is still Q1379 divide / Q1376 multiply. |
| R2: minimal selector publication | KILLED | Divide parity-zero selectors have rank zero in overflow on both signs, with exact secp witnesses. Multiply can decode `add_out = plus_f XOR doubled_out XOR minus_f`, but one complementary `doubled_out XOR add_out` rank remains after quotient cleanup. |
| R3: nonlinear/lifetime escape | KILLED | The exact 22-bit phase predicate restricts to `AND(x0..x21)`, whose 21-AND lower bound matches the source comparator. Retaining fewer than 237 predecessor ranks can save at most two CCX per cell, below the 1,500-T target; retaining 237 or more fails Q even under perfect dirty-host replacement. |

## Phase-aware and exact-transfer evidence

The reduced baseline miter exhausts widths 5 through 9 over all canonical
source/target pairs, sign arms, independent HMR outcomes, and forward plus
inverse cleanup:

- 1,040,532 basis cases;
- 15,868,400 phase coefficients;
- zero value, selector, fold-cleanup, or inverse mismatches;
- no uncovered sign or measurement arm.

The constructive exact-local retained-chain miter covers the same 1,040,532
basis cases and 8,974,732 independent carry-HMR coefficients, with zero value,
phase, ancilla, or inverse mismatches and final candidate phase zero. Thus the
construction really can remove the source's intentional
`overflow XOR cmp22` residual; the rejection is a lifetime/economic result, not
a classical- or phase-correctness failure.

The production-source transfer then closes the small-width gap:

- all 4,194,304 assignments of the exact 22-bit top window were checked at
  canonical secp256k1 source/target embeddings for both sites;
- comparison, canonical-range, selector, parity, quotient, and correction
  mismatches were all zero;
- divide embeds missing carry as `AND22` while all four low selectors are zero;
- multiply embeds the complementary carrier as `1 XOR AND22` at fixed
  sign 0, quotient 1, correction `+f`, and the disjoint fold width 53;
- the independent exact multiply transfer covers all eight
  `(sign, doubled_out, add_out)` arms and satisfies
  `doubled_out XOR add_out = post_fold[0] XOR sign XOR source[0]` with zero
  mismatches.

For the comparator restriction, set `u0=0`, `v0=x0`, and for each `i>=1`,
`ui=1 XOR xi`, `vi=0`. Then `[u<v]=AND(x0..x[n-1])`. Exhaustive widths 5
through 9 cover 992 restriction cases with zero mismatches. In an XOR/AND
(Clifford/Toffoli Boolean) circuit, producing the n-variable monomial requires
at least `n-1` binary nonlinear merges, so the exact width-22 lower bound is 21
CCX: the existing ripple is optimal within the permitted model.

## T economics and lifetime census

The source's final 22-bit repair uses 21 CCX under one quantum condition, or
10.5 average executed T per cell and 14,521.5 across all 1,383 cells.

- Uniform all-site eligibility starts at three saved CCX per cell: 2,074.5
  gross average T, leaving at most 574.5 for every added nonlinear operation.
- Optimizing only divide or only multiply starts at five saved CCX per cell:
  1,730.0 or 1,727.5 gross average T respectively.
- A retained suffix of `k` predecessor ranks leaves an exact boundary predicate
  over `256-k` bits and therefore needs at least `255-k` nonlinear gates.
  `k=236` saves at most two CCX/cell, only 1,383 gross average T. `k=237`
  first reaches three; `k=239` first reaches the five required for one site.

The exact static census covers every cell and charges every coexisting retained
carry:

| Site | Cells | Final chunk width | Fold entry | Fold peak | Cell peak | Literal retained peak | Fits Q1266 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Divide | 692 | 51..127 | 1142..1213 | 1193..1264 | 1234..1265 | 1289..1320 | 0 cells |
| Multiply | 691 | 51..128 | 1139..1213 | 1189..1263 | 1234..1265 | 1288..1319 | 0 cells |

The strongest dirty-host relaxation assumes that all 51 divide or 50 multiply
fold-carry hosts replace retained storage at zero conversion cost. Even then,
`k=237` peaks at Q1379/Q1376, and the one-site `k=239` case peaks at
Q1381/Q1378. These are lower bounds on a real implementation's peak, and all
exceed Q1266 before added nonlinear cleanup is charged.

## Verification and artifacts

Final local commands:

```text
git apply --check --ignore-space-change src/point_add/memory/repro/final_carry_handoff_static_census.patch
python3 -m unittest -v src/point_add/memory/repro/test_final_carry_handoff.py
env SUB4_PP_ROUNDS=694 SUB4_PP_ROUNDS_MUL=693 cargo build --locked --offline
```

Results: the patch check passes; all 15 focused tests pass in 19.960 seconds;
the locked offline Rust build passes with three inherited warnings. No full
evaluator, provider, network/fetch, push, submission, or official artifact was
used or changed.

Deterministic packet hashes:

| Artifact | SHA-256 |
|---|---|
| `final_carry_handoff.py` | `6c0aa4426dd527eae7d2936840d38032c76ca5a35836f1f610cfeff6c9e8c1c2` |
| `test_final_carry_handoff.py` | `76c8e871959cddf9f9b04d7e6634f6684b1988ffc41db6f66795c6380d48361e` |
| `final_carry_handoff_inventory.json` | `85e025ce84412003d0c60c99bbd13a2b5cb0f2469c921ae43ac3437328a80c4b` |
| `final_carry_handoff_evidence.json` | `5862c7dd7e42fa76cd34f9296990989aa4a1d4741519e0078315e4e47be49cf7` |
| `final_carry_handoff_static_census.patch` | `3d95f32eaef0bab18e3c0408d0004484cfdf55c8cd53a99072989bdd1a9cd668` |

The cheapest next gate is an independent, read-only REFUTE audit of this
committed packet against the contract traps. A sustained counterexample should
reopen only the affected route; otherwise this bounded family remains closed.
