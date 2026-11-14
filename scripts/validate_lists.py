"""Check metadata, duplicate rules and local include graphs; not a uBO parser."""
import argparse
from datetime import datetime
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("Title", "Version", "Expires", "Homepage", "Description", "License")


def validate(root=ROOT):
    errors = []
    if root.is_symlink():
        return ["root directory must not be a symlink"]
    v2_dir = root / "v2"
    v2_symlink = v2_dir.is_symlink()
    if v2_symlink:
        errors.append("v2: directory must not be a symlink")
    paths = sorted(list(root.glob("*.txt")) + ([] if v2_symlink else list(v2_dir.glob("*.txt"))))
    graph = {}
    metadata_by_path = {}
    for path in paths:
        name = path.relative_to(root).as_posix()
        if path.is_symlink():
            errors.append(f"{name}: source list must not be a symlink")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{name}: unreadable UTF-8 text: {exc}")
            continue
        lines = text.splitlines()
        if not lines or lines[0] != "[Adblock Plus 2.0]":
            errors.append(f"{name}: missing format header")
        if not text.endswith("\n"):
            errors.append(f"{name}: missing final newline")
        metadata = {}
        for key in REQUIRED:
            values = [line[len(key) + 3:].strip() for line in lines[:30] if line.startswith(f"! {key}:")]
            if len(values) != 1 or not values[0]:
                errors.append(f"{name}: expected exactly one nonempty {key}")
            else:
                metadata[key] = values[0]
        version = metadata.get("Version", "")
        if not re.fullmatch(r"\d{8}\.\d+", version):
            errors.append(f"{name}: invalid version")
        else:
            try:
                datetime.strptime(version[:8], "%Y%m%d")
            except ValueError:
                errors.append(f"{name}: invalid version date")
        if not re.fullmatch(r"[1-9]\d* days?", metadata.get("Expires", "")):
            errors.append(f"{name}: invalid expiry")
        homepage = metadata.get("Homepage", "")
        if (not homepage.startswith("https://") or len(homepage) <= len("https://")
                or any(ch.isspace() or ord(ch) < 32 for ch in homepage)):
            errors.append(f"{name}: homepage must use HTTPS")
        metadata_by_path[path] = metadata
        seen = set()
        graph[path] = []
        for number, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith("!#include"):
                target_name = line[len("!#include"):].strip()
                target = path.parent / target_name
                if (not target_name or "/" in target_name or "\\" in target_name
                        or Path(target_name).is_absolute()
                        or ".." in Path(target_name).parts
                        or target.is_symlink() or not target.is_file()
                        or not target.resolve().is_relative_to(path.parent.resolve())):
                    errors.append(f"{name}:{number}: invalid or missing include")
                else:
                    graph[path].append(target)
            if not line or line.startswith(("!", "[")):
                continue
            if line in seen:
                errors.append(f"{name}:{number}: duplicate active rule")
            seen.add(line)
        if not seen:
            errors.append(f"{name}: no active rules")
    visiting, visited = set(), set()

    def visit(path):
        if path in visiting:
            errors.append(f"{path.relative_to(root).as_posix()}: include cycle")
            return
        if path in visited:
            return
        if path not in graph:
            errors.append(f"{path.relative_to(root).as_posix()}: include target outside validated lists")
            return
        visiting.add(path)
        for target in graph[path]:
            visit(target)
        visiting.remove(path)
        visited.add(path)

    for path in graph:
        visit(path)
    for path, targets in graph.items():
        name = path.relative_to(root).as_posix()
        parent_meta = metadata_by_path.get(path, {})
        for target in targets:
            target_meta = metadata_by_path.get(target)
            if target_meta is None:
                continue
            target_rel = target.relative_to(root).as_posix()
            if (parent_meta.get("Version") and target_meta.get("Version")
                    and parent_meta["Version"] != target_meta["Version"]):
                errors.append(f"{name}: included list {target_rel} version mismatch")
            if (parent_meta.get("License") and target_meta.get("License")
                    and parent_meta["License"] != target_meta["License"]):
                errors.append(f"{name}: included list {target_rel} license mismatch")
    if not paths and not v2_symlink:
        errors.append("no filter lists found")
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root directory")
    args = parser.parse_args(argv)
    errors = validate(args.root)
    for error in errors:
        print("ERROR:", error)
    print("LIST CHECK FAILED" if errors else "LIST CHECK PASSED: metadata, duplicate rules, include graph")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
