"""Report common privacy risks in the working tree and reachable Git history.

Only categories and file paths are printed; matched content is never printed.
This is a screening aid and cannot replace a human review.
"""

from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE" + r" KEY-----"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{25,}\b"),
    "api_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "url_credentials": re.compile(r"https?://[^/\s:@]+:[^/\s@]+@", re.IGNORECASE),
    "windows_profile_path": re.compile(r"\b[A-Za-z]:[\\/](?:Users|Documents and Settings)[\\/][^\\/\s]+", re.IGNORECASE),
    "unix_profile_path": re.compile(r"/(?:home|Users)/[^/\s]+"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
}
WINDOWS_PATH = re.compile(r"\b[A-Za-z]:[\\/][^\s\"'<>`]+")
MAX_FILE_BYTES = 5 * 1024 * 1024


def scan_content(content: bytes) -> set[str]:
    if len(content) > MAX_FILE_BYTES:
        return {"file_too_large_to_scan"}
    if b"\0" in content:
        return {"binary_file_requires_review"}
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return {"non_utf8_file_requires_review"}
    findings = {name for name, pattern in PATTERNS.items() if pattern.search(text)}
    paths = [m.group().replace("/", "\\").lower().rstrip(".,;)") for m in WINDOWS_PATH.finditer(text)]
    placeholder = "c:" + "\\" + "\\".join(("path", "to", "your", "skills"))
    if any(path != placeholder for path in paths):
        findings.add("absolute_windows_path_requires_review")
    return findings


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)


def audit(root: Path) -> list[tuple[str, str, str]]:
    findings: set[tuple[str, str, str]] = set()
    paths = git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    for raw in filter(None, paths.split(b"\0")):
        relative = raw.decode("utf-8", errors="replace")
        path = root / relative
        if path.is_symlink():
            findings.add(("working-tree", relative, "symlink_requires_review"))
        elif path.is_file():
            if path.stat().st_size > MAX_FILE_BYTES:
                findings.add(("working-tree", relative, "file_too_large_to_scan"))
                continue
            for category in scan_content(path.read_bytes()):
                findings.add(("working-tree", relative, category))

    commits = git(root, "rev-list", "--all").decode("ascii").splitlines()
    seen: set[tuple[str, str]] = set()
    for commit in commits:
        tree = git(root, "ls-tree", "-r", "-z", "--full-tree", commit)
        for entry in filter(None, tree.split(b"\0")):
            metadata, raw_path = entry.split(b"\t", 1)
            mode, kind, object_id = metadata.decode("ascii").split(" ")
            if kind != "blob":
                continue
            relative = raw_path.decode("utf-8", errors="replace")
            key = (object_id, relative)
            if key in seen:
                continue
            seen.add(key)
            if mode == "120000":
                findings.add(("history", relative, "symlink_requires_review"))
            if int(git(root, "cat-file", "-s", object_id)) > MAX_FILE_BYTES:
                findings.add(("history", relative, "file_too_large_to_scan"))
                continue
            for category in scan_content(git(root, "cat-file", "blob", object_id)):
                findings.add(("history", relative, category))

    identities = git(root, "log", "--all", "--format=%ae%x00%ce%x00").decode("utf-8", errors="replace")
    for identity in identities.replace("\n", "").split("\0"):
        if identity and not identity.lower().endswith("@users.noreply.github.com"):
            findings.add(("history", "commit metadata", "non_noreply_email_requires_review"))
    return sorted(findings)


def main() -> int:
    try:
        findings = audit(ROOT)
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        print(f"Privacy scan could not complete: {type(error).__name__}", file=sys.stderr)
        return 2
    for source, path, category in findings:
        safe_path = "[redacted path]" if scan_content(path.encode("utf-8")) else path
        print(f"{source}: {safe_path}: {category}")
    print(f"Privacy scan: {len(findings)} item(s) require review; manual review is still required.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
