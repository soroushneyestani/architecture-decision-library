import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHECKER = PROJECT_ROOT / "scripts" / "check_adrs.py"
ADR_NAME = "0001-version-decisions.md"


def adr_text(title="Version decisions", status="Accepted", evidence="../evidence/proof.md", replacement=None):
    successor = f"\nSuperseded by: [Replacement]({replacement})" if replacement is not None else ""
    return f"""# {title}

Status: {status}
Date: 2026-11-18{successor}

## Context

Teams need a way to recover why the design changed.

## Options

- Keep discussions in an issue tracker.
- Store decisions alongside changes.

## Decision

Adopt versioned decision records.

## Trade-offs

Maintainers must keep the decision index current.

## Confirmation

A documented rationale and its verification file appear together in version control.

## Evidence

- [Fixture evidence]({evidence})
"""


class CheckerContractTests(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory(dir=PROJECT_ROOT, prefix=".verify-adr-")
        self.addCleanup(scratch.cleanup)
        self.fixture = Path(scratch.name)
        self.root = self.fixture / "repository with spaces"
        self.adrs = self.root / "docs" / "adr"
        self.evidence = self.root / "docs" / "evidence"
        self.adrs.mkdir(parents=True)
        self.evidence.mkdir()
        self.index = self.adrs / "README.md"
        self.record = self.adrs / ADR_NAME
        self.write(self.record, adr_text())
        self.write(self.evidence / "proof.md", "# Synthetic evidence\n")

    @staticmethod
    def write(path, content):
        path.write_text(content, encoding="utf-8", newline="\n")

    def run_checker(self, *options):
        return subprocess.run(
            [sys.executable, "-X", "utf8", "-B", str(CHECKER), "--root", str(self.root), *options],
            cwd=self.fixture,
            capture_output=True,
            encoding="utf-8",
            timeout=15,
            check=False,
        )

    def assert_valid(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

    def assert_invalid(self, result, path=None):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr.strip())
        if path:
            self.assertIn(path, result.stderr)

    def test_render_is_stable_sorted_utf8_and_round_trips(self):
        self.write(self.record, adr_text(title="Décision α"))
        self.write(self.adrs / "0021-replace-build.md", adr_text("Replace build", "Superseded", replacement=ADR_NAME))
        self.write(self.adrs / "0009-share-design.md", adr_text("Share design", "Proposed"))
        self.write(self.adrs / "TEMPLATE.md", "# This is a template\n")
        self.write(self.index, "# This index is discarded in print mode\n")

        rendered = self.run_checker("--print-index")
        self.assert_valid(rendered)
        self.assertTrue(rendered.stdout.startswith("# Architecture decisions\n"))
        rows = [
            "| 0001 | [Décision α](0001-version-decisions.md) | Accepted | 2026-11-18 |",
            "| 0009 | [Share design](0009-share-design.md) | Proposed | 2026-11-18 |",
            "| 0021 | [Replace build](0021-replace-build.md) | Superseded | 2026-11-18 |",
        ]
        self.assertEqual([line for line in rendered.stdout.splitlines() if line.startswith("| 0")], rows)
        self.assertEqual(self.run_checker("--print-index").stdout, rendered.stdout)

        self.write(self.index, rendered.stdout)
        checked = self.run_checker()
        self.assert_valid(checked)
        self.assertEqual(checked.stdout, "Verified 3 architecture decisions.\n")

    def test_missing_or_stale_index_is_rejected(self):
        missing = self.run_checker()
        self.assert_invalid(missing)
        self.assertIn("index", missing.stderr.casefold())

        rendered = self.run_checker("--print-index")
        self.assert_valid(rendered)
        self.write(self.index, rendered.stdout)
        self.write(self.record, adr_text(title="Replace the decision title"))
        stale = self.run_checker()
        self.assert_invalid(stale)
        self.assertIn("index", stale.stderr.casefold())

    def test_invalid_metadata_or_structure_is_rejected(self):
        valid = adr_text()
        trade_offs = "## Trade-offs\n\nMaintainers must keep the decision index current.\n\n"
        out_of_order = (
            valid.replace("## Decision", "## Placeholder")
            .replace("## Trade-offs", "## Decision")
            .replace("## Placeholder", "## Trade-offs")
        )
        invalid_records = {
            "no level-one title": valid.replace("# Version decisions", "Version decisions"),
            "unknown status": valid.replace("Status: Accepted", "Status: Draft"),
            "mis-cased status": valid.replace("Status: Accepted", "Status: accepted"),
            "duplicate metadata": valid.replace("Status: Accepted", "Status: Accepted\nStatus: Proposed"),
            "invalid calendar date": valid.replace("2026-11-18", "2026-02-29"),
            "non-ISO date": valid.replace("2026-11-18", "2026-1-8"),
            "missing section": valid.replace(trade_offs, ""),
            "missing confirmation": valid.replace("## Confirmation\n", ""),
            "empty confirmation": valid.replace("A documented rationale and its verification file appear together in version control.", ""),
            "empty section": valid.replace("Adopt versioned decision records.", ""),
            "out of order sections": out_of_order,
            "duplicate section": valid.replace("## Evidence", "## Decision\n\nChoose again.\n\n## Evidence"),
            "one option": valid.replace("- Store decisions alongside changes.\n", ""),
            "no evidence links": valid.replace("- [Fixture evidence](../evidence/proof.md)", "A description without a link."),
        }
        for case, document in invalid_records.items():
            with self.subTest(case=case):
                self.write(self.record, document)
                self.assert_invalid(self.run_checker("--print-index"), ADR_NAME)

    def test_superseded_chain_can_end_at_an_accepted_record(self):
        second = "0002-first-replacement.md"
        third = "0003-current-decision.md"
        self.write(self.record, adr_text(status="Superseded", replacement=second))
        self.write(self.adrs / second, adr_text("First replacement", "Superseded", replacement=third))
        self.write(self.adrs / third, adr_text("Current decision"))

        result = self.run_checker("--print-index")
        self.assert_valid(result)
        self.write(self.index, result.stdout)
        self.assert_valid(self.run_checker())

    def test_replacement_metadata_is_required_only_for_superseded(self):
        invalid = (
            adr_text(status="Superseded"),
            adr_text(status="Superseded", replacement="../evidence/proof.md"),
            adr_text(status="Superseded", replacement=f"./{ADR_NAME}"),
            adr_text(status="Superseded", replacement=f"{ADR_NAME}#context"),
            adr_text(status="Proposed", replacement=ADR_NAME),
            adr_text(replacement=ADR_NAME),
        )
        for document in invalid:
            with self.subTest(document=document):
                self.write(self.record, document)
                result = self.run_checker("--print-index")
                self.assert_invalid(result, ADR_NAME)
                self.assertIn("Superseded", result.stderr)

    def test_missing_and_proposed_successors_fail(self):
        successor = "0002-future-decision.md"
        self.write(self.record, adr_text(status="Superseded", replacement=successor))
        missing = self.run_checker("--print-index")
        self.assert_invalid(missing, ADR_NAME)
        self.assertIn("missing successor", missing.stderr)

        self.write(self.adrs / successor, adr_text("Future decision", "Proposed"))
        proposed = self.run_checker("--print-index")
        self.assert_invalid(proposed, ADR_NAME)
        self.assertIn("is Proposed", proposed.stderr)

    def test_self_reference_and_successor_cycles_fail(self):
        self.write(self.record, adr_text(status="Superseded", replacement=ADR_NAME))
        itself = self.run_checker("--print-index")
        self.assert_invalid(itself, ADR_NAME)
        self.assertIn("itself", itself.stderr)

        successor = "0002-replace-decision.md"
        self.write(self.record, adr_text(status="Superseded", replacement=successor))
        self.write(self.adrs / successor, adr_text("Replace decision", "Superseded", replacement=ADR_NAME))
        cycle = self.run_checker("--print-index")
        self.assert_invalid(cycle, ADR_NAME)
        self.assertIn("cycle", cycle.stderr)

    def test_supported_body_references_and_fenced_examples(self):
        references = (
            "See [source](../evidence/proof.md#detail) and [this ADR](./0001-version-decisions.md). "
            "A [section](#confirmation) and [web reference](https://example.invalid/proof) can provide context.\n\n"
            "The literal syntax example `` [code span](missing.md) with one ` inside `` is plain text.\n\n"
            "````markdown\n## Ignored heading\n[illustrative only](missing.md)\n```\n````\n\n"
            "~~~markdown\n[also illustrative](missing.md)\n~~~"
        )
        self.write(self.record, adr_text().replace("Adopt versioned decision records.", references))
        result = self.run_checker("--print-index")
        self.assert_valid(result)

    def test_broken_local_references_outside_evidence_fail(self):
        self.write(self.fixture / "outside.md", "# Outside the synthetic repository\n")
        (self.evidence / "directory").mkdir()
        for target in (
            "missing.md",
            "../evidence/missing.md#detail",
            "../../../outside.md",
            "../evidence/directory",
            "/docs/evidence/proof.md",
            "../evidence/proof%20not%20supported.md",
            "../evidence/proof.md/",
            "../evidence/proof.md/.",
        ):
            with self.subTest(target=target):
                self.write(self.record, adr_text().replace(
                    "Adopt versioned decision records.", f"Consult [the requirement]({target}).",
                ))
                result = self.run_checker("--print-index")
                self.assert_invalid(result, ADR_NAME)
                self.assertIn(target.split("#")[0], result.stderr)

    def test_unclosed_code_fence_reports_the_record(self):
        self.write(self.record, adr_text().replace("Adopt versioned decision records.", "```markdown\n# Broken fence"))
        result = self.run_checker("--print-index")
        self.assert_invalid(result, ADR_NAME)
        self.assertIn("unclosed Markdown code fence", result.stderr)

    def test_duplicate_and_malformed_filenames_are_rejected(self):
        duplicate = self.adrs / "0001-other-decision.md"
        self.write(duplicate, adr_text(title="Another decision"))
        result = self.run_checker("--print-index")
        self.assert_invalid(result)
        self.assertIn("0001", result.stderr)
        duplicate.unlink()

        for name in ("0000-zero-id.md", "9999_not-kebab.md", "0002-Uppercase.md"):
            with self.subTest(name=name):
                candidate = self.adrs / name
                self.write(candidate, adr_text())
                self.assert_invalid(self.run_checker("--print-index"), name)
                candidate.unlink()

    def test_invalid_utf8_reports_adr_path(self):
        self.record.write_bytes(b"# malformed UTF-8\xff\n")
        self.assert_invalid(self.run_checker("--print-index"), ADR_NAME)

    def test_missing_external_escaping_and_directory_targets_are_rejected(self):
        self.write(self.fixture / "outside.md", "# Outside the synthetic repository\n")
        (self.evidence / "directory.md").mkdir()
        for target in (
            "../evidence/missing.md",
            "https://example.invalid/proof.md",
            "../evidence/../../../outside.md",
            "../evidence/directory.md",
            "../evidence/proof.md/",
        ):
            with self.subTest(target=target):
                self.write(self.record, adr_text(evidence=target))
                self.assert_invalid(self.run_checker("--print-index"), ADR_NAME)

    def test_symlink_cannot_escape_the_repository(self):
        outside = self.fixture / "outside.md"
        self.write(outside, "# Outside the synthetic repository\n")
        try:
            (self.evidence / "link.md").symlink_to(outside)
        except (NotImplementedError, OSError) as error:
            self.skipTest(f"cannot create a symlink in this environment: {error}")
        self.write(self.record, adr_text(evidence="../evidence/link.md"))
        self.assert_invalid(self.run_checker("--print-index"), ADR_NAME)

    def test_argument_misuse_returns_two(self):
        for arguments in (("--unknown-flag",), ("--root",)):
            with self.subTest(arguments=arguments):
                result = self.run_checker(*arguments)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertIn("usage:", result.stderr.casefold())


if __name__ == "__main__":
    unittest.main()
