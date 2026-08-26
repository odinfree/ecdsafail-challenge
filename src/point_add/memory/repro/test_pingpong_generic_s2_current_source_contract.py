from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
ROUTE = REPO / "src/point_add/pingpong_div.rs"
POINT_ADD = REPO / "src/point_add/mod.rs"


def function_body(source: str, name: str) -> str:
    match = re.search(rf"fn\s+{re.escape(name)}\s*\(", source)
    if match is None:
        raise AssertionError(f"missing function {name}")
    start = source.find("{", match.end())
    depth = 0
    for index in range(start, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]
    raise AssertionError(f"unterminated function {name}")


class CurrentSourceGenericS2ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.route = ROUTE.read_text()
        cls.point_add = POINT_ADD.read_text()

    def test_zero_route_env_bakes_exact_composition(self) -> None:
        for name, value in {
            "SUB4_PP_THIRD_PASSENGER": "1",
            "SUB4_PP_FOURTH_PASSENGER": "0",
            "SUB4_PP_ELIDE_ROUND0_A0": "1",
            "SUB4_PP_ELIDE_GENERIC_S2": "1",
        }.items():
            self.assertRegex(
                self.point_add,
                rf'set_default_env\("{name}",\s*"{value}"\)',
                name,
            )

    def test_a0_route_lock_composes_with_fourth_off(self) -> None:
        self.assertIn('(\"SUB4_PP_THIRD_PASSENGER\", \"1\")', self.route)
        self.assertIn('(\"SUB4_PP_FOURTH_PASSENGER\", \"0\")', self.route)
        self.assertIn('(\"SUB4_PP_ELIDE_ROUND0_A0\", \"1\")', self.route)

    def test_generic_s2_parser_is_fail_closed_and_source_bound(self) -> None:
        parser = function_body(self.route, "generic_s2_elision_enabled")
        self.assertRegex(parser, r"None\s*=>\s*false")
        self.assertRegex(parser, r'value\s*==\s*"0"\s*=>\s*false')
        self.assertRegex(parser, r'value\s*==\s*"1"\s*=>\s*true')
        self.assertIn("panic!", parser)
        self.assertRegex(
            parser,
            re.compile(
                r"if\s+enabled\s*\{.*?require_round0_a0_exact_route\(\).*?"
                r'SUB4_PP_ELIDE_GENERIC_S2.*?Some\("1"\)',
                re.DOTALL,
            ),
        )

        entry = function_body(self.route, "pingpong_mod_mul_div_in_place")
        self.assertIn("let _ = generic_s2_elision_enabled()", entry)
        self.assertIn("let selected_plan = plan(direction, rounds)", entry)
        self.assertRegex(
            entry,
            re.compile(
                r"!generic_s2_elision_enabled\(\)\s*\|\|\s*selected_plan\.is_some\(\)",
                re.DOTALL,
            ),
        )

    def test_round_two_owns_no_wire_and_every_consumer_gets_a_host(self) -> None:
        self.assertGreaterEqual(self.route.count("tape.push(NO_QUBIT)"), 2)
        self.assertGreaterEqual(self.route.count("assert_eq!(tape[2], NO_QUBIT"), 1)

        main = function_body(self.route, "pingpong_mod_mul_div_in_place")
        self.assertEqual(main.count("toggle_checkpoint_s2_host"), 4)
        self.assertRegex(
            main,
            re.compile(
                r"if\s+r\s*==\s*2\s*&&\s*generic_s2_elision_enabled\(\).*?"
                r"toggle_checkpoint_s2_host.*?replay_halving_round.*?"
                r"toggle_checkpoint_s2_host",
                re.DOTALL,
            ),
        )
        self.assertRegex(
            main,
            re.compile(
                r"if\s+r\s*==\s*2\s*&&\s*generic_s2_elision_enabled\(\).*?"
                r"toggle_checkpoint_s2_host.*?replay_doubling_round.*?"
                r"toggle_checkpoint_s2_host",
                re.DOTALL,
            ),
        )

    def test_local_affine_transform_is_exact_and_restored(self) -> None:
        toggle = function_body(self.route, "toggle_local_s2_host")
        self.assertIn("assert_ne!(host, NO_QUBIT", toggle)
        self.assertIn("SECP256K1_P.bit(1)", toggle)
        self.assertIn("b.cx(source[1], host)", toggle)

        forward = function_body(self.route, "walk_round2_with_s1_host")
        self.assertEqual(forward.count("toggle_local_s2_host"), 2)
        self.assertIn("let round = 2usize", forward)
        self.assertIn("signed_add_wrapping", forward)

        reverse = function_body(self.route, "walk_back_round2_with_s1_host")
        self.assertEqual(reverse.count("toggle_local_s2_host"), 2)
        self.assertLess(
            reverse.index("grow_to(b, u, v, width)"),
            reverse.index("toggle_local_s2_host"),
        )
        self.assertIn("let reset_scratch = b.alloc_qubit()", reverse)
        self.assertIn("b.free(reset_scratch)", reverse)

    def test_checkpoint_affine_transform_excludes_sentinel(self) -> None:
        toggle = function_body(self.route, "toggle_checkpoint_s2_host")
        self.assertIn("assert_eq!(tape[2], NO_QUBIT", toggle)
        self.assertIn("let host = tape[1]", toggle)
        self.assertIn("SECP256K1_P.bit(1)", toggle)
        self.assertIn("b.cx(old_operand[1], host)", toggle)
        self.assertIn("&tape[3..]", toggle)
        self.assertNotIn("tape[2]", toggle[toggle.index("for &sign") :])

    def test_forward_and_reverse_walk_lifecycles_dispatch_hosting(self) -> None:
        entry = function_body(self.route, "pingpong_mod_mul_div_in_place")
        self.assertIn("walk_round2_with_s1_host", entry)
        self.assertIn("walk_back_round2_with_s1_host", entry)

        forward = function_body(self.route, "value_walk")
        self.assertIn("walk_round2_with_s1_host", forward)
        self.assertIn("tape.push(NO_QUBIT)", forward)

        reverse = function_body(self.route, "value_walk_back")
        self.assertIn("assert_eq!(tape[round], NO_QUBIT)", reverse)
        self.assertIn("walk_back_round2_with_s1_host", reverse)

    def test_affine_width_selfcheck_is_dispatched_before_build(self) -> None:
        selfcheck = function_body(self.route, "generic_s2_host_selfcheck")
        self.assertIn("for width in 4..=10usize", selfcheck)
        self.assertIn("for denominator in 1..p", selfcheck)
        self.assertIn("tape[2], NO_QUBIT", selfcheck)
        self.assertRegex(
            self.point_add,
            re.compile(
                r"SUB4_PP_GENERIC_S2_SELFTEST.*?generic_s2_host_selfcheck\(\);.*?"
                r"return Vec::new\(\);",
                re.DOTALL,
            ),
        )


if __name__ == "__main__":
    unittest.main()
