# Structural History Fiber Falsifier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an exhaustive reduced-width falsifier that measures the exact resident-code requirement of ping-pong sign-history fibers before any circuit edit.

**Architecture:** A dependency-free Python model implements the fixed-width signed ping-pong walk and matching modular coefficient replay. It enumerates every legal `(denominator, numerator)` pair for two odd moduli, groups histories by exact endpoint state, verifies encode/decode round trips, and emits deterministic JSON for the mission gate.

**Tech Stack:** Python 3 standard library, `unittest`, JSON, SHA256, and the Rust source-bound equations documented in `12-structural-history-fiber-mission.md`.

## Global Constraints

- Bind all claims to commit `67524171baaf568dc3dc606f38515745f70804ff` and tree `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`.
- Modify only `src/point_add/memory/` during this plan.
- Use exact enumeration at widths 5 and 6; sampling is not an admission artifact.
- A reduced-width result is diagnostic and cannot open provider, nonce, public, push, or submission gates.
- Fail closed if round-trip, divisibility, convergence, or deterministic receipt checks fail.
- Preserve the authoritative score thresholds Q1100/T1049755 and Q1000/T1154731.

---

### Task 1: Exact fixed-width walk and replay model

**Files:**
- Create: `src/point_add/memory/repro/pp_history_fiber.py`
- Create: `src/point_add/memory/repro/test_pp_history_fiber.py`

**Interfaces:**
- Produces: `bit1(value: int, width: int) -> int`, `half_mod(value: int, modulus: int) -> int`, `step(config: Config, state: State, round_index: int) -> tuple[State, int]`, and `run_case(config: Config, denominator: int, numerator: int) -> Trace`.
- `State` contains signed walk integers `u`, `v` and modular coefficient integers `x`, `y`.
- `Trace` contains every post-round state and the accumulated sign word.

- [x] **Step 1: Write failing arithmetic tests**

```python
class ArithmeticTests(unittest.TestCase):
    def test_bit1_uses_fixed_width_twos_complement(self):
        self.assertEqual(bit1(-1, 5), 1)
        self.assertEqual(bit1(-3, 5), 0)

    def test_half_mod_is_inverse_of_doubling(self):
        for value in range(29):
            self.assertEqual((2 * half_mod(value, 29)) % 29, value)

    def test_each_walk_step_is_integral_and_odd(self):
        trace = run_case(Config(width=5, modulus=29, rounds=12), 7, 11)
        for state in trace.states:
            self.assertEqual(state.u & 1, 1)
            self.assertEqual(state.v & 1, 1)
```

- [x] **Step 2: Run the arithmetic tests and verify the missing-module failure**

Run: `python3 -m unittest src.point_add.memory.repro.test_pp_history_fiber.ArithmeticTests -v`

Expected: import failure for `pp_history_fiber` before the implementation exists.

- [x] **Step 3: Implement the exact small-width recurrence**

Implement the following equations in `step`:

```python
source_name, target_name = ("u", "v") if round_index % 2 == 0 else ("v", "u")
sign = bit1(getattr(state, source_name), width) ^ bit1(getattr(state, target_name), width)
walk_target = (walk_target + (-walk_source if sign else walk_source)) // 2

if round_index == 0:
    replay_target = half_mod(replay_target, modulus)
elif round_index == 1:
    replay_target = half_mod(-replay_source if sign else replay_source, modulus)
else:
    replay_target = half_mod(replay_target + (-replay_source if sign else replay_source), modulus)
```

Initialize `u=modulus`, `v=denominator` for odd denominators and
`v=denominator-modulus` for even denominators, with `x=0` and `y=numerator`.
Reject a walk numerator that is not divisible by two before division.

- [x] **Step 4: Run the arithmetic tests and verify PASS**

Run: `python3 -m unittest src.point_add.memory.repro.test_pp_history_fiber.ArithmeticTests -v`

Expected: 3 tests pass.

- [x] **Step 5: Commit the exact model checkpoint**

```bash
git add src/point_add/memory/repro/pp_history_fiber.py src/point_add/memory/repro/test_pp_history_fiber.py
git commit -m "research: model pingpong history fibers"
```

### Task 2: Exhaustive fiber encoder and decoder

**Files:**
- Modify: `src/point_add/memory/repro/pp_history_fiber.py`
- Modify: `src/point_add/memory/repro/test_pp_history_fiber.py`

**Interfaces:**
- Produces: `enumerate_fibers(config: Config) -> FiberReport`.
- `FiberReport` records per round: input count, endpoint count, maximum fiber size, minimum code bits, raw history bits, and a SHA256 over sorted endpoint/history members.
- Produces: `encode(endpoint: State, history: int, members: Mapping[State, tuple[int, ...]]) -> int` and `decode(endpoint: State, code: int, members: Mapping[State, tuple[int, ...]]) -> int`.

- [x] **Step 1: Write failing exhaustive round-trip tests**

```python
class FiberTests(unittest.TestCase):
    def test_every_width5_history_round_trips(self):
        report = enumerate_fibers(Config(width=5, modulus=29, rounds=12))
        self.assertEqual(report.input_count, 29 * 28)
        self.assertEqual(report.rounds[-1].round_index, 12)
        self.assertTrue(report.round_trip_ok)

    def test_local_walk_endpoint_has_two_predecessor_signs(self):
        self.assertEqual(local_predecessor_signs(source=5, post_target=3, width=5), (0, 1))
```

- [x] **Step 2: Run the fiber tests and verify missing-symbol failures**

Run: `python3 -m unittest src.point_add.memory.repro.test_pp_history_fiber.FiberTests -v`

Expected: failures for `enumerate_fibers` and `local_predecessor_signs`.

- [x] **Step 3: Implement deterministic endpoint fibers**

Enumerate `denominator in range(1, modulus)` and `numerator in range(modulus)`.
At every round, group the distinct accumulated history integers by the full
post-round `State`. Sort and deduplicate each fiber. Assign the code as the
zero-based index in the sorted tuple. Set `minimum_code_bits` to
`(maximum_fiber_size - 1).bit_length()`. Re-encode and decode every member;
raise `AssertionError` on any mismatch.

- [x] **Step 4: Run all reduced-width tests and verify PASS**

Run: `python3 -m unittest src.point_add.memory.repro.test_pp_history_fiber -v`

Expected: 5 tests pass with no warnings.

- [x] **Step 5: Commit the exhaustive codec checkpoint**

```bash
git add src/point_add/memory/repro/pp_history_fiber.py src/point_add/memory/repro/test_pp_history_fiber.py
git commit -m "research: enumerate exact history fibers"
```

### Task 3: Two-width receipt and mission verdict

**Files:**
- Modify: `src/point_add/memory/repro/pp_history_fiber.py`
- Create: `src/point_add/memory/14-structural-history-fiber-verdict.json`
- Modify: `src/point_add/memory/12-structural-history-fiber-mission.md`

**Interfaces:**
- Command: `python3 src/point_add/memory/repro/pp_history_fiber.py --width 5 --modulus 29 --rounds 12 --width 6 --modulus 61 --rounds 17`.
- Produces deterministic JSON on standard output with source commit/tree, both reports, scaling ratios, Q1100/Q1000 projections, and `ADMIT` or `HARD_NACK`.

- [x] **Step 1: Add a deterministic CLI receipt test**

```python
class CliTests(unittest.TestCase):
    def test_receipt_is_byte_deterministic(self):
        args = ["--width", "5", "--modulus", "29", "--rounds", "12"]
        self.assertEqual(render_receipt(args), render_receipt(args))
```

- [x] **Step 2: Run the CLI test and verify the missing-renderer failure**

Run: `python3 -m unittest src.point_add.memory.repro.test_pp_history_fiber.CliTests -v`

Expected: failure for `render_receipt`.

- [x] **Step 3: Implement the CLI and gate calculation**

The receipt must include the exact source binding, `input_count`, every
per-round fiber row, and these projections:

```python
history_cap_q1100 = 469
history_cap_q1000 = 369
toffoli_headroom_q1100 = 1_049_755 - 911_390
toffoli_headroom_q1000 = 1_154_731 - 911_390
```

Return `ADMIT` only when both widths round-trip, the final code/raw ratio does
not increase from width 5 to width 6, the linear projection of resident code
at 636 raw signs is at most 469, and the receipt explicitly leaves circuit
decoder cost unresolved for the next source-bound synthesis gate. Otherwise
return `HARD_NACK` with the first failed predicate. This is admission to
decoder synthesis only, never candidate admission.

- [x] **Step 4: Run the full suite and generate the receipt**

Run: `python3 -m unittest src.point_add.memory.repro.test_pp_history_fiber -v`

Expected: 6 tests pass.

Run: `python3 src/point_add/memory/repro/pp_history_fiber.py --width 5 --modulus 29 --rounds 12 --width 6 --modulus 61 --rounds 17`

Expected: valid JSON with two reports and one explicit mission verdict.

- [x] **Step 5: Save, hash, and independently re-render the receipt**

Use `apply_patch` to add the exact standard output as
`src/point_add/memory/14-structural-history-fiber-verdict.json`. Re-run the
command and compare its standard output byte-for-byte with the saved file.
Run `shasum -a 256` on the saved receipt and record that SHA256 plus the verdict
in `12-structural-history-fiber-mission.md`.

- [x] **Step 6: Commit the phase verdict**

```bash
git add src/point_add/memory/12-structural-history-fiber-mission.md src/point_add/memory/14-structural-history-fiber-verdict.json src/point_add/memory/repro/pp_history_fiber.py src/point_add/memory/repro/test_pp_history_fiber.py
git commit -m "research: close history fiber falsifier"
```

## Self-review

- Spec coverage: the plan binds source, tests the local ambiguity witness,
  exhaustively enumerates two widths, checks round trips, measures the resident
  code, and emits the only allowed phase verdict.
- Placeholder scan: the plan contains no deferred implementation placeholders;
  every task names exact files, interfaces, commands, and expected results.
- Type consistency: `Config`, `State`, `Trace`, `FiberReport`, `encode`,
  `decode`, `enumerate_fibers`, and `render_receipt` retain the same names and
  roles across all tasks.
