# KILL — retained-word splice has no complete production sign source

Resolved: 2026-08-23T09:08:41Z.
Lane: `research/b523-retained-splice-canonical`.
Binding predeclaration:
`.lane/PREDECLARATION-RETAINED-SPLICE-CANONICAL-B523.md`, commit `6217000`.
Frozen parent: `ab578fe491f7d4988cb1dca7191199758178020e`.

## Verdict

**Terminal KILL at the complete NM64 closure gate.** The retained-word splice is
bit-exact on a real, canonical, nonzero production Divide slice covering fused
rounds 2 through 7, but that is only 6 of 696 Divide fused calls and covers 0 of
694 Multiply fused calls. The frozen source has no retained-word sign source
past round 7. Consequently the predeclared complete production splice was not
constructed, the full NM64 fixture is not covered, and Q/T economics cannot be
measured.

The bounded slice is positive evidence, not a candidate and not a score
projection. No second sign decoder, live value-walk carrier, ANF extension,
repair, tuning pass, nonce change, provider, hunt, submission, or public note
was opened.

## Exact bounded result

Command:

```text
SUB4_PP_RETAINED_SPLICE_CANONICAL=1 ./target/release/build_circuit
```

Independent receipt after the compile-only repair:

```text
RSC op_stream_identity=OK ops=12972689 stream_sha256=048c3a42ab1375dc4c67a222ed3ecefbd2602c8fce0ee8a220886c9b904f3c17
RSC P64 classical=0 phase=0 ancilla=0
RSC NM64 fixture nonzero_coeff_lanes=64/64 nonzero_numer_lanes=64/64 per_round_nonzero_coeff=[64, 64, 64, 64, 64, 64] noncanon_boundary_values=0 fixture_sha256=d7d708dc18e02fea2f7f4598098b7c838e7742d5f1933e10a5a47d4b43d31c60
RSC NM64 oracle_sign_vs_production sign_mismatch_lanes=0/64
RSC NM64 closure candidate_phase=0 candidate_ancilla=0 candidate_peak_q=1114 candidate_abi_q=768 candidate_extra_peak_q=346 candidate_total_q=1114 candidate_ops=69199 candidate_emitted_t=12524 candidate_executed_t_per_lane_fwd_and_rev=12123.531 persistent_carrier_bits=0 max_live_sign_bits=1 fixed_oracle_scratch_q=2 verdict=CLOSED
RSC M64 miter boundary_mismatch=0 reference_phase=0 reference_ancilla=0 reference_total_q=606 verdict=MATCH
RSC Gate3 economics NOT_MEASURED reason=no_sign_source_past_round_7
```

The fixture is the actual round-2 entry state captured from the frozen R64
point-add composition. Every lane has a nonzero coefficient and numerator; all
source, target-before, and target-after values at rounds 2..7 are canonical
`< p`. Candidate signs reconstructed from the retained denominator match the
production tape in all 64 lanes. The unchanged forward fused cell followed by
the unchanged inverse fused cell restores coefficient, numerator, denominator,
retained word, sign, two oracle scratch qubits, phase, and ancillas exactly.

The 12,123.531 executed-Toffoli figure is the measured forward-and-reverse
six-round component average per lane. It is not multiplied, extrapolated, or
used as a whole-circuit estimate.

## Complete production support remains exact for the unchanged pair

The inherited full trajectory probe was rerun after the new diagnostic hook:

```text
FUSED_TRAJ P64 classical=0 phase=0 ancilla=0
FUSED_TRAJ calls halve|divide=696 double|multiply=694 other=0 rows=88960
FUSED_TRAJ canonicity noncanon_target_before=0 noncanon_target_after=0 noncanon_source=0
FUSED_TRAJ rows_sha256=798b8c1c2f92b8af4b95a2b2df7ec7a7b7238e8a957614ccda993ccb77d4e63e
FUSED_TRAJ C64 unique_tuples=79205 corpus_sha256=2e3ca70d1879b85ddcaae72fa571424e955a4b92ea3523ac4fa0bc8659ef5126 restore_fail=0 source_fail=0 sign_fail=0 phase_fail=0 ancilla_fail=0 verdict=EXACT_INVERSE_ON_REACHABLE
```

This confirms the arithmetic pair is not the blocker. The missing resource is
the retained-word mechanism that must supply and clear the production sign for
every call without recreating a tape or a second denominator-sized carrier.

The unchanged arbitrary-input negative control also still binds the domain:

```text
signed_mod_add_pm_halve_fused|signed_mod_double_add_pm_fused
restore_fail=3 phase_fail=2 ancilla_fail=0 verdict=NOT_INVERSE
```

No generic `[0,p)` claim is made.

## Protected default

After the bounded closure passed, a fresh absent-flag build reproduced:

```text
emitted operations  12,972,785
ops.bin bytes       50,798,742
ops.bin SHA256      e33245d491a16192068ef7024a2c82375047c17af3c8f802c81066de0568cb0a
```

The diagnostic hook emits no operation and allocates no wire when disarmed.
Both fused cell bodies are unchanged; the source diff adds the gated recorder,
self-check, and build dispatch only.

## Why the full gate is killed

The predeclaration freezes a **complete** retained splice on the R64
Divide/Multiply inputs. Its gate requires every candidate fused call to match
the reference call at the same shot and position. Production contains 1,390
such calls:

```text
Divide   696 fused calls
Multiply 694 fused calls
```

The only exact retained-word oracle present in the source reconstructs signs 1
through 7. Since fused replay begins at round 2, the implemented nonzero splice
can cover six consecutive Divide calls. It cannot supply rounds 8 onward and
does not cover the Multiply traversal. Therefore:

```text
covered Divide calls      6 / 696
covered Multiply calls    0 / 694
complete call coverage    6 / 1390
```

The known literal ANF term counts already grow from 2 terms at early signs to
16,433 terms at sign 14. Extending that enumeration to hundreds of signs is not
the predeclared bounded family. Holding a denominator-derived value-walk
register across replay would add a persistent second denominator carrier,
which the predeclaration explicitly forbids. Either move would open a second
architecture and was not attempted.

Because full exactness is absent, the Q1114 strict ceiling
`T <= 1,049,462` is **not reached for measurement**. Reporting the six-round
Q1114 prototype as a whole-circuit candidate would be false. No full 9,024-shot
candidate evaluation is authorized or useful after this gate fires.

## Gate ledger

| gate | measured outcome | verdict |
|---|---|---|
| frozen source/predeclaration | exact parent `ab578fe`; predecl pushed at `6217000` before model edits | PASS |
| complete NM64 nonzero closure | rounds 2..7 exact and clean, but only 6/1390 production fused calls; no sign source past 7 | **KILL — incomplete fixture coverage** |
| protected default | 12,972,785 ops; 50,798,742 bytes; protected SHA256 exact | PASS control only |
| focused bounded M64 | boundary/reference value/phase/ancilla `0/0/0`; full candidate absent | PASS bounded evidence only |
| Q1114/T economics | no complete candidate exists; no projection permitted | NOT REACHED |
| square/point-add64/full9024 candidate composition | economic exact candidate absent | NOT REACHED |

## Independent implementation audit

The first release build found one Rust type error in the diagnostic-only local
helper: `Simulator` was named without its reader generic. Human-side review
changed that helper to a generic local function, then rebuilt successfully and
reran all receipts above. Human review also added the explicit P64 ancilla
counter; the rerun returned `0`.

`cargo build --release --bin build_circuit --bin eval_circuit` passes. The
repository-wide `cargo fmt --all -- --check` remains non-green on extensive
pre-existing formatting differences outside this lane; no bulk formatter was
run and no unrelated file was changed.

Generated `target/`, `ops.bin`, traces, logs, binaries, scores, and
`results.tsv` rows are excluded from commits.

## Next architecture recommendation (not opened)

The next structural family must solve the sign-source problem directly: one
uniform reversible transducer or pebbling schedule that emits and erases signs
8 through the terminal round from the retained denominator without a resident
round tape or a second denominator-sized carrier. Its first static gate should
price the full sign-production/unproduction cost against Q1114/T1,049,462
before integrating replay cells. Do not revisit the fused inverse or the
`{0,p}` normalization toggle; both are cleared on canonical production support.

## Model receipt

Claude Fable 5 high-effort session
`5dfc35b8-3231-43b3-aa87-fc3ab8dd4852`; exact spend `$8.90274400`:
`claude-fable-5` `$0.08642800`, `claude-opus-4-8` `$6.97751600`, and
`claude-opus-5` `$1.83880000`. Spend was appended to
`/Users/olifreuler/ecdsa-ops/SPEND.md`. The model had no shell, network,
commit, push, provider, hunt, submission, or publication authority.
