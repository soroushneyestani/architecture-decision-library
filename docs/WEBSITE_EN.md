# Architecture Decision Library

Architecture decisions tend to survive in code while their reasons disappear into issue comments, reviews, and memory. Architecture Decision Library gives those reasons a place in Git. Someone reviewing a change can find the original constraint, the options considered, the costs the project accepted, and the evidence available for the choice.

## What the library contains

The library combines an original Markdown template, a generated decision index, and a Python 3.13 checker that uses the standard library. The structure takes inspiration from Markdown Architectural Decision Records. Each numbered record has explicit status and date metadata and six required sections covering context, options, the decision, trade-offs, confirmation, and evidence. [Decision record contract](SPEC.md) · [MADR reference](https://adr.github.io/madr/)

Confirmation and evidence serve different purposes. A confirmation criterion states what an implementation must demonstrate. An evidence note points to the exact code or test result available for review. For a command-line decision, the criterion might specify the exit status observed by a calling script and the note can direct the reviewer to the compiled-process fixture that asserts it.

## Six decisions with traceable context

The library records six decisions, five accepted and one superseded. The records describe the use of Cobra for a Go command line, the original whole-file search behavior and its later streaming replacement, a fixed Windows CI entry point, an exact-toolchain Go build workflow, and the design of the ADR checker itself. The numbered index makes each record and its supporting note easy to find. [Browse the decision index](adr/README.md)

The search records show the reason for keeping superseded decisions. The earlier implementation chose whole-file validation to prevent results from a file that could later prove ineligible. The subsequent record explains the streaming choice in its own context and links to its implementation evidence. The two records preserve both the original constraint and the reason the solution changed. [Earlier search decision](adr/0002-workspace-search-validation.md) · [Streaming replacement](adr/0006-stream-search-and-stage-matches.md)

The checker also has its own decision record. A small parser and a deterministic renderer were chosen over adding a general-purpose Markdown parser. That keeps the installation surface small and the format reviewable. In return, authors follow a specific heading order and supported subset of Markdown. Format changes need coordinated updates to the checker, the authoring template, and regression fixtures. [Checker design decision](adr/0005-standard-library-adr-checker.md)

## Authoring and maintenance

A maintainer starts a decision as `Proposed`, describes at least two viable approaches, and defines how acceptance can be checked. A reviewed decision becomes `Accepted`. When a later decision replaces it, the earlier record becomes `Superseded` and points to its replacement. The checker validates replacement links, rejects cycles, and requires a replacement chain to end at an accepted decision. Preserving both records leaves their original reasons available to later reviewers.

The checker verifies filenames and unique IDs, exact metadata, the ordered document structure, supported local file references, and consistency of the committed index. A stale index fails the check. The same command can emit the canonical Markdown table in ID order so contributors can regenerate the committed file. Run the checks before review.

```powershell
python -X utf8 scripts/check_adrs.py
pwsh -NoProfile -File scripts/verify.ps1
```

The test fixtures exercise successful validation as well as malformed input such as missing or invalid metadata, duplicate IDs, broken references, and invalid replacement relationships. The GitHub Actions workflow checks the project on Windows and Ubuntu. The evidence record lists the actual verification checkpoints. [Source and verification instructions](../README.md) · [Verification evidence](RELEASE_EVIDENCE.md)

## Where the checks stop

File checks establish that the supported local targets in ADRs exist and that the records and index agree. Reviewers assess the strength of the evidence, the quality of the alternatives, and the effect of the trade-offs. They also check the destination of external links, Markdown fragments, and references inside the evidence notes. Running file checks locally keeps them reproducible and gives maintainers concrete errors to resolve before discussing the architectural choice.

Version `v0.1.0` is the initial source release. The documented format and commands describe that starting contract. [Source and release documentation](../README.md)
