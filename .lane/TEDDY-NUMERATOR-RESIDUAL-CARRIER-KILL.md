# Teddy numerator-residual carrier X010 terminal KILL

Closed: 2026-08-23

Verdict: `KILL_Q_CAP`.

## Exact scope and identity

This is the sole Stage-B construction selected by
`.lane/TEDDY-NUMERATOR-RESIDUAL-DEPENDENCY.md`. It implements the declared
direct source-cell residual expression, one modular correction, and its paired
immediate inverse. It does not try a lookup, alternate arithmetic formula,
second carrier, predecessor copy, or repair ladder.

- Stage-B base commit:
  `f9cc5fed8ba8dc45a81192142fb1d5533aeb18c7`.
- Stage-B base tree:
  `0c04961b85e483cdd619b02753cc0eb116da3b5f`.
- Production source SHA-256, unchanged:
  `22c4820a9ba3b2356eb785d0d0d452b0939a643cb6c65241706554d19b7df376`.
- Terminal opt-in construction module SHA-256:
  `c01fc293fd450a57c3ef3bb0e0810578f0c7a33fc7855ef847b18edec9caf041`.
- Terminal env-gate source SHA-256:
  `3670583800b82b467ca07a6fe256ec49779bb4e12ab91cddfd35d83e79bc9e5f`.
- Frozen corpus SHA-256:
  `53b06714ffdf079be23b2d3e1d25706c0d2853ab08d13345588f9a505c9409b0`.
- Predeclaration SHA-256:
  `cbf69ce1fc934bd07eabd5ba13af40ecec9fc8feb863154da5c0d93798f846f7`.
- Dependency-gate SHA-256:
  `4aafffd18a4bbdc167b3e21ae76a6e230d622a55ea39eabca9d3d989fcf3d4ba`.

Protected production remains untouched. The terminal source is reachable only
through `SUB4_TEDDY_NUMERATOR_RESIDUAL_CARRIER_SELFTEST=1`.

## Exact build and KILL

Commands from the worktree root:

```text
cargo build --release --bin build_circuit
SUB4_TEDDY_NUMERATOR_RESIDUAL_CARRIER_SELFTEST=1 target/release/build_circuit
```

The release build succeeds with the same three unrelated pre-existing
warnings. The opt-in selfcheck exits101 at the frozen static-Q gate before the
simulator receives any row.

```text
TEDDY_NUMERATOR_RESIDUAL_CARRIER_BUILD rows=4096 candidate_abi_q=768 candidate_base_q=1284 candidate_peak_q=1544 candidate_peak_phase=teddy_numerator_residual_correct candidate_q_cap=1370 candidate_ops=43584 candidate_emitted_t=4646 candidate_round_emitted_t=0:65,1:141,2:4063,3:377 carrier_stage_emitted_t=compute:819,correct:2048,uncompute:819 carrier_cumulative_peak_q=before_compute:1370,after_compute:1371,after_correct:1544,after_uncompute:1544 carrier_bits=256 carrier_count=1 predecessor_bits=0 second_carrier_bits=0 normalization_flags=1 concurrent_flags=0 correction_primitive=mod_add_qq_lowq
TEDDY_NUMERATOR_RESIDUAL_CARRIER FAIL class=KILL_Q_CAP candidate_peak_q=1544 candidate_peak_phase=teddy_numerator_residual_correct candidate_q_cap=1370 excess_q=174 semantic_rows_run=0 relative_phase_rows_run=0 cleanup_rows_run=0 second_construction_authorized=0
```

Two direct executions return the same two-line receipt byte-for-byte at
SHA-256
`148513dcd03efa7f3189b07a99c4897845d7458e0dfa58a6585bd4b0b91934e2`.
The release executable SHA-256 for those runs is
`694fbde59633d509fcfb031877e9bd4e4dd685f17081e7e00f97765a86198014`.
Binaries and raw logs remain outside Git.

## Exact debt and first failure

The allowed base is exactly Q1284:

```text
ABI768 + retained256 + sign1 + scratch2 + normalization flag1
+ residual carrier256 = Q1284.
```

The inherited round-2 cell reaches the declared Q1370 boundary before carrier
computation. The exact source-cell residual compute then reaches Q1371, so the
earliest chronological overage is one qubit. The modular correction requires
260 transient qubits over Q1284 and owns the final Q1544 peak, 174 above the
hard cap. Immediate uncompute adds no higher peak.

The full static construction would contain43,584 operations and4,646 emitted
T, versus X009/X007's13,659 operations and960 emitted T: debt29,925 operations
and3,686 emitted T. That entire T debt is in round2, split819 compute,2,048
correction,819 uncompute. T is only a static prototype price because no row was
executed.

## Gate boundary

Per the frozen order, Q1371 is an immediate KILL. Therefore:

- residual-value equality is not run, even for row0;
- candidate/raw relative phase is not run after the construction;
- carrier/sign/scratch/flag/ancilla cleanup is not run;
- no Stage-B executed-T average exists;
- the Stage-A dependency and entropy facts remain valid, but the chosen
  source-semantic carrier expression is not claimed value-exact;
- no production replay slice or first whole-production splice gate is named.

X010 is terminal. A smaller correction primitive or a changed cap would be a
new premise and new experiment, not a repair inside X010. This packet
authorizes no second construction, lookup fallback, round4, whole-circuit or
score claim, provider, range, hunt, submission, CUDA work, nonce change, or
public note.
