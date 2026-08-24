#!/usr/bin/env python3
"""Hard gate for fixed raw and self-delimiting quotient-Euclid compilers."""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
from typing import Any

import affine_shell_transducer as shell
import quotient_euclid_unit_action as recurrence


COMPONENT_Q_CAP = 1_100
COMPONENT_T_CAP = 335_738.86
INPUT_QUBITS = 512
REPLAY_PARTNER_QUBITS = 256

# Archaeological lower-bound ledger from c1aea55. It deliberately grants one
# compare plus one masked subtraction at three Toffolis per active word bit and
# omits alignment, delimiters, pointers, controls, canonicalization, and phase
# cleanup. The 587-Toffoli replay price is from the same internally consistent
# historical ledger, not a current-source component measurement.
HISTORICAL_REPLAY_TOFFOLIS_PER_PAYLOAD_BIT = 587
HISTORICAL_EXTRACT_TOFFOLIS_PER_PAYLOAD_BIT_ONE_WAY = 3 * 256

HISTORICAL_WITNESSES = {
    "ordinary_raw_layout": "f6fc46c465bef21aa157ad9f54917f2b2f07fc8e",
    "prefix_code": "ec4d5d0",
    "live_input_recompute": "13fe1be",
    "centered_rank_decoder": "192bc54",
    "fixed_scan": "0721c17",
    "packed_alignment": "c1aea55",
    "halfgcd_state": "6232c5e",
    "halfgcd_mbuc": "7067522",
}


@functools.lru_cache(maxsize=1)
def _production_witness() -> dict[str, Any]:
    return recurrence.production_sample_report(10_000)


def layout_gate() -> dict[str, Any]:
    witness = _production_witness()
    raw_bits = witness["max_quotient_payload_bits"]
    gamma_bits = witness["max_gamma_bits"]
    scratch_cap = COMPONENT_Q_CAP - INPUT_QUBITS

    def layout(name: str, transcript_bits: int) -> dict[str, Any]:
        peak = INPUT_QUBITS + REPLAY_PARTNER_QUBITS + transcript_bits
        return {
            "name": name,
            "transcript_bits": transcript_bits,
            "replay_partner_qubits": REPLAY_PARTNER_QUBITS,
            "peak_qubits": peak,
            "gap_to_q_cap": peak - COMPONENT_Q_CAP,
            "fits_q": peak <= COMPONENT_Q_CAP,
            "linear_history_violation": transcript_bits > 0,
        }

    return {
        "component_q_cap": COMPONENT_Q_CAP,
        "input_qubits": INPUT_QUBITS,
        "scratch_cap": scratch_cap,
        "sample_count": witness["sample_count"],
        "sample_sha256": witness["sample_sha256"],
        "raw_layout": layout("RAW_CONCATENATED_PAYLOAD", raw_bits),
        "gamma_layout": layout("ELIAS_GAMMA_STREAM", gamma_bits),
    }


def historical_cost_gate() -> dict[str, Any]:
    payload_bits = _production_witness()["max_quotient_payload_bits"]
    replay = payload_bits * HISTORICAL_REPLAY_TOFFOLIS_PER_PAYLOAD_BIT
    extract_one_way = (
        payload_bits * HISTORICAL_EXTRACT_TOFFOLIS_PER_PAYLOAD_BIT_ONE_WAY
    )
    optimistic_total = replay + 2 * extract_one_way
    return {
        "scope": "ARCHAEOLOGICAL_OPTIMISTIC_LEDGER_NOT_CURRENT_MEASUREMENT",
        "payload_bits": payload_bits,
        "replay_toffolis_per_payload_bit": (
            HISTORICAL_REPLAY_TOFFOLIS_PER_PAYLOAD_BIT
        ),
        "extract_toffolis_per_payload_bit_one_way": (
            HISTORICAL_EXTRACT_TOFFOLIS_PER_PAYLOAD_BIT_ONE_WAY
        ),
        "replay_toffolis": replay,
        "extract_one_way_toffolis": extract_one_way,
        "optimistic_total_toffolis": optimistic_total,
        "component_t_cap": COMPONENT_T_CAP,
        "gap_to_component_cap": optimistic_total - COMPONENT_T_CAP,
        "fits_t": optimistic_total <= COMPONENT_T_CAP,
        "omitted_costs": [
            "alignment",
            "self_delimiting_boundaries",
            "pointer_state",
            "controls",
            "modular_canonicalization",
            "phase_repair",
            "ancilla_cleanup",
        ],
    }


def run_gate() -> dict[str, Any]:
    layout = layout_gate()
    cost = historical_cost_gate()
    direct_layouts_fail = (
        not layout["raw_layout"]["fits_q"]
        and not layout["gamma_layout"]["fits_q"]
        and layout["raw_layout"]["linear_history_violation"]
        and layout["gamma_layout"]["linear_history_violation"]
    )
    payload: dict[str, Any] = {
        "schema": "quotient-euclid-static-compiler-gate-v1",
        "scope": "RAW_GAMMA_FIXED_SCAN_AND_ARCHAEOLOGICAL_PARSER_FAMILY",
        "layout_gate": layout,
        "historical_cost_gate": cost,
        "historical_witnesses": HISTORICAL_WITNESSES,
        "direct_layouts_fail": direct_layouts_fail,
        "verdict": (
            "HARD_NACK_QUOTIENT_EUCLID_STATIC_TRANSCRIPT_COMPILER"
            if direct_layouts_fail
            else "HOLD_QUOTIENT_EUCLID_STATIC_TRANSCRIPT_COMPILER"
        ),
        "recurrence_remains_admitted": True,
        "full_field_candidate": False,
        "next_grammar": "ONLINE_TRANSPOSED_UNIT_ACTION",
        "revival_premise": (
            "absorb quotient information into the two output words without a "
            "linear tape, dense decoder, or third persistent field word"
        ),
        "authority": {
            "provider": False,
            "nonce_grind": False,
            "fleet": False,
            "queue": False,
            "push": False,
            "public_note": False,
            "promotion": False,
            "submission": False,
        },
    }
    payload["receipt_sha256"] = hashlib.sha256(shell.canonical_json(payload)).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_gate(), sort_keys=True, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
