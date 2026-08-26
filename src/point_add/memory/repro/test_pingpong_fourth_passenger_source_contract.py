from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
ROUTE = REPO / "src/point_add/pingpong_div.rs"


class FourthPassengerSourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = ROUTE.read_text()

    def assert_source(self, pattern: str, label: str) -> None:
        self.assertIsNotNone(
            re.search(pattern, self.source, re.DOTALL),
            f"missing fourth-passenger {label}",
        )

    def test_exact_literal_flag_and_third_precondition_are_wired(self) -> None:
        self.assert_source(
            r'fn\s+fourth_interleaved_passenger_enabled\(.*?'
            r'std::env::var\("SUB4_PP_FOURTH_PASSENGER"\).*?'
            r'std::env::var\("SUB4_PP_THIRD_PASSENGER"\).*?'
            r'fourth_feature_enabled\(',
            "literal flag and third precondition",
        )

    def test_loan_struct_retains_the_exact_inverse_recipe(self) -> None:
        self.assert_source(
            r'struct\s+InterleavedPassengerLoan\s*\{.*?'
            r'fourth:\s*Option<\(QubitId,\s*Vec<QubitId>\)>',
            "loan field",
        )
        self.assert_source(
            r'let\s+fourth\s*=\s*if\s+fourth_interleaved_passenger_enabled.*?'
            r'fourth_passenger\(after_round\).*?'
            r'BitOnePassenger::U\s*=>\s*u\[1\].*?'
            r'BitOnePassenger::V\s*=>\s*v\[1\]',
            "parity-selected opposite bit-1 wire",
        )

    def test_clear_is_x_then_complete_tape_fan_in_and_release(self) -> None:
        self.assert_source(
            r'fourth_tape_control_indices\(\s*after_round,\s*tape\.len\(\)\s*,?\s*\).*?'
            r'b\.x\(passenger\);.*?'
            r'for\s+index\s+in\s+control_indices.*?'
            r'b\.cx\(tape\[index\],\s*passenger\);.*?'
            r'b\.release_clean\(passenger\);',
            "clear sequence",
        )

    def test_fourth_is_nonaliasing_with_odd_third_and_tape_controls(self) -> None:
        self.assert_source(
            r'assert!\(!odd\.contains\(&passenger\)\);.*?'
            r'if\s+let\s+Some\(\(third_passenger,\s*_,\s*_\)\)\s*=\s*third.*?'
            r'assert_ne!\(passenger,\s*third_passenger\);.*?'
            r'assert!\(controls\.iter\(\)\.all\(\|&control\|\s*control\s*!=\s*passenger\)\);',
            "nonalias checks",
        )

    def test_restore_reacquires_fourth_first_and_exactly_reverses_clear(self) -> None:
        self.assert_source(
            r'fn\s+restore_interleaved_odd_passengers.*?'
            r'if\s+let\s+Some\(\(passenger,\s*controls\)\)\s*=\s*loan\.fourth\s*\{'
            r'.*?b\.reacquire\(passenger\);.*?'
            r'for\s+&control\s+in\s+controls\.iter\(\)\.rev\(\).*?'
            r'b\.cx\(control,\s*passenger\);.*?'
            r'b\.x\(passenger\);.*?\}\s*'
            r'if\s+let\s+Some\(\(passenger,\s*source2,\s*tape1\)\)\s*=\s*loan\.third',
            "LIFO inverse restore",
        )


if __name__ == "__main__":
    unittest.main()
