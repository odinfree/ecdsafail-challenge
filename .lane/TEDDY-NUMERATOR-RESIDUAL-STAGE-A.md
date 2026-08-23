# Teddy numerator-residual carrier X010 Stage A

Observed: 2026-08-23

Status: `STAGE_A_CHARACTERIZATION_COMPLETE`.

## Scope and identity

This is the observation-only first stage declared by
`.lane/TEDDY-NUMERATOR-RESIDUAL-CARRIER-PREDECLARATION.md`. It allocates no
carrier, applies no correction, and makes no rounds-`0..3` candidate-parity or
production-splice claim.

- Pre-characterization commit:
  `da9ba19237424a2248f1c8aaae890fd75e492eff`.
- Production `src/point_add/pingpong_div.rs` SHA-256:
  `22c4820a9ba3b2356eb785d0d0d452b0939a643cb6c65241706554d19b7df376`.
- Characterization module SHA-256:
  `5dc2d883c6a5e5e19c7794b36b14b117e1f9586405ed9618565fa9e7080eba82`.
- Env-gate source SHA-256:
  `929285bf81b19c8a0b2eb8d75bc1ca44e8ed847de4627b87891b075bbcc55bde`.
- Frozen corpus SHA-256:
  `53b06714ffdf079be23b2d3e1d25706c0d2853ab08d13345588f9a505c9409b0`.
- Release executable SHA-256:
  `ddc26953fcc50855344527252fe86a32cd8bb72f79bb6bb4c456ba71445f4330`.

The protected production source is byte-identical to the X010 predeclaration.
Only the isolated retained-replay module and its opt-in environment gate were
changed.

## Exact commands

From the worktree root:

```text
cargo build --release --bin build_circuit
SUB4_TEDDY_NUMERATOR_RESIDUAL_CHARACTERIZE=1 target/release/build_circuit
```

The release build passed with three pre-existing unrelated warnings. The
direct characterization exited zero.

## Complete observation

The direct log contains 4,169 lines / 4,368,614 bytes:

- exactly 4,096 full-state residual rows;
- exactly 64 per-denominator phase-mask batches;
- one bound build line and one terminal PASS line;
- complete raw finite inverse `4096/4096` and raw per-denominator forward
  injectivity `64/64`;
- raw walkback cleanup exact;
- candidate rounds `0..3` observed without accepting its known round-2/3
  mismatch;
- carrier allocated `0`, correction applied `0`.

Direct log SHA-256:
`c3fc02dc470a5279af5247e6c5a3f9200b254d07ebf961bb5ebe0fef67dd1b9c`.

The normalized complete X010 record set (build, all rows, all batches, PASS)
has SHA-256
`7ce27cc97c07d8303c5c0f1f5b86c91c26377a0349225a85425b67a3b62b90b9`.
The two-line build/PASS receipt has SHA-256
`6cf260cb0077fb0a363c86886411daf2f9914f8a3a319712cb209c88fe945e6a`.
Logs and binaries remain outside Git.

## Resource receipt

```text
TEDDY_NUMERATOR_RESIDUAL_CHARACTERIZE_BUILD rows=4096 denominators=64 seeds=64 production_seeds=32 stress_seeds=32 candidate_peak_q=1114 candidate_peak_phase=teddy_nonzero_round2_signed_mod_add_pm_halve_fused candidate_abi_q=768 candidate_ops=13659 candidate_emitted_t=960 candidate_round_emitted_t=0:65,1:141,2:377,3:377 reference_peak_q=1546 reference_peak_phase=teddy_nonzero_reference_walk reference_abi_q=768 reference_ops=40605 reference_emitted_t=4010 shared_stochastic_events=1866 reference_walk_stochastic_events=2053 normalization_flags=1 concurrent_flags=0 persistent_carrier_bits=0 relative_phase=1
TEDDY_NUMERATOR_RESIDUAL_CHARACTERIZE PASS observation_only=1 rows=4096 denominators=64 production_seeds=32 stress_seeds=32 raw_forward_injective=64/64 finite_inverse=4096/4096 raw_cleanup=exact candidate_rounds0_through3_observed=1 candidate_peak_q=1114 candidate_ops=13659 candidate_emitted_t=960 candidate_executed_t=894.242 reference_peak_q=1546 reference_ops=40605 reference_emitted_t=4010 reference_executed_t=3944.242 carrier_allocated=0 correction_applied=0
```

The candidate executed-T observation differs slightly from X007 because X010
uses X009's source-event-bound relative-phase stream. It is not a new resource
shape: emitted operations and per-round T are unchanged.

## Boundary and next gate

Stage A proves only that the declared raw/candidate state census completed on
the frozen corpus under the exact source and stochastic bindings. The next
ordered action is the predeclared deterministic dependency, entropy, effective
width, and source-formula gate. Construction is forbidden unless that gate
finds a source-semantic one-carrier compute/correct/uncompute mapping. No
provider, range, hunt, submission, round 4, full-circuit, or promotion action
follows from this observation.
