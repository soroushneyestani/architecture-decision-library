# Decision record and index contract

The library stores one Markdown file per decision in `docs/adr/`. Give each record a unique positive four-digit ID and a lowercase kebab-case filename, such as `0001-use-literal-search.md`. The checker reads UTF-8 and accepts a byte-order mark and Windows or Unix line endings.

## Record structure

Start with an H1 title, a `Status:` line and a `Date:` line in calendar format `YYYY-MM-DD`. Use `Proposed`, `Accepted` or `Superseded` with exact case. A superseded record has a third metadata line, `Superseded by: [Replacement title](0002-replacement.md)`. Provide these nonempty H2 sections exactly once in order.

1. **Context** describes the problem, constraints and decision drivers.
2. **Options** lists at least two distinct choices with `- ` bullets. Describe why each could fit or fail its relevant constraints.
3. **Decision** describes the selected option and rationale.
4. **Trade-offs** records benefits, costs, limitations and when to revisit them.
5. **Confirmation** states which observable criteria support or would confirm the decision.
6. **Evidence** lists local Markdown-style file links with `- ` bullets. A note can link to exact implementation revisions, tests or CI runs.

## Lifecycle

- **Proposed** records a decision under review. Use the evidence note for planned or preliminary verification and label its state.
- **Accepted** records a selected design with real supporting evidence. Choose this status through review after the confirmation criteria have been met.
- **Superseded** retains the old rationale and links to an existing replacement ADR in the same index. Each chain must end at an accepted record. Missing or proposed replacements, self-references and cycles fail validation.

Keep the original dated rationale and update its supersession metadata when replacing it. Give the replacement its own ID. The index is sorted by ID and includes all statuses.

## Checker boundaries

The checker compares the generated index only after validating the records. It validates relative file targets in supported ordinary inline Markdown links in the ADR body and requires file targets to stay within the repository even after resolving symlinks. Use plain ASCII paths with forward slashes and no spaces. A fragment after a file link does not alter the file being checked. Evidence bullets take plain relative file paths. Review heading anchors, HTTP(S) destinations, advanced Markdown link forms and evidence quality separately.

Run `python -X utf8 -B scripts/check_adrs.py` to validate the records and compare the committed index. It reports the record count on stdout and exits zero when consistent. With `--print-index`, it validates the records and emits the canonical index on stdout in ID order. `--root DIRECTORY` selects a repository root for either mode. Consistency and file errors exit 1 and produce diagnostics on stderr. Invalid CLI arguments exit 2.
