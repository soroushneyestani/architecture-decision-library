# Validate Markdown records and derive the index with Python

Status: Accepted
Date: 2026-11-18

## Context

The architecture decision library needs readable Markdown records with working evidence references and a current index. A manually edited table can omit records or preserve obsolete metadata after a decision changes.

## Options

- Parse a small project-specific Markdown structure with the Python standard library and render a canonical index from the validated records.
- Use a general Markdown parser and build project-specific rules on its syntax tree, with a package dependency for the parser.

## Decision

Check numbered Markdown records, their required metadata and section order, and local evidence references using a Python standard-library script. Render an index from validated records in a fixed order. Provide a print mode for regenerating the table and a check mode that reports a stale committed index as a failure.

## Trade-offs

The checker needs only Python and provides a repeatable index comparison. The supported authoring format is deliberately narrow. Changes to the format require updating the checker, fixtures and template together. The checker establishes that evidence files and local references resolve. Readers still assess whether the linked evidence substantiates a decision. Revisit parser choice if the project needs general Markdown syntax or a shared schema across repositories.

## Confirmation

Run the checker and compare the committed index with the rendered output. Exercise valid and invalid fixtures for metadata, duplicate identifiers, status and lifecycle references, missing evidence, and a stale index. Confirm rejected fixtures produce diagnostics and the consistency check exits nonzero.

## Evidence

- [Checker source, fixtures, and verification entry point](../evidence/adr-checker.md)
