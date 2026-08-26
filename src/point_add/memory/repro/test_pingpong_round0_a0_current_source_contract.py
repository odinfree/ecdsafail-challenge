from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
ROUTE = REPO / "src/point_add/pingpong_div.rs"
POINT_ADD = REPO / "src/point_add/mod.rs"
SELECTOR = REPO / "src/point_add/pingpong_third_passenger_selector.rs"

EXACT_ROUTE = {
    "SUB4_PP_ROUNDS": "695",
    "SUB4_PP_ROUNDS_MUL": "694",
    "SUB4_PP_R1": "335",
    "SUB4_PP_R1_MUL": "315",
    "SUB4_PP_R2": "645",
    "SUB4_PP_PEAK": "1267",
    "SUB4_PP_WALK_PEAK": "1265",
    "SUB4_PP_REPLAY_CHUNK": "96",
    "SUB4_PP_REPLAY_CHUNK_COMPARE": "22",
    "SUB4_PP_REPLAY_FOLD_WINDOW": "54",
    "SUB4_PP_REPLAY_FOLD_WINDOW_MUL": "53",
    "SUB4_PP_ENDPOINT_FOLD_WINDOW": "26",
    "SUB4_PP_REPLAY_FLAG_COMPARE": "22",
    "SUB4_PP_SIGNED_FRAME": "0",
    "SUB4_PINGPONG_LOW56_FOLD": "1",
    "SUB4_PINGPONG_INPUT_AWARE_CONSTPROP": "1",
    "SUB4_PP_THIRD_PASSENGER": "1",
    "SUB4_PP_FOURTH_PASSENGER": "0",
    "SUB4_PP_FUSE_ROUND1": "1",
    "SUB4_PP_ROUND0_SPARSE_FWD": "1",
    "SUB4_APPLY_STRIP": "0",
    "SUB4_SQUARE_CHUNK_MIN": "18446744073709551615",
    "SUB4_SQUARE_LADDER": "243",
    "SUB4_SQUARE_KARATSUBA2": "1",
    "SUB4_SQUARE_BK2_MIN": "128",
    "SUB4_SQUARE_B_LOCAL_K2": "1",
    "SUB4_SQUARE_AMAT_MIN": "128",
    "SUB4_SQUARE_CMAT_MIN": "128",
    "SUB4_SQUARE_A_MAT": "1",
    "SUB4_SQUARE_C_MAT": "1",
    "TLM_CASCADE_DISABLE": "1",
    "TLM_FFG_MAX_G": "55",
    "SUB4_PINGPONG_TAIL_NONCE": "12023044890526",
    "SUB4_PP_ELIDE_ROUND0_A0": "1",
}

FORBIDDEN_ROUTE_ENV = {
    "SUB4_PP_SCHED_LINEAR",
    "SUB4_PP_WSCHED_FILE",
    "SUB4_PP_SCHED_BIAS",
    "SUB4_PP_WIDTH_RESCALE",
    "SUB4_PP_WIDTH_REPAIR",
    "SUB4_PP_WALK_TOP_SKIP",
    "SUB4_PP_NO_WALK_SPLIT",
    "SUB4_PP_LEGACY_LADDER",
    "SUB4_PP_NO_INTERLEAVE",
    "SUB4_PP_LEGACY_CHUNK_ORDER",
    "SUB4_PP_LOAN_ONE",
    "SUB4_PP_SIGNED_REPAIR",
    "SUB4_PINGPONG_SEPARATE_LIFT",
    "SUB4_PINGPONG_SEPARATE_ENDPOINT",
    "SUB4_PINGPONG_SPLIT_ROUND0",
    "SUB4_PINGPONG_UNFUSED_INVERSE",
    "SUB4_PINGPONG_GENERIC_WALK",
    "SUB4_PINGPONG_KEEP_ODD_LIFT",
    "SUB4_SQUARE_ACK2_MIN",
    "TLM_CONSTPROP_STRADDLE",
}


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


class CurrentSourceRoundZeroA0ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.route = ROUTE.read_text()
        cls.point_add = POINT_ADD.read_text()
        cls.selector = SELECTOR.read_text()

    def test_zero_route_env_bakes_every_exact_candidate_knob(self) -> None:
        for name, value in EXACT_ROUTE.items():
            if name in {"SUB4_APPLY_STRIP", "TLM_FFG_MAX_G"}:
                pattern = rf'std::env::set_var\("{name}",\s*"{value}"\)'
            else:
                pattern = rf'set_default_env\("{name}",\s*"{value}"\)'
            self.assertRegex(self.point_add, pattern, name)

    def test_official_g55_and_fallback_nonce_are_preserved(self) -> None:
        g55 = self.point_add.index('std::env::set_var("TLM_FFG_MAX_G", "55")')
        baked = self.point_add.index('set_default_env("SUB4_PP_ELIDE_ROUND0_A0", "1")')
        fallback = self.point_add.index(".unwrap_or(12023044890526)")
        self.assertLess(g55, baked)
        self.assertLess(baked, fallback)

    def test_enabled_feature_raw_locks_every_exact_knob(self) -> None:
        for name, value in EXACT_ROUTE.items():
            self.assertIn(f'("{name}", "{value}")', self.route, name)
        lock = function_body(self.route, "require_round0_a0_exact_route")
        self.assertIn("std::env::var(name)", lock)
        self.assertIn("assert_eq!(raw, want", lock)
        self.assertNotIn("rounds()", lock)
        self.assertNotIn("tuned_window", lock)
        parser = function_body(self.route, "round0_a0_elision_enabled")
        self.assertRegex(
            parser,
            re.compile(r"if\s+enabled\s*\{.*?require_round0_a0_exact_route\(\)", re.DOTALL),
        )

    def test_enabled_feature_rejects_every_route_override(self) -> None:
        for name in FORBIDDEN_ROUTE_ENV:
            self.assertIn(f'"{name}"', self.route, name)
        lock = function_body(self.route, "require_round0_a0_exact_route")
        self.assertIn("std::env::var_os(name).is_none()", lock)

    def test_parser_is_fail_closed_outside_baked_builder(self) -> None:
        parser = function_body(self.route, "round0_a0_elision_enabled")
        self.assertRegex(parser, r"None\s*=>\s*false")
        self.assertRegex(parser, r'value\s*==\s*"0"\s*=>\s*false')
        self.assertRegex(parser, r'value\s*==\s*"1"\s*=>\s*true')
        self.assertIn("panic!", parser)

    def test_all_four_round_zero_lifecycles_use_fail_closed_wrappers(self) -> None:
        self.assertEqual(self.route.count("walk_round0_forward_tape(b, v)"), 2)
        self.assertEqual(self.route.count("walk_round0_reverse_tape(b, v,"), 2)
        self.assertNotRegex(
            self.route,
            r"if\s+round\s*==\s*0.*?fused_lift_round0_(?:forward|reverse)\(b,\s*v",
        )
        reverse = function_body(self.route, "walk_round0_reverse_tape")
        self.assertIn("assert_eq!(tape0, crate::circuit::NO_QUBIT)", reverse)
        self.assertIn("let a0 = b.alloc_qubit()", reverse)
        self.assertIn("b.cx(v[N - 1], a0)", reverse)

    def test_round_zero_replay_never_consumes_the_sentinel(self) -> None:
        halve = function_body(self.route, "replay_halving_round")
        round0_halve = re.search(r"if\s+round\s*==\s*0\s*\{(.*?)\}", halve, re.DOTALL)
        self.assertIsNotNone(round0_halve)
        self.assertNotIn("sign", round0_halve.group(1))
        double = function_body(self.route, "replay_doubling_round")
        self.assertRegex(double, r"if\s+fused\s*&&\s*round\s*>\s*1")
        self.assertRegex(double, r"else\s+if\s+round\s*>\s*1\s*&&\s*!fused")
        self.assertNotRegex(double, r"round\s*==\s*0.*?(?:b\.(?:x|cx|ccx)|signed_).*?sign")

    def test_passenger_controls_start_at_tape_one(self) -> None:
        loan = function_body(self.route, "loan_interleaved_odd_passengers")
        self.assertIn("tape[1]", loan)
        self.assertNotIn("tape[0]", loan)
        controls = function_body(self.selector, "fourth_tape_control_indices")
        self.assertIn("Ok(1..=after_round)", controls)
        self.assertIn('after_round == 0', controls)

    def test_round_zero_reconstruction_occurs_after_width_restoration(self) -> None:
        direct = function_body(self.route, "walk_back_round")
        self.assertLess(direct.index("grow_to(b, u, v, width)"), direct.index("walk_round0_reverse_tape"))
        full = function_body(self.route, "value_walk_back")
        self.assertLess(full.index("while u.len() < width"), full.index("walk_round0_reverse_tape"))

    def test_directed_selfcheck_is_dispatched_before_build(self) -> None:
        self.assertIn("pub(crate) fn round0_a0_elision_selfcheck()", self.route)
        self.assertRegex(
            self.point_add,
            re.compile(
                r'SUB4_PP_ROUND0_A0_SELFTEST.*?round0_a0_elision_selfcheck\(\);.*?return Vec::new\(\);',
                re.DOTALL,
            ),
        )

    def test_a0_differential_isolates_then_restores_generic_s2_host(self) -> None:
        selfcheck = function_body(self.route, "round0_a0_elision_selfcheck")
        disable = selfcheck.index('set_var("SUB4_PP_ELIDE_GENERIC_S2", "0")')
        retained = selfcheck.index("let retained_walk = run_walk_lifecycle(false)")
        restore = selfcheck.index('set_var("SUB4_PP_ELIDE_GENERIC_S2", "1")')
        simulator = selfcheck.index("pingpong_simulator_selfcheck()")
        self.assertLess(disable, retained)
        self.assertLess(retained, restore)
        self.assertLess(restore, simulator)

    def test_dense_exception_boundaries_are_exact(self) -> None:
        modulus = (1 << 256) - (1 << 32) - 977
        f = (1 << 256) - modulus
        h = (f - 1) // 2
        low_last = f - 2
        high_first = (1 << 256) - 2 * f + 2
        high_last = modulus - 3

        def exceptional(value: int) -> bool:
            half = value >> 1
            if value & 3 == 3:
                return half < h
            if value & 3 == 0:
                return bool(((half + f) & ((1 << 256) - 1)) >> 255)
            return False

        matches = [0, 1, 2, f + 2, high_first - 4, modulus - 4, modulus - 2, modulus - 1]
        exceptions = [3, low_last, high_first, high_last]
        self.assertTrue(all(not exceptional(value) for value in matches))
        self.assertTrue(all(exceptional(value) for value in exceptions))
        self.assertEqual(h, 2_147_484_136)


if __name__ == "__main__":
    unittest.main()
