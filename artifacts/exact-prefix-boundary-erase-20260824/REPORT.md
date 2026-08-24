# C2 exact-prefix boundary erase report

## Binding

- Base commit: `67524171baaf568dc3dc606f38515745f70804ff`
- Base tree: `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`
- Branch: `research/codex-exact-boundary-recompute-20260824`
- Host: local macOS CPU only
- External actions: no fetch, push, provider, or submission

The experiment is enabled only by
`SUB4_PP_EXACT_PREFIX_BOUNDARY_ERASE=1`. It changes the existing erase
closure's comparator range from the local upper slice to `0..hi`. Chunk
allocation, chunk order, immediate erase timing, and the at-most-two live
boundary wires are unchanged.

## Commands

```bash
cargo build --offline --release --bin build_circuit

env -u SUB4_PP_EXACT_PREFIX_BOUNDARY_ERASE -u PP_PROFILE \
  ./target/release/build_circuit
shasum -a 256 ops.bin
cp ops.bin /tmp/ecdsafail-c2-67524171-baseline.ops.bin

env -u SUB4_PP_EXACT_PREFIX_BOUNDARY_ERASE \
  PP_PROFILE=1 PP_PROFILE_SEED=0 \
  ./target/release/build_circuit

cargo test --offline --bin build_circuit \
  exact_prefix_boundary_erase_includes_global_zero_carry \
  -- --exact --nocapture

SUB4_PP_EXACT_PREFIX_BOUNDARY_ERASE=1 \
  SUB4_PINGPONG_POINT_ADD_SELFTEST=1 \
  ./target/release/build_circuit

env -u SUB4_PP_EXACT_PREFIX_BOUNDARY_ERASE -u PP_PROFILE \
  ./target/release/build_circuit
shasum -a 256 ops.bin /tmp/ecdsafail-c2-67524171-baseline.ops.bin
cmp -s ops.bin /tmp/ecdsafail-c2-67524171-baseline.ops.bin

SUB4_PP_EXACT_PREFIX_BOUNDARY_ERASE=1 \
  PP_PROFILE=1 PP_PROFILE_SEED=0 \
  ./target/release/build_circuit
```

All Cargo commands used `--offline`. The final two builder invocations used
the release binary produced by that offline build.

## TDD and repository caveat

The focused counterexample is `0xff + 0x01` at an eight-bit boundary with a
four-bit local replay. The local upper-nibble relation reports no carry, while
the full prefix under global-zero carry reports the exact carry.

The RED `cargo test` compile produced 167 errors: the two intended missing
`boundary_erase_compare_start` errors plus 165 unrelated stale `cfg(test)`
errors already present at the exact base. After implementing the helper, the
two intended errors disappeared; the same target remains non-runnable because
of the 165 pre-existing errors. The repository's supported component hook,
`SUB4_PINGPONG_POINT_ADD_SELFTEST=1`, executes the same range assertions and
the real 64-lane affine-add simulation. With exact-prefix erase enabled it
exited zero and reported:

```text
pingpong full affine add: 1220174 emitted / 1043558.219 executed Toffoli, 1416 qubits
```

`cargo fmt --check` is likewise red on broad pre-existing formatting drift.
The bounded diff passes `git -c core.whitespace=cr-at-eol diff --check`; the
source file retains its original CRLF convention.

## Default identity

The flag-absent build before and after the source change is byte-identical:

| field | before | after |
| --- | ---: | ---: |
| emitted ops | 12,593,858 | 12,593,858 |
| `ops.bin` bytes | 45,668,102 | 45,668,102 |
| SHA-256 | `87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e` | `87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e` |

`cmp -s` exited zero.

## Paired 64-lane PP_PROFILE result

Both profiles used `PP_PROFILE_SEED=0` and finished with
`classical_mismatch=0 phase=0x0 dirty_qubits=0`.

| metric | exact-675 default | exact full-prefix | delta |
| --- | ---: | ---: | ---: |
| peak qubits | 1,267 | 1,416 | +149 |
| average executed Toffoli | 911,220.656250 | 1,044,268.921875 | +133,048.265625 |
| profiled ops | 12,593,762 | 15,773,876 | +3,180,114 |
| emitted CCX/CCZ | 955,170 | 1,220,174 | +265,004 |
| projected `Q*T` | 1,154,516,571.468750 | 1,478,684,793.375000 | +324,168,221.906250 |

The exact Toffoli fractions are recovered from the profiler's integer gate
totals divided by 64; its display rounds them to `911220.66` and `1044268.92`.
The projected score increases by 28.078264957%. The enabled compressed artifact
has 15,773,972 emitted ops, 63,231,145 bytes, and SHA-256
`36c71b657945a95e8fab74273d33448c961ed8d6cbc65fa9cdd7129baca48ff0`.

Raw receipt hashes:

| artifact | SHA-256 |
| --- | --- |
| `baseline-pp-profile.log` | `300736a6b9c5f5648e8f861c237193fe14022f0d56ac891449f2e72c4193c5d7` |
| `exact-prefix-pp-profile.log` | `2cb125396c7c4ae8666b8418726f56c0e596271782ea0dadd4cb1d32c22ced65` |
| `exact-prefix-selfcheck.log` | `2bb31b5dca583820b708d05d87e7ab5cd45460b4ffdb3ce1986cc0f6a777eacc` |

## Tony / RCI post-run audit

- Decision audited: admit the full-prefix immediate eraser on exact 675.
- Problem: local replay can miss a lower-prefix carry; full-prefix replay is
  exact but widens the temporary comparator.
- Evidence: the counterexample and both 64-lane receipts above.
- Effect: correctness is exact, but peak width rises by 149 and executed
  Toffoli by 133,048.265625. The projected score is 28.078264957% worse.
- Smallest useful fix tested: switch only the existing comparator start index
  under the strict env flag.
- Gate: exact correctness, `Q < 1267`, and projected score below the exact-675
  baseline.
- Decision: `HARD_NACK`.
- Owner: Lane C2.
- Next action: do not lift this schedule; any future exact repair must avoid a
  full-width temporary carry ladder, not merely avoid retaining boundary wires.

The mechanism clears the exactness gate but fails both economics gates. It is
149 qubits above the baseline and 150 qubits above the largest value allowed by
the strict `Q < 1267` condition.
