# Pin toolchains and build one artifact in reusable Go CI

Status: Accepted
Date: 2026-11-18

## Context

Go applications can share their module, vet, test, scan, and build checks. Consumers need a predictable toolchain and one downloadable artifact from successful runs.

## Options

- Use an exact Go release and a root executable contract with one supported target per caller job. Start with Linux and add named targets only when they have hosted evidence.
- Accept arbitrary runner labels, toolchain selectors and package directories, with separate validation and ownership of each supported combination.

## Decision

Require an exact Go release at or above 1.26.0 and a root `main` package. Disable automatic toolchain switching and workspace mode. The released runner choices are `ubuntu-24.04` and `windows-2025`. Cache Go dependencies and build outputs on a push to the caller's default branch when `go.sum` exists. Pin actions and audit tools. Run vet, tests, a build, a dependency check and a redacted Git history scan. Upload one executable from a successful job and expose its artifact metadata to the caller.

## Trade-offs

The constrained platforms and package layout give callers predictable artifact names and testable failures. Library-only modules, nested executable packages and other architectures remain outside the contract. Dependency checks and an uncached build can require network access. Each additional runner would need a corresponding build, download and execution fixture.

## Confirmation

Verify hosted builds for both supported runners, then download and execute each artifact from the same caller run. Check cache miss, save and hit on both platforms. Confirm that deliberately failed tests and missing project configuration stop the build lanes and leave zero artifacts.

## Evidence

- [Go workflow, synthetic module checks, and hosted proof](../evidence/pinned-go-ci.md)
