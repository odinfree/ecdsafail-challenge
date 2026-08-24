#!/usr/bin/env python3
"""Exact field-polynomial separation census on curve-supported shell states."""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
import hashlib
import json

import affine_shell_transducer as shell
import curve_support_product_invariants as support


BASE_COMMIT = "cbf229dbd46a7c677fe2e28da882b4f8a02bac7f"
BASE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
DEFAULT_PRIMES = (31, 61, 127, 251)
Node = tuple[str, int]
Edge = tuple[int, int, int]


def _node_json(node: Node) -> dict[str, int | str]:
    return {"kind": "T" if node[0] == "t" else "lambda", "value": node[1]}


def _edge_json(edge: Edge) -> dict[str, int]:
    t, lam, product = edge
    return {"T": t, "lambda": lam, "product": product}


def _edge_nodes(edge: Edge) -> tuple[Node, Node]:
    return ("t", edge[0]), ("l", edge[1])


def _cycle_from_conflict(
    prime: int,
    left: Node,
    right: Node,
    conflict: Edge,
    parent: dict[Node, tuple[Node, Edge] | None],
) -> dict[str, object]:
    def path(node: Node) -> tuple[list[Node], list[Edge]]:
        nodes = [node]
        edges: list[Edge] = []
        while parent[node] is not None:
            previous, edge = parent[node]
            edges.append(edge)
            node = previous
            nodes.append(node)
        return nodes, edges

    left_nodes, left_edges = path(left)
    right_nodes, right_edges = path(right)
    right_positions = {node: index for index, node in enumerate(right_nodes)}
    left_stop = next(
        index for index, node in enumerate(left_nodes) if node in right_positions
    )
    common = left_nodes[left_stop]
    right_stop = right_positions[common]

    cycle_nodes = left_nodes[: left_stop + 1] + list(
        reversed(right_nodes[:right_stop])
    )
    cycle_edges = (
        left_edges[:left_stop]
        + list(reversed(right_edges[:right_stop]))
        + [conflict]
    )
    if len(cycle_nodes) != len(cycle_edges) or len(cycle_nodes) % 2:
        raise AssertionError("bipartite conflict did not produce an even cycle")

    residual = sum(
        (1 if index % 2 == 0 else -1) * edge[2]
        for index, edge in enumerate(cycle_edges)
    ) % prime
    if residual == 0:
        raise AssertionError("conflicting edge produced a zero cycle residual")
    return {
        "prime": prime,
        "nodes": [_node_json(node) for node in cycle_nodes],
        "edges": [_edge_json(edge) for edge in cycle_edges],
        "alternating_residual": residual,
    }


def verify_cycle_witness(witness: dict[str, object]) -> bool:
    prime = int(witness["prime"])
    nodes = [
        (
            "t" if row["kind"] == "T" else "l",
            int(row["value"]),
        )
        for row in witness["nodes"]
    ]
    edges = [
        (int(row["T"]), int(row["lambda"]), int(row["product"]))
        for row in witness["edges"]
    ]
    if len(nodes) != len(edges) or len(nodes) % 2:
        return False
    for index, edge in enumerate(edges):
        endpoints = set(_edge_nodes(edge))
        if endpoints != {nodes[index], nodes[(index + 1) % len(nodes)]}:
            return False
        if edge[2] != edge[0] * edge[1] % prime:
            return False
    residual = sum(
        (1 if index % 2 == 0 else -1) * edge[2]
        for index, edge in enumerate(edges)
    ) % prime
    return residual != 0 and residual == int(witness["alternating_residual"])


def support_graph_certificate(prime: int) -> dict[str, object]:
    if not support._is_prime(prime):
        raise ValueError("modulus must be prime")
    _case, rows = support._support_rows(prime)
    adjacency: dict[Node, list[tuple[Node, Edge]]] = defaultdict(list)
    for _x, _y, _d, t, lam, product in rows:
        edge = (t, lam, product)
        t_node = ("t", t)
        lambda_node = ("l", lam)
        adjacency[t_node].append((lambda_node, edge))
        adjacency[lambda_node].append((t_node, edge))

    potential: dict[Node, int] = {}
    parent: dict[Node, tuple[Node, Edge] | None] = {}
    component_count = 0
    witness: dict[str, object] | None = None
    for root in sorted(adjacency):
        if root in potential:
            continue
        component_count += 1
        potential[root] = 0
        parent[root] = None
        queue = deque([root])
        while queue:
            left = queue.popleft()
            for right, edge in adjacency[left]:
                wanted = (edge[2] - potential[left]) % prime
                if right not in potential:
                    potential[right] = wanted
                    parent[right] = (left, edge)
                    queue.append(right)
                elif potential[right] != wanted and witness is None:
                    witness = _cycle_from_conflict(
                        prime, left, right, edge, parent
                    )

    potential_failures = sum(
        (potential[("t", t)] + potential[("l", lam)] - product) % prime != 0
        for _x, _y, _d, t, lam, product in rows
    )
    return {
        "prime": prime,
        "support_states": len(rows),
        "distinct_T": len({row[3] for row in rows}),
        "distinct_lambda": len({row[4] for row in rows}),
        "vertices": len(adjacency),
        "components": component_count,
        "unrestricted_separable": witness is None,
        "potential_failures": potential_failures,
        "cycle_witness": witness,
    }


class _FieldColumnBasis:
    def __init__(self, prime: int) -> None:
        self.prime = prime
        self.rows: dict[int, tuple[list[int], dict[int, int]]] = {}

    def add(self, column: list[int], index: int) -> bool:
        p = self.prime
        vector = list(column)
        combination = {index: 1}
        for pivot in sorted(self.rows):
            row, row_combination = self.rows[pivot]
            scale = vector[pivot]
            if not scale:
                continue
            vector = [(left - scale * right) % p for left, right in zip(vector, row)]
            for source, coefficient in row_combination.items():
                combination[source] = (
                    combination.get(source, 0) - scale * coefficient
                ) % p
                if combination[source] == 0:
                    del combination[source]
        try:
            pivot = next(index for index, value in enumerate(vector) if value)
        except StopIteration:
            return False
        inverse = pow(vector[pivot], p - 2, p)
        vector = [value * inverse % p for value in vector]
        combination = {
            source: coefficient * inverse % p
            for source, coefficient in combination.items()
        }
        self.rows[pivot] = (vector, combination)
        return True

    def solve(self, target: list[int]) -> dict[int, int] | None:
        p = self.prime
        vector = list(target)
        solution: dict[int, int] = {}
        for pivot in sorted(self.rows):
            row, combination = self.rows[pivot]
            scale = vector[pivot]
            if not scale:
                continue
            vector = [(left - scale * right) % p for left, right in zip(vector, row)]
            for source, coefficient in combination.items():
                solution[source] = (
                    solution.get(source, 0) + scale * coefficient
                ) % p
                if solution[source] == 0:
                    del solution[source]
        return None if any(vector) else solution


def _minimum_polynomial_solution(
    prime: int,
    rows: list[tuple[int, int, int, int, int, int]],
    target: list[int],
) -> tuple[int, list[str], dict[int, int]]:
    t_values = [row[3] for row in rows]
    lambda_values = [row[4] for row in rows]
    maximum_degree = max(len(set(t_values)), len(set(lambda_values))) - 1
    basis = _FieldColumnBasis(prime)
    names = ["1"]
    basis.add([1] * len(rows), 0)
    t_power = [1] * len(rows)
    lambda_power = [1] * len(rows)
    for degree in range(1, maximum_degree + 1):
        t_power = [value * t % prime for value, t in zip(t_power, t_values)]
        lambda_power = [
            value * lam % prime for value, lam in zip(lambda_power, lambda_values)
        ]
        names.append(f"T^{degree}")
        basis.add(t_power, len(names) - 1)
        names.append(f"lambda^{degree}")
        basis.add(lambda_power, len(names) - 1)
        solution = basis.solve(target)
        if solution is not None:
            return degree, names, solution
    raise AssertionError("consistent support graph was not polynomially interpolable")


def _solution_failures(
    prime: int,
    rows: list[tuple[int, int, int, int, int, int]],
    target: list[int],
    names: list[str],
    solution: dict[int, int],
) -> int:
    failures = 0
    for row, expected in zip(rows, target):
        t, lam = row[3], row[4]
        actual = 0
        for index, coefficient in solution.items():
            name = names[index]
            if name == "1":
                feature = 1
            elif name.startswith("T^"):
                feature = pow(t, int(name[2:]), prime)
            else:
                feature = pow(lam, int(name[7:]), prime)
            actual = (actual + coefficient * feature) % prime
        failures += actual != expected
    return failures


def case_report(prime: int) -> dict[str, object]:
    case, rows = support._support_rows(prime)
    graph = support_graph_certificate(prime)
    minimum_degree: int | None = None
    coefficients: list[dict[str, int | str]] = []
    coefficient_sha256: str | None = None
    solution_failures: int | None = None
    if graph["unrestricted_separable"]:
        target = [row[5] for row in rows]
        minimum_degree, names, solution = _minimum_polynomial_solution(
            prime, rows, target
        )
        solution_failures = _solution_failures(
            prime, rows, target, names, solution
        )
        coefficients = [
            {"feature": names[index], "coefficient": solution[index]}
            for index in sorted(solution)
        ]
        coefficient_sha256 = hashlib.sha256(
            shell.canonical_json(coefficients)
        ).hexdigest()
    return {
        "prime": prime,
        "width": prime.bit_length(),
        "a": case.a,
        "b": case.b,
        "support_states": len(rows),
        "distinct_T": graph["distinct_T"],
        "distinct_lambda": graph["distinct_lambda"],
        "graph_components": graph["components"],
        "unrestricted_separable": graph["unrestricted_separable"],
        "potential_failures": graph["potential_failures"],
        "cycle_witness": graph["cycle_witness"],
        "minimum_symmetric_degree": minimum_degree,
        "minimum_degree_over_prime": (
            None if minimum_degree is None else minimum_degree / prime
        ),
        "nonzero_coefficient_count": len(coefficients),
        "coefficient_sha256": coefficient_sha256,
        "solution_failures": solution_failures,
        "support_sha256": hashlib.sha256(shell.canonical_json(rows)).hexdigest(),
    }


def synthetic_control_report(prime: int) -> dict[str, object]:
    _case, rows = support._support_rows(prime)
    target = [(row[3] ** 2 + row[4] ** 3) % prime for row in rows]
    degree, names, solution = _minimum_polynomial_solution(prime, rows, target)
    return {
        "prime": prime,
        "target": "T^2 + lambda^3",
        "minimum_symmetric_degree": degree,
        "solution_failures": _solution_failures(
            prime, rows, target, names, solution
        ),
    }


def run_census(primes: tuple[int, ...]) -> dict[str, object]:
    cases = [case_report(prime) for prime in primes]
    controls = [synthetic_control_report(prime) for prime in primes]
    material_family = all(
        row["unrestricted_separable"]
        and row["minimum_symmetric_degree"] is not None
        and int(row["minimum_symmetric_degree"]) <= 4 * int(row["width"])
        for row in cases
    )
    payload: dict[str, object] = {
        "schema": "separable-field-polynomial-v1",
        "scope": "SEPARABLE_FIELD_POLYNOMIAL",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "identity": "T*lambda = f(T) + g(lambda) mod p",
        "cases": cases,
        "synthetic_controls": controls,
        "material_family": material_family,
        "admission_rule": "uniform exact family with degree and coefficient count polynomial in bit width plus complete reversible Q/T schedule",
        "verdict": (
            "ADMIT_SEPARABLE_FIELD_POLYNOMIAL"
            if material_family
            else "HARD_NACK_SEPARABLE_FIELD_POLYNOMIAL"
        ),
        "verdict_scope": "additive separation into univariate field polynomials on exact curve support",
        "next_grammar": "ALGEBRAIC_ROOT_OR_DIRECT_UNIT_ACTION",
        "authority": {
            "provider": False,
            "nonce_grind": False,
            "push": False,
            "submission": False,
        },
    }
    payload["receipt_sha256"] = hashlib.sha256(shell.canonical_json(payload)).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prime", type=int, action="append")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    report = run_census(tuple(args.prime or DEFAULT_PRIMES))
    print(json.dumps(report, sort_keys=True, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
