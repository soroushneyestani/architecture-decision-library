# Use Go and Cobra for the developer CLI

Status: Accepted
Date: 2026-11-18

## Context

The Developer CLI Toolkit exposes `search` and `inspect` as a single native executable. Its contract requires predictable help, argument counts, repeated suffix filters, and distinct exit statuses for matches, empty search results, and errors.

## Options

- Use Go with Cobra to define commands, flags, help, and version output. Keep the application responsible for output and exit behavior.
- Use Go's standard `flag` package and implement command dispatch, repeated flags, and command-specific help in the project.

## Decision

Use Cobra v1.10.2 on Go 1.26 or later. Keep command definitions, output and process exit handling in `main.go`. Keep opening a workspace, enumerating entries and inspecting files in `workspace.go`. Translate command and I/O errors to exit 2 at the application boundary.

## Trade-offs

Cobra provides a consistent command interface and removes custom parsing work. The project takes on dependency pinning, license notices, and updates. Process tests take longer than unit tests, and they cover what users and shell scripts observe. Revisit the dependency if a version change threatens the command contract or the interface shrinks enough for the standard library to cover it simply.

## Confirmation

Build the CLI and exercise the public commands with synthetic files. Confirm that matches return 0, empty searches return 1 and invalid commands or I/O errors return 2. Check help, repeatable suffix filters, and text and NDJSON outputs at the process boundary, including their stdout and stderr behavior.

## Evidence

- [CLI implementation and Windows process checks](../evidence/cli-command-framework.md)
