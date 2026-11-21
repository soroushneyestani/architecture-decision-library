# Stream search and stage matches through validation

Status: Accepted
Date: 2026-11-21

## Context

Developer CLI Toolkit searches regular files beneath an opened workspace root. Its file-level eligibility rule must discard every match in a file if any later byte is invalid UTF-8 or NUL. The earlier implementation satisfied that rule by reading the entire file into memory. Source files can be much larger than the matches a user needs.

## Options

- Keep whole-file allocation and validate the resulting slice before matching. This keeps the state machine simple and makes memory depend on the largest file.
- Validate the file in a first pass, then read it again to search. This reduces source buffering and adds another read of eligible input and a consistency check between passes.
- Stream through the open file, stage matches until validation finishes and spill large stages to disk.

## Decision

In the released streaming design, process source through a fixed-size buffer and validate as the search progresses. Stage matching records until the file passes validation. Replay eligible matches in line order, with temporary file storage for stages that exceed the memory budget. Long matching lines are reread through the same file handle and compared against their scanned digest. Retain rooted filesystem operations, sorted relative paths and the public output and exit behavior.

## Trade-offs

Most source data is read once and unmatched lines need no full-line memory buffer. Dense matches can require temporary storage, and a long matching line can still require memory proportional to its rendered text. The sorted path list also consumes memory, and concurrent changes in the live tree can affect reads. Spill I/O can fail even for an otherwise eligible file. Revisit staging when measured workloads show that dense output, very long matches or temporary storage constrain use.

## Confirmation

Exercise early matches followed by invalid bytes, long lines and matches spanning buffer fragments, a changed long line, and temporary spill cleanup. Confirm that eligible inputs retain ordering and exit behavior. Run native verification on the supported platforms before using a released source revision as evidence.

## Evidence

- [Released streaming implementation and regression tests](../evidence/stream-search.md)
