# Contributing

Keep a decision focused on one consequential choice. Start from the [template](docs/adr/TEMPLATE.md), use the next unused ID and add context, at least two alternatives, rationale, benefits and costs, and an observable confirmation criterion. Include a local evidence note. Keep proprietary material, sensitive data and private links out of a contribution. Use exact public revisions and public tests where possible.

Open a pull request with the decision, evidence and regenerated index. Reviewers compare the alternatives, check whether the cited implementation and tests support the rationale, and decide whether the status reflects the evidence. Keep a proposal open until its criteria have been verified. To replace an accepted design, preserve its record, mark it superseded, link to the replacement, and regenerate the index. [Lifecycle and format](docs/SPEC.md)

Use Python 3.13 and run `pwsh -NoProfile -File scripts/verify.ps1`. The suite validates the actual library and exercises control and misuse cases. Verify the same behavior in GitHub Actions before merging. For a checker change, update the format and the relevant contract case along with the implementation.
