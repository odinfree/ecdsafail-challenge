# Promoted Q1272 add3x repair retrospective gate

Date: 2026-08-23

Verdict: `RUST_RETROSPECTIVE_PASS / SHARED_CPP_TARGET_PASS / NEW_HOLDOUT_REQUIRED`.

The implementation follows predeclaration `030829c` exactly. The exact Rust
model now uses one source-local `coord_add3x_circuit` helper at the traced and
production add3x call sites. It computes exact `3 * coord mod p`, performs the
raw 256-bit add, and, only on carry, adds F inside the low 53-bit window while
dropping that window's outgoing carry. No circuit, width schedule, replay,
square, Fiat-Shamir, operation-stream, or trusted-evaluator source changed.

Corrected identities:

- Rust source SHA-256:
  `39371fca9e77d7aab3cfda7111bdbc03c11d8cfc03966cd15b2ea77d79836e38`;
- local arm64 qualification binary SHA-256:
  `ea7f1410a17ee84c8b05ae44ff1763b53dd2564bbd9bb607cfae8a6648d7b454`;
- exact operation count: `12,904,643`;
- exact operation SHA-256 remains
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`.

The targeted boundary for nonce `66961008849867`, shot `8729`, is now
`0825f1939e72bfaa2f2b73486057bee9b205a9d4ff6907f758a000005baa7c14`,
exactly matching the diagnostic circuit state. The corrected predictor marks
shot 8729 as a fault and reports the full trusted count 27.

Retrospective complete-mask gates against the already revealed immutable
trusted fixtures:

- inherited nonce: 23/23, exact complete mask, stdout SHA-256
  `e137d9d4f4ec455830a7cada3fe508ca6f302e3ff0982f660a46d1c5d9dee428`;
- H64: 64/64 rows, 1,144/1,144 faults, zero mask differences, stdout
  SHA-256
  `6147c21129876a2193cd5813944b95d09ae1f149802c53ca731824a11be54adc`;
- spent D32: 32/32 rows, 559/559 faults, zero mask differences, corrected
  stdout SHA-256
  `f6684ce97550f8ff689061c34d7ea897db2f94ebd5da5419ddae911b5606c1f9`.

The built-in SHAKE256, square-register, operation-count, checkpoint, and
reference point-add KATs also passed.

The shared C++ source already contained the predeclared finite-width helper
`pp_mod_add_exact_model`; no C++ edit was needed. Its unchanged source SHA-256
is `120979945f82318e9df77014fabea3d2f8a9dea3c433e1ff5636cb3cb654424b`
and its local arm64 binary SHA-256 is
`501ee20c42ab402189d524c4053cc50276a06b6248ff83f51f55925ee76818ed`.
On the falsifying nonce it reports all 27 fault rows including `8729 16`;
targeted fault-row stdout SHA-256 is
`4abeb50fb64aa5eee36bb02d4e1f7b49705cf290c8abc463a2b1bcb7b456db53`.
Full shared-C++ fixture parity remains a separate packet gate.

These are retrospective gates on revealed corpora. CUDA and range scanning
remain blocked until a genuinely new, disjoint, predeclared holdout passes the
corrected Rust and shared models against the trusted evaluator. Provider
compute, hunting, and submissions remain disabled.
