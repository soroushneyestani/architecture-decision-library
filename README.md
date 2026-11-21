# Architecture Decision Library

Architecture Decision Library keeps the reasoning behind software design changes in versioned Markdown. Each record states the alternatives, consequences, confirmation criteria and evidence. A Python checker validates the records and compares them with a generated index. The original template takes inspiration from MADR. [MADR reference](https://adr.github.io/madr/)

The examples cover a native developer CLI, a reusable CI toolkit and the library itself. The index retains replaced decisions alongside their successors. Evidence notes link to exact public source and test runs where available. [Decision index](docs/adr/README.md) · [Template](docs/adr/TEMPLATE.md) · [Documentation](docs/README.md)

## Verify the library

Use Python 3.13. The checker and contract suite use the standard library. With PowerShell 7 on Ubuntu or Windows, run:

```powershell
python -X utf8 -B scripts/check_adrs.py
pwsh -NoProfile -File scripts/verify.ps1
```

For Windows PowerShell 5.1, run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1`. The first command checks the records and committed index. The second also runs positive and negative contract tests. [Format and exit codes](docs/SPEC.md) · [Release evidence](docs/RELEASE_EVIDENCE.md)

## Maintain a decision

1. Copy the template into `docs/adr/` under the next unused four-digit ID and set `Status: Proposed`.
2. Record the design drivers, compare at least two viable options, choose an outcome and document its benefits, costs and criteria for revisiting it.
3. Add confirmation criteria and a local evidence note. Review the rationale with the change. Mark the record `Accepted` once the supporting evidence is verified.
4. When a later decision replaces it, retain the original ID and rationale. Mark the old record `Superseded` and link to its replacement in the metadata.
5. Regenerate the index and commit it with the affected records and evidence notes.

```powershell
$index = & python -X utf8 -B scripts/check_adrs.py --print-index
if ($LASTEXITCODE -ne 0) { throw 'Decision records failed validation.' }
$index | Set-Content -LiteralPath docs/adr/README.md -Encoding utf8
python -X utf8 -B scripts/check_adrs.py
```

The checker validates the library's Markdown conventions, local references and supersession graph. Reviewers judge whether the evidence supports the decision. External links and heading fragments are reviewed by people. [Contribution guide](CONTRIBUTING.md) · [Security reporting](SECURITY.md) · [License](LICENSE)

## Source distribution

The initial release is `v0.1.0`. The source ZIP includes the checker, its tests, all six decisions, evidence and documentation. Use the provided `SHA256SUMS.txt` to check the download, then run the verifier inside the extracted directory. [Release notes](docs/releases/v0.1.0.md) · [Changelog](CHANGELOG.md) · [Third-party notices](THIRD_PARTY_NOTICES.md)
