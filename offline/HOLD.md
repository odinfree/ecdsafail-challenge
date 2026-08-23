# HOLD — d919 dirty-carry experiment

Status: **HOLD**

Source under test: `d919bc64a3b6a236e17870a69993fd76a21a8092`,
`src/point_add/arith/adder.rs:cuccaro_add_fast_borrowed_carries`.

The existing sequence does not accept arbitrary borrowed-wire values. It only
works when the carry scratch enters as zero. The fail-closed truth-table scan
stopped on its second scheduled case, the first nonzero borrowed value.

## Minimal counterexample

```text
width       = 2
acc         = 0b00
addend      = 0b00
carry_in    = 0
borrowed d0 = 1
cout target = 0

expected: acc=0b00, addend=0b00, carry_in=0, d0=1, cout=0, phase=0
actual:   acc=0b10, addend=0b00, carry_in=0, d0=0, cout=0, phase=m0
```

The first destructive operation is zero-based gate 11, `HMR d0 m0`:

```text
before: acc=0b10, addend=0b00, carry_in=0, d0=1, cout=0, phase=0
after:  acc=0b10, addend=0b00, carry_in=0, d0=0, cout=0, phase=m0
```

The following conditioned phase correction has zero quantum controls for this
input, so it cannot cancel `m0`. Thus all three required channels fail:

- classical: `acc` is `2`, not `0`;
- phase: the residual phase depends on measurement outcome `m0`;
- ancilla/borrowed identity: `d0` is erased instead of restored.

Applying the specified arithmetic inverse to the actual output recovers
`acc=2`, not the input `acc=0`, so forward/inverse identity fails too.

## Conditional cost accounting

The carry-out-instrumented sequence has `n` Toffolis: `n-1` in the d919 carry
prefix and one for the clean carry-out sink. A clean owned ladder has the same
`n` Toffolis. If the dirty-wire premise had held, it would replace `n-1` owned
ancillas with `n-1` borrowed wires:

| width | candidate T | owned-ladder T | candidate owned ancilla | owned-ladder ancilla |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 2 | 2 | 0 | 1 |
| 3 | 3 | 3 | 0 | 2 |
| 4 | 4 | 4 | 0 | 3 |
| 5 | 5 | 5 | 0 | 4 |
| 6 | 6 | 6 | 0 | 5 |
| 7 | 7 | 7 | 0 | 6 |
| 8 | 8 | 8 | 0 | 7 |

Those ancilla savings are invalidated by the counterexample. No pass/cost
receipt is issued.

## Reproduce

```sh
python3 offline/dirty_carry_truth_table.py --pretty
```

Expected exit status: `1`. The JSON output contains `status: "HOLD"`, the
counterexample, the exact gate state, symbolic phase mask, and cost table.
