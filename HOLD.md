# HOLD — d919 implicit-zero comparator hybrid

Date: 2026-08-23

## Scope

- Base: `d919bc64a3b6a236e17870a69993fd76a21a8092`
- Branch: `research/d919-implicit-zero-hybrid`
- Feature flag: `CMP_LT_PHASE_IMPLICIT_ZERO_HYBRID=1`
- Changed primitive: `cmp_lt_phase_conditioned` only
- No provider use, nonce processing, search, submission, or public mutation

The opt-in path removes the standalone clean `c_in` from the lower comparator
prefix using the implicit-zero construction from `51c6c31`, while retaining
d919's top CNOT/CZ phase factorization. Width 1 deliberately falls back to the
unchanged d919 path.

## Exactness gates

PASS — the standalone self-test exhaustively compared every `(u, v)` pair for
widths 2 through 8. Baseline and hybrid used identically seeded deterministic
HMR readers for every 64-lane batch. It asserted:

- identical restored `u` and `v` registers;
- identical accumulated phase;
- identical classical HMR bits;
- zero non-input quantum ancillas;
- one fewer primitive peak qubit;
- fewer primitive ops; and
- identical primitive CCX/CCZ count.

Command:

```text
CMP_LT_PHASE_IMPLICIT_ZERO_HYBRID=selftest ./target/release/build_circuit
```

Receipt:

```text
CMP_LT_PHASE_IMPLICIT_ZERO_HYBRID: PASS widths=2..8 exhaustive deterministic-HMR value/phase/ancilla equivalence
```

PASS — flag-off emitted ops remained byte-identical to the unmodified d919
baseline:

```text
SHA-256 4cf51bba513b4c3a742b2d0544c7763206b137780cedeb9f2c83688fdde11929
emitted ops 12,825,363
```

## Global resource gate

HOLD — the hybrid improved the local primitive but did not lower either global
score factor.

| metric | d919 flag off | hybrid flag on | delta |
|---|---:|---:|---:|
| allocator peak qubits | 1,273 | 1,273 | 0 |
| emitted CCX | 949,041 | 949,041 | 0 |
| emitted CCZ | 40 | 40 | 0 |
| pre-tail ops | 12,825,267 | 12,815,039 | -10,228 |
| final emitted ops | 12,825,363 | 12,815,135 | -10,228 |
| deterministic 64-lane executed Toffoli | 908,776.80 | 908,818.05 | +41.25 |
| classical mismatches | 0 | 0 | 0 |
| phase | `0x0` | `0x0` | clean |
| dirty qubits | 0 | 0 | clean |

The active-timeline peak stayed in `pp_div_replay`. The B0 peak census stayed
composition-identical: 339 retained walk qubits, 256 initial x, 256 replay,
145 initial y, 145 inverse scratch, 128 replay high-ladder carries, and four
single-qubit owners. The removed comparator `c_in` was not a binding peak
owner. The peak op index shifted from 2,517,949 to 2,516,932 only because the
stream became shorter.

The 10,228-op reduction is a Clifford-stream cleanup, but peak qubits and
emitted Toffoli are unchanged, and the bounded deterministic executed-Toffoli
sample moved slightly upward. This does not qualify as a global score/resource
win under the requested gate, so the branch is held locally and must not be
pushed or promoted.

## Harness notes

Repository-wide `cargo test` is not a usable gate on this exact historical
source: the unmodified d919 test target has unrelated stale test-only symbols
and simulator API calls that fail compilation. The opt-in standalone miter was
therefore compiled into the normal release `build_circuit` binary and run to
completion. An interrupted B0 artifact write filled `ops.bin.tmp`; that exact
temporary file was removed, and no further production build was run.
