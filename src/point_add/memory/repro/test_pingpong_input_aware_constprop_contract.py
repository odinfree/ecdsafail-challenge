#!/usr/bin/env python3

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
POINT_ADD = ROOT / "mod.rs"
CONSTPROP = ROOT / "trailmix_ludicrous" / "constprop.rs"


class PingpongInputAwareConstpropContractTest(unittest.TestCase):
    def pingpong_return_block(self) -> str:
        source = POINT_ADD.read_text()
        start = source.index("let mut ops = pingpong_div::build_pingpong_point_add();")
        end = source.index("return ops;", start)
        return source[start:end]

    def test_constprop_api_accepts_explicit_public_bits(self) -> None:
        source = CONSTPROP.read_text()
        start = source.index("fn analyze(")
        end = source.index("let mut decisions", start)
        constant_analyzer_setup = source[start:end]
        self.assertIn("pub(crate) fn run_with_inputs", source)
        self.assertIn("input_bits: &[BitId]", source)
        self.assertIn("b: vec![Zero; num_b]", constant_analyzer_setup)
        self.assertIn("for &bit in input_bits", constant_analyzer_setup)
        self.assertIn("a.b[bit.0 as usize] = Unknown", constant_analyzer_setup)

    def test_f11_hook_binds_exact_public_register_geometry(self) -> None:
        block = self.pingpong_return_block()
        self.assertIn('var_os("SUB4_PINGPONG_INPUT_AWARE_CONSTPROP")', block)
        self.assertIn("(0..512).map(QubitId)", block)
        self.assertIn("(0..512).map(BitId)", block)
        self.assertIn("constprop::run_with_inputs", block)

    def test_exact_mode_disables_cascade_and_straddle(self) -> None:
        block = self.pingpong_return_block()
        self.assertIn('var("TLM_CASCADE_DISABLE")', block)
        self.assertIn('Some("1")', block)
        self.assertIn('var_os("TLM_CONSTPROP_STRADDLE").is_none()', block)

    def test_constprop_runs_before_protected_tail(self) -> None:
        block = self.pingpong_return_block()
        self.assertLess(
            block.index("constprop::run_with_inputs"),
            block.index("ops.extend(std::iter::repeat_n(x, 96))"),
        )

    def test_f20_profile_scans_the_post_nonce_candidate(self) -> None:
        block = self.pingpong_return_block()
        self.assertIn('var_os("SUB4_PINGPONG_F20_PROFILE")', block)
        self.assertLess(block.index("apply_tail_nonce"), block.index("dirtyscan::scan"))

    def test_profile_reports_classical_condition_discounted_t(self) -> None:
        source = (ROOT / "dirtyscan.rs").read_text()
        self.assertIn("executed_t", source)
        self.assertIn("cond.count_ones()", source)

    def test_profile_binds_full_state_and_authoritative_t_counter(self) -> None:
        source = (ROOT / "dirtyscan.rs").read_text()
        self.assertIn("outcome_digest", source)
        self.assertIn("sim.stats.toffoli_gates", source)
        self.assertIn("mirror executed-T counter diverged", source)

    def test_transform_trace_binds_each_source_condition(self) -> None:
        source = CONSTPROP.read_text()
        self.assertIn('var_os("CONSTPROP_TRANSFORM_TRACE")', source)
        self.assertIn("CONSTPROP_TRANSFORM label=", source)
        self.assertIn("op.c_condition.0", source)


if __name__ == "__main__":
    unittest.main()
