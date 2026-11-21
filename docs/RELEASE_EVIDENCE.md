# 0.1.0 verification

Version 0.1.0 contains six decision records, a generated index, an original template, and the Python checker and contract suite. Five records are accepted. The whole-file search record is superseded by the implemented streaming design. Follow each confirmation section to its evidence note. [Decision index](adr/README.md)

| Check | Evidence |
| --- | --- |
| Record and index consistency | Windows PowerShell 5.1 and Python 3.13.1 verified all six records and the committed ID-ordered index. The 15 contract tests passed, including an escaping symlink fixture. |
| Lifecycle and reference cases | The suite covers missing confirmation and invalid status, duplicate IDs, broken or escaping links, a symlink escape, missing or Proposed replacements, self-references and cycles. An accepted terminal replacement has a passing fixture. |
| Released implementations | The CLI and CI case studies cite exact public revisions, test source and successful public runs. The retained search decision has historical release evidence and the streaming replacement has its own implementation and verification links. |
| Runtime and CI | Actionlint 1.7.12 validated the workflow. It runs the Python 3.13 verifier on Ubuntu 24.04 and Windows Server 2025, and the Ubuntu job also checks the source archive and scans Git history. |

[Format contract](SPEC.md) · [Contract tests](../tests/test_check_adrs.py) · [CI workflow](../.github/workflows/ci.yml)

## Reproduce the checks

```powershell
python -X utf8 -B scripts/check_adrs.py
python -X utf8 -B tests/test_check_adrs.py -v
pwsh -NoProfile -File scripts/verify.ps1
```

From a Git checkout, run `python -X utf8 -B scripts/package_source.py FULL_REVIEWED_SHA`. The packager takes bytes from Git, excludes workspace governance and private development records, embeds the commit in the ZIP comment, reads back each ZIP entry, and writes the SHA-256 manifest. An extracted source archive can run the checker and tests without Git metadata. Rebuilding the archive requires the Git commit.

The checker verifies structure, supported local targets and status relationships offline. A reviewer checks external destinations, heading fragments, and whether the cited tests substantiate the decisions. A hosted run's successful outcome applies to its recorded commit, runner and toolchain. Release review records the source SHA, archive checksum and hosted run history independently of the source ZIP.
