#!/usr/bin/env python3
"""Machine-check the exact asymmetric-Q1265 plus F20 composition packet."""

from __future__ import annotations

import argparse
import json
import re
import struct
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from artifact_io import RECORD_BYTES, _zstd, fingerprint, read_header


NO_BIT = (1 << 64) - 1
ADMIT = "ADMIT_TO_HUMAN_REVIEW_F21"

_TRANSFORM_RE = re.compile(
    r"^CONSTPROP_TRANSFORM label=(?P<label>\S+) "
    r"index=(?P<index>\d+) decision=(?P<decision>.*?) "
    r"kind=(?P<kind>\S+) .* condition=(?P<condition>\d+)$"
)
_ITER_RE = re.compile(
    r"^CONSTPROP iter=(?P<iter>\d+) ccx_total=(?P<ccx_total>\d+) "
    r"dropped=(?P<dropped>\d+) folded_cx=(?P<folded_cx>\d+) "
    r"folded_x=(?P<folded_x>\d+) inverse_pairs=(?P<inverse_pairs>\d+) "
    r"aff_drop=(?P<aff_drop>\d+) aff_fold=(?P<aff_fold>\d+) "
    r"\(this-iter toffoli removed = (?P<removed>\d+)\)$"
)


def _integer(value: str, field: str) -> int:
    try:
        return int(value, 0)
    except ValueError as error:
        raise ValueError(f"DIRTY_SCAN {field} is not an integer: {value}") from error


def _fraction(value: str, field: str) -> tuple[int, int]:
    pieces = value.split("/", 1)
    if len(pieces) != 2:
        raise ValueError(f"DIRTY_SCAN {field} is not count/rounds: {value}")
    return _integer(pieces[0], field), _integer(pieces[1], field)


def parse_scan(text: str) -> dict[str, Any]:
    """Parse exactly one faithful DIRTY_SCAN summary from stderr text."""

    summaries = [
        line for line in text.splitlines() if line.startswith("DIRTY_SCAN rounds=")
    ]
    if len(summaries) != 1:
        raise ValueError(
            f"expected exactly one DIRTY_SCAN summary, found {len(summaries)}"
        )
    faithful_count = text.count(
        "DIRTY_SCAN mirror_check -> FAITHFUL (qubits, bits and phase all agree)"
    )
    if faithful_count != 1:
        raise ValueError(
            f"expected exactly one faithful mirror check, found {faithful_count}"
        )

    raw: dict[str, str] = {}
    for token in summaries[0].split()[1:]:
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        if key in raw:
            raise ValueError(f"duplicate DIRTY_SCAN field: {key}")
        raw[key] = value

    integer_fields = (
        "rounds",
        "lanes",
        "ops",
        "executed_t",
        "classical",
        "phase_shots",
        "any_fault_shots",
        "dirty_free_events",
    )
    required = {
        *integer_fields,
        "average_t",
        "phase_bad_rounds",
        "ancilla_bad_rounds",
        "attributable",
        "last_phase",
        "outcome_digest",
    }
    missing = sorted(required - raw.keys())
    if missing:
        raise ValueError(f"DIRTY_SCAN missing fields: {', '.join(missing)}")

    parsed: dict[str, Any] = {field: _integer(raw[field], field) for field in integer_fields}
    try:
        parsed["average_t"] = float(raw["average_t"])
    except ValueError as error:
        raise ValueError(f"DIRTY_SCAN average_t is invalid: {raw['average_t']}") from error
    parsed["phase_bad_rounds"] = _fraction(
        raw["phase_bad_rounds"], "phase_bad_rounds"
    )
    parsed["ancilla_bad_rounds"] = _fraction(
        raw["ancilla_bad_rounds"], "ancilla_bad_rounds"
    )
    if raw["attributable"] not in {"true", "false"}:
        raise ValueError("DIRTY_SCAN attributable must be true or false")
    parsed["attributable"] = raw["attributable"] == "true"
    parsed["last_phase"] = _integer(raw["last_phase"], "last_phase")
    digest = raw["outcome_digest"].lower()
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("DIRTY_SCAN outcome_digest must be 64 lowercase hex digits")
    parsed["outcome_digest"] = digest
    parsed["mirror_faithful"] = True
    return parsed


def parse_transforms(text: str) -> list[dict[str, Any]]:
    transforms: list[dict[str, Any]] = []
    for line in text.splitlines():
        if not line.startswith("CONSTPROP_TRANSFORM "):
            continue
        match = _TRANSFORM_RE.fullmatch(line)
        if match is None:
            raise ValueError(f"malformed CONSTPROP_TRANSFORM row: {line}")
        row: dict[str, Any] = match.groupdict()
        row["index"] = int(row["index"])
        row["condition"] = int(row["condition"])
        transforms.append(row)
    return transforms


def parse_iterations(text: str) -> list[dict[str, int]]:
    iterations: list[dict[str, int]] = []
    for line in text.splitlines():
        if not line.startswith("CONSTPROP iter="):
            continue
        match = _ITER_RE.fullmatch(line)
        if match is None:
            raise ValueError(f"malformed CONSTPROP iteration row: {line}")
        iterations.append({key: int(value) for key, value in match.groupdict().items()})
    return iterations


def map_transform_indices(transforms: list[dict[str, Any]]) -> list[int]:
    """Map constant/affine pass indices back to the baseline operation stream."""

    constant_drops = sorted(
        row["index"]
        for row in transforms
        if row["label"] == "constant" and row["decision"].startswith("Drop")
    )
    original_indices: list[int] = []
    for row in transforms:
        if row["label"] == "constant":
            original_indices.append(row["index"])
            continue
        if row["label"] != "affine":
            raise ValueError(f"unsupported transform label: {row['label']}")
        original = row["index"]
        for dropped in constant_drops:
            if dropped <= original:
                original += 1
        original_indices.append(original)
    if len(set(original_indices)) != len(original_indices):
        raise ValueError("transform source indices are not unique after remapping")
    return original_indices


def verify_transform_source_binding(
    baseline_path: Path, transforms: list[dict[str, Any]]
) -> dict[str, int]:
    """Bind every trace row to an unconditional baseline CCX at stack depth zero."""

    original_indices = map_transform_indices(transforms)
    wanted = set(original_indices)
    found = 0
    kind_ccx = 0
    direct_no_bit = 0
    depth_zero = 0
    condition_depth = 0
    decoded_ops = 0
    remainder = b""
    with baseline_path.open("rb", buffering=0) as source:
        _, expected_ops = read_header(source)
        decoder = subprocess.Popen(
            [_zstd(), "-d", "-q", "-c"],
            stdin=source,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert decoder.stdout is not None
        while data := decoder.stdout.read(RECORD_BYTES * 100_000):
            data = remainder + data
            complete = len(data) - len(data) % RECORD_BYTES
            for offset in range(0, complete, RECORD_BYTES):
                kind = struct.unpack_from("<I", data, offset)[0]
                if decoded_ops in wanted:
                    condition = struct.unpack_from("<Q", data, offset + 40)[0]
                    found += 1
                    kind_ccx += kind == 13
                    direct_no_bit += condition == NO_BIT
                    depth_zero += condition_depth == 0
                if kind == 15:
                    condition_depth += 1
                elif kind == 16:
                    condition_depth -= 1
                    if condition_depth < 0:
                        raise ValueError(
                            f"condition stack underflow at baseline op {decoded_ops}"
                        )
                decoded_ops += 1
            remainder = data[complete:]
        decoder.stdout.close()
        stderr = (
            decoder.stderr.read().decode("utf-8", errors="replace")
            if decoder.stderr
            else ""
        )
        if decoder.stderr:
            decoder.stderr.close()
        returncode = decoder.wait()
    if returncode != 0:
        raise RuntimeError(f"zstd decoder failed: {stderr.strip()}")
    if remainder or decoded_ops != expected_ops:
        raise ValueError("baseline artifact record stream is incomplete")
    if condition_depth != 0:
        raise ValueError("baseline artifact ends inside a pushed condition")
    expected = len(transforms)
    if (found, kind_ccx, direct_no_bit, depth_zero) != (expected,) * 4:
        raise ValueError(
            "transform source binding failed: "
            f"found={found} kind_ccx={kind_ccx} direct_no_bit={direct_no_bit} "
            f"depth_zero={depth_zero} expected={expected}"
        )
    return {
        "transforms": expected,
        "constant": sum(row["label"] == "constant" for row in transforms),
        "affine": sum(row["label"] == "affine" for row in transforms),
        "constant_drops": sum(
            row["label"] == "constant" and row["decision"].startswith("Drop")
            for row in transforms
        ),
        "kind_ccx": kind_ccx,
        "direct_no_bit": direct_no_bit,
        "condition_stack_depth_zero": depth_zero,
        "decoded_ops": decoded_ops,
        "final_condition_depth": condition_depth,
    }


def _require_q1265(name: str, facts: dict[str, Any]) -> None:
    if facts.get("qubits") != 1265 or facts.get("max_referenced_qubit_id") != 1264:
        raise ValueError(
            f"{name} is not exact Q1265/QID1264: "
            f"qubits={facts.get('qubits')} max_qid={facts.get('max_referenced_qubit_id')}"
        )


def check_evidence(
    baseline_fingerprint: dict[str, Any],
    candidate_fingerprint: dict[str, Any],
    baseline_scan: dict[str, Any],
    candidate_scan: dict[str, Any],
    transforms: list[dict[str, Any]],
    iterations: list[dict[str, int]],
    expected_rounds: int,
) -> dict[str, Any]:
    """Validate the exact F21 pair and return a deterministic admission record."""

    _require_q1265("baseline", baseline_fingerprint)
    _require_q1265("candidate", candidate_fingerprint)
    for name, facts, scan in (
        ("baseline", baseline_fingerprint, baseline_scan),
        ("candidate", candidate_fingerprint, candidate_scan),
    ):
        if scan["rounds"] != expected_rounds or scan["lanes"] != 64 * expected_rounds:
            raise ValueError(
                f"{name} scan geometry mismatch: rounds={scan['rounds']} "
                f"lanes={scan['lanes']} expected_rounds={expected_rounds}"
            )
        if scan["ops"] != facts["emitted_ops"]:
            raise ValueError(
                f"{name} scan/artifact op mismatch: {scan['ops']} != {facts['emitted_ops']}"
            )
        average = scan["executed_t"] / scan["lanes"]
        if abs(scan["average_t"] - average) > 5e-9:
            raise ValueError(f"{name} average_t does not match executed_t/lanes")
        for field in ("phase_bad_rounds", "ancilla_bad_rounds"):
            if scan[field][1] != expected_rounds:
                raise ValueError(f"{name} {field} denominator does not match rounds")

    if candidate_fingerprint["emitted_ops"] >= baseline_fingerprint["emitted_ops"]:
        raise ValueError("candidate does not reduce emitted operations")

    state_fields = (
        "classical",
        "phase_shots",
        "any_fault_shots",
        "phase_bad_rounds",
        "ancilla_bad_rounds",
        "dirty_free_events",
        "attributable",
        "last_phase",
        "outcome_digest",
    )
    for field in state_fields:
        if candidate_scan[field] != baseline_scan[field]:
            raise ValueError(
                f"paired complete-state field {field} differs: "
                f"{baseline_scan[field]} != {candidate_scan[field]}"
            )

    if not transforms:
        raise ValueError("candidate has no traced transforms")
    if any(row["condition"] != NO_BIT for row in transforms):
        raise ValueError("every transform must have direct condition NO_BIT")
    if any(row["kind"] != "CCX" for row in transforms):
        raise ValueError("every transform must originate from CCX")

    if len(iterations) < 2 or [row["iter"] for row in iterations] != list(
        range(1, len(iterations) + 1)
    ):
        raise ValueError("candidate must report contiguous iterations and a fixpoint")
    first = iterations[0]
    final = iterations[-1]
    if first["removed"] <= 0 or final["removed"] != 0:
        raise ValueError("candidate must end at a zero-removal fixpoint")
    removal_fields = (
        "dropped",
        "folded_cx",
        "folded_x",
        "inverse_pairs",
        "aff_drop",
        "aff_fold",
    )
    if any(final[field] != 0 for field in removal_fields):
        raise ValueError("candidate final iteration is not a complete fixpoint")
    if len(transforms) != first["removed"]:
        raise ValueError("transform census does not match first-pass T removals")

    executed_t_delta = baseline_scan["executed_t"] - candidate_scan["executed_t"]
    lanes = baseline_scan["lanes"]
    if executed_t_delta <= 0 or executed_t_delta % lanes:
        raise ValueError("executed-T reduction is not positive integral per-lane")
    per_lane = executed_t_delta // lanes
    if per_lane != first["removed"]:
        raise ValueError(
            "executed-T per-lane delta does not equal unconditional transform removals"
        )

    classes = Counter(row["label"] for row in transforms)
    decisions = Counter(row["decision"].split(" ", 1)[0] for row in transforms)
    return {
        "verdict": ADMIT,
        "expected_rounds": expected_rounds,
        "lanes": lanes,
        "baseline_ops": baseline_fingerprint["emitted_ops"],
        "candidate_ops": candidate_fingerprint["emitted_ops"],
        "operation_delta": (
            candidate_fingerprint["emitted_ops"]
            - baseline_fingerprint["emitted_ops"]
        ),
        "baseline_executed_t": baseline_scan["executed_t"],
        "candidate_executed_t": candidate_scan["executed_t"],
        "executed_t_delta_per_lane": per_lane,
        "transform_count": len(transforms),
        "transform_classes": dict(sorted(classes.items())),
        "transform_decisions": dict(sorted(decisions.items())),
        "all_direct_no_bit": True,
        "fixpoint_iterations": len(iterations),
        "paired_outcome_digest": baseline_scan["outcome_digest"],
        "baseline_fingerprint": baseline_fingerprint,
        "candidate_fingerprint": candidate_fingerprint,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-ops", required=True, type=Path)
    parser.add_argument("--candidate-ops", required=True, type=Path)
    parser.add_argument("--baseline-log", required=True, type=Path)
    parser.add_argument("--candidate-log", required=True, type=Path)
    parser.add_argument("--expected-rounds", required=True, type=int)
    args = parser.parse_args()

    baseline_text = args.baseline_log.read_text()
    candidate_text = args.candidate_log.read_text()
    if parse_transforms(baseline_text) or parse_iterations(baseline_text):
        raise ValueError("baseline unexpectedly contains constprop evidence")
    transforms = parse_transforms(candidate_text)
    result = check_evidence(
        fingerprint(args.baseline_ops),
        fingerprint(args.candidate_ops),
        parse_scan(baseline_text),
        parse_scan(candidate_text),
        transforms,
        parse_iterations(candidate_text),
        args.expected_rounds,
    )
    result["source_binding"] = verify_transform_source_binding(
        args.baseline_ops, transforms
    )
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
