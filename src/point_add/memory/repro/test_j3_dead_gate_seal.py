#!/usr/bin/env python3
"""Fail-closed tests for the J3 dead-gate evidence sealer."""

from __future__ import annotations

import contextlib
import io
import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

try:
    from src.point_add.memory.repro import j3_dead_gate_seal as seal
except ImportError:
    seal = None


class ModulePresenceTests(unittest.TestCase):
    def test_sealer_module_exists(self) -> None:
        self.assertIsNotNone(seal, "j3_dead_gate_seal implementation is missing")

    def test_sealer_artifact_api_exists(self) -> None:
        self.assertTrue(
            all(
                hasattr(seal, name)
                for name in ("fingerprint_ops", "seal_evidence", "verify_evidence", "main")
            ),
            "artifact sealing API is incomplete",
        )

    def test_independent_predicate_model_exists(self) -> None:
        self.assertTrue(
            hasattr(seal, "IndependentPredicate"),
            "independent exact-source predicate model is missing",
        )


@unittest.skipIf(seal is None, "mapping implementation is not present yet")
class ParentMapperTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="j3-seal-map-")
        self.repo = Path(self._temporary.name)
        self._git("init", "-q")
        self._git("config", "user.name", "J3 Test")
        self._git("config", "user.email", "j3@example.invalid")
        (self.repo / "src/point_add").mkdir(parents=True)
        self.source = self.repo / "src/point_add/sample.rs"
        self.source.write_bytes(b"alpha\nbeta\ngamma\n")
        self._git("add", ".")
        self._git("commit", "-qm", "parent")
        self.parent = self._git("rev-parse", "HEAD").strip()

    def tearDown(self) -> None:
        self._temporary.cleanup()

    def _git(self, *arguments: str) -> str:
        return subprocess.run(
            ["git", *arguments],
            cwd=self.repo,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ).stdout

    def _commit_audit(self) -> None:
        self._git("add", "-A")
        self._git("commit", "-qm", "audit")

    def test_unchanged_line_with_preceding_insertions_maps_uniquely(self) -> None:
        self.source.write_bytes(b"inserted\nalpha\nbeta\ngamma\n")
        self._commit_audit()

        mapped = seal.SourceMapper(self.repo, self.parent).map_site(
            "src/point_add/sample.rs", 3
        )

        self.assertEqual(mapped.parent_file, "src/point_add/sample.rs")
        self.assertEqual(mapped.parent_line, 2)
        self.assertFalse(mapped.audit_generated)
        self.assertTrue(mapped.family_candidate)

    def test_changed_hunk_line_fails(self) -> None:
        self.source.write_bytes(b"alpha\nchanged\ngamma\n")
        self._commit_audit()

        with self.assertRaisesRegex(seal.SealError, "changed hunk"):
            seal.SourceMapper(self.repo, self.parent).map_site(
                "src/point_add/sample.rs", 2
            )

    def test_deleted_or_absent_audit_line_fails(self) -> None:
        self.source.write_bytes(b"alpha\ngamma\n")
        self._commit_audit()

        with self.assertRaisesRegex(seal.SealError, "absent audit line"):
            seal.SourceMapper(self.repo, self.parent).map_site(
                "src/point_add/sample.rs", 3
            )

    def test_renamed_path_fails(self) -> None:
        renamed = self.repo / "src/point_add/renamed.rs"
        self.source.rename(renamed)
        self._commit_audit()

        with self.assertRaisesRegex(seal.SealError, "parent path"):
            seal.SourceMapper(self.repo, self.parent).map_site(
                "src/point_add/renamed.rs", 2
            )

    def test_outside_point_add_path_fails(self) -> None:
        with self.assertRaisesRegex(seal.SealError, "outside src/point_add"):
            seal.SourceMapper(self.repo, self.parent).map_site("src/circuit.rs", 1)

    def test_absolute_and_parent_traversal_paths_fail(self) -> None:
        mapper = seal.SourceMapper(self.repo, self.parent)
        for invalid in (
            str(self.source),
            "src/point_add/../circuit.rs",
            "src/point_add/nested/../../circuit.rs",
        ):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(seal.SealError, "source path"):
                    mapper.map_site(invalid, 1)

    def test_line_bytes_differing_after_structural_mapping_fail(self) -> None:
        self.source.write_bytes(b"alpha\nchanged\ngamma\n")
        self._commit_audit()
        mapper = seal.SourceMapper(self.repo, self.parent)

        with mock.patch.object(mapper, "_hunks_for_path", return_value=()):
            with self.assertRaisesRegex(seal.SealError, "line bytes differ"):
                mapper.map_site("src/point_add/sample.rs", 2)

    def test_synthetic_site_stays_covered_but_is_not_a_family_candidate(self) -> None:
        mapper = seal.SourceMapper(self.repo, self.parent)

        mapped = seal.map_origin_site(
            mapper,
            "src/point_add/audit_generated.rs",
            99,
            seal.ORIGIN_SYNTHETIC_TAIL,
        )

        self.assertEqual(mapped.parent_file, "-")
        self.assertIsNone(mapped.parent_line)
        self.assertTrue(mapped.audit_generated)
        self.assertFalse(mapped.family_candidate)


@unittest.skipUnless(
    seal is not None and hasattr(seal, "seal_evidence"),
    "artifact sealing implementation is not present yet",
)
class SealerCliTests(unittest.TestCase):
    RAW_NAMES = {
        "audit-diagnostics.log",
        "families.tsv",
        "manifest.raw",
        "sites.tsv",
        "summary.raw",
        "witnesses.tsv",
    }

    FAMILY_HEADER = (
        "audit_path\taudit_line\ttrace_context\tkind\tdecision_count"
        "\tkeep_count\tno_cost_identity_count\tdrop_count\tlower_to_x_count"
        "\tlower_to_cx_count\tlower_to_neg_count\tlower_to_z_count"
        "\tlower_to_cz_count\tnone_count\teffective_condition_known0_count"
        "\tccx_control_known0_count\tccx_both_controls_known1_count"
        "\tccx_one_control_known1_count\tccz_operand_known0_count"
        "\tccz_three_operands_known1_count\tccz_two_operands_known1_count"
        "\tccz_one_operand_known1_count\tdisposition"
        "\tpredicate_source_literal_key\tpredicate_source_literal_value\n"
    )
    SITE_HEADER = (
        "site_id\taudit_path\taudit_line\ttrace_context\tsource_literal_key"
        "\tsource_literal_value\tinverse_depth\tflags\toccurrence_count"
        "\ttransform_chain\n"
    )
    WITNESS_HEADER = (
        "op_index\taudit_path\taudit_line\ttrace_context\tkind\tq_control2"
        "\tq_control1\tq_target\tc_condition\tfact_control2\tfact_control1"
        "\tfact_target\teffective_condition\taction\trule\tscore_eligible"
        "\tsite_id\temission_ordinal\tinverse_depth\tflags\ttransform_chain\n"
    )

    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="j3-seal-cli-")
        self.root = Path(self._temporary.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self._git("init", "-q")
        self._git("config", "user.name", "J3 Test")
        self._git("config", "user.email", "j3@example.invalid")
        (self.repo / "src/point_add").mkdir(parents=True)
        (self.repo / "src/point_add/sample.rs").write_text(
            "emit_ccx();\nemit_ccz();\n", encoding="ascii"
        )
        (self.repo / "Cargo.toml").write_text("[package]\nname='fixture'\n", encoding="ascii")
        (self.repo / "Cargo.lock").write_text("# fixture\n", encoding="ascii")
        (self.repo / "benchmark.sh").write_text("#!/bin/sh\n", encoding="ascii")
        self._git("add", ".")
        self._git("commit", "-qm", "parent")
        self.parent = self._git("rev-parse", "HEAD").strip()
        self.parent_tree = self._git("rev-parse", "HEAD^{tree}").strip()
        (self.repo / "benchmark.sh").write_text("#!/bin/sh\n# audit fixture\n", encoding="ascii")
        self._git("add", "benchmark.sh")
        self._git("commit", "-qm", "implementation")

        self.ops = self.root / "ops.bin"
        self._write_ops(self.ops, [13, 13, 14])
        self.fingerprint = seal.fingerprint_ops(self.ops)
        self.raw = self.root / "raw"
        self.out = self.root / "evidence"
        self._write_raw()

        self._pins = mock.patch.multiple(
            seal,
            PINNED_OPERATION_COUNT=self.fingerprint.operation_count,
            PINNED_COMPRESSED_BYTES=self.fingerprint.compressed_bytes,
            PINNED_COMPRESSED_SHA256=self.fingerprint.compressed_sha256,
            PINNED_CANONICAL_RECORDS_SHA256=self.fingerprint.canonical_records_sha256,
            PINNED_TRUSTED_XOF32=self.fingerprint.trusted_xof32,
        )
        self._pins.start()
        self._rustc = mock.patch.object(
            seal, "_rustc_version", return_value="rustc fixture\\nrelease: 1.93.0"
        )
        self._rustc.start()

    def tearDown(self) -> None:
        self._rustc.stop()
        self._pins.stop()
        self._temporary.cleanup()

    def _git(self, *arguments: str) -> str:
        return subprocess.run(
            ["git", *arguments],
            cwd=self.repo,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ).stdout

    @staticmethod
    def _write_ops(path: Path, kinds: list[int]) -> None:
        records = bytearray()
        missing = (1 << 64) - 1
        for index, kind in enumerate(kinds):
            operands = [missing] * 6
            if kind in (13, 14):
                operands[:3] = [index * 3, index * 3 + 1, index * 3 + 2]
            records.extend(struct.pack("<I4x6Q", kind, *operands))
        compressed = subprocess.run(
            ["zstd", "-q", "-c"],
            input=bytes(records),
            check=True,
            stdout=subprocess.PIPE,
        ).stdout
        path.write_bytes(b"QECCOPSZ" + struct.pack("<Q", len(kinds)) + compressed)

    @staticmethod
    def _family_row(
        *,
        line: int,
        kind: str,
        decision_count: int,
        actions: dict[str, int],
        rules: dict[str, int],
        disposition: str = "uniform_provisional",
        predicate: tuple[str, str] = ("-", "-"),
    ) -> str:
        action_names = (
            "keep",
            "no_cost_identity",
            "drop",
            "lower_to_x",
            "lower_to_cx",
            "lower_to_neg",
            "lower_to_z",
            "lower_to_cz",
        )
        rule_names = (
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
        values = [
            "src/point_add/sample.rs",
            str(line),
            "7",
            kind,
            str(decision_count),
            *(str(actions.get(name, 0)) for name in action_names),
            *(str(rules.get(name, 0)) for name in rule_names),
            disposition,
            predicate[0],
            predicate[1],
        ]
        return "\t".join(values) + "\n"

    @staticmethod
    def _witness_row(
        op_index: int,
        action: str,
        rule: str,
        score_eligible: int,
        *,
        flags: int = 0,
    ) -> str:
        values = [
            str(op_index),
            "src/point_add/sample.rs",
            "1",
            "7",
            "ccx",
            "0",
            "1",
            "2",
            str((1 << 64) - 1),
            "known0",
            "unknown",
            "unknown",
            "known1",
            action,
            rule,
            str(score_eligible),
            "0",
            str(op_index),
            "0",
            str(flags),
            "synthetic_tail" if flags & 1 else "-",
        ]
        return "\t".join(values) + "\n"

    def _write_raw(
        self,
        *,
        ccx_actions: tuple[tuple[str, str, int], ...] = (
            ("drop", "ccx_control_known0", 1),
            ("drop", "ccx_control_known0", 1),
        ),
        synthetic_ccx: bool = False,
    ) -> None:
        if self.raw.exists():
            shutil.rmtree(self.raw)
        self.raw.mkdir()
        flags = 1 if synthetic_ccx else 0
        transform = "synthetic_tail" if synthetic_ccx else "-"
        sites = self.SITE_HEADER
        sites += (
            "0\tsrc/point_add/sample.rs\t1\t7\t4294967295\t4294967295"
            f"\t0\t{flags}\t2\t{transform}\n"
        )
        sites += (
            "1\tsrc/point_add/sample.rs\t2\t7\t4294967295\t4294967295"
            "\t0\t0\t1\t-\n"
        )
        (self.raw / "sites.tsv").write_text(sites, encoding="ascii")

        action_counts: dict[str, int] = {}
        rule_counts: dict[str, int] = {}
        witnesses = self.WITNESS_HEADER
        for index, (action, rule, score_eligible) in enumerate(ccx_actions):
            action_counts[action] = action_counts.get(action, 0) + 1
            rule_counts[rule] = rule_counts.get(rule, 0) + 1
            if action != "keep":
                witnesses += self._witness_row(
                    index, action, rule, score_eligible, flags=flags
                )
        (self.raw / "witnesses.tsv").write_text(witnesses, encoding="ascii")

        nonzero_actions = sum(value != 0 for value in action_counts.values())
        nonzero_rules = sum(value != 0 for value in rule_counts.values())
        disposition = (
            "uniform_provisional"
            if nonzero_actions == 1 and nonzero_rules == 1
            else "diagnostic_mixed"
        )
        families = self.FAMILY_HEADER
        families += self._family_row(
            line=1,
            kind="ccx",
            decision_count=2,
            actions=action_counts,
            rules=rule_counts,
            disposition=disposition,
        )
        families += self._family_row(
            line=2,
            kind="ccz",
            decision_count=1,
            actions={"keep": 1},
            rules={"none": 1},
        )
        (self.raw / "families.tsv").write_text(families, encoding="ascii")

        witness_count = sum(action != "keep" for action, _, _ in ccx_actions)
        manifest = {
            "canonical_records_sha256": self.fingerprint.canonical_records_sha256,
            "ccx_count": "2",
            "ccz_count": "1",
            "decision_count": "3",
            "family_count": "2",
            "format": "j3-dead-gate-raw-v1",
            "operation_count": "3",
            "provenance_count": "3",
            "provenance_sha256": "a" * 64,
            "trusted_xof32": self.fingerprint.trusted_xof32,
            "witness_count": str(witness_count),
            "xof_words_consumed": "0",
        }
        (self.raw / "manifest.raw").write_text(
            "".join(f"{key}={value}\n" for key, value in manifest.items()),
            encoding="ascii",
        )
        summary = {
            "diagnostic_family_count": str(int(disposition == "diagnostic_mixed")),
            "exact_predicate_provisional_family_count": "0",
            "keep_decision_count": str(sum(action == "keep" for action, _, _ in ccx_actions) + 1),
            "non_keep_decision_count": str(witness_count),
            "uniform_provisional_family_count": str(
                int(disposition == "uniform_provisional") + 1
            ),
        }
        (self.raw / "summary.raw").write_text(
            "".join(f"{key}={value}\n" for key, value in summary.items()),
            encoding="ascii",
        )
        (self.raw / "audit-diagnostics.log").write_bytes(b"")
        self.assertEqual({entry.name for entry in self.raw.iterdir()}, self.RAW_NAMES)

    def _seal(self, out: Path | None = None) -> dict[str, str]:
        return seal.seal_evidence(
            self.repo,
            self.parent,
            self.parent_tree,
            self.raw,
            self.ops,
            self.out if out is None else out,
        )

    def _mark_ccx_family_as_exact_predicate(self, key: int, value: int) -> None:
        families_path = self.raw / "families.tsv"
        lines = families_path.read_text(encoding="ascii").splitlines()
        header = lines[0].split("\t")
        fields = lines[1].split("\t")
        fields[header.index("disposition")] = "exact_predicate_provisional"
        fields[header.index("predicate_source_literal_key")] = str(key)
        fields[header.index("predicate_source_literal_value")] = str(value)
        lines[1] = "\t".join(fields)
        families_path.write_text("\n".join(lines) + "\n", encoding="ascii")
        summary = self.raw / "summary.raw"
        summary.write_text(
            summary.read_text(encoding="ascii")
            .replace("diagnostic_family_count=1", "diagnostic_family_count=0")
            .replace(
                "exact_predicate_provisional_family_count=0",
                "exact_predicate_provisional_family_count=1",
            ),
            encoding="ascii",
        )

    @staticmethod
    def _replace_key(path: Path, key: str, replacement: str) -> None:
        rows = path.read_text(encoding="ascii").splitlines()
        rewritten = [
            f"{key}={replacement}" if row.startswith(f"{key}=") else row
            for row in rows
        ]
        path.write_text("\n".join(rewritten) + "\n", encoding="ascii")

    def test_fingerprint_validates_padding_and_all_three_digests(self) -> None:
        self.assertEqual(self.fingerprint.operation_count, 3)
        self.assertEqual(self.fingerprint.kind_counts[13:15], (2, 1))
        bad = self.root / "bad-padding.bin"
        missing = (1 << 64) - 1
        record = struct.pack("<I", 13) + b"\x01\0\0\0" + struct.pack(
            "<6Q", 0, 1, 2, missing, missing, missing
        )
        compressed = subprocess.run(
            ["zstd", "-q", "-c"], input=record, check=True, stdout=subprocess.PIPE
        ).stdout
        bad.write_bytes(b"QECCOPSZ" + struct.pack("<Q", 1) + compressed)
        with self.assertRaisesRegex(seal.SealError, "padding"):
            seal.fingerprint_ops(bad)

    def test_raw_directory_requires_exact_file_names(self) -> None:
        (self.raw / "extra.log").write_bytes(b"")
        with self.assertRaisesRegex(seal.SealError, "raw artifact set"):
            self._seal()
        self.assertFalse(self.out.exists())

    def test_raw_manifest_requires_exact_duplicate_free_schema(self) -> None:
        manifest = self.raw / "manifest.raw"
        original = manifest.read_text(encoding="ascii").splitlines(keepends=True)
        for mutation in ("duplicate", "missing", "extra"):
            with self.subTest(mutation=mutation):
                rows = original.copy()
                if mutation == "duplicate":
                    rows.insert(1, rows[0])
                elif mutation == "missing":
                    rows.pop(0)
                else:
                    rows.append("unexpected=1\n")
                manifest.write_text("".join(rows), encoding="ascii")
                with self.assertRaisesRegex(seal.SealError, "manifest"):
                    self._seal()
        manifest.write_text("".join(original), encoding="ascii")

    def test_duplicate_and_missing_tsv_keys_fail(self) -> None:
        sites = self.raw / "sites.tsv"
        sites.write_bytes(sites.read_bytes() + sites.read_bytes().splitlines(keepends=True)[1])
        with self.assertRaisesRegex(seal.SealError, "duplicate site key"):
            self._seal()
        self._write_raw()
        witnesses = self.raw / "witnesses.tsv"
        lines = witnesses.read_text(encoding="ascii").splitlines()
        fields = lines[1].split("\t")
        fields[self.WITNESS_HEADER.rstrip("\n").split("\t").index("site_id")] = "9"
        lines[1] = "\t".join(fields)
        witnesses.write_text("\n".join(lines) + "\n", encoding="ascii")
        with self.assertRaisesRegex(seal.SealError, "missing site key"):
            self._seal()

    def test_occurrence_count_and_origin_count_drift_fail(self) -> None:
        sites = self.raw / "sites.tsv"
        sites.write_text(
            sites.read_text(encoding="ascii").replace("\t0\t0\t1\t-\n", "\t0\t0\t2\t-\n"),
            encoding="ascii",
        )
        with self.assertRaisesRegex(seal.SealError, "occurrence count"):
            self._seal()
        self._write_raw()
        self._replace_key(self.raw / "manifest.raw", "provenance_count", "2")
        with self.assertRaisesRegex(seal.SealError, "provenance_count"):
            self._seal()

    def test_incomplete_ccx_ccz_census_fails(self) -> None:
        self._replace_key(self.raw / "manifest.raw", "decision_count", "2")
        with self.assertRaisesRegex(seal.SealError, "decision census"):
            self._seal()

    def test_mixed_family_is_rejected(self) -> None:
        self._write_raw(
            ccx_actions=(
                ("drop", "ccx_control_known0", 1),
                ("keep", "none", 0),
            )
        )
        manifest = self._seal()
        self.assertEqual(manifest["qualifying_family_count"], "0")
        self.assertEqual(manifest["verdict"], "HARD_NACK")

    @unittest.skipUnless(
        seal is not None and hasattr(seal, "IndependentPredicate"),
        "independent predicate implementation is not present yet",
    )
    def test_exact_predicate_requires_matching_independent_registration(self) -> None:
        self._write_raw(
            ccx_actions=(
                ("drop", "ccx_control_known0", 1),
                ("keep", "none", 0),
            )
        )
        self._mark_ccx_family_as_exact_predicate(2, 2)
        predicate = seal.IndependentPredicate(
            "src/point_add/sample.rs",
            1,
            7,
            "ccx",
            1,
            1,
            "source_literal_key=1,value=1",
        )
        with mock.patch.object(
            seal, "INDEPENDENT_EXACT_PARENT_PREDICATES", (predicate,)
        ):
            manifest = self._seal()
        self.assertEqual(manifest["verdict"], "HARD_NACK")

    @unittest.skipUnless(
        seal is not None and hasattr(seal, "IndependentPredicate"),
        "independent predicate implementation is not present yet",
    )
    def test_matching_independent_exact_predicate_is_admitted(self) -> None:
        self._write_raw(
            ccx_actions=(
                ("drop", "ccx_control_known0", 1),
                ("keep", "none", 0),
            )
        )
        self._mark_ccx_family_as_exact_predicate(1, 1)
        predicate = seal.IndependentPredicate(
            "src/point_add/sample.rs",
            1,
            7,
            "ccx",
            1,
            1,
            "source_literal_key=1,value=1",
        )
        with mock.patch.object(
            seal, "INDEPENDENT_EXACT_PARENT_PREDICATES", (predicate,)
        ):
            manifest = self._seal()
            seal.verify_evidence(
                self.repo,
                self.parent,
                self.parent_tree,
                self.out,
                self.ops,
            )
        self.assertEqual(manifest["qualifying_family_count"], "1")
        self.assertEqual(manifest["verdict"], "ADMIT")

    def test_uniform_score_eligible_family_is_admitted(self) -> None:
        manifest = self._seal()
        self.assertEqual(manifest["qualifying_family_count"], "1")
        self.assertEqual(manifest["verdict"], "ADMIT")

    def test_no_cost_only_family_is_rejected(self) -> None:
        self._write_raw(
            ccx_actions=(
                ("no_cost_identity", "effective_condition_known0", 0),
                ("no_cost_identity", "effective_condition_known0", 0),
            )
        )
        manifest = self._seal()
        self.assertEqual(manifest["verdict"], "HARD_NACK")

    def test_audit_generated_family_is_rejected(self) -> None:
        self._write_raw(synthetic_ccx=True)
        manifest = self._seal()
        self.assertEqual(manifest["verdict"], "HARD_NACK")

    def test_seals_byte_identical_output_and_excludes_build_stderr(self) -> None:
        (self.raw.parent / "build-stderr.log").write_text(
            "ordinary compiler stderr\n", encoding="ascii"
        )
        first = self.root / "first"
        second = self.root / "second"
        self._seal(first)
        self._seal(second)
        for name in seal.FINAL_NAMES:
            self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
        self.assertEqual((first / "stderr.log").read_bytes(), b"")

    def test_raw_hash_mismatches_fail(self) -> None:
        for key in ("canonical_records_sha256", "trusted_xof32"):
            with self.subTest(key=key):
                self._write_raw()
                self._replace_key(self.raw / "manifest.raw", key, "0" * 64)
                with self.assertRaisesRegex(seal.SealError, key):
                    self._seal()

    def test_every_pinned_ops_binding_mismatch_fails(self) -> None:
        mutations = {
            "PINNED_OPERATION_COUNT": self.fingerprint.operation_count + 1,
            "PINNED_COMPRESSED_BYTES": self.fingerprint.compressed_bytes + 1,
            "PINNED_COMPRESSED_SHA256": "0" * 64,
            "PINNED_CANONICAL_RECORDS_SHA256": "0" * 64,
            "PINNED_TRUSTED_XOF32": "0" * 64,
        }
        for name, value in mutations.items():
            with self.subTest(name=name), mock.patch.object(seal, name, value):
                with self.assertRaisesRegex(seal.SealError, "mismatch"):
                    self._seal()

    def test_audit_failure_does_not_create_or_replace_final_directory(self) -> None:
        self.out.mkdir()
        sentinel = self.out / "sentinel"
        sentinel.write_text("preserve", encoding="ascii")
        (self.raw / "audit-diagnostics.log").write_text("audit failed\n", encoding="ascii")
        with self.assertRaisesRegex(seal.SealError, "audit diagnostics"):
            self._seal()
        self.assertEqual(sentinel.read_text(encoding="ascii"), "preserve")
        self.assertEqual({entry.name for entry in self.out.iterdir()}, {"sentinel"})

    def test_verify_accepts_valid_fixture(self) -> None:
        self._seal()
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = seal.main(
                [
                    "verify",
                    "--repo",
                    str(self.repo),
                    "--parent",
                    self.parent,
                    "--parent-tree",
                    self.parent_tree,
                    "--evidence",
                    str(self.out),
                    "--ops",
                    str(self.ops),
                ]
            )
        self.assertEqual(result, 0)
        self.assertEqual(stdout.getvalue(), "VERIFIED j3-dead-gate-audit-v1\n")

    def test_verify_accepts_unrelated_commit_after_implementation(self) -> None:
        self._seal()
        (self.repo / "README.md").write_text("unrelated\n", encoding="ascii")
        self._git("add", "README.md")
        self._git("commit", "-qm", "unrelated")
        seal.verify_evidence(
            self.repo,
            self.parent,
            self.parent_tree,
            self.out,
            self.ops,
        )

    def test_verify_rejects_scoped_source_change_after_implementation(self) -> None:
        self._seal()
        (self.repo / "benchmark.sh").write_text("#!/bin/sh\n# changed later\n", encoding="ascii")
        self._git("add", "benchmark.sh")
        self._git("commit", "-qm", "scoped change")
        with self.assertRaisesRegex(seal.SealError, "scoped source changed"):
            seal.verify_evidence(
                self.repo,
                self.parent,
                self.parent_tree,
                self.out,
                self.ops,
            )

    def test_verify_rejects_mutation_of_every_final_file(self) -> None:
        for name in seal.FINAL_NAMES:
            with self.subTest(name=name):
                if self.out.exists():
                    shutil.rmtree(self.out)
                self._seal()
                path = self.out / name
                path.write_bytes(path.read_bytes() + b"mutation\n")
                before = {entry.name: entry.read_bytes() for entry in self.out.iterdir()}
                with self.assertRaises(seal.SealError):
                    seal.verify_evidence(
                        self.repo,
                        self.parent,
                        self.parent_tree,
                        self.out,
                        self.ops,
                    )
                after = {entry.name: entry.read_bytes() for entry in self.out.iterdir()}
                self.assertEqual(after, before)

    def test_verify_rejects_duplicate_missing_and_extra_manifest_keys(self) -> None:
        for mutation in ("duplicate", "missing", "extra"):
            with self.subTest(mutation=mutation):
                if self.out.exists():
                    shutil.rmtree(self.out)
                self._seal()
                manifest = self.out / "manifest.txt"
                rows = manifest.read_text(encoding="ascii").splitlines(keepends=True)
                if mutation == "duplicate":
                    rows.append(rows[0])
                elif mutation == "missing":
                    rows.pop(0)
                else:
                    rows.append("unexpected=1\n")
                manifest.write_text("".join(rows), encoding="ascii")
                with self.assertRaisesRegex(seal.SealError, "manifest"):
                    seal.verify_evidence(
                        self.repo,
                        self.parent,
                        self.parent_tree,
                        self.out,
                        self.ops,
                    )

    def test_verify_rejects_each_manifest_field_class(self) -> None:
        mutations = {
            "parent_commit": "0" * 40,
            "canonical_records_sha256": "0" * 64,
            "operation_count": "4",
            "format": "wrong-format",
            "audit_flag": "J3_DEAD_GATE_AUDIT=0",
            "rustc_version": "rustc wrong",
            "verdict": "HARD_NACK",
        }
        for key, value in mutations.items():
            with self.subTest(key=key):
                if self.out.exists():
                    shutil.rmtree(self.out)
                self._seal()
                self._replace_key(self.out / "manifest.txt", key, value)
                with self.assertRaises(seal.SealError):
                    seal.verify_evidence(
                        self.repo,
                        self.parent,
                        self.parent_tree,
                        self.out,
                        self.ops,
                    )

    def test_verify_rejects_family_count_witness_row_and_verdict_mutations(self) -> None:
        for target in ("family_count", "witness", "verdict"):
            with self.subTest(target=target):
                if self.out.exists():
                    shutil.rmtree(self.out)
                self._seal()
                if target == "family_count":
                    self._replace_key(self.out / "manifest.txt", "family_count", "99")
                elif target == "witness":
                    path = self.out / "witnesses.tsv"
                    path.write_text(
                        path.read_text(encoding="ascii").replace("\tdrop\t", "\tlower_to_x\t", 1),
                        encoding="ascii",
                    )
                else:
                    self._replace_key(self.out / "manifest.txt", "verdict", "HARD_NACK")
                with self.assertRaises(seal.SealError):
                    seal.verify_evidence(
                        self.repo,
                        self.parent,
                        self.parent_tree,
                        self.out,
                        self.ops,
                    )


class BenchmarkWrapperTests(unittest.TestCase):
    def test_wrapper_separates_stderr_and_seals_only_exact_audit_raw_files(self) -> None:
        benchmark = Path(__file__).resolve().parents[4] / "benchmark.sh"
        source = benchmark.read_text(encoding="utf-8")
        self.assertIn('${ops_scratch}/build-stderr.log', source)
        self.assertIn('cat "${ops_scratch}/build-stderr.log" >&2', source)
        self.assertIn('J3_DEAD_GATE_AUDIT:-0', source)
        self.assertIn('j3_dead_gate_seal.py', source)
        self.assertIn('--raw-dir "${raw_audit_dir}"', source)
        self.assertNotIn('--raw-dir "${ops_scratch}"', source)


if __name__ == "__main__":
    unittest.main()
