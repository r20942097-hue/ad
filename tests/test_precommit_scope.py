"""Regression checks for the public filter repository's local guard."""
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".github" / "hooks" / "pre-commit"


@unittest.skipUnless(HOOK.is_file(), "local hook is intentionally excluded from the downstream pinned source copy")
class PublicPreCommitScopeTests(unittest.TestCase):
    def run_staged(self, filename: str, payload: bytes) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(
                ["git", "-C", str(root), "remote", "add", "origin",
                 "https://github.com/r20942097-hue/s.git"], check=True
            )
            (root / filename).write_bytes(payload)
            subprocess.run(["git", "-C", str(root), "add", filename], check=True)
            return subprocess.run(
                ["bash", str(HOOK)], cwd=root, capture_output=True,
                text=True, check=False,
            )

    def test_typescript_is_source_not_mpeg_transport_stream(self) -> None:
        result = self.run_staged("module.ts", b"export const ready = true;\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("archive/binary file", result.stderr)

    def test_public_filter_repo_still_blocks_archive(self) -> None:
        result = self.run_staged("fixture.zip", b"fixture bytes")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("archive/binary file", result.stderr)

    def test_public_filter_repo_still_blocks_oversize_blob(self) -> None:
        result = self.run_staged("fixture.bin", b"x" * (1_048_576 + 1))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("file over 1MB", result.stderr)


if __name__ == "__main__":
    unittest.main()
