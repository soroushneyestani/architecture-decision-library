"""Build and verify the source ZIP from a reviewed Git commit."""

import argparse
from hashlib import sha256
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
VERSION = "v0.1.0"
PACKAGE = f"architecture-decision-library-{VERSION}"
PRIVATE_FILES = {"AGENTS.md", "PROJECT_STATE.json", "docs/EVIDENCE.md", "docs/TASKS.md"}
PUBLIC_FILES = {
    ".github/workflows/ci.yml", ".gitignore", "CHANGELOG.md", "CONTRIBUTING.md", "LICENSE",
    "README.md", "SECURITY.md", "THIRD_PARTY_NOTICES.md",
    "docs/COVER.md", "docs/INSTAGRAM_EN.md", "docs/INSTAGRAM_FA.md", "docs/LEARNING_FA.md",
    "docs/LINKEDIN_DE.md", "docs/README.md", "docs/RELEASE_EVIDENCE.md", "docs/SPEC.md",
    "docs/WEBSITE_EN.md", "scripts/check_adrs.py", "scripts/package_source.py",
    "scripts/verify.ps1", "tests/test_check_adrs.py",
}
PUBLIC_DIRECTORIES = ("docs/adr/", "docs/evidence/", "docs/releases/")


def git(*args: str) -> bytes:
    command = ["git", "-c", f"safe.directory={ROOT.as_posix()}", "-C", str(ROOT), *args]
    return subprocess.check_output(command, stderr=subprocess.PIPE, timeout=30)


def release_files(commit: str) -> dict[str, bytes]:
    if git("rev-parse", "--verify", f"{commit}^{{commit}}").strip().decode("ascii") != commit:
        raise ValueError("The reviewed SHA must identify a commit.")
    files = {}
    for row in git("ls-tree", "-rz", "--full-tree", commit).split(b"\0"):
        if not row:
            continue
        metadata, filename = row.split(b"\t", 1)
        mode, kind, object_id = metadata.decode("ascii").split()
        name = filename.decode("utf-8")
        if name in PRIVATE_FILES:
            continue
        if name not in PUBLIC_FILES and not name.startswith(PUBLIC_DIRECTORIES):
            raise ValueError(f"Classify the unreviewed path before packaging: {name}")
        if mode not in {"100644", "100755"} or kind != "blob":
            raise ValueError(f"Expected a regular tracked file: {name}")
        if not re.fullmatch(r"[A-Za-z0-9_./-]+", name) or any(
            segment in {"", ".", "..", ".git"} for segment in name.split("/")
        ):
            raise ValueError(f"Unsupported archive path: {name}")
        files[f"{PACKAGE}/{name}"] = git("cat-file", "blob", object_id)
    missing = {f"{PACKAGE}/{name}" for name in PUBLIC_FILES} - files.keys()
    if missing:
        raise ValueError(f"Missing release files: {', '.join(sorted(missing))}")
    return files


def package_source(commit: str) -> tuple[Path, str, int]:
    files = release_files(commit)
    destination = ROOT / "bin" / "release" / VERSION / commit
    destination.mkdir(parents=True, exist_ok=True)
    output = destination / f"{PACKAGE}-source.zip"
    with TemporaryDirectory(prefix=".package-", dir=destination) as scratch:
        staged = Path(scratch) / output.name
        with ZipFile(staged, "w") as archive:
            archive.comment = commit.encode("ascii")
            for name, data in sorted(files.items()):
                entry = ZipInfo(name)
                entry.create_system = 3
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, data)
        with ZipFile(staged) as archive:
            if (
                archive.comment != commit.encode("ascii")
                or archive.testzip() is not None
                or archive.namelist() != sorted(files)
                or any(archive.read(name) != data for name, data in files.items())
            ):
                raise ValueError("Source archive differs from the reviewed Git tree.")
        digest = sha256(staged.read_bytes()).hexdigest()
        manifest = Path(scratch) / "SHA256SUMS.txt"
        manifest.write_bytes(f"{digest}  {output.name}\n".encode("ascii"))
        staged.replace(output)
        manifest.replace(destination / manifest.name)
    return output, digest, len(files)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("commit", help="Full reviewed Git commit SHA")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.commit):
        parser.error("commit must be a full lowercase Git SHA")
    try:
        output, digest, file_count = package_source(args.commit)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"Source packaging failed: {error}", file=sys.stderr)
        return 1
    print(f"Verified {file_count} Git files in {output.relative_to(ROOT).as_posix()}")
    print(f"SHA-256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
