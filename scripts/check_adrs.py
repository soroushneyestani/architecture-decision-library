"""Validate the ADR library or print its canonical Markdown index."""

import argparse
from dataclasses import dataclass
from datetime import date
import os
from pathlib import Path
import re
import sys


SECTIONS = ("Context", "Options", "Decision", "Trade-offs", "Confirmation", "Evidence")
STATUSES = ("Proposed", "Accepted", "Superseded")
FILENAME = re.compile(r"([0-9]{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md")
SUPERSEDED_BY = re.compile(r"Superseded by: \[([^\[\]]+)\]\(([^()]+)\)")
EVIDENCE_LINK = re.compile(r"- \[([^\[\]]+)\]\(([a-zA-Z0-9_./-]+)\)")
INLINE_TOKENS = re.compile(
    r"(?<![\\`])(?P<ticks>`+)(?!`).*?(?<!`)(?P=ticks)(?!`)"
    r"|(?<![!\\])\[[^\[\]]*\]\((?P<target>[^()]*)\)"
)
INLINE_PATH = re.compile(r"[a-zA-Z0-9_./-]+")
FENCE = re.compile(r" {0,3}(`{3,}|~{3,})(.*)")


@dataclass(frozen=True)
class Record:
    identifier: str
    filename: str
    title: str
    status: str
    decided_on: date
    successor: str | None = None


def local_path(path: Path, root: Path) -> Path:
    if not Path(os.path.abspath(path)).is_relative_to(root):
        raise ValueError(f"{path.relative_to(root)}: path escapes the repository")
    try:
        resolved = path.resolve()
    except RuntimeError as error:
        raise ValueError(f"{path.relative_to(root)}: cannot resolve path") from error
    if not resolved.is_relative_to(root):
        raise ValueError(f"{path.relative_to(root)}: path escapes the repository")
    return resolved


def read_utf8(path: Path, root: Path) -> str:
    try:
        return local_path(path, root).read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError(f"{path.relative_to(root)}: invalid UTF-8 ({error.reason})") from error


def outside_fences(lines: list[str], name: Path) -> list[str]:
    """Blank fenced lines while preserving section offsets in the source."""
    visible = []
    fence = ""
    for line in lines:
        marker = FENCE.fullmatch(line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = ""
            visible.append("")
        elif marker and (marker[1][0] == "~" or "`" not in marker[2]):
            fence = marker[1]
            visible.append("")
        else:
            visible.append(line)
    if fence:
        raise ValueError(f"{name}: unclosed Markdown code fence")
    return visible


def check_file_reference(path: Path, root: Path, target: str, label: str) -> None:
    name = path.relative_to(root)
    if target.rpartition("/")[2] in {"", ".", ".."}:
        raise ValueError(f"{name}: invalid {label} file target {target}")
    try:
        referenced = local_path(path.parent / target, root)
    except ValueError as error:
        raise ValueError(f"{name}: invalid {label} target {target} ({error})") from error
    if not referenced.is_file():
        raise ValueError(f"{name}: missing {label} file {target}")


def check_body_references(path: Path, root: Path, lines: list[str]) -> None:
    for line in lines:
        for token in INLINE_TOKENS.finditer(line):
            target = token["target"]
            if target is None or target.startswith(("https://", "http://", "#")):
                continue
            filename = target.partition("#")[0]
            if not INLINE_PATH.fullmatch(filename) or filename.startswith("/"):
                raise ValueError(f"{path.relative_to(root)}: invalid local reference {target!r}")
            check_file_reference(path, root, filename, "reference")


def read_record(path: Path, root: Path, identifier: str) -> Record:
    name = path.relative_to(root)
    lines = read_utf8(path, root).splitlines()
    if not lines or not lines[0].startswith("# ") or not lines[0][2:].strip():
        raise ValueError(f"{name}: expected a nonempty title on the first line")
    title = lines[0][2:].strip()
    visible = outside_fences(lines, name)
    headings = [(index, line[3:].strip()) for index, line in enumerate(visible) if line.startswith("## ")]
    if tuple(heading for _, heading in headings) != SECTIONS:
        raise ValueError(f"{name}: expected these sections in order: {', '.join(SECTIONS)}")

    metadata = [line for line in lines[1:headings[0][0]] if line.strip()]
    if not 2 <= len(metadata) <= 3:
        raise ValueError(f"{name}: expected Status and Date after the title")
    status = metadata[0].removeprefix("Status: ")
    if not metadata[0].startswith("Status: ") or status not in STATUSES:
        raise ValueError(f"{name}: invalid Status; expected {', '.join(STATUSES)}")
    if not re.fullmatch(r"Date: [0-9]{4}-[0-9]{2}-[0-9]{2}", metadata[1]):
        raise ValueError(f"{name}: expected Date in YYYY-MM-DD format")
    try:
        decided_on = date.fromisoformat(metadata[1][6:])
    except ValueError as error:
        raise ValueError(f"{name}: invalid calendar date {metadata[1][6:]}") from error

    successor = None
    if status == "Superseded":
        replacement = SUPERSEDED_BY.fullmatch(metadata[2]) if len(metadata) == 3 else None
        if replacement is None or not replacement[1].strip() or not FILENAME.fullmatch(replacement[2]):
            raise ValueError(f"{name}: Superseded requires a Superseded by link to an ADR filename")
        successor = replacement[2]
    elif len(metadata) != 2:
        raise ValueError(f"{name}: unexpected metadata after Date; Superseded by is only for Superseded records")

    section_ends = [index for index, _ in headings[1:]] + [len(lines)]
    contents = {}
    for (start, heading), end in zip(headings, section_ends):
        section = lines if heading == "Evidence" else visible
        contents[heading] = [line for line in section[start + 1:end] if line.strip()]
        if not contents[heading]:
            raise ValueError(f"{name}: empty {heading} section")

    options = {line[2:].strip() for line in contents["Options"] if line.startswith("- ") and line[2:].strip()}
    if len(options) < 2:
        raise ValueError(f"{name}: Options must name at least two distinct choices in a bulleted list")
    for heading in SECTIONS[:-1]:
        check_body_references(path, root, contents[heading])
    for line in contents["Evidence"]:
        link = EVIDENCE_LINK.fullmatch(line)
        if link is None or not link[1].strip() or link[2].startswith("/"):
            raise ValueError(f"{name}: Evidence must use file links relative to the record")
        check_file_reference(path, root, link[2], "evidence")

    return Record(identifier, path.name, title, status, decided_on, successor)


def check_successors(records: list[Record]) -> None:
    indexed = {record.filename: record for record in records}
    successors = {record.filename: record.successor for record in records if record.successor is not None}
    for filename, successor in successors.items():
        if successor == filename:
            raise ValueError(f"docs/adr/{filename}: a record cannot supersede itself")
        if successor not in indexed:
            raise ValueError(f"docs/adr/{filename}: missing successor ADR {successor}")
        if indexed[successor].status == "Proposed":
            raise ValueError(f"docs/adr/{filename}: successor ADR {successor} is Proposed")

    checked = set()
    for filename in successors:
        chain = set()
        while filename in successors and filename not in checked:
            if filename in chain:
                raise ValueError(f"docs/adr/{filename}: successor chain contains a cycle")
            chain.add(filename)
            filename = successors[filename]
        checked.update(chain)


def collect_records(directory: Path, root: Path) -> list[Record]:
    local_path(directory, root)
    records = []
    seen = set()
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() != ".md" or path.name in {"README.md", "TEMPLATE.md"}:
            continue
        match = FILENAME.fullmatch(path.name)
        if match is None or match[1] == "0000":
            raise ValueError(f"{path.relative_to(root)}: expected a positive ID and kebab-case filename")
        identifier = match[1]
        if identifier in seen:
            raise ValueError(f"{path.relative_to(root)}: duplicate ID {identifier}")
        seen.add(identifier)
        records.append(read_record(path, root, identifier))
    if not records:
        raise ValueError(f"{directory.relative_to(root)}: no architecture decisions found")
    check_successors(records)
    return records


def render_index(records: list[Record]) -> str:
    lines = [
        "# Architecture decisions",
        "",
        "| ID | Decision | Status | Date |",
        "| --- | --- | --- | --- |",
    ]
    for record in records:
        title = re.sub(r"([\\|\[\]])", r"\\\1", record.title)
        lines.append(f"| {record.identifier} | [{title}]({record.filename}) | {record.status} | {record.decided_on} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="project directory")
    parser.add_argument("--print-index", action="store_true", help="print the canonical index instead of comparing it")
    args = parser.parse_args()
    try:
        root = args.root.resolve()
        directory = root / "docs" / "adr"
        records = collect_records(directory, root)
        index = render_index(records)
        if args.print_index:
            sys.stdout.write(index)
            return 0
        try:
            committed_index = read_utf8(directory / "README.md", root)
        except FileNotFoundError as error:
            raise ValueError("docs/adr/README.md: missing index; create it with --print-index") from error
        if committed_index != index:
            raise ValueError("docs/adr/README.md: stale index; regenerate it with --print-index")
        print(f"Verified {len(records)} architecture decisions.")
    except (OSError, ValueError) as error:
        print(f"ADR check failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
