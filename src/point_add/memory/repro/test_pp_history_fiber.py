from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPRO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPRO_DIR))

from pp_history_fiber import Config, bit1, half_mod, run_case


class ArithmeticTests(unittest.TestCase):
    def test_bit1_uses_fixed_width_twos_complement(self) -> None:
        self.assertEqual(bit1(-1, 5), 1)
        self.assertEqual(bit1(-3, 5), 0)

    def test_half_mod_is_inverse_of_doubling(self) -> None:
        for value in range(29):
            self.assertEqual((2 * half_mod(value, 29)) % 29, value)

    def test_each_walk_step_is_integral_and_odd(self) -> None:
        trace = run_case(Config(width=5, modulus=29, rounds=12), 7, 11)
        for state in trace.states:
            self.assertEqual(state.u & 1, 1)
            self.assertEqual(state.v & 1, 1)


if __name__ == "__main__":
    unittest.main()
