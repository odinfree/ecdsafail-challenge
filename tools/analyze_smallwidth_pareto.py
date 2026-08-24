#!/usr/bin/env python3
"""Exact Pareto/step detector for smallwidth_pareto JSONL.

Rows are never compared across different semantics. Single-add kernels,
two-add co-binder kernels, exact boundary repairs, and approximate boundary
repairs each receive separate comparison scopes.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open() as handle:
        for lineno, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("schema") != "smallwidth-pareto-v1":
                raise ValueError(f"{path}:{lineno}: unsupported schema")
            rows.append(row)
    if not rows:
        raise ValueError(f"{path}: no rows")
    commits = {row["source_commit"] for row in rows}
    if len(commits) != 1:
        raise ValueError(f"mixed source commits: {sorted(commits)}")
    return rows


def comparison_scope(row: dict[str, Any]) -> str:
    if row["family"] == "boundary_repair":
        repair = row["boundary_repair"]
        return "boundary_exact" if repair != "approximate_no_cin" else "boundary_approx"
    if row["family"] == "co_binder_topclean":
        return "two_add_co_binder"
    return "single_exact_add"


def dominates(left: dict[str, Any], right: dict[str, Any]) -> bool:
    lq, lt = left["peak_qubits"], left["emitted_toffoli"]
    rq, rt = right["peak_qubits"], right["emitted_toffoli"]
    return lq <= rq and lt <= rt and (lq < rq or lt < rt)


def pareto(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    values = list(rows)
    frontier = [row for row in values if not any(dominates(other, row) for other in values)]
    return sorted(
        frontier,
        key=lambda row: (
            row["peak_qubits"],
            row["emitted_toffoli"],
            row["family"],
            row["knob_value"],
        ),
    )


def median_abs_deviation(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    median = statistics.median(values)
    mad = statistics.median(abs(value - median) for value in values)
    return float(median), float(mad)


def row_id(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "width_bits": row["width_bits"],
        "family": row["family"],
        "boundary_repair": row["boundary_repair"],
        "knob_name": row["knob_name"],
        "knob_value": row["knob_value"],
    }


def detect_events(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    by_series: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_series[
            (
                row["width_bits"],
                row["family"],
                row["boundary_repair"],
                row["knob_name"],
            )
        ].append(row)

    for key, series in sorted(by_series.items()):
        series.sort(key=lambda row: row["knob_value"])
        deltas_q = [
            float(right["peak_qubits"] - left["peak_qubits"])
            for left, right in zip(series, series[1:])
        ]
        deltas_t = [
            float(right["emitted_toffoli"] - left["emitted_toffoli"])
            for left, right in zip(series, series[1:])
        ]
        median_q, mad_q = median_abs_deviation(deltas_q)
        median_t, mad_t = median_abs_deviation(deltas_t)
        for left, right in zip(series, series[1:]):
            dq = right["peak_qubits"] - left["peak_qubits"]
            dt = right["emitted_toffoli"] - left["emitted_toffoli"]
            reasons: list[str] = []
            if right["peak_owner"] != left["peak_owner"]:
                reasons.append("peak_owner_migration")
            if dq == 0 and dt != 0:
                reasons.append("qubit_plateau")
            q_threshold = max(1.0, 3.0 * mad_q)
            t_threshold = max(1.0, 3.0 * mad_t)
            if abs(dq - median_q) > q_threshold:
                reasons.append("qubit_step")
            if abs(dt - median_t) > t_threshold:
                reasons.append("toffoli_step")
            if reasons:
                events.append(
                    {
                        "schema": "smallwidth-discontinuity-v1",
                        "event": "adjacent_step",
                        "series": {
                            "width_bits": key[0],
                            "family": key[1],
                            "boundary_repair": key[2],
                            "knob_name": key[3],
                        },
                        "left": row_id(left),
                        "right": row_id(right),
                        "delta_q": dq,
                        "delta_t": dt,
                        "median_delta_q": median_q,
                        "median_delta_t": median_t,
                        "reasons": reasons,
                    }
                )

    by_scope: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_scope[(row["width_bits"], comparison_scope(row))].append(row)
    for (width, scope), scope_rows in sorted(by_scope.items()):
        for left, right in zip(pareto(scope_rows), pareto(scope_rows)[1:]):
            dq = right["peak_qubits"] - left["peak_qubits"]
            dt = right["emitted_toffoli"] - left["emitted_toffoli"]
            events.append(
                {
                    "schema": "smallwidth-discontinuity-v1",
                    "event": "pareto_adjacency",
                    "width_bits": width,
                    "comparison_scope": scope,
                    "left": row_id(left),
                    "right": row_id(right),
                    "delta_q": dq,
                    "delta_t": dt,
                    "toffoli_per_qubit_saved": (
                        None if dq == 0 else abs(dt / dq)
                    ),
                }
            )
    return events


def coefficient_of_variation(values: list[float]) -> float:
    if not values:
        return math.inf
    mean = statistics.fmean(values)
    return 0.0 if mean == 0 else statistics.pstdev(values) / abs(mean)


def lift_assessment(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compare normalized rows at canonical, scale-independent knob points."""
    selected: dict[tuple[str, str, float], list[dict[str, Any]]] = defaultdict(list)
    canonical_ratios = (0.0, 0.25, 0.5, 0.75)
    for row in rows:
        if row["family"] in {"topclean", "co_binder_topclean"}:
            ratio = min(canonical_ratios, key=lambda value: abs(value - row["knob_ratio"]))
            if abs(ratio - row["knob_ratio"]) <= 1.0 / row["width_bits"]:
                selected[(row["family"], row["boundary_repair"], ratio)].append(row)
        elif row["family"] == "lowq":
            selected[(row["family"], row["boundary_repair"], 0.0)].append(row)
        elif row["family"] == "boundary_repair" and row["knob_ratio"] in canonical_ratios:
            selected[(row["family"], row["boundary_repair"], row["knob_ratio"])].append(row)

    assessments: list[dict[str, Any]] = []
    for (family, repair, ratio), group in sorted(selected.items()):
        # One nearest row per width.
        by_width: dict[int, dict[str, Any]] = {}
        for row in group:
            current = by_width.get(row["width_bits"])
            if current is None or abs(row["knob_ratio"] - ratio) < abs(
                current["knob_ratio"] - ratio
            ):
                by_width[row["width_bits"]] = row
        if len(by_width) < 3:
            continue
        values = list(by_width.values())
        q_cv = coefficient_of_variation([row["q_per_n"] for row in values])
        t_cv = coefficient_of_variation([row["t_per_n"] for row in values])
        if max(q_cv, t_cv) <= 0.05:
            verdict = "transferable_linear_mechanism"
        elif max(q_cv, t_cv) <= 0.15:
            verdict = "finite_size_correction_needed"
        else:
            verdict = "constant_or_scale_specific"
        assessments.append(
            {
                "schema": "smallwidth-lift-v1",
                "family": family,
                "boundary_repair": repair,
                "knob_ratio": ratio,
                "widths": sorted(by_width),
                "q_per_n_cv": q_cv,
                "t_per_n_cv": t_cv,
                "verdict": verdict,
            }
        )
    return assessments


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def write_summary(
    path: Path,
    rows: list[dict[str, Any]],
    events: list[dict[str, Any]],
    lifts: list[dict[str, Any]],
) -> None:
    widths = sorted({row["width_bits"] for row in rows})
    owners = [event for event in events if "peak_owner_migration" in event.get("reasons", [])]
    plateaus = [event for event in events if "qubit_plateau" in event.get("reasons", [])]
    exact_boundary = [
        row
        for row in rows
        if row["boundary_repair"] == "topW_with_window_entry_carry"
    ]
    approximate_boundary = {
        (row["width_bits"], row["knob_value"]): row
        for row in rows
        if row["boundary_repair"] == "approximate_no_cin"
    }
    paired = [
        (approximate_boundary[(row["width_bits"], row["knob_value"])], row)
        for row in exact_boundary
        if (row["width_bits"], row["knob_value"]) in approximate_boundary
    ]
    q_deltas = sorted({exact["peak_qubits"] - approx["peak_qubits"] for approx, exact in paired})
    t_deltas = sorted(
        {exact["emitted_toffoli"] - approx["emitted_toffoli"] for approx, exact in paired}
    )

    lines = [
        "# Reduced-width Pareto summary",
        "",
        "Hypothesis origin: Justin Drake. Any promoted circuit win derived from this lane must credit him.",
        "",
        f"- Source: `{rows[0]['source_commit']}`",
        f"- Widths: {', '.join(map(str, widths))}",
        f"- Resource rows: {len(rows)}",
        f"- Detected peak-owner migrations: {len(owners)}",
        f"- Detected qubit plateaus: {len(plateaus)}",
        "- Adder normalization: `Q/n`, `T/n`; `T/n^2` is retained for comparison with quadratic point-add stages.",
        "",
        "## Boundary-repair lead",
        "",
        "`topW_with_window_entry_carry` is locally exact, while `approximate_no_cin` has",
        "uniform-input fault probability `2^-(W+1)`. Across measured widths/windows the exact",
        f"repair changes peak Q by {q_deltas or ['n/a']} and emitted T by {t_deltas or ['n/a']}.",
        "This is a candidate mechanism, not a 256-bit circuit win: the promoted route must still",
        "prove or host the carry entering the top-W slice and re-run trusted validation.",
        "",
        "## Lift classifications",
        "",
    ]
    for lift in lifts:
        lines.append(
            f"- `{lift['family']}` / `{lift['boundary_repair']}` at ratio "
            f"{lift['knob_ratio']:.2f}: **{lift['verdict']}** "
            f"(CV Q/n={lift['q_per_n_cv']:.3f}, T/n={lift['t_per_n_cv']:.3f})."
        )
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--lifts", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()

    rows = load_rows(args.input)
    events = detect_events(rows)
    lifts = lift_assessment(rows)
    write_jsonl(args.events, events)
    write_jsonl(args.lifts, lifts)
    write_summary(args.summary, rows, events, lifts)


if __name__ == "__main__":
    main()
