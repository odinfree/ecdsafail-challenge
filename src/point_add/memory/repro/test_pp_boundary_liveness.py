from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPRO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPRO_DIR))

from pp_boundary_liveness import (
    PeakOwner,
    chunk_input_collisions,
    dependency_chain,
    maj_host_forward,
    maj_host_inverse,
    render_receipt,
    top_window_ambiguities,
)


class InformationTests(unittest.TestCase):
    def test_chunk_outputs_do_not_determine_input_carry(self) -> None:
        for width in range(1, 9):
            collisions = chunk_input_collisions(width)
            self.assertGreater(len(collisions), 0)
            witness = collisions[0]
            self.assertEqual(witness.left.output_key, witness.right.output_key)
            self.assertNotEqual(witness.left.carry_in, witness.right.carry_in)

    def test_top_window_needs_its_exact_entry_carry(self) -> None:
        for width in range(2, 9):
            for window in range(1, width):
                self.assertGreater(len(top_window_ambiguities(width, window)), 0)


class SourceHostTests(unittest.TestCase):
    def test_maj_host_round_trips_with_predecessor(self) -> None:
        for source in (0, 1):
            for accumulator in (0, 1):
                for predecessor in (0, 1):
                    hosted = maj_host_forward(source, accumulator, predecessor)
                    self.assertEqual(
                        maj_host_inverse(*hosted),
                        (source, source ^ accumulator ^ predecessor, predecessor),
                    )

    def test_host_state_without_predecessor_is_noninjective(self) -> None:
        states: dict[tuple[int, int], set[tuple[int, int, int]]] = {}
        for source in (0, 1):
            for accumulator in (0, 1):
                for predecessor in (0, 1):
                    hosted_source, twisted_acc, _ = maj_host_forward(
                        source, accumulator, predecessor
                    )
                    states.setdefault((hosted_source, twisted_acc), set()).add(
                        (source, accumulator, predecessor)
                    )
        self.assertTrue(any(len(inputs) > 1 for inputs in states.values()))

    def test_binding_entry_requires_full_predecessor_chain(self) -> None:
        self.assertEqual(dependency_chain(106), tuple(range(105, -1, -1)))


class BindingTests(unittest.TestCase):
    def test_owner_equation_is_q1267(self) -> None:
        owner = PeakOwner()
        self.assertEqual(owner.total, 1267)
        self.assertEqual(owner.entry_carry_index, 106)
        self.assertEqual(owner.q1268_strict_t_ceiling, 910671)

    def test_receipt_is_byte_deterministic(self) -> None:
        first = render_receipt([])
        self.assertEqual(first, render_receipt([]))
        receipt = json.loads(first)
        self.assertEqual(receipt["peak_owner"]["total"], 1267)
        self.assertEqual(receipt["verdict"], "HARD_NACK_ONE_ENTRY_CARRY_HOST")


if __name__ == "__main__":
    unittest.main()
