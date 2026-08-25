import hashlib
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import final_carry_gate_oracle as oracle


EVIDENCE = pathlib.Path(__file__).with_name("final_carry_handoff_evidence.json")
ORACLE_EVIDENCE = pathlib.Path(__file__).with_name(
    "final_carry_gate_oracle_evidence.json"
)


class PhaseAndGadgetTests(unittest.TestCase):
    def test_phase_and_gadget_is_exhaustive_clean_and_costed(self) -> None:
        report = oracle.exhaust_phase_and_gadget(range(5, 10))

        self.assertEqual(report["widths"], [5, 6, 7, 8, 9])
        self.assertEqual(report["basis_cases"], sum(1 << n for n in range(5, 10)))
        self.assertEqual(report["phase_mismatches"], 0)
        self.assertEqual(report["ancilla_mismatches"], 0)
        self.assertEqual(
            report["toffoli_class_by_width"],
            {str(n): n - 2 for n in range(5, 10)},
        )

    def test_nontrivial_phase_gadget_mutations_turn_green_to_red(self) -> None:
        report = oracle.phase_gadget_mutation_report(range(5, 10))

        self.assertEqual(
            set(report),
            {"drop_terminal_ccz", "wrong_prefix_control", "skip_hmr_correction"},
        )
        for mutation, result in report.items():
            with self.subTest(mutation=mutation):
                self.assertGreater(result["phase_mismatches"], 0)
                self.assertIsNotNone(result["first_witness"])


class DelayedCarryCircuitTests(unittest.TestCase):
    def test_delayed_carry_program_executes_forward_and_inverse_cleanup(self) -> None:
        report = oracle.exhaust_delayed_carry_program(range(5, 10))

        self.assertEqual(report["widths"], [5, 6, 7, 8, 9])
        self.assertEqual(
            report["basis_cases"],
            sum(1 << (2 * n + 1) for n in range(5, 10)),
        )
        self.assertEqual(report["forward_value_mismatches"], 0)
        self.assertEqual(report["source_restore_mismatches"], 0)
        self.assertEqual(report["inverse_cleanup_mismatches"], 0)
        self.assertEqual(report["phase_coefficient_mismatches"], 0)
        self.assertEqual(report["ancilla_mismatches"], 0)
        self.assertEqual(report["uncovered_measurement_arms"], [])

    def test_delayed_carry_mutations_turn_gate_oracle_green_to_red(self) -> None:
        report = oracle.delayed_carry_mutation_report(range(5, 10))

        self.assertEqual(
            set(report),
            {
                "drop_top_restore",
                "wrong_hmr_control",
                "skip_delayed_inverse",
            },
        )
        for mutation, result in report.items():
            with self.subTest(mutation=mutation):
                total = sum(
                    result[key]
                    for key in (
                        "forward_value_mismatches",
                        "source_restore_mismatches",
                        "inverse_cleanup_mismatches",
                        "phase_coefficient_mismatches",
                        "ancilla_mismatches",
                    )
                )
                self.assertGreater(total, 0)
                self.assertIsNotNone(result["first_witness"])


class FusedFoldCircuitTests(unittest.TestCase):
    def test_fused_fold_gate_program_covers_all_digits_and_cleanup(self) -> None:
        report = oracle.exhaust_fused_fold_program(range(5, 10))

        self.assertEqual(report["widths"], [5, 6, 7, 8, 9])
        self.assertEqual(report["covered_digits"], [-1, 0, 1, 2])
        self.assertEqual(
            report["basis_cases"],
            sum(4 * (1 << n) for n in range(5, 10)),
        )
        self.assertEqual(report["forward_value_mismatches"], 0)
        self.assertEqual(report["selector_restore_mismatches"], 0)
        self.assertEqual(report["inverse_cleanup_mismatches"], 0)
        self.assertEqual(report["phase_coefficient_mismatches"], 0)
        self.assertEqual(report["ancilla_mismatches"], 0)

    def test_fused_fold_mutations_turn_gate_oracle_green_to_red(self) -> None:
        report = oracle.fused_fold_mutation_report(range(5, 10))

        self.assertEqual(
            set(report),
            {"drop_terminal_carry", "wrong_minus_orientation", "skip_fold_hmr_correction"},
        )
        for mutation, result in report.items():
            with self.subTest(mutation=mutation):
                total = sum(
                    result[key]
                    for key in (
                        "forward_value_mismatches",
                        "selector_restore_mismatches",
                        "inverse_cleanup_mismatches",
                        "phase_coefficient_mismatches",
                        "ancilla_mismatches",
                    )
                )
                self.assertGreater(total, 0)
                self.assertIsNotNone(result["first_witness"])


class DirtyHostSynthesisTests(unittest.TestCase):
    def test_one_nonlinear_gate_cannot_convert_disjoint_dirty_host(self) -> None:
        report = oracle.exhaust_single_dirty_host_synthesis()

        self.assertEqual(report["basis_cases"], 16)
        self.assertEqual(report["affine_forms"], 32)
        self.assertEqual(report["one_gate_candidates"], 1_024)
        self.assertEqual(report["one_gate_solutions"], 0)
        self.assertTrue(report["two_gate_witness_passes"])
        self.assertTrue(report["clean_host_one_gate_control_passes"])

    def test_every_exact_cell_needs_dirty_host_reuse_at_three_saved_ccx(self) -> None:
        evidence = json.loads(EVIDENCE.read_text())
        report = oracle.exact_reuse_requirement_report(
            evidence["static_census_records"],
            saved_ccx_per_cell=3,
            peak_limit=1_266,
        )

        self.assertEqual(report["cells"], 1_383)
        self.assertEqual(report["cells_requiring_reuse"], 1_383)
        self.assertEqual(report["minimum_reused_hosts"], 5)
        self.assertEqual(report["maximum_reused_hosts"], 37)
        self.assertEqual(report["gross_average_t"], 2_074.5)
        self.assertEqual(report["net_if_one_depth1_gate_per_cell"], 1_383.0)
        self.assertEqual(report["net_if_one_unconditioned_gate_per_cell"], 691.5)

    def test_arbitrary_clifford_conjugation_still_needs_two_products(self) -> None:
        report = oracle.exhaust_affine_dirty_host_conjugation()

        self.assertEqual(report["basis_cases"], 16)
        self.assertEqual(report["physical_affine_forms"], 64)
        self.assertEqual(report["control_pairs"], 4_096)
        self.assertEqual(report["one_gate_span_swap_solutions"], 0)
        self.assertTrue(report["two_gate_span_swap_witness_passes"])
        self.assertTrue(report["mutation_drop_dirty_term_has_solutions"])
        self.assertTrue(report["mutation_allow_mixed_residual_has_solutions"])

    def test_selector_function_rank_covers_every_exact_local_arm(self) -> None:
        report = oracle.selector_code_rank_report()

        for site, arms in (("divide", 8), ("multiply", 16)):
            with self.subTest(site=site):
                row = report[site]
                self.assertEqual(row["local_arms"], arms)
                self.assertEqual(row["exact_source_witnessed_arms"], arms)
                self.assertEqual(row["operand_function_rank"], 3)
                self.assertEqual(row["operand_plus_first_carry_rank"], 4)
                self.assertEqual(row["operand_first_and_final_carry_rank"], 5)
                self.assertEqual(row["distinct_operand_functions"], 5)
        self.assertEqual(report["divide"]["zero_t_wire_reclaim_upper_bound"], 0)
        self.assertEqual(report["multiply"]["zero_t_wire_reclaim_upper_bound"], 1)

    def test_strong_phase_and_selector_optimism_still_forces_reuse(self) -> None:
        evidence = json.loads(EVIDENCE.read_text())
        report = oracle.optimistic_phase_host_report(
            evidence["static_census_records"],
            saved_ccx_per_cell=3,
            phase_terminal_discount=25,
            free_selector_wires=1,
            peak_limit=1_266,
        )

        self.assertEqual(report["cells"], 1_383)
        self.assertEqual(report["unretained_bits_at_same_phase_cost"], 43)
        self.assertEqual(report["cells_still_requiring_host_reuse"], 1_170)
        self.assertEqual(report["minimum_reused_hosts"], 0)
        self.assertEqual(report["maximum_reused_hosts"], 11)
        self.assertEqual(report["gross_average_t"], 2_074.5)
        self.assertEqual(
            report["added_if_one_depth1_gate_per_affected_cell"], 585.0
        )
        self.assertEqual(report["net_upper_bound_after_one_depth1_gate"], 1_489.5)

    def test_retained_carry_bank_has_full_independent_source_valid_image(self) -> None:
        report = oracle.carry_bank_independence_report(range(5, 10), exact_rank=37)

        self.assertEqual(report["reduced_widths"], [5, 6, 7, 8, 9])
        self.assertEqual(report["reduced_patterns"], sum(1 << n for n in range(5, 10)))
        self.assertEqual(report["reduced_recurrence_mismatches"], 0)
        self.assertEqual(report["reduced_missing_patterns"], 0)
        self.assertEqual(report["exact_rank"], 37)
        self.assertEqual(report["exact_patterns_per_site"], 41)
        self.assertEqual(report["exact_canonical_mismatches"], 0)
        self.assertEqual(report["exact_recurrence_mismatches"], 0)
        self.assertEqual(report["exact_low_fold_state_mismatches"], 0)
        self.assertEqual(
            report["sites"],
            {"divide": {"patterns": 41}, "multiply": {"patterns": 41}},
        )

    def test_retained_carries_are_independent_modulo_the_live_add_interface(self) -> None:
        report = oracle.carry_checkpoint_quotient_rank_report(range(5, 10))

        self.assertEqual(report["reduced_widths"], [5, 6, 7, 8, 9])
        self.assertEqual(
            report["reduced_raw_carry_quotient_rank"],
            {str(width): width for width in range(5, 10)},
        )
        self.assertEqual(
            report["reduced_transformed_carry_quotient_rank"],
            {str(width): width for width in range(5, 10)},
        )
        self.assertEqual(report["rank_mismatches"], 0)
        self.assertEqual(report["exact_axis_source_valid_patterns"], 513)
        self.assertEqual(report["exact_canonical_mismatches"], 0)
        self.assertEqual(report["exact_recurrence_mismatches"], 0)
        self.assertEqual(
            report["exact_transfer"],
            {
                "divide": {
                    "maximum_final_chunk_width": 127,
                    "quotient_rank": 127,
                    "source_valid_patterns": 131,
                },
                "multiply": {
                    "maximum_final_chunk_width": 128,
                    "quotient_rank": 128,
                    "source_valid_patterns": 132,
                },
            },
        )

    def test_fold_value_nonlinear_rank_already_uses_every_source_ccx(self) -> None:
        report = oracle.fold_nonlinear_rank_report(range(5, 10))

        self.assertEqual(
            report["reduced_nonlinear_rank"],
            {str(width): width - 2 for width in range(5, 10)},
        )
        self.assertEqual(
            report["reduced_source_ccx"],
            {str(width): width - 2 for width in range(5, 10)},
        )
        self.assertEqual(
            report["exact"],
            {
                "divide": {"width": 54, "nonlinear_rank": 52, "source_ccx": 52},
                "multiply": {"width": 53, "nonlinear_rank": 51, "source_ccx": 51},
            },
        )
        self.assertEqual(report["rank_mismatches"], 0)

    def test_separable_handoff_dichotomy_exceeds_added_cost_ceiling(self) -> None:
        evidence = json.loads(EVIDENCE.read_text())
        report = oracle.separable_handoff_cost_report(
            evidence["static_census_records"], peak_limit=1_266
        )

        self.assertEqual(report["cells"], 1_383)
        self.assertEqual(report["cells_requiring_release_or_reuse"], 1_170)
        self.assertEqual(report["unitary_dirty_swap_extra_gates_per_affected_cell"], 1)
        self.assertEqual(report["measured_checkpoint_extra_phase_gates_per_affected_cell"], 1)
        self.assertEqual(report["minimum_added_average_t"], 585.0)
        self.assertEqual(report["allowed_added_average_t"], 574.5)
        self.assertEqual(report["net_average_t_upper_bound"], 1_489.5)
        self.assertFalse(report["economics_can_reach_target"])
        self.assertFalse(report["is_terminal_whole_family_proof"])

    def test_two_bank_global_affine_amortization_still_needs_overhead(self) -> None:
        report = oracle.exhaust_two_bank_affine_conjugation()

        self.assertEqual(report["logical_variables"], 8)
        self.assertEqual(report["physical_affine_forms_per_side"], 2_048)
        self.assertEqual(report["admissible_first_products_start"], 8)
        self.assertEqual(report["admissible_first_products_goal"], 8)
        self.assertEqual(report["one_gate_subspaces_start"], 3_582)
        self.assertEqual(report["one_gate_subspaces_goal"], 3_582)
        self.assertEqual(report["two_gate_clean_intersections"], 0)
        self.assertEqual(report["clean_fold_product_gates"], 2)
        self.assertEqual(report["dirty_swap_gate_lower_bound"], 3)
        self.assertGreater(report["mutation_keep_dirty_offsets_intersections"], 0)

    def test_two_bank_mixed_quadratic_catalyst_cannot_make_a_three_gate_swap(self) -> None:
        report = oracle.exhaust_two_bank_quadratic_catalysts()

        self.assertEqual(report["logical_variables"], 8)
        self.assertEqual(report["decomposable_quadratic_forms"], 10_795)
        self.assertEqual(report["dirty_to_fold_graph_isomorphisms"], 6)
        self.assertEqual(report["three_generator_coset_candidates"], 64_770)
        self.assertEqual(report["three_decomposable_generator_solutions"], 0)
        self.assertEqual(report["decomposable_generator_lower_bound"], 4)
        self.assertTrue(report["four_generator_clear_create_witness"])
        self.assertEqual(report["mutation_allow_rank_four_direct_solutions"], 6)
        self.assertFalse(report["is_larger_bank_direct_sum_proof"])


class GateOracleEvidenceTests(unittest.TestCase):
    def test_compact_packet_is_bound_nonterminal_and_matches_live_checks(self) -> None:
        raw = ORACLE_EVIDENCE.read_bytes()
        evidence = json.loads(raw)
        census = json.loads(EVIDENCE.read_text())["static_census_records"]

        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            "bc2397ca3403aa05cbf03d234f4d7441110e03a306ca5f963066f1068f7ad73c",
        )
        self.assertEqual(evidence["schema"], "final-carry-gate-oracle-evidence-v1")
        self.assertEqual(
            evidence["binding"]["source_commit"],
            "522d00296ab014b0f4d128915b53851516f17f4d",
        )
        self.assertEqual(
            evidence["binding"]["source_tree"],
            "eab2326ce33549eceeb5c10aa64eae33f148b0ac",
        )
        self.assertEqual(evidence["status"], "ALIVE_GLOBAL_MIXED_ENCODING_GAP")
        self.assertFalse(evidence["admission"])
        self.assertFalse(evidence["whole_family_hard_nack"])
        self.assertEqual(evidence["primitive_oracles"]["mutation_reds"], 9)

        quotient = oracle.carry_checkpoint_quotient_rank_report(range(5, 10))
        catalysts = oracle.exhaust_two_bank_quadratic_catalysts()
        cost = oracle.separable_handoff_cost_report(census, peak_limit=1_266)
        s4 = oracle.optimistic_phase_host_report(
            census,
            saved_ccx_per_cell=4,
            phase_terminal_discount=25,
            free_selector_wires=1,
            peak_limit=1_266,
        )
        self.assertEqual(evidence["carry_quotient_rank"], quotient)
        self.assertEqual(evidence["two_bank_quadratic_catalysts"], catalysts)
        self.assertEqual(evidence["separable_s3_cost"], cost)
        self.assertEqual(evidence["higher_savings_loophole_s4"], s4)


if __name__ == "__main__":
    unittest.main()
