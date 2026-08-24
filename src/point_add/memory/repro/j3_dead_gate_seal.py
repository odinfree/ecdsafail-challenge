#!/usr/bin/env python3
"""Seal and verify source-bound J3 dead-gate audit evidence."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence


ORIGIN_SYNTHETIC_TAIL = 1
ORIGIN_TAIL_NONCE_REWRITTEN = 2
ORIGIN_EMIT_INVERSE = 4

RAW_FORMAT = "j3-dead-gate-raw-v1"
FINAL_FORMAT = "j3-dead-gate-audit-v1"
AUDIT_FLAG = "J3_DEAD_GATE_AUDIT=1"
OPS_MAGIC = b"QECCOPSZ"
OPS_HEADER_BYTES = 16
OPS_RECORD_BYTES = 56
OPS_CANONICAL_RECORD_BYTES = 49
OPS_KIND_COUNT = 18
TRUSTED_XOF_DOMAIN = b"quantum_ecc-fiat-shamir-v2"

PINNED_OPERATION_COUNT = 12_593_858
PINNED_COMPRESSED_BYTES = 45_668_102
PINNED_COMPRESSED_SHA256 = (
    "87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e"
)
PINNED_CANONICAL_RECORDS_SHA256 = (
    "e11f8622c77f6731b8f14368743356f499e8c5cc6dfaf109fb74f438e625964e"
)
PINNED_TRUSTED_XOF32 = (
    "f84d9689ec5eabb50625cec835d4de23aae2a9c9756e29262e84eeaa4251de71"
)

RAW_NAMES = (
    "audit-diagnostics.log",
    "families.tsv",
    "manifest.raw",
    "sites.tsv",
    "summary.raw",
    "witnesses.tsv",
)
FINAL_NAMES = (
    "families.tsv",
    "manifest.txt",
    "stderr.log",
    "summary.md",
    "witnesses.tsv",
)
RAW_MANIFEST_KEYS = (
    "canonical_records_sha256",
    "ccx_count",
    "ccz_count",
    "decision_count",
    "family_count",
    "format",
    "operation_count",
    "provenance_count",
    "provenance_sha256",
    "trusted_xof32",
    "witness_count",
    "xof_words_consumed",
)
RAW_SUMMARY_KEYS = (
    "diagnostic_family_count",
    "exact_predicate_provisional_family_count",
    "keep_decision_count",
    "non_keep_decision_count",
    "uniform_provisional_family_count",
)
FINAL_MANIFEST_KEYS = (
    "audit_diff_sha256",
    "audit_flag",
    "canonical_records_sha256",
    "ccx_count",
    "ccz_count",
    "compressed_ops_bytes",
    "compressed_ops_sha256",
    "decision_count",
    "family_count",
    "format",
    "implementation_commit",
    "implementation_tree",
    "operation_count",
    "parent_commit",
    "parent_tree",
    "provenance_count",
    "provenance_sha256",
    "qualifying_family_count",
    "rustc_version",
    "trusted_xof32",
    "verdict",
    "witness_count",
)

ACTION_NAMES = (
    "keep",
    "no_cost_identity",
    "drop",
    "lower_to_x",
    "lower_to_cx",
    "lower_to_neg",
    "lower_to_z",
    "lower_to_cz",
)
RULE_NAMES = (
    "none",
    "effective_condition_known0",
    "ccx_control_known0",
    "ccx_both_controls_known1",
    "ccx_one_control_known1",
    "ccz_operand_known0",
    "ccz_three_operands_known1",
    "ccz_two_operands_known1",
    "ccz_one_operand_known1",
)
FACT_NAMES = {"known0", "known1", "unknown"}
KIND_NAMES = {"ccx", "ccz"}
DISPOSITION_NAMES = {
    "uniform_provisional",
    "exact_predicate_provisional",
    "diagnostic_mixed",
}

SITE_HEADER = (
    "site_id",
    "audit_path",
    "audit_line",
    "trace_context",
    "source_literal_key",
    "source_literal_value",
    "inverse_depth",
    "flags",
    "occurrence_count",
    "transform_chain",
)
RAW_WITNESS_HEADER = (
    "op_index",
    "audit_path",
    "audit_line",
    "trace_context",
    "kind",
    "q_control2",
    "q_control1",
    "q_target",
    "c_condition",
    "fact_control2",
    "fact_control1",
    "fact_target",
    "effective_condition",
    "action",
    "rule",
    "score_eligible",
    "site_id",
    "emission_ordinal",
    "inverse_depth",
    "flags",
    "transform_chain",
)
RAW_FAMILY_HEADER = (
    "audit_path",
    "audit_line",
    "trace_context",
    "kind",
    "decision_count",
    *(f"{name}_count" for name in ACTION_NAMES),
    *(f"{name}_count" for name in RULE_NAMES),
    "disposition",
    "predicate_source_literal_key",
    "predicate_source_literal_value",
)
FINAL_WITNESS_HEADER = (
    "op_index",
    "kind",
    "q_control2",
    "q_control1",
    "q_target",
    "c_condition",
    "effective_condition",
    "operand_facts",
    "action",
    "proof_rule",
    "score_eligible",
    "parent_file",
    "parent_line",
    "audit_file",
    "audit_line",
    "trace_context",
    "emission_ordinal",
    "inverse_depth",
    "flags",
    "transform_chain",
)
FINAL_FAMILY_HEADER = (
    "parent_file",
    "parent_line",
    "trace_context",
    "kind",
    "decision_count",
    *(f"{name}_count" for name in ACTION_NAMES),
    *(f"{name}_count" for name in RULE_NAMES),
    "score_eligible_count",
    "audit_generated_count",
    "source_predicate",
    "admission",
)

@dataclass(frozen=True)
class IndependentPredicate:
    parent_file: str
    parent_line: int
    trace_context: int
    kind: str
    source_literal_key: int
    source_literal_value: int
    rendered: str


# Exact source predicates must be independently registered against frozen parent
# coordinates and the Rust-selected source literal. J3A begins empty.
INDEPENDENT_EXACT_PARENT_PREDICATES: tuple[IndependentPredicate, ...] = ()


class SealError(RuntimeError):
    """A deterministic fail-closed validation error."""


@dataclass(frozen=True)
class DiffHunk:
    old_start: int
    old_count: int
    new_start: int
    new_count: int


@dataclass(frozen=True)
class MappedCoordinate:
    parent_file: str
    parent_line: int | None
    audit_generated: bool

    @property
    def family_candidate(self) -> bool:
        return not self.audit_generated and self.parent_line is not None


@dataclass(frozen=True)
class OpsFingerprint:
    compressed_bytes: int
    compressed_sha256: str
    canonical_records_sha256: str
    trusted_xof32: str
    operation_count: int
    kind_counts: tuple[int, ...]


@dataclass(frozen=True)
class RawSite:
    site_id: int
    audit_path: str
    audit_line: int
    trace_context: int
    source_literal_key: int
    source_literal_value: int
    inverse_depth: int
    flags: int
    occurrence_count: int
    transform_chain: str

    @property
    def key(self) -> tuple[int, int, int]:
        return (self.site_id, self.inverse_depth, self.flags)

    @property
    def coordinate(self) -> tuple[str, int, int]:
        return (self.audit_path, self.audit_line, self.trace_context)


@dataclass(frozen=True)
class RawWitness:
    op_index: int
    audit_path: str
    audit_line: int
    trace_context: int
    kind: str
    q_control2: int
    q_control1: int
    q_target: int
    c_condition: int
    facts: tuple[str, str, str]
    effective_condition: str
    action: str
    rule: str
    score_eligible: int
    site_id: int
    emission_ordinal: int
    inverse_depth: int
    flags: int
    transform_chain: str

    @property
    def site_key(self) -> tuple[int, int, int]:
        return (self.site_id, self.inverse_depth, self.flags)

    @property
    def audit_family_key(self) -> tuple[str, int, int, str]:
        return (self.audit_path, self.audit_line, self.trace_context, self.kind)


@dataclass(frozen=True)
class RawFamily:
    audit_path: str
    audit_line: int
    trace_context: int
    kind: str
    decision_count: int
    action_counts: tuple[int, ...]
    rule_counts: tuple[int, ...]
    disposition: str
    predicate_key: int | None
    predicate_value: int | None

    @property
    def key(self) -> tuple[str, int, int, str]:
        return (self.audit_path, self.audit_line, self.trace_context, self.kind)


@dataclass(frozen=True)
class FinalWitness:
    raw: RawWitness
    mapped: MappedCoordinate

    @property
    def family_key(self) -> tuple[str, int | None, int, str]:
        return (
            self.mapped.parent_file,
            self.mapped.parent_line,
            self.raw.trace_context,
            self.raw.kind,
        )


@dataclass
class FinalFamily:
    parent_file: str
    parent_line: int | None
    trace_context: int
    kind: str
    decision_count: int
    action_counts: list[int]
    rule_counts: list[int]
    score_eligible_count: int = 0
    audit_generated_count: int = 0
    source_predicate: str = "-"
    admission: str = "diagnostic"
    predicate_evidence: set[tuple[int, int] | None] = field(
        default_factory=set, repr=False
    )

    @property
    def key(self) -> tuple[str, int, int, str]:
        return (
            self.parent_file,
            -1 if self.parent_line is None else self.parent_line,
            self.trace_context,
            self.kind,
        )


def _validate_source_path(path: str) -> str:
    if not path or path.startswith("/") or "\\" in path:
        raise SealError(f"invalid source path {path!r}")
    if any(character in path for character in "\t\n\r\0"):
        raise SealError(f"invalid source path {path!r}")
    parts = path.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise SealError(f"invalid source path {path!r}")
    if len(parts) < 3 or parts[:2] != ["src", "point_add"]:
        raise SealError(f"source path is outside src/point_add: {path!r}")
    return path


def _zstd_executable() -> str:
    executable = shutil.which("zstd")
    if executable is None:
        raise SealError("zstd executable not found")
    return executable


def fingerprint_ops(path: Path) -> OpsFingerprint:
    """Independently validate and fingerprint one QECCOPSZ artifact."""
    if path.is_symlink() or not path.is_file():
        raise SealError(f"ops artifact is not a regular file: {path}")
    path = path.resolve(strict=True)
    compressed_bytes = path.stat().st_size
    compressed_hasher = hashlib.sha256()
    with path.open("rb", buffering=0) as source:
        while chunk := source.read(8 * 1024 * 1024):
            compressed_hasher.update(chunk)

    with path.open("rb", buffering=0) as source:
        header = source.read(OPS_HEADER_BYTES)
        if len(header) != OPS_HEADER_BYTES:
            raise SealError("ops artifact is too short for the QECCOPSZ header")
        if header[:8] != OPS_MAGIC:
            raise SealError("ops artifact has invalid QECCOPSZ magic")
        operation_count = struct.unpack("<Q", header[8:])[0]
        canonical = hashlib.sha256()
        trusted = hashlib.shake_256()
        trusted.update(TRUSTED_XOF_DOMAIN)
        trusted.update(struct.pack("<Q", operation_count))
        kind_counts = [0] * OPS_KIND_COUNT
        decoded = 0
        remainder = b""
        decoder = subprocess.Popen(
            [_zstd_executable(), "-d", "-q", "-c"],
            stdin=source,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert decoder.stdout is not None
        try:
            while chunk := decoder.stdout.read(OPS_RECORD_BYTES * 100_000):
                data = remainder + chunk
                complete = len(data) - (len(data) % OPS_RECORD_BYTES)
                canonical_block = bytearray(
                    (complete // OPS_RECORD_BYTES) * OPS_CANONICAL_RECORD_BYTES
                )
                canonical_offset = 0
                for offset in range(0, complete, OPS_RECORD_BYTES):
                    kind = struct.unpack_from("<I", data, offset)[0]
                    if kind >= OPS_KIND_COUNT:
                        raise SealError(f"unknown operation kind {kind} at op {decoded}")
                    if data[offset + 4 : offset + 8] != b"\0\0\0\0":
                        raise SealError(f"nonzero operation padding at op {decoded}")
                    kind_counts[kind] += 1
                    canonical_block[canonical_offset] = kind
                    canonical_block[
                        canonical_offset + 1 : canonical_offset + OPS_CANONICAL_RECORD_BYTES
                    ] = data[offset + 8 : offset + OPS_RECORD_BYTES]
                    canonical_offset += OPS_CANONICAL_RECORD_BYTES
                    decoded += 1
                canonical.update(canonical_block)
                trusted.update(canonical_block)
                remainder = data[complete:]
        except BaseException:
            decoder.kill()
            decoder.wait()
            if decoder.stderr is not None:
                decoder.stderr.close()
            raise
        finally:
            decoder.stdout.close()
        stderr = b""
        if decoder.stderr is not None:
            stderr = decoder.stderr.read()
            decoder.stderr.close()
        returncode = decoder.wait()
    if returncode != 0:
        detail = stderr.decode("utf-8", errors="replace").strip()
        raise SealError(
            "zstd decompression failed" + (f": {detail}" if detail else "")
        )
    if remainder:
        raise SealError(
            f"decompressed ops body has {len(remainder)} trailing partial-record bytes"
        )
    if decoded != operation_count:
        raise SealError(
            f"decoded operation count {decoded} does not match header {operation_count}"
        )
    return OpsFingerprint(
        compressed_bytes=compressed_bytes,
        compressed_sha256=compressed_hasher.hexdigest(),
        canonical_records_sha256=canonical.hexdigest(),
        trusted_xof32=trusted.hexdigest(32),
        operation_count=operation_count,
        kind_counts=tuple(kind_counts),
    )


def _require_pinned_fingerprint(fingerprint: OpsFingerprint) -> None:
    expected = {
        "operation_count": (fingerprint.operation_count, PINNED_OPERATION_COUNT),
        "compressed_ops_bytes": (
            fingerprint.compressed_bytes,
            PINNED_COMPRESSED_BYTES,
        ),
        "compressed_ops_sha256": (
            fingerprint.compressed_sha256,
            PINNED_COMPRESSED_SHA256,
        ),
        "canonical_records_sha256": (
            fingerprint.canonical_records_sha256,
            PINNED_CANONICAL_RECORDS_SHA256,
        ),
        "trusted_xof32": (fingerprint.trusted_xof32, PINNED_TRUSTED_XOF32),
    }
    for field, (actual, pinned) in expected.items():
        if actual != pinned:
            raise SealError(f"{field} mismatch: found {actual}, pinned {pinned}")


class SourceMapper:
    """Map audit-tree lines to unchanged lines in one frozen parent."""

    _HUNK = re.compile(
        rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(?: .*)?$"
    )

    def __init__(self, repo: Path, parent: str):
        self.repo = repo.resolve(strict=True)
        self.parent = self._git_text(
            "rev-parse", "--verify", f"{parent}^{{commit}}"
        ).strip()
        self._hunk_cache: dict[str, tuple[DiffHunk, ...]] = {}
        self._audit_file_cache: dict[str, bytes] = {}
        self._parent_file_cache: dict[str, bytes] = {}

    def _git_bytes(self, *arguments: str) -> bytes:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=self.repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if completed.returncode != 0:
            diagnostic = completed.stderr.decode("utf-8", errors="replace").strip()
            raise SealError(
                f"git {' '.join(arguments)} failed"
                + (f": {diagnostic}" if diagnostic else "")
            )
        return completed.stdout

    def _git_text(self, *arguments: str) -> str:
        return self._git_bytes(*arguments).decode("ascii", errors="strict")

    def _hunks_for_path(self, path: str) -> tuple[DiffHunk, ...]:
        cached = self._hunk_cache.get(path)
        if cached is not None:
            return cached
        diff = self._git_bytes(
            "diff",
            "--no-ext-diff",
            "--unified=0",
            self.parent,
            "--",
            path,
        )
        hunks = []
        for line in diff.splitlines():
            if not line.startswith(b"@@"):
                continue
            match = self._HUNK.fullmatch(line)
            if match is None:
                raise SealError(f"malformed zero-context hunk header {line!r}")
            old_start, old_count, new_start, new_count = match.groups()
            hunks.append(
                DiffHunk(
                    int(old_start),
                    1 if old_count is None else int(old_count),
                    int(new_start),
                    1 if new_count is None else int(new_count),
                )
            )
        result = tuple(hunks)
        self._hunk_cache[path] = result
        return result

    @staticmethod
    def _line_at(contents: bytes, line_number: int, description: str) -> bytes:
        if line_number <= 0:
            raise SealError(f"{description} has absent audit line {line_number}")
        lines = contents.splitlines(keepends=True)
        if line_number > len(lines):
            raise SealError(f"{description} has absent audit line {line_number}")
        return lines[line_number - 1]

    def map_site(self, audit_path: str, audit_line: int) -> MappedCoordinate:
        path = _validate_source_path(audit_path)
        audit_file = self.repo / path
        if audit_file.is_symlink() or not audit_file.is_file():
            raise SealError(f"audit source path is not a regular file: {path}")

        if path not in self._parent_file_cache:
            try:
                self._parent_file_cache[path] = self._git_bytes(
                    "show", f"{self.parent}:{path}"
                )
            except SealError as error:
                raise SealError(f"parent path is absent: {path}") from error
        parent_contents = self._parent_file_cache[path]
        if path not in self._audit_file_cache:
            self._audit_file_cache[path] = audit_file.read_bytes()
        audit_contents = self._audit_file_cache[path]
        audit_bytes = self._line_at(audit_contents, audit_line, path)

        cumulative_delta = 0
        previous_new_start = -1
        for hunk in self._hunks_for_path(path):
            if hunk.new_start < previous_new_start:
                raise SealError(f"non-monotonic hunk map for {path}")
            previous_new_start = hunk.new_start
            if hunk.new_count and hunk.new_start <= audit_line < (
                hunk.new_start + hunk.new_count
            ):
                raise SealError(
                    f"audit coordinate is inside a changed hunk: {path}:{audit_line}"
                )
            precedes = (
                audit_line > hunk.new_start
                if hunk.new_count == 0
                else audit_line >= hunk.new_start + hunk.new_count
            )
            if precedes:
                cumulative_delta += hunk.new_count - hunk.old_count

        parent_line = audit_line - cumulative_delta
        if parent_line <= 0:
            raise SealError(f"mapped parent line is absent: {path}:{parent_line}")
        parent_lines = parent_contents.splitlines(keepends=True)
        if parent_line > len(parent_lines):
            raise SealError(f"mapped parent line is absent: {path}:{parent_line}")
        if audit_bytes != parent_lines[parent_line - 1]:
            raise SealError(
                f"mapped line bytes differ: {path}:{audit_line} -> {path}:{parent_line}"
            )
        return MappedCoordinate(path, parent_line, False)


def map_origin_site(
    mapper: SourceMapper, audit_path: str, audit_line: int, flags: int
) -> MappedCoordinate:
    if flags & ORIGIN_SYNTHETIC_TAIL:
        _validate_source_path(audit_path)
        return MappedCoordinate("-", None, True)
    return mapper.map_site(audit_path, audit_line)


def _read_exact_directory(
    directory: Path, expected_names: Sequence[str], label: str
) -> dict[str, bytes]:
    if directory.is_symlink() or not directory.is_dir():
        raise SealError(f"{label} is not a regular directory: {directory}")
    entries = list(directory.iterdir())
    actual_names = tuple(sorted(entry.name for entry in entries))
    expected = tuple(sorted(expected_names))
    if actual_names != expected:
        raise SealError(
            f"{label} artifact set mismatch: found {actual_names!r}, expected {expected!r}"
        )
    result = {}
    for entry in entries:
        if entry.is_symlink() or not entry.is_file():
            raise SealError(f"{label} entry is not a regular non-symlink file: {entry.name}")
        result[entry.name] = entry.read_bytes()
    return result


def _ascii_text(data: bytes, label: str, *, allow_empty: bool = False) -> str:
    try:
        text = data.decode("ascii", errors="strict")
    except UnicodeDecodeError as error:
        raise SealError(f"{label} is not ASCII") from error
    if not text:
        if allow_empty:
            return text
        raise SealError(f"{label} is empty")
    if not text.endswith("\n") or text.endswith("\n\n") or "\r" in text:
        raise SealError(f"{label} must have exactly one trailing LF")
    return text


def _parse_key_values(
    data: bytes, expected_keys: Sequence[str], label: str
) -> dict[str, str]:
    text = _ascii_text(data, label)
    rows = text[:-1].split("\n")
    parsed: dict[str, str] = {}
    order = []
    for row in rows:
        if "=" not in row:
            raise SealError(f"{label} has malformed row {row!r}")
        key, value = row.split("=", 1)
        if not key or not value:
            raise SealError(f"{label} has empty key or value")
        if key in parsed:
            raise SealError(f"{label} has duplicate manifest key {key}")
        parsed[key] = value
        order.append(key)
    expected = list(expected_keys)
    if order != expected:
        missing = sorted(set(expected) - set(order))
        extra = sorted(set(order) - set(expected))
        raise SealError(
            f"{label} manifest schema mismatch: missing={missing!r} extra={extra!r}"
        )
    return parsed


def _parse_tsv(
    data: bytes, expected_header: Sequence[str], label: str
) -> list[dict[str, str]]:
    text = _ascii_text(data, label)
    lines = text[:-1].split("\n")
    header = tuple(lines[0].split("\t"))
    expected = tuple(expected_header)
    if header != expected:
        raise SealError(f"{label} TSV header mismatch")
    rows = []
    for row_number, line in enumerate(lines[1:], start=2):
        fields = line.split("\t")
        if len(fields) != len(expected):
            raise SealError(
                f"{label} row {row_number} has {len(fields)} fields, expected {len(expected)}"
            )
        if any(field == "" for field in fields):
            raise SealError(f"{label} row {row_number} has an empty field")
        rows.append(dict(zip(expected, fields, strict=True)))
    return rows


def _decimal(
    value: str,
    field: str,
    *,
    minimum: int = 0,
    maximum: int = (1 << 64) - 1,
) -> int:
    if not re.fullmatch(r"0|[1-9][0-9]*", value):
        raise SealError(f"{field} is not canonical decimal: {value!r}")
    result = int(value)
    if not minimum <= result <= maximum:
        raise SealError(f"{field} is out of range: {result}")
    return result


def _lower_hex64(value: str, field: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{64}", value):
        raise SealError(f"{field} is not lowercase 64-hex")
    return value


def _expected_transform_chain(inverse_depth: int, flags: int) -> str:
    if flags & ~(ORIGIN_SYNTHETIC_TAIL | ORIGIN_TAIL_NONCE_REWRITTEN | ORIGIN_EMIT_INVERSE):
        raise SealError(f"origin flags contain unsupported bits: {flags}")
    if (inverse_depth == 0) != ((flags & ORIGIN_EMIT_INVERSE) == 0):
        raise SealError("origin inverse depth and emit_inverse flag disagree")
    components = ["emit_inverse"] * inverse_depth
    if flags & ORIGIN_SYNTHETIC_TAIL:
        components.append("synthetic_tail")
    if flags & ORIGIN_TAIL_NONCE_REWRITTEN:
        components.append("tail_nonce_rewritten")
    return ">".join(components) if components else "-"


def _validate_independent_predicates() -> None:
    seen = set()
    for predicate in INDEPENDENT_EXACT_PARENT_PREDICATES:
        coordinate = (
            _validate_source_path(predicate.parent_file),
            predicate.parent_line,
            predicate.trace_context,
            predicate.kind,
            predicate.source_literal_key,
            predicate.source_literal_value,
        )
        if not 1 <= predicate.parent_line < (1 << 32):
            raise SealError("independent predicate parent_line is out of range")
        if not 0 <= predicate.trace_context < (1 << 32):
            raise SealError("independent predicate trace_context is out of range")
        if predicate.kind not in KIND_NAMES:
            raise SealError("independent predicate kind is invalid")
        if not 0 <= predicate.source_literal_key < (1 << 32) or not (
            0 <= predicate.source_literal_value < (1 << 32)
        ):
            raise SealError("independent predicate source literal is out of range")
        if (
            not predicate.rendered
            or not predicate.rendered.isascii()
            or any(character in predicate.rendered for character in "\t\n\r")
        ):
            raise SealError("independent predicate rendering is not canonical TSV text")
        if coordinate in seen:
            raise SealError("duplicate independent predicate registration")
        seen.add(coordinate)


def _parse_raw_sites(data: bytes) -> list[RawSite]:
    parsed = []
    seen_keys = set()
    previous_key: tuple[int, int, int] | None = None
    site_metadata: dict[int, tuple[object, ...]] = {}
    for row in _parse_tsv(data, SITE_HEADER, "sites.tsv"):
        site = RawSite(
            site_id=_decimal(row["site_id"], "site_id", maximum=(1 << 32) - 1),
            audit_path=_validate_source_path(row["audit_path"]),
            audit_line=_decimal(
                row["audit_line"], "audit_line", minimum=1, maximum=(1 << 32) - 1
            ),
            trace_context=_decimal(
                row["trace_context"], "trace_context", maximum=(1 << 32) - 1
            ),
            source_literal_key=_decimal(
                row["source_literal_key"],
                "source_literal_key",
                maximum=(1 << 32) - 1,
            ),
            source_literal_value=_decimal(
                row["source_literal_value"],
                "source_literal_value",
                maximum=(1 << 32) - 1,
            ),
            inverse_depth=_decimal(
                row["inverse_depth"], "inverse_depth", maximum=(1 << 16) - 1
            ),
            flags=_decimal(row["flags"], "flags", maximum=(1 << 16) - 1),
            occurrence_count=_decimal(
                row["occurrence_count"], "occurrence_count", minimum=1
            ),
            transform_chain=row["transform_chain"],
        )
        if site.transform_chain != _expected_transform_chain(site.inverse_depth, site.flags):
            raise SealError(f"site {site.key} has noncanonical transform_chain")
        if site.key in seen_keys:
            raise SealError(f"duplicate site key {site.key}")
        if previous_key is not None and site.key <= previous_key:
            raise SealError("site keys are duplicate or unsorted")
        seen_keys.add(site.key)
        previous_key = site.key
        metadata = (
            site.audit_path,
            site.audit_line,
            site.trace_context,
            site.source_literal_key,
            site.source_literal_value,
        )
        existing = site_metadata.setdefault(site.site_id, metadata)
        if existing != metadata:
            raise SealError(f"site_id {site.site_id} has inconsistent metadata")
        parsed.append(site)
    if not parsed:
        raise SealError("sites.tsv has no site rows")
    return parsed


def _parse_raw_witnesses(data: bytes, operation_count: int) -> list[RawWitness]:
    parsed = []
    previous_index = -1
    for row in _parse_tsv(data, RAW_WITNESS_HEADER, "witnesses.tsv"):
        action = row["action"]
        rule = row["rule"]
        kind = row["kind"]
        facts = (row["fact_control2"], row["fact_control1"], row["fact_target"])
        if kind not in KIND_NAMES:
            raise SealError(f"witness has unsupported kind {kind!r}")
        if any(fact not in FACT_NAMES for fact in facts):
            raise SealError("witness has unsupported operand fact")
        if row["effective_condition"] not in FACT_NAMES:
            raise SealError("witness has unsupported effective condition")
        if action not in ACTION_NAMES or action == "keep":
            raise SealError(f"witness has unsupported non-Keep action {action!r}")
        if rule not in RULE_NAMES:
            raise SealError(f"witness has unsupported proof rule {rule!r}")
        witness = RawWitness(
            op_index=_decimal(row["op_index"], "op_index", maximum=operation_count - 1),
            audit_path=_validate_source_path(row["audit_path"]),
            audit_line=_decimal(row["audit_line"], "audit_line", minimum=1, maximum=(1 << 32) - 1),
            trace_context=_decimal(row["trace_context"], "trace_context", maximum=(1 << 32) - 1),
            kind=kind,
            q_control2=_decimal(row["q_control2"], "q_control2"),
            q_control1=_decimal(row["q_control1"], "q_control1"),
            q_target=_decimal(row["q_target"], "q_target"),
            c_condition=_decimal(row["c_condition"], "c_condition"),
            facts=facts,
            effective_condition=row["effective_condition"],
            action=action,
            rule=rule,
            score_eligible=_decimal(row["score_eligible"], "score_eligible", maximum=1),
            site_id=_decimal(row["site_id"], "site_id", maximum=(1 << 32) - 1),
            emission_ordinal=_decimal(
                row["emission_ordinal"], "emission_ordinal", maximum=(1 << 32) - 1
            ),
            inverse_depth=_decimal(row["inverse_depth"], "inverse_depth", maximum=(1 << 16) - 1),
            flags=_decimal(row["flags"], "flags", maximum=(1 << 16) - 1),
            transform_chain=row["transform_chain"],
        )
        if witness.op_index <= previous_index:
            raise SealError("witness op_index keys are duplicate or unsorted")
        previous_index = witness.op_index
        if witness.transform_chain != _expected_transform_chain(
            witness.inverse_depth, witness.flags
        ):
            raise SealError(f"witness {witness.op_index} has noncanonical transform_chain")
        parsed.append(witness)
    return parsed


def _parse_raw_families(data: bytes) -> list[RawFamily]:
    parsed = []
    seen = set()
    previous_key: tuple[str, int, int, str] | None = None
    for row in _parse_tsv(data, RAW_FAMILY_HEADER, "families.tsv"):
        kind = row["kind"]
        if kind not in KIND_NAMES:
            raise SealError(f"family has unsupported kind {kind!r}")
        action_counts = tuple(
            _decimal(row[f"{name}_count"], f"{name}_count") for name in ACTION_NAMES
        )
        rule_counts = tuple(
            _decimal(row[f"{name}_count"], f"{name}_count") for name in RULE_NAMES
        )
        predicate_fields = (
            row["predicate_source_literal_key"],
            row["predicate_source_literal_value"],
        )
        if predicate_fields == ("-", "-"):
            predicate_key = predicate_value = None
        elif "-" in predicate_fields:
            raise SealError("family has incomplete predicate fields")
        else:
            predicate_key = _decimal(
                predicate_fields[0], "predicate_source_literal_key", maximum=(1 << 32) - 1
            )
            predicate_value = _decimal(
                predicate_fields[1], "predicate_source_literal_value", maximum=(1 << 32) - 1
            )
        family = RawFamily(
            audit_path=_validate_source_path(row["audit_path"]),
            audit_line=_decimal(row["audit_line"], "audit_line", minimum=1, maximum=(1 << 32) - 1),
            trace_context=_decimal(row["trace_context"], "trace_context", maximum=(1 << 32) - 1),
            kind=kind,
            decision_count=_decimal(row["decision_count"], "decision_count", minimum=1),
            action_counts=action_counts,
            rule_counts=rule_counts,
            disposition=row["disposition"],
            predicate_key=predicate_key,
            predicate_value=predicate_value,
        )
        if family.disposition not in DISPOSITION_NAMES:
            raise SealError(f"family has unsupported disposition {family.disposition!r}")
        if sum(action_counts) != family.decision_count or sum(rule_counts) != family.decision_count:
            raise SealError(f"family {family.key} has incomplete decision census")
        uniform = sum(count != 0 for count in action_counts) == 1 and sum(
            count != 0 for count in rule_counts
        ) == 1
        if uniform:
            expected_disposition = "uniform_provisional"
        elif predicate_key is not None:
            expected_disposition = "exact_predicate_provisional"
        else:
            expected_disposition = "diagnostic_mixed"
        if family.disposition != expected_disposition:
            raise SealError(f"family {family.key} has inconsistent disposition")
        if uniform and predicate_key is not None:
            raise SealError(f"uniform family {family.key} unexpectedly carries a predicate")
        if family.key in seen:
            raise SealError(f"duplicate family key {family.key}")
        if previous_key is not None and family.key <= previous_key:
            raise SealError("family keys are duplicate or unsorted")
        seen.add(family.key)
        previous_key = family.key
        parsed.append(family)
    return parsed


@dataclass(frozen=True)
class SourceBinding:
    parent_commit: str
    parent_tree: str
    implementation_commit: str
    implementation_tree: str
    audit_diff_sha256: str
    rustc_version: str


SCOPED_PATHS = ("Cargo.toml", "Cargo.lock", "benchmark.sh", "src/point_add")


def _run_git(repo: Path, *arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise SealError(
            f"git {' '.join(arguments)} failed" + (f": {detail}" if detail else "")
        )
    return completed.stdout


def _git_ascii(repo: Path, *arguments: str) -> str:
    try:
        return _run_git(repo, *arguments).decode("ascii", errors="strict")
    except UnicodeDecodeError as error:
        raise SealError("git identifier output is not ASCII") from error


def _rustc_version() -> str:
    completed = subprocess.run(
        ["rustc", "+1.93.0", "-Vv"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise SealError(
            "rustc +1.93.0 -Vv failed" + (f": {detail}" if detail else "")
        )
    try:
        output = completed.stdout.decode("ascii", errors="strict")
    except UnicodeDecodeError as error:
        raise SealError("rustc version output is not ASCII") from error
    if not output.endswith("\n") or "\r" in output:
        raise SealError("rustc version output is not canonical LF-terminated text")
    return output[:-1].replace("\n", "\\n")


def _require_scoped_clean(repo: Path) -> None:
    for cached in (False, True):
        arguments = ["git", "diff", "--quiet"]
        if cached:
            arguments.append("--cached")
        arguments.extend(("HEAD", "--", *SCOPED_PATHS))
        completed = subprocess.run(
            arguments,
            cwd=repo,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        if completed.returncode == 1:
            raise SealError("scoped tracked source tree has uncommitted changes")
        if completed.returncode != 0:
            detail = completed.stderr.decode("utf-8", errors="replace").strip()
            raise SealError(
                "cannot inspect scoped tracked source tree"
                + (f": {detail}" if detail else "")
            )


def _resolve_binding(
    repo: Path,
    parent: str,
    supplied_parent_tree: str,
    *,
    implementation_commit: str | None = None,
    require_clean: bool = True,
) -> SourceBinding:
    repo = repo.resolve(strict=True)
    if require_clean:
        _require_scoped_clean(repo)
    parent_commit = _git_ascii(
        repo, "rev-parse", "--verify", f"{parent}^{{commit}}"
    ).strip()
    parent_tree = _git_ascii(
        repo, "rev-parse", "--verify", f"{parent_commit}^{{tree}}"
    ).strip()
    if parent_tree != supplied_parent_tree:
        raise SealError(
            f"parent_tree mismatch: resolved {parent_tree}, supplied {supplied_parent_tree}"
        )
    if implementation_commit is None:
        implementation_commit = _git_ascii(
            repo, "rev-parse", "--verify", "HEAD^{commit}"
        ).strip()
    else:
        implementation_commit = _git_ascii(
            repo,
            "rev-parse",
            "--verify",
            f"{implementation_commit}^{{commit}}",
        ).strip()
    implementation_tree = _git_ascii(
        repo,
        "rev-parse",
        "--verify",
        f"{implementation_commit}^{{tree}}",
    ).strip()
    audit_diff = _run_git(
        repo,
        "diff",
        "--binary",
        "--no-ext-diff",
        "--full-index",
        parent_commit,
        implementation_commit,
        "--",
        *SCOPED_PATHS,
    )
    return SourceBinding(
        parent_commit=parent_commit,
        parent_tree=parent_tree,
        implementation_commit=implementation_commit,
        implementation_tree=implementation_tree,
        audit_diff_sha256=hashlib.sha256(audit_diff).hexdigest(),
        rustc_version=_rustc_version(),
    )


@dataclass(frozen=True)
class ParsedRawEvidence:
    manifest: dict[str, str]
    sites: tuple[RawSite, ...]
    witnesses: tuple[RawWitness, ...]
    families: tuple[RawFamily, ...]
    diagnostics: bytes


def _validate_raw_evidence(
    raw_files: Mapping[str, bytes], fingerprint: OpsFingerprint
) -> ParsedRawEvidence:
    manifest = _parse_key_values(
        raw_files["manifest.raw"], RAW_MANIFEST_KEYS, "manifest.raw"
    )
    if manifest["format"] != RAW_FORMAT:
        raise SealError(f"unsupported raw manifest format {manifest['format']!r}")
    for field in (
        "canonical_records_sha256",
        "provenance_sha256",
        "trusted_xof32",
    ):
        _lower_hex64(manifest[field], field)
    numeric = {
        key: _decimal(manifest[key], key)
        for key in RAW_MANIFEST_KEYS
        if key not in {"format", "canonical_records_sha256", "provenance_sha256", "trusted_xof32"}
    }
    if numeric["operation_count"] != fingerprint.operation_count:
        raise SealError("raw operation_count does not match independent fingerprint")
    if numeric["provenance_count"] != numeric["operation_count"]:
        raise SealError("raw provenance_count does not match operation_count")
    if manifest["canonical_records_sha256"] != fingerprint.canonical_records_sha256:
        raise SealError("raw canonical_records_sha256 does not match independent fingerprint")
    if manifest["trusted_xof32"] != fingerprint.trusted_xof32:
        raise SealError("raw trusted_xof32 does not match independent fingerprint")
    if numeric["ccx_count"] != fingerprint.kind_counts[13]:
        raise SealError("raw ccx_count does not match independent operation census")
    if numeric["ccz_count"] != fingerprint.kind_counts[14]:
        raise SealError("raw ccz_count does not match independent operation census")
    if numeric["xof_words_consumed"] != (
        fingerprint.kind_counts[11] + fingerprint.kind_counts[12]
    ):
        raise SealError("raw xof_words_consumed does not match independent operation census")

    sites = _parse_raw_sites(raw_files["sites.tsv"])
    witnesses = _parse_raw_witnesses(
        raw_files["witnesses.tsv"], fingerprint.operation_count
    )
    families = _parse_raw_families(raw_files["families.tsv"])
    site_by_key = {site.key: site for site in sites}
    for witness in witnesses:
        site = site_by_key.get(witness.site_key)
        if site is None:
            raise SealError(f"witness {witness.op_index} references a missing site key")
        if (
            witness.audit_path,
            witness.audit_line,
            witness.trace_context,
            witness.transform_chain,
        ) != (
            site.audit_path,
            site.audit_line,
            site.trace_context,
            site.transform_chain,
        ):
            raise SealError(f"witness {witness.op_index} disagrees with its site row")
    occurrence_count = sum(site.occurrence_count for site in sites)
    if occurrence_count != numeric["provenance_count"]:
        raise SealError(
            f"site occurrence count {occurrence_count} does not match provenance_count"
        )
    if len(witnesses) != numeric["witness_count"]:
        raise SealError("raw witness_count does not match witnesses.tsv")
    if len(families) != numeric["family_count"]:
        raise SealError("raw family_count does not match families.tsv")
    if numeric["decision_count"] != numeric["ccx_count"] + numeric["ccz_count"]:
        raise SealError("raw decision census is incomplete for CCX/CCZ")
    if sum(family.decision_count for family in families) != numeric["decision_count"]:
        raise SealError("family decision census does not match manifest")
    for kind, manifest_key in (("ccx", "ccx_count"), ("ccz", "ccz_count")):
        if sum(family.decision_count for family in families if family.kind == kind) != numeric[
            manifest_key
        ]:
            raise SealError(f"family {kind} census does not match manifest")

    site_coordinates = {site.coordinate for site in sites}
    witnesses_by_family: dict[tuple[str, int, int, str], list[RawWitness]] = defaultdict(list)
    for witness in witnesses:
        witnesses_by_family[witness.audit_family_key].append(witness)
    for family in families:
        if family.key[:3] not in site_coordinates:
            raise SealError(f"family {family.key} has no covered site coordinate")
        family_witnesses = witnesses_by_family.get(family.key, [])
        action_census = Counter(witness.action for witness in family_witnesses)
        rule_census = Counter(witness.rule for witness in family_witnesses)
        if family.disposition == "exact_predicate_provisional" and len(
            {(witness.action, witness.rule) for witness in family_witnesses}
        ) != 1:
            raise SealError(
                f"exact-predicate family {family.key} lacks one coherent non-Keep signature"
            )
        for index, action in enumerate(ACTION_NAMES):
            expected = family.action_counts[index]
            if action != "keep" and action_census[action] != expected:
                raise SealError(f"family {family.key} witness action census mismatch")
        keep_count = family.action_counts[ACTION_NAMES.index("keep")]
        for index, rule in enumerate(RULE_NAMES):
            actual = rule_census[rule] + (keep_count if rule == "none" else 0)
            if actual != family.rule_counts[index]:
                raise SealError(f"family {family.key} witness rule census mismatch")
    if set(witnesses_by_family) - {family.key for family in families}:
        raise SealError("witnesses.tsv contains a missing family key")

    computed_summary = {
        "diagnostic_family_count": sum(
            family.disposition == "diagnostic_mixed" for family in families
        ),
        "exact_predicate_provisional_family_count": sum(
            family.disposition == "exact_predicate_provisional" for family in families
        ),
        "keep_decision_count": sum(
            family.action_counts[ACTION_NAMES.index("keep")] for family in families
        ),
        "non_keep_decision_count": len(witnesses),
        "uniform_provisional_family_count": sum(
            family.disposition == "uniform_provisional" for family in families
        ),
    }
    summary = _parse_key_values(
        raw_files["summary.raw"], RAW_SUMMARY_KEYS, "summary.raw"
    )
    for key, expected in computed_summary.items():
        if _decimal(summary[key], key) != expected:
            raise SealError(f"raw summary field {key} does not match independent census")
    diagnostics = raw_files["audit-diagnostics.log"]
    _ascii_text(diagnostics, "audit-diagnostics.log", allow_empty=True)
    if diagnostics:
        raise SealError("raw audit diagnostics indicate audit failure")
    return ParsedRawEvidence(
        manifest=manifest,
        sites=tuple(sites),
        witnesses=tuple(witnesses),
        families=tuple(families),
        diagnostics=diagnostics,
    )


def _map_and_aggregate(
    repo: Path, parent_commit: str, raw: ParsedRawEvidence
) -> tuple[list[FinalWitness], list[FinalFamily]]:
    mapper = SourceMapper(repo, parent_commit)
    mapped_sites: dict[tuple[int, int, int], MappedCoordinate] = {}
    coordinate_sites: dict[tuple[str, int, int], list[RawSite]] = defaultdict(list)
    for site in raw.sites:
        mapped_sites[site.key] = map_origin_site(
            mapper, site.audit_path, site.audit_line, site.flags
        )
        coordinate_sites[site.coordinate].append(site)

    final_witnesses = [
        FinalWitness(witness, mapped_sites[witness.site_key])
        for witness in raw.witnesses
    ]
    aggregate: dict[tuple[str, int | None, int, str], FinalFamily] = {}
    for family in raw.families:
        site_classes = coordinate_sites.get(family.key[:3], [])
        if not site_classes:
            raise SealError(f"family {family.key} lacks a provenance site")
        any_generated = any(site.flags & ORIGIN_SYNTHETIC_TAIL for site in site_classes)
        non_generated_mappings = {
            mapped_sites[site.key]
            for site in site_classes
            if not (site.flags & ORIGIN_SYNTHETIC_TAIL)
        }
        if len(non_generated_mappings) > 1:
            raise SealError(f"family {family.key} maps to multiple parent coordinates")
        if non_generated_mappings:
            mapped = next(iter(non_generated_mappings))
        else:
            mapped = MappedCoordinate("-", None, True)
        key = (
            mapped.parent_file,
            mapped.parent_line,
            family.trace_context,
            family.kind,
        )
        target = aggregate.get(key)
        if target is None:
            target = FinalFamily(
                parent_file=mapped.parent_file,
                parent_line=mapped.parent_line,
                trace_context=family.trace_context,
                kind=family.kind,
                decision_count=0,
                action_counts=[0] * len(ACTION_NAMES),
                rule_counts=[0] * len(RULE_NAMES),
            )
            aggregate[key] = target
        target.decision_count += family.decision_count
        for index, count in enumerate(family.action_counts):
            target.action_counts[index] += count
        for index, count in enumerate(family.rule_counts):
            target.rule_counts[index] += count
        if any_generated:
            target.audit_generated_count += family.decision_count
        if family.disposition == "exact_predicate_provisional":
            if family.predicate_key is None or family.predicate_value is None:
                raise SealError(f"family {family.key} is missing its exact predicate")
            target.predicate_evidence.add(
                (family.predicate_key, family.predicate_value)
            )
        else:
            target.predicate_evidence.add(None)

    for witness in final_witnesses:
        family = aggregate.get(witness.family_key)
        if family is None:
            raise SealError(f"mapped witness {witness.raw.op_index} has no parent family")
        family.score_eligible_count += witness.raw.score_eligible

    for family in aggregate.values():
        registered = [
            predicate
            for predicate in INDEPENDENT_EXACT_PARENT_PREDICATES
            if (
                predicate.parent_file,
                predicate.parent_line,
                predicate.trace_context,
                predicate.kind,
            )
            == (
                family.parent_file,
                family.parent_line,
                family.trace_context,
                family.kind,
            )
            and family.predicate_evidence
            == {(predicate.source_literal_key, predicate.source_literal_value)}
        ]
        if len(registered) > 1:
            raise SealError(f"multiple independent predicates registered for {family.key}")
        if registered:
            family.source_predicate = registered[0].rendered
        nonzero_actions = [
            ACTION_NAMES[index]
            for index, count in enumerate(family.action_counts)
            if count
        ]
        nonzero_rules = [
            RULE_NAMES[index] for index, count in enumerate(family.rule_counts) if count
        ]
        uniformly_qualifying = (
            family.audit_generated_count == 0
            and len(nonzero_actions) == 1
            and nonzero_actions[0] not in {"keep", "no_cost_identity"}
            and len(nonzero_rules) == 1
            and family.action_counts[ACTION_NAMES.index(nonzero_actions[0])]
            == family.decision_count
            and family.rule_counts[RULE_NAMES.index(nonzero_rules[0])]
            == family.decision_count
            and family.score_eligible_count == family.decision_count
        )
        predicate_qualifying = (
            family.audit_generated_count == 0
            and family.source_predicate != "-"
            and family.score_eligible_count
            == family.decision_count
            - family.action_counts[ACTION_NAMES.index("keep")]
            > 0
        )
        if uniformly_qualifying or predicate_qualifying:
            family.admission = "qualifying"
    return sorted(final_witnesses, key=lambda witness: witness.raw.op_index), sorted(
        aggregate.values(), key=lambda family: family.key
    )


def _render_final_witnesses(witnesses: Iterable[FinalWitness]) -> bytes:
    lines = ["\t".join(FINAL_WITNESS_HEADER)]
    for witness in witnesses:
        raw = witness.raw
        parent_line = "-" if witness.mapped.parent_line is None else str(witness.mapped.parent_line)
        lines.append(
            "\t".join(
                (
                    str(raw.op_index),
                    raw.kind,
                    str(raw.q_control2),
                    str(raw.q_control1),
                    str(raw.q_target),
                    str(raw.c_condition),
                    raw.effective_condition,
                    ",".join(raw.facts),
                    raw.action,
                    raw.rule,
                    str(raw.score_eligible),
                    witness.mapped.parent_file,
                    parent_line,
                    raw.audit_path,
                    str(raw.audit_line),
                    str(raw.trace_context),
                    str(raw.emission_ordinal),
                    str(raw.inverse_depth),
                    str(raw.flags),
                    raw.transform_chain,
                )
            )
        )
    return ("\n".join(lines) + "\n").encode("ascii")


def _render_final_families(families: Iterable[FinalFamily]) -> bytes:
    lines = ["\t".join(FINAL_FAMILY_HEADER)]
    for family in families:
        parent_line = "-" if family.parent_line is None else str(family.parent_line)
        lines.append(
            "\t".join(
                (
                    family.parent_file,
                    parent_line,
                    str(family.trace_context),
                    family.kind,
                    str(family.decision_count),
                    *(str(count) for count in family.action_counts),
                    *(str(count) for count in family.rule_counts),
                    str(family.score_eligible_count),
                    str(family.audit_generated_count),
                    family.source_predicate,
                    family.admission,
                )
            )
        )
    return ("\n".join(lines) + "\n").encode("ascii")


def _render_manifest(manifest: Mapping[str, str]) -> bytes:
    if tuple(sorted(manifest)) != FINAL_MANIFEST_KEYS:
        raise SealError("internal final manifest schema mismatch")
    return "".join(f"{key}={manifest[key]}\n" for key in FINAL_MANIFEST_KEYS).encode(
        "ascii"
    )


def _render_summary(manifest: Mapping[str, str], families: Sequence[FinalFamily]) -> bytes:
    action_totals = {
        action: sum(family.action_counts[index] for family in families)
        for index, action in enumerate(ACTION_NAMES)
    }
    lines = [
        "# J3 dead-gate audit",
        "",
        f"- Verdict: `{manifest['verdict']}`",
        f"- Operations: {manifest['operation_count']}",
        f"- CCX decisions: {manifest['ccx_count']}",
        f"- CCZ decisions: {manifest['ccz_count']}",
        f"- Non-Keep witnesses: {manifest['witness_count']}",
        f"- Parent families: {manifest['family_count']}",
        f"- Qualifying families: {manifest['qualifying_family_count']}",
        "",
        "## Action census",
        "",
        "| Action | Count |",
        "| --- | ---: |",
    ]
    lines.extend(f"| `{action}` | {action_totals[action]} |" for action in ACTION_NAMES)
    return ("\n".join(lines) + "\n").encode("ascii")


def _fsync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _publish_atomically(output: Path, files: Mapping[str, bytes]) -> None:
    if tuple(sorted(files)) != tuple(sorted(FINAL_NAMES)):
        raise SealError("internal final artifact set mismatch")
    parent = output.parent
    parent.mkdir(parents=True, exist_ok=True)
    if parent.is_symlink() or not parent.is_dir():
        raise SealError(f"final artifact parent is not a regular directory: {parent}")
    temporary = Path(tempfile.mkdtemp(prefix=f".{output.name}.tmp-", dir=parent))
    backup = parent / f".{output.name}.backup-{os.getpid()}-{uuid.uuid4().hex}"
    moved_existing = False
    try:
        for name in sorted(files):
            path = temporary / name
            with path.open("xb") as destination:
                destination.write(files[name])
                destination.flush()
                os.fsync(destination.fileno())
        _fsync_directory(temporary)
        if output.exists() or output.is_symlink():
            _read_exact_directory(output, FINAL_NAMES, "existing final")
            os.replace(output, backup)
            moved_existing = True
        try:
            os.replace(temporary, output)
            _fsync_directory(parent)
        except BaseException:
            if moved_existing and backup.exists() and not output.exists():
                os.replace(backup, output)
            raise
        if moved_existing:
            shutil.rmtree(backup)
            _fsync_directory(parent)
    except BaseException:
        if temporary.exists():
            shutil.rmtree(temporary)
        if moved_existing and backup.exists() and not output.exists():
            os.replace(backup, output)
        raise


def seal_evidence(
    repo: Path,
    parent: str,
    parent_tree: str,
    raw_dir: Path,
    ops: Path,
    output: Path,
) -> dict[str, str]:
    repo = repo.resolve(strict=True)
    _validate_independent_predicates()
    binding = _resolve_binding(repo, parent, parent_tree)
    fingerprint = fingerprint_ops(ops)
    _require_pinned_fingerprint(fingerprint)
    raw_files = _read_exact_directory(raw_dir, RAW_NAMES, "raw")
    raw = _validate_raw_evidence(raw_files, fingerprint)
    witnesses, families = _map_and_aggregate(repo, binding.parent_commit, raw)
    qualifying_count = sum(family.admission == "qualifying" for family in families)
    verdict = "ADMIT" if qualifying_count else "HARD_NACK"
    manifest = {
        "audit_diff_sha256": binding.audit_diff_sha256,
        "audit_flag": AUDIT_FLAG,
        "canonical_records_sha256": fingerprint.canonical_records_sha256,
        "ccx_count": str(fingerprint.kind_counts[13]),
        "ccz_count": str(fingerprint.kind_counts[14]),
        "compressed_ops_bytes": str(fingerprint.compressed_bytes),
        "compressed_ops_sha256": fingerprint.compressed_sha256,
        "decision_count": raw.manifest["decision_count"],
        "family_count": str(len(families)),
        "format": FINAL_FORMAT,
        "implementation_commit": binding.implementation_commit,
        "implementation_tree": binding.implementation_tree,
        "operation_count": str(fingerprint.operation_count),
        "parent_commit": binding.parent_commit,
        "parent_tree": binding.parent_tree,
        "provenance_count": raw.manifest["provenance_count"],
        "provenance_sha256": raw.manifest["provenance_sha256"],
        "qualifying_family_count": str(qualifying_count),
        "rustc_version": binding.rustc_version,
        "trusted_xof32": fingerprint.trusted_xof32,
        "verdict": verdict,
        "witness_count": str(len(witnesses)),
    }
    artifacts = {
        "manifest.txt": _render_manifest(manifest),
        "summary.md": _render_summary(manifest, families),
        "witnesses.tsv": _render_final_witnesses(witnesses),
        "families.tsv": _render_final_families(families),
        "stderr.log": raw.diagnostics,
    }
    _publish_atomically(output, artifacts)
    return manifest


def _parse_final_witnesses(
    data: bytes, operation_count: int, mapper: SourceMapper
) -> list[FinalWitness]:
    parsed = []
    previous_index = -1
    for row in _parse_tsv(data, FINAL_WITNESS_HEADER, "sealed witnesses.tsv"):
        kind = row["kind"]
        action = row["action"]
        rule = row["proof_rule"]
        if kind not in KIND_NAMES or action not in ACTION_NAMES or action == "keep":
            raise SealError("sealed witness has invalid kind or action")
        if rule not in RULE_NAMES:
            raise SealError("sealed witness has invalid proof rule")
        facts = tuple(row["operand_facts"].split(","))
        if len(facts) != 3 or any(fact not in FACT_NAMES for fact in facts):
            raise SealError("sealed witness has invalid operand_facts")
        if row["effective_condition"] not in FACT_NAMES:
            raise SealError("sealed witness has invalid effective_condition")
        op_index = _decimal(row["op_index"], "op_index", maximum=operation_count - 1)
        if op_index <= previous_index:
            raise SealError("sealed witness op_index keys are duplicate or unsorted")
        previous_index = op_index
        audit_path = _validate_source_path(row["audit_file"])
        audit_line = _decimal(
            row["audit_line"], "audit_line", minimum=1, maximum=(1 << 32) - 1
        )
        flags = _decimal(row["flags"], "flags", maximum=(1 << 16) - 1)
        inverse_depth = _decimal(
            row["inverse_depth"], "inverse_depth", maximum=(1 << 16) - 1
        )
        if row["transform_chain"] != _expected_transform_chain(inverse_depth, flags):
            raise SealError(f"sealed witness {op_index} has invalid transform_chain")
        mapped = map_origin_site(mapper, audit_path, audit_line, flags)
        expected_parent_line = "-" if mapped.parent_line is None else str(mapped.parent_line)
        if row["parent_file"] != mapped.parent_file or row["parent_line"] != expected_parent_line:
            raise SealError(f"sealed witness {op_index} parent coordinate mismatch")
        raw = RawWitness(
            op_index=op_index,
            audit_path=audit_path,
            audit_line=audit_line,
            trace_context=_decimal(
                row["trace_context"], "trace_context", maximum=(1 << 32) - 1
            ),
            kind=kind,
            q_control2=_decimal(row["q_control2"], "q_control2"),
            q_control1=_decimal(row["q_control1"], "q_control1"),
            q_target=_decimal(row["q_target"], "q_target"),
            c_condition=_decimal(row["c_condition"], "c_condition"),
            facts=(facts[0], facts[1], facts[2]),
            effective_condition=row["effective_condition"],
            action=action,
            rule=rule,
            score_eligible=_decimal(
                row["score_eligible"], "score_eligible", maximum=1
            ),
            site_id=0,
            emission_ordinal=_decimal(
                row["emission_ordinal"], "emission_ordinal", maximum=(1 << 32) - 1
            ),
            inverse_depth=inverse_depth,
            flags=flags,
            transform_chain=row["transform_chain"],
        )
        parsed.append(FinalWitness(raw, mapped))
    return parsed


def _family_is_qualifying(family: FinalFamily) -> bool:
    nonzero_actions = [
        ACTION_NAMES[index] for index, count in enumerate(family.action_counts) if count
    ]
    nonzero_rules = [
        RULE_NAMES[index] for index, count in enumerate(family.rule_counts) if count
    ]
    uniformly_qualifying = (
        family.audit_generated_count == 0
        and len(nonzero_actions) == 1
        and nonzero_actions[0] not in {"keep", "no_cost_identity"}
        and len(nonzero_rules) == 1
        and family.action_counts[ACTION_NAMES.index(nonzero_actions[0])]
        == family.decision_count
        and family.rule_counts[RULE_NAMES.index(nonzero_rules[0])]
        == family.decision_count
        and family.score_eligible_count == family.decision_count
    )
    predicate_qualifying = (
        family.audit_generated_count == 0
        and family.source_predicate != "-"
        and family.score_eligible_count
        == family.decision_count
        - family.action_counts[ACTION_NAMES.index("keep")]
        > 0
    )
    return uniformly_qualifying or predicate_qualifying


def _parse_final_families(
    data: bytes, repo: Path, parent_commit: str
) -> list[FinalFamily]:
    parsed = []
    seen = set()
    previous_key: tuple[str, int, int, str] | None = None
    parent_files: dict[str, list[bytes]] = {}
    for row in _parse_tsv(data, FINAL_FAMILY_HEADER, "sealed families.tsv"):
        kind = row["kind"]
        if kind not in KIND_NAMES:
            raise SealError("sealed family has invalid kind")
        if row["parent_file"] == "-" or row["parent_line"] == "-":
            if (row["parent_file"], row["parent_line"]) != ("-", "-"):
                raise SealError("sealed family has an incomplete generated coordinate")
            parent_file = "-"
            parent_line = None
        else:
            parent_file = _validate_source_path(row["parent_file"])
            parent_line = _decimal(
                row["parent_line"], "parent_line", minimum=1, maximum=(1 << 32) - 1
            )
            if parent_file not in parent_files:
                contents = _run_git(repo, "show", f"{parent_commit}:{parent_file}")
                parent_files[parent_file] = contents.splitlines(keepends=True)
            if parent_line > len(parent_files[parent_file]):
                raise SealError(
                    f"sealed family parent coordinate is absent: {parent_file}:{parent_line}"
                )
        family = FinalFamily(
            parent_file=parent_file,
            parent_line=parent_line,
            trace_context=_decimal(
                row["trace_context"], "trace_context", maximum=(1 << 32) - 1
            ),
            kind=kind,
            decision_count=_decimal(row["decision_count"], "decision_count", minimum=1),
            action_counts=[
                _decimal(row[f"{name}_count"], f"{name}_count")
                for name in ACTION_NAMES
            ],
            rule_counts=[
                _decimal(row[f"{name}_count"], f"{name}_count") for name in RULE_NAMES
            ],
            score_eligible_count=_decimal(
                row["score_eligible_count"], "score_eligible_count"
            ),
            audit_generated_count=_decimal(
                row["audit_generated_count"], "audit_generated_count"
            ),
            source_predicate=row["source_predicate"],
            admission=row["admission"],
        )
        if sum(family.action_counts) != family.decision_count or sum(
            family.rule_counts
        ) != family.decision_count:
            raise SealError(f"sealed family {family.key} has incomplete census")
        if family.score_eligible_count > family.decision_count:
            raise SealError(f"sealed family {family.key} has excessive score eligibility")
        if family.audit_generated_count > family.decision_count:
            raise SealError(f"sealed family {family.key} has excessive audit-generated count")
        registered_predicates = [
            predicate.rendered
            for predicate in INDEPENDENT_EXACT_PARENT_PREDICATES
            if (
                predicate.parent_file,
                predicate.parent_line,
                predicate.trace_context,
                predicate.kind,
            )
            == (
                family.parent_file,
                family.parent_line,
                family.trace_context,
                family.kind,
            )
        ]
        expected_predicate = registered_predicates[0] if len(registered_predicates) == 1 else "-"
        if len(registered_predicates) > 1 or family.source_predicate != expected_predicate:
            raise SealError(f"sealed family {family.key} predicate is not independently registered")
        expected_admission = "qualifying" if _family_is_qualifying(family) else "diagnostic"
        if family.admission != expected_admission:
            raise SealError(f"sealed family {family.key} admission mismatch")
        if family.key in seen or (previous_key is not None and family.key <= previous_key):
            raise SealError("sealed family keys are duplicate or unsorted")
        seen.add(family.key)
        previous_key = family.key
        parsed.append(family)
    return parsed


def _verify_final_cross_census(
    manifest: Mapping[str, str],
    witnesses: Sequence[FinalWitness],
    families: Sequence[FinalFamily],
) -> None:
    numeric = {
        field: _decimal(manifest[field], field)
        for field in (
            "ccx_count",
            "ccz_count",
            "decision_count",
            "family_count",
            "operation_count",
            "provenance_count",
            "qualifying_family_count",
            "witness_count",
        )
    }
    if len(witnesses) != numeric["witness_count"]:
        raise SealError("sealed witness_count does not match witnesses.tsv")
    if len(families) != numeric["family_count"]:
        raise SealError("sealed family_count does not match families.tsv")
    if sum(family.decision_count for family in families) != numeric["decision_count"]:
        raise SealError("sealed family decision census does not match manifest")
    if numeric["decision_count"] != numeric["ccx_count"] + numeric["ccz_count"]:
        raise SealError("sealed decision census is incomplete")
    for kind, field in (("ccx", "ccx_count"), ("ccz", "ccz_count")):
        if sum(family.decision_count for family in families if family.kind == kind) != numeric[
            field
        ]:
            raise SealError(f"sealed {kind} family census mismatch")
    family_by_key = {
        (family.parent_file, family.parent_line, family.trace_context, family.kind): family
        for family in families
    }
    witness_groups: dict[tuple[str, int | None, int, str], list[FinalWitness]] = defaultdict(list)
    for witness in witnesses:
        witness_groups[witness.family_key].append(witness)
    if set(witness_groups) - set(family_by_key):
        raise SealError("sealed witness references a missing parent family")
    for key, family in family_by_key.items():
        group = witness_groups.get(key, [])
        action_counts = Counter(witness.raw.action for witness in group)
        rule_counts = Counter(witness.raw.rule for witness in group)
        for index, action in enumerate(ACTION_NAMES):
            if action != "keep" and action_counts[action] != family.action_counts[index]:
                raise SealError(f"sealed family {family.key} witness action census mismatch")
        keep_count = family.action_counts[ACTION_NAMES.index("keep")]
        for index, rule in enumerate(RULE_NAMES):
            actual = rule_counts[rule] + (keep_count if rule == "none" else 0)
            if actual != family.rule_counts[index]:
                raise SealError(f"sealed family {family.key} witness rule census mismatch")
        if sum(witness.raw.score_eligible for witness in group) != family.score_eligible_count:
            raise SealError(f"sealed family {family.key} score eligibility mismatch")
        generated_witnesses = sum(witness.mapped.audit_generated for witness in group)
        if generated_witnesses > family.audit_generated_count:
            raise SealError(f"sealed family {family.key} audit-generated census mismatch")
    qualifying_count = sum(family.admission == "qualifying" for family in families)
    if qualifying_count != numeric["qualifying_family_count"]:
        raise SealError("sealed qualifying_family_count mismatch")
    expected_verdict = "ADMIT" if qualifying_count else "HARD_NACK"
    if manifest["verdict"] != expected_verdict:
        raise SealError("sealed verdict does not match qualifying family census")


def verify_evidence(
    repo: Path,
    parent: str,
    parent_tree: str,
    evidence: Path,
    ops: Path,
) -> dict[str, str]:
    repo = repo.resolve(strict=True)
    _validate_independent_predicates()
    final_files = _read_exact_directory(evidence, FINAL_NAMES, "final")
    manifest = _parse_key_values(
        final_files["manifest.txt"], FINAL_MANIFEST_KEYS, "manifest.txt"
    )
    if manifest["format"] != FINAL_FORMAT:
        raise SealError(f"unsupported final manifest format {manifest['format']!r}")
    if manifest["audit_flag"] != AUDIT_FLAG:
        raise SealError("final manifest audit_flag mismatch")
    if manifest["verdict"] not in {"ADMIT", "HARD_NACK"}:
        raise SealError("final manifest verdict is invalid")
    for field in (
        "audit_diff_sha256",
        "canonical_records_sha256",
        "compressed_ops_sha256",
        "provenance_sha256",
        "trusted_xof32",
    ):
        _lower_hex64(manifest[field], field)
    for field in (
        "implementation_commit",
        "implementation_tree",
        "parent_commit",
        "parent_tree",
    ):
        if not re.fullmatch(r"[0-9a-f]{40}", manifest[field]):
            raise SealError(f"final manifest {field} is not lowercase 40-hex")
    for field in (
        "ccx_count",
        "ccz_count",
        "compressed_ops_bytes",
        "decision_count",
        "family_count",
        "operation_count",
        "provenance_count",
        "qualifying_family_count",
        "witness_count",
    ):
        _decimal(manifest[field], field)
    if manifest["provenance_count"] != manifest["operation_count"]:
        raise SealError("sealed provenance_count does not match operation_count")

    binding = _resolve_binding(
        repo,
        parent,
        parent_tree,
        implementation_commit=manifest["implementation_commit"],
    )
    head = _git_ascii(repo, "rev-parse", "--verify", "HEAD^{commit}").strip()
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", binding.implementation_commit, head],
        cwd=repo,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    if ancestor.returncode != 0:
        raise SealError("sealed implementation_commit is not an ancestor of current HEAD")
    scoped_diff = subprocess.run(
        [
            "git",
            "diff",
            "--quiet",
            binding.implementation_commit,
            head,
            "--",
            *SCOPED_PATHS,
        ],
        cwd=repo,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    if scoped_diff.returncode != 0:
        raise SealError("scoped source changed after sealed implementation_commit")
    expected_binding = {
        "audit_diff_sha256": binding.audit_diff_sha256,
        "implementation_commit": binding.implementation_commit,
        "implementation_tree": binding.implementation_tree,
        "parent_commit": binding.parent_commit,
        "parent_tree": binding.parent_tree,
        "rustc_version": binding.rustc_version,
    }
    for field, expected in expected_binding.items():
        if manifest[field] != expected:
            raise SealError(f"sealed {field} does not match independent source binding")

    fingerprint = fingerprint_ops(ops)
    _require_pinned_fingerprint(fingerprint)
    expected_fingerprint = {
        "canonical_records_sha256": fingerprint.canonical_records_sha256,
        "ccx_count": str(fingerprint.kind_counts[13]),
        "ccz_count": str(fingerprint.kind_counts[14]),
        "compressed_ops_bytes": str(fingerprint.compressed_bytes),
        "compressed_ops_sha256": fingerprint.compressed_sha256,
        "operation_count": str(fingerprint.operation_count),
        "trusted_xof32": fingerprint.trusted_xof32,
    }
    for field, expected in expected_fingerprint.items():
        if manifest[field] != expected:
            raise SealError(f"sealed {field} does not match independent ops fingerprint")

    mapper = SourceMapper(repo, binding.parent_commit)
    witnesses = _parse_final_witnesses(
        final_files["witnesses.tsv"], fingerprint.operation_count, mapper
    )
    families = _parse_final_families(
        final_files["families.tsv"], repo, binding.parent_commit
    )
    _verify_final_cross_census(manifest, witnesses, families)
    expected_summary = _render_summary(manifest, families)
    if final_files["summary.md"] != expected_summary:
        raise SealError("sealed summary.md does not match independent rendering")
    if final_files["stderr.log"]:
        raise SealError("sealed stderr.log contains non-audit or failed-audit diagnostics")
    return manifest


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    seal_parser = subcommands.add_parser("seal")
    seal_parser.add_argument("--repo", type=Path, required=True)
    seal_parser.add_argument("--parent", required=True)
    seal_parser.add_argument("--parent-tree", required=True)
    seal_parser.add_argument("--raw-dir", type=Path, required=True)
    seal_parser.add_argument("--ops", type=Path, required=True)
    seal_parser.add_argument("--out", type=Path, required=True)
    verify_parser = subcommands.add_parser("verify")
    verify_parser.add_argument("--repo", type=Path, required=True)
    verify_parser.add_argument("--parent", required=True)
    verify_parser.add_argument("--parent-tree", required=True)
    verify_parser.add_argument("--evidence", type=Path, required=True)
    verify_parser.add_argument("--ops", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _argument_parser().parse_args(argv)
    try:
        if arguments.command == "seal":
            manifest = seal_evidence(
                arguments.repo,
                arguments.parent,
                arguments.parent_tree,
                arguments.raw_dir,
                arguments.ops,
                arguments.out,
            )
            print(f"SEALED {manifest['verdict']} {FINAL_FORMAT}")
        else:
            verify_evidence(
                arguments.repo,
                arguments.parent,
                arguments.parent_tree,
                arguments.evidence,
                arguments.ops,
            )
            print(f"VERIFIED {FINAL_FORMAT}")
        return 0
    except SealError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
