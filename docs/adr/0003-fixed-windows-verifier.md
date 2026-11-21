# Use a fixed caller entry point for Windows CI

Status: Accepted
Date: 2026-11-18

## Context

Repositories need a shared Windows CI job while retaining their own lint, test, and build checks. Keeping checkout and permissions in the reusable workflow gives each caller the same execution contract.

## Options

- Execute a fixed `scripts/verify.ps1` from the caller checkout with a dedicated PowerShell process.
- Accept a command string or script path from each caller, with additional validation for command and path handling.

## Decision

Use `workflow_call` on `windows-2025`. Check out the caller with a read-only contents token and disable persisted credentials. Execute the fixed `scripts/verify.ps1` entry point from the checkout root in a noninteractive child PowerShell process with profiles disabled. Return its exit status to the job. The released interface supports an optional Go setup version for callers that need Go. It accepts no caller-selected shell command, script path, or secrets.

## Trade-offs

The fixed path reduces configuration and makes success and failure repeatable in local fixtures. Each caller supplies its verifier and manages its build requirements. The job executes code from the caller revision, so token permissions and checkout settings matter in pull request workflows. Revisit the fixed Windows contract if callers need independently verified execution on another platform or a different entry point.

## Confirmation

Verify child-process execution from the checkout root, propagation of a nonzero status, and rejection of a missing script or a directory at the entry point. Confirm the hosted workflow runs the caller verifier on Windows and grants read-only contents access.

## Evidence

- [Windows workflow and exit-contract fixtures](../evidence/fixed-windows-verifier.md)
