# Scope workspace reads and validate whole files before matching

Status: Superseded
Date: 2026-11-18
Superseded by: [Stream search and stage matches through validation](0006-stream-search-and-stage-matches.md)

## Context

The developer CLI searches a user-selected directory. It skips symbolic-link entries and binary or invalid UTF-8 files. A file may contain a matching line before a later byte makes the whole file ineligible.

## Options

- Resolve all filesystem operations through an opened directory root and validate each file's contents before emitting results from it.
- Use an opened root with a separate validation pass, then reopen eligible files to stream matches with lower peak memory.

## Decision

Reject a link as the workspace root and use `os.OpenRoot` for descendant operations. Skip nonregular entries and sort relative paths before processing. Read and validate one complete file before emitting matches from it. Inspect file metadata without reading contents.

## Trade-offs

Complete-file validation delivered the skip rule in one read and avoided a line-length limit. Memory scaled with the largest file being read and the number of selected paths. The opened root constrained operations to that tree. Enumeration and reads still observed a live filesystem, so concurrent in-root changes could alter results. The later decision retained rooted operations and replaced the complete-file allocation.

## Confirmation

At the original release, check that symlink roots are rejected and symlink entries skipped. Confirm that an early match produces no output from a file if a later byte fails the UTF-8 or NUL eligibility checks. Confirm that inspection uses metadata and results follow the sorted relative paths.

## Evidence

- [Workspace implementation and filesystem fixtures](../evidence/workspace-search-validation.md)
