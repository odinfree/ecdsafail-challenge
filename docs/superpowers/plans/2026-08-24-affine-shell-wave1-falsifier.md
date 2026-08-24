# Affine-Shell Wave 1 Falsifier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic reduced-width oracle and algebraic certificate that proves the exceptional-safe affine shell while deciding whether the low-degree two-register shear grammar can realize it.

**Architecture:** A standard-library Python module models the complete shell permutation and its inverse over small prime fields. A separate certificate computes the target transducer's nonzero-fiber Jacobian determinant and compares it with the constant-determinant invariant of compositions of additive shears, swaps, translations, and constant unit scalings. The CLI emits one content-addressed JSON receipt that closes only this exact grammar and names the next grammar when it is killed.

**Tech Stack:** Python 3 standard library, `unittest`, JSON, SHA-256, existing repository research conventions under `src/point_add/memory/repro/`.

## Global Constraints

- Base commit is `cbf229dbd46a7c677fe2e28da882b4f8a02bac7f`; base tree is `eab2326ce33549eceeb5c10aa64eae33f148b0ac`.
- Do not modify production Rust in this wave.
- Do not import arbitrary truth tables, QROM, nonce data, provider data, or fitted verifier samples.
- A `HARD_NACK` closes only the low-degree shear grammar, not the full two-register affine-shell family.
- Provider, nonce-grind, push, public-note, promotion, and submission gates remain closed.
- Every receipt must reproduce byte-for-byte and bind the exact source and design specification.

---

### Task 1: Exact exceptional-safe shell oracle

**Files:**
- Create: `src/point_add/memory/repro/affine_shell_transducer.py`
- Create: `src/point_add/memory/repro/test_affine_shell_transducer.py`

**Interfaces:**
- Consumes: an odd prime `p`, a valid classical curve point `(a,b)`, and field-state tuples.
- Produces: `FieldCase`, `shell_from_input`, `unshell_to_input`, `transducer`, `inverse_transducer`, `reference_report`, and `first_curve_point`.

- [ ] **Step 1: Write failing oracle tests**

```python
from __future__ import annotations

import unittest

import affine_shell_transducer as shell


class AffineShellOracleTests(unittest.TestCase):
    def test_total_shell_is_bijective_and_invertible(self) -> None:
        case = shell.FieldCase(prime=17, a=1, b=5)
        report = shell.reference_report(case)
        self.assertEqual(report["states"], 17 * 17)
        self.assertEqual(report["unique_outputs"], 17 * 17)
        self.assertEqual(report["inverse_failures"], 0)
        self.assertEqual(report["curve_failures"], 0)
        self.assertGreaterEqual(report["valid_t_zero_inputs"], 1)

    def test_transducer_inverse_covers_zero_and_nonzero_fibers(self) -> None:
        case = shell.FieldCase(prime=17, a=1, b=5)
        for t in range(case.prime):
            for lam in range(case.prime):
                out = shell.transducer(case, t, lam)
                self.assertEqual(shell.inverse_transducer(case, *out), (t, lam))

    def test_first_curve_point_is_deterministic_and_valid(self) -> None:
        case = shell.first_curve_point(127)
        self.assertEqual(case.prime, 127)
        self.assertNotEqual(case.b, 0)
        self.assertEqual((case.b * case.b - case.a**3 - 7) % case.prime, 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and verify the intended RED state**

Run:

```bash
cd src/point_add/memory/repro
python3 -m unittest -v test_affine_shell_transducer.py
```

Expected: FAIL with `ModuleNotFoundError: No module named 'affine_shell_transducer'`.

- [ ] **Step 3: Implement the exact oracle**

```python
#!/usr/bin/env python3
"""Exact reduced-width model of the exceptional-safe affine shell."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldCase:
    prime: int
    a: int
    b: int

    def __post_init__(self) -> None:
        if self.prime <= 2 or self.prime % 2 == 0:
            raise ValueError("prime must be an odd integer")
        if not (0 <= self.a < self.prime and 0 <= self.b < self.prime):
            raise ValueError("coordinates must be canonical field elements")
        if (self.b * self.b - self.a**3 - 7) % self.prime != 0:
            raise ValueError("classical point is not on y^2=x^3+7")


def inv(value: int, prime: int) -> int:
    value %= prime
    if value == 0:
        raise ZeroDivisionError("zero has no field inverse")
    return pow(value, prime - 2, prime)


def unit(value: int, prime: int) -> int:
    value %= prime
    return value if value else 1


def lambda_zero(case: FieldCase) -> int:
    return (3 * case.a * case.a * inv(unit(2 * case.b, case.prime), case.prime)) % case.prime


def transducer(case: FieldCase, t: int, lam: int) -> tuple[int, int]:
    p = case.prime
    t %= p
    lam %= p
    x_out = (case.a - t) % p
    if t:
        y_out = (t * lam - case.b) % p
    else:
        y_out = (lam - lambda_zero(case) - case.b) % p
    return x_out, y_out


def inverse_transducer(case: FieldCase, x_out: int, y_out: int) -> tuple[int, int]:
    p = case.prime
    t = (case.a - x_out) % p
    if t:
        lam = ((y_out + case.b) * inv(t, p)) % p
    else:
        lam = (y_out + case.b + lambda_zero(case)) % p
    return t, lam


def shell_from_input(case: FieldCase, x: int, y: int) -> tuple[int, int]:
    p = case.prime
    d = (x - case.a) % p
    e = (y - case.b) % p
    lam = (e * inv(unit(d, p), p)) % p
    t = (d + 3 * case.a - lam * lam) % p
    return transducer(case, t, lam)


def unshell_to_input(case: FieldCase, x_out: int, y_out: int) -> tuple[int, int]:
    p = case.prime
    t, lam = inverse_transducer(case, x_out, y_out)
    d = (t - 3 * case.a + lam * lam) % p
    e = (lam * unit(d, p)) % p
    return (d + case.a) % p, (e + case.b) % p


def ec_add(case: FieldCase, x: int, y: int) -> tuple[int, int] | None:
    p = case.prime
    if x % p == case.a:
        if (y + case.b) % p == 0:
            return None
        slope = (3 * x * x * inv(2 * y, p)) % p
    else:
        slope = ((y - case.b) * inv(x - case.a, p)) % p
    x_out = (slope * slope - x - case.a) % p
    y_out = (slope * (x - x_out) - y) % p
    return x_out, y_out


def first_curve_point(prime: int) -> FieldCase:
    for a in range(prime):
        rhs = (a**3 + 7) % prime
        for b in range(1, prime):
            if b * b % prime == rhs:
                return FieldCase(prime=prime, a=a, b=b)
    raise ValueError(f"no nonzero-y curve point found for p={prime}")


def reference_report(case: FieldCase) -> dict[str, int]:
    p = case.prime
    outputs: set[tuple[int, int]] = set()
    inverse_failures = 0
    curve_failures = 0
    valid_t_zero_inputs = 0
    curve_inputs = 0
    for x in range(p):
        for y in range(p):
            out = shell_from_input(case, x, y)
            outputs.add(out)
            if unshell_to_input(case, *out) != (x, y):
                inverse_failures += 1
            if (y * y - x**3 - 7) % p == 0 and x != case.a:
                expected = ec_add(case, x, y)
                if expected is not None:
                    curve_inputs += 1
                    d = (x - case.a) % p
                    lam = ((y - case.b) * inv(d, p)) % p
                    t = (d + 3 * case.a - lam * lam) % p
                    valid_t_zero_inputs += int(t == 0)
                    if out != expected:
                        curve_failures += 1
    return {
        "states": p * p,
        "unique_outputs": len(outputs),
        "inverse_failures": inverse_failures,
        "curve_inputs": curve_inputs,
        "curve_failures": curve_failures,
        "valid_t_zero_inputs": valid_t_zero_inputs,
    }
```

- [ ] **Step 4: Run the oracle tests and verify GREEN**

Run: `cd src/point_add/memory/repro && python3 -m unittest -v test_affine_shell_transducer.py`

Expected: 3 tests pass, 0 failures.

- [ ] **Step 5: Commit the oracle**

```bash
git add src/point_add/memory/repro/affine_shell_transducer.py \
  src/point_add/memory/repro/test_affine_shell_transducer.py
git commit -m "research: add exact affine shell oracle"
```

### Task 2: Constant-Jacobian grammar falsifier

**Files:**
- Modify: `src/point_add/memory/repro/affine_shell_transducer.py`
- Modify: `src/point_add/memory/repro/test_affine_shell_transducer.py`

**Interfaces:**
- Consumes: `FieldCase` and the transducer equation from Task 1.
- Produces: `target_nonzero_determinants`, `low_degree_shear_certificate`, and the scoped `HARD_NACK_LOW_DEGREE_SHEAR` verdict.

- [ ] **Step 1: Add failing determinant-certificate tests**

```python
    def test_target_has_variable_nonzero_fiber_determinant(self) -> None:
        case = shell.FieldCase(prime=17, a=1, b=5)
        determinants = shell.target_nonzero_determinants(case)
        self.assertEqual(determinants, set(range(1, case.prime)))

    def test_low_degree_shear_grammar_is_hard_nacked(self) -> None:
        case = shell.FieldCase(prime=31, a=0, b=10)
        certificate = shell.low_degree_shear_certificate(case)
        self.assertEqual(certificate["verdict"], "HARD_NACK_LOW_DEGREE_SHEAR")
        self.assertEqual(certificate["grammar_determinant_class"], "constant_nonzero")
        self.assertEqual(certificate["target_determinant_count"], 30)
        self.assertEqual(certificate["next_grammar"], "REGISTER_SHARED_EUCLID")
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `cd src/point_add/memory/repro && python3 -m unittest -v test_affine_shell_transducer.AffineShellOracleTests.test_target_has_variable_nonzero_fiber_determinant test_affine_shell_transducer.AffineShellOracleTests.test_low_degree_shear_grammar_is_hard_nacked`

Expected: FAIL because the two certificate functions do not exist.

- [ ] **Step 3: Implement the algebraic certificate**

Append:

```python
def target_nonzero_determinants(case: FieldCase) -> set[int]:
    """Jacobian determinants of (T,L)->(a-T,T*L-b) for T != 0.

    The derivative matrix is [[-1, 0], [L, T]], so det=-T. The
    returned set is normalized to positive field representatives.
    """
    p = case.prime
    return {(-t) % p for t in range(1, p)}


def low_degree_shear_certificate(case: FieldCase) -> dict[str, object]:
    """Close the additive-shear grammar by its determinant invariant.

    Translations and additive triangular shears have determinant one; swaps
    have determinant minus one; multiplication by a classical field unit has
    a fixed nonzero determinant. A composition therefore has one constant
    nonzero determinant on the nonzero-T region. The target has determinant
    -T and assumes every nonzero value when p > 3.
    """
    determinants = target_nonzero_determinants(case)
    variable = len(determinants) > 1
    return {
        "grammar": "LOW_DEGREE_TWO_REGISTER_SHEARS",
        "grammar_determinant_class": "constant_nonzero",
        "target_determinants": sorted(determinants),
        "target_determinant_count": len(determinants),
        "target_is_variable": variable,
        "zero_branch_relevant": False,
        "proof_scope": "nonzero T fibers; zero-only corrections cannot repair the mismatch",
        "verdict": "HARD_NACK_LOW_DEGREE_SHEAR" if variable else "INCONCLUSIVE",
        "next_grammar": "REGISTER_SHARED_EUCLID",
    }
```

- [ ] **Step 4: Run the full module test suite and verify GREEN**

Run: `cd src/point_add/memory/repro && python3 -m unittest -v test_affine_shell_transducer.py`

Expected: 5 tests pass, 0 failures.

- [ ] **Step 5: Commit the scoped falsifier**

```bash
git add src/point_add/memory/repro/affine_shell_transducer.py \
  src/point_add/memory/repro/test_affine_shell_transducer.py
git commit -m "research: falsify low degree affine shell grammar"
```

### Task 3: Content-addressed multi-width receipt

**Files:**
- Modify: `src/point_add/memory/repro/affine_shell_transducer.py`
- Modify: `src/point_add/memory/repro/test_affine_shell_transducer.py`
- Create: `src/point_add/memory/42-affine-shell-wave1-receipt.json`
- Create: `src/point_add/memory/43-affine-shell-wave1-verdict.md`

**Interfaces:**
- Consumes: the oracle and certificate from Tasks 1-2.
- Produces: `run_wave1`, deterministic canonical JSON, a receipt SHA-256, and a human-readable scoped verdict.

- [ ] **Step 1: Add failing receipt tests**

```python
    def test_wave1_receipt_is_deterministic_and_multi_width(self) -> None:
        first = shell.run_wave1((31, 127, 251))
        second = shell.run_wave1((31, 127, 251))
        self.assertEqual(first, second)
        self.assertEqual(first["verdict"], "HARD_NACK_LOW_DEGREE_SHEAR")
        self.assertEqual([row["prime"] for row in first["cases"]], [31, 127, 251])
        self.assertTrue(all(row["inverse_failures"] == 0 for row in first["cases"]))
        self.assertTrue(all(row["curve_failures"] == 0 for row in first["cases"]))
        self.assertEqual(len(first["receipt_sha256"]), 64)
```

- [ ] **Step 2: Run the receipt test and verify RED**

Run: `cd src/point_add/memory/repro && python3 -m unittest -v test_affine_shell_transducer.AffineShellOracleTests.test_wave1_receipt_is_deterministic_and_multi_width`

Expected: FAIL because `run_wave1` does not exist.

- [ ] **Step 3: Implement canonical receipt generation and CLI**

Add imports `argparse`, `hashlib`, and `json`, then append:

```python
BASE_COMMIT = "cbf229dbd46a7c677fe2e28da882b4f8a02bac7f"
BASE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
DESIGN_PATH = "docs/superpowers/specs/2026-08-24-affine-shell-transducer-design.md"


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def run_wave1(primes: tuple[int, ...]) -> dict[str, object]:
    cases: list[dict[str, object]] = []
    for prime in primes:
        case = first_curve_point(prime)
        row: dict[str, object] = {
            "prime": prime,
            "a": case.a,
            "b": case.b,
        }
        row.update(reference_report(case))
        row["certificate"] = low_degree_shear_certificate(case)
        cases.append(row)
    payload: dict[str, object] = {
        "schema": "affine-shell-wave1-v1",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "design_path": DESIGN_PATH,
        "grammar": "LOW_DEGREE_TWO_REGISTER_SHEARS",
        "cases": cases,
        "verdict": "HARD_NACK_LOW_DEGREE_SHEAR",
        "scope": "translations, additive triangular shears, swaps, constant unit scalings, and zero-only corrections",
        "next_grammar": "REGISTER_SHARED_EUCLID",
        "authority": {
            "provider": False,
            "nonce_grind": False,
            "push": False,
            "submission": False,
        },
    }
    payload["receipt_sha256"] = hashlib.sha256(canonical_json(payload)).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prime", type=int, action="append")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    primes = tuple(args.prime or (31, 127, 251))
    report = run_wave1(primes)
    print(json.dumps(report, sort_keys=True, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run all focused tests and emit the receipt**

Run:

```bash
cd src/point_add/memory/repro
python3 -m unittest -v test_affine_shell_transducer.py
python3 affine_shell_transducer.py --compact > ../42-affine-shell-wave1-receipt.json
python3 affine_shell_transducer.py --compact | shasum -a 256
shasum -a 256 ../42-affine-shell-wave1-receipt.json
```

Expected:

- 6 tests pass, 0 failures;
- both displayed SHA-256 values are identical;
- receipt verdict is `HARD_NACK_LOW_DEGREE_SHEAR`;
- all three cases report zero inverse and curve failures.

- [ ] **Step 5: Write the scoped verdict**

Create `src/point_add/memory/43-affine-shell-wave1-verdict.md` with this exact
content. The content-addressed digest remains authoritative inside the adjacent
JSON receipt, avoiding a second manually copied digest:

```markdown
# Affine-shell wave 1 verdict

Verdict: `HARD_NACK_LOW_DEGREE_SHEAR`.

The exceptional-safe shell is a full permutation and matches curve addition
on every exhaustively checked valid input at p=31, p=127, and p=251. Its
nonzero-fiber Jacobian determinant is `-T`, which assumes every nonzero field
value. Any composition of translations, additive triangular shears, swaps,
constant unit scalings, and zero-only corrections has one constant nonzero
determinant on that region. The grammar therefore cannot realize the target.

This does not close the direct two-register affine-shell family. It proves the
next construction must contain a genuinely variable-coefficient reversible
operation. The next grammar is `REGISTER_SHARED_EUCLID`: data-dependent rows
whose branch is recoverable from bounded length/location metadata instead of a
linear history tape.

No production Rust, provider, nonce, push, public, or submission action is
authorized by this receipt.
```

- [ ] **Step 6: Verify hashes, formatting, and release baseline**

Run:

```bash
git diff --check
cargo build --release --locked --offline --bin build_circuit
python3 -m py_compile src/point_add/memory/repro/affine_shell_transducer.py \
  src/point_add/memory/repro/test_affine_shell_transducer.py
```

Expected: all commands exit 0; the Rust build retains only the three known
warnings from the untouched promoted source.

- [ ] **Step 7: Commit the wave-1 receipt**

```bash
git add src/point_add/memory/repro/affine_shell_transducer.py \
  src/point_add/memory/repro/test_affine_shell_transducer.py \
  src/point_add/memory/42-affine-shell-wave1-receipt.json \
  src/point_add/memory/43-affine-shell-wave1-verdict.md
git commit -m "research: close low degree affine shell grammar"
```

### Task 4: Open the next structural grammar without implementing it

**Files:**
- Create: `docs/superpowers/specs/2026-08-24-register-shared-euclid-question.md`

**Interfaces:**
- Consumes: the wave-1 receipt and exact historical/current owner evidence.
- Produces: one bounded architecture question and one cheapest falsifier for the next design cycle.

- [ ] **Step 1: Write the architecture question**

Create the file with this exact content:

```markdown
# Register-Shared Euclid Architecture Question

Status: bounded design question following
`HARD_NACK_LOW_DEGREE_SHEAR`.

## Question

Can a signed Euclid multiply row become injective on reachable state when
augmented only by `O(log n)` length/location metadata, allowing the branch to
be recomputed during reverse traversal without a linear sign tape?

## Required evidence

- Exhaustive reachable-state enumeration at prime widths 31 and 127.
- One width-parameterized metadata formula used unchanged at both widths.
- Every augmented post-row state has exactly one reachable predecessor.
- The reverse row computes its branch from the augmented state and queries no
  external oracle or table.
- A symbolic 256-bit Q/T equation includes metadata update, branch recovery,
  row arithmetic, inverse traversal, zero handling, and scratch cleanup.

## Continue condition

Continue only if every reachable forward row has one predecessor after adding
the declared metadata, the same metadata formula works at both widths, metadata
is `O(log n)`, and the conservative component projection is at most Q1100 and
T335738.86.

## Kill condition

Kill the exact metadata grammar if any collision requires metadata growing
linearly with row count or field width; any reverse row queries an omitted
oracle; any branch record accumulates across iterations; or the conservative
256-bit component exceeds Q1100 or T335738.86.

## Exclusions

- The killed 254-bit reachable-fiber rank and its exponential count oracle.
- The 796-scratch direct-centered sidecar and its 117-bit branch tail.
- The Q1150/T628k TrailMix lifecycle with a temporary word.
- Arbitrary QROM or truth-table synthesis.
- Production Rust work before the two-width injectivity result.

## Authority

Local reduced-width research only. Provider, nonce, push, public-note,
promotion, and submission gates remain closed.
```

- [ ] **Step 2: Verify and commit the next question**

Run: `git diff --check`

Expected: exit 0.

```bash
git add docs/superpowers/specs/2026-08-24-register-shared-euclid-question.md
git commit -m "research: frame register shared euclid falsifier"
```

## Self-review

- Spec coverage: Tasks 1-3 cover totality, inverse, zero fiber, multi-width
  transfer, deterministic evidence, exact scope, and authority. Task 4 ensures
  a killed grammar advances directly to a different cleanup representation.
- Placeholder scan: no runtime placeholder is copied into source or prose; the
  JSON receipt contains its own deterministic content hash.
- Type consistency: `FieldCase`, oracle tuple types, certificate dictionaries,
  and `run_wave1` names are identical across all tasks.
