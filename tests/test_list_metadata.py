from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_lists import validate

TEMPLATE = """[Adblock Plus 2.0]
! Title: Test
! Version: 20261011.1
! Expires: 5 days
! Homepage: https://example.com/
! Description: Test list
! License: CC0-1.0
||example.com^$third-party
"""


class ListMetadataTests(unittest.TestCase):
    def test_repository_lists(self):
        self.assertEqual(validate(), [])

    def test_include_cycle_is_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text(TEMPLATE + "!#include b.txt\n", encoding="utf-8", newline="\n")
            (root / "b.txt").write_text(TEMPLATE + "!#include a.txt\n", encoding="utf-8", newline="\n")
            self.assertTrue(any("include cycle" in e for e in validate(root)))

    def test_parent_include_is_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text(TEMPLATE + "!#include ../outside.txt\n", encoding="utf-8", newline="\n")
            self.assertTrue(any("invalid or missing include" in e for e in validate(root)))

    def test_missing_include_is_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text(TEMPLATE + "!#include missing.txt\n", encoding="utf-8", newline="\n")
            self.assertTrue(any("invalid or missing include" in e for e in validate(root)))

    def test_duplicate_rule_and_invalid_date_are_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text(
                TEMPLATE.replace("20261011", "20261340") + "||example.com^$third-party\n",
                encoding="utf-8",
                newline="\n",
            )
            errors = validate(root)
            self.assertTrue(any("invalid version date" in e for e in errors))
            self.assertTrue(any("duplicate active rule" in e for e in errors))

    def test_symlinked_v2_directory_is_rejected(self):
        with TemporaryDirectory() as tmp, TemporaryDirectory() as outside_tmp:
            root = Path(tmp)
            outside = Path(outside_tmp)
            (outside / "ad.txt").write_text(TEMPLATE, encoding="utf-8", newline="\n")
            try:
                (root / "v2").symlink_to(outside, target_is_directory=True)
                errors = validate(root)
            except (OSError, NotImplementedError):
                (root / "v2").mkdir()
                (root / "v2" / "ad.txt").write_text(TEMPLATE, encoding="utf-8", newline="\n")
                orig_is_symlink = Path.is_symlink
                with patch.object(
                    Path, "is_symlink", lambda p: True if p == (root / "v2") else orig_is_symlink(p)
                ):
                    errors = validate(root)
            self.assertTrue(any("v2: directory must not be a symlink" in e for e in errors))

    def test_symlinked_root_directory_is_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text(TEMPLATE, encoding="utf-8", newline="\n")
            orig_is_symlink = Path.is_symlink
            with patch.object(
                Path, "is_symlink", lambda p: True if p == root else orig_is_symlink(p)
            ):
                errors = validate(root)
            self.assertEqual(errors, ["root directory must not be a symlink"])

    def test_invalid_utf8_list_reports_error(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "bad.txt").write_bytes(b"\xff\xfe[Adblock Plus 2.0]\n")
            errors = validate(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("bad.txt: unreadable UTF-8 text:", errors[0])

    def test_include_version_or_license_mismatch_and_subdir_include_are_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sub").mkdir()
            (root / "sub" / "child.txt").write_text(TEMPLATE, encoding="utf-8", newline="\n")
            (root / "child_ver.txt").write_text(
                TEMPLATE.replace("20261011.1", "20261012.1"), encoding="utf-8", newline="\n"
            )
            (root / "child_lic.txt").write_text(
                TEMPLATE.replace("CC0-1.0", "MIT"), encoding="utf-8", newline="\n"
            )
            (root / "parent.txt").write_text(
                TEMPLATE + "!#include sub/child.txt\n!#include child_ver.txt\n!#include child_lic.txt\n",
                encoding="utf-8",
                newline="\n",
            )
            errors = validate(root)
            self.assertTrue(any("invalid or missing include" in e for e in errors))
            self.assertTrue(any("parent.txt: included list child_ver.txt version mismatch" == e for e in errors))
            self.assertTrue(any("parent.txt: included list child_lic.txt license mismatch" == e for e in errors))

    def test_cli_main_supports_root_and_help(self):
        import contextlib
        import io
        import validate_lists

        help_out = io.StringIO()
        with contextlib.redirect_stdout(help_out), self.assertRaises(SystemExit) as raised:
            validate_lists.main(["--help"])
        self.assertEqual(raised.exception.code, 0)
        self.assertIn("--root", help_out.getvalue())

        ok_out = io.StringIO()
        with contextlib.redirect_stdout(ok_out):
            rc_ok = validate_lists.main(["--root", str(validate_lists.ROOT)])
        self.assertEqual(rc_ok, 0)
        self.assertIn("LIST CHECK PASSED", ok_out.getvalue())

        with TemporaryDirectory() as tmp:
            bad_out = io.StringIO()
            with contextlib.redirect_stdout(bad_out):
                rc_bad = validate_lists.main(["--root", tmp])
            self.assertEqual(rc_bad, 1)
            self.assertIn("LIST CHECK FAILED", bad_out.getvalue())


if __name__ == "__main__":
    unittest.main()
