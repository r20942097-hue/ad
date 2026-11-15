from __future__ import annotations

import contextlib
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify  # noqa: E402


class VerifyRunnerTest(unittest.TestCase):
    def test_registered_script_paths_exist(self) -> None:
        self.assertGreaterEqual(len(verify.CHECKS), 4)
        root_resolved = ROOT.resolve()
        for name, command in verify.CHECKS:
            if command[0].startswith("scripts/"):
                target = ROOT / command[0]
                self.assertTrue(target.is_file(), f"Missing target for {name}: {command[0]}")
                self.assertTrue(target.resolve().is_relative_to(root_resolved))

    def test_list_and_unknown_check_pattern(self) -> None:
        list_out = io.StringIO()
        with contextlib.redirect_stdout(list_out):
            rc = verify.main(["--list"])
        self.assertEqual(rc, 0)
        for name, _ in verify.CHECKS:
            self.assertIn(name, list_out.getvalue())

        err_out = io.StringIO()
        with contextlib.redirect_stderr(err_out):
            bad_rc = verify.main(["--check", "nonexistent-check-pattern"])
        self.assertEqual(bad_rc, 2)
        self.assertIn("No offline checks matched --check", err_out.getvalue())

    def test_check_subset_runs_subscription_contract(self) -> None:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = verify.main(["--check", "Subscription contract"])
        self.assertEqual(rc, 0)
        self.assertIn("PASS  Subscription contract", out.getvalue())
        self.assertIn("1/1 checks passed", out.getvalue())

    def test_main_aggregates_results_and_rejects_symlink_root(self) -> None:
        out = io.StringIO()
        with patch.object(verify, "run_check", return_value=True) as mock_run, contextlib.redirect_stdout(out):
            rc = verify.main([])
        self.assertEqual(rc, 0)
        self.assertEqual(mock_run.call_count, len(verify.CHECKS))
        self.assertIn(f"{len(verify.CHECKS)}/{len(verify.CHECKS)} checks passed", out.getvalue())

        fail_out = io.StringIO()
        side_effects = [i != 1 for i in range(len(verify.CHECKS))]
        with patch.object(verify, "run_check", side_effect=side_effects), contextlib.redirect_stdout(fail_out):
            fail_rc = verify.main([])
        self.assertEqual(fail_rc, 1)
        self.assertIn("FAIL  Filter list validation", fail_out.getvalue())

        orig_is_symlink = Path.is_symlink
        err_out = io.StringIO()
        with (
            patch.object(Path, "is_symlink", autospec=True, side_effect=lambda p: p == verify.ROOT or orig_is_symlink(p)),
            contextlib.redirect_stderr(err_out),
        ):
            sym_rc = verify.main([])
        self.assertEqual(sym_rc, 1)
        self.assertIn("repository root must not be a symlink", err_out.getvalue())


    def test_generate_lists_accepts_write_flag(self) -> None:
        completed = verify.subprocess.run(
            [sys.executable, "scripts/generate_lists.py", "--write", "--dry-run"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False,
        )
        self.assertEqual(completed.returncode, 2)
        completed_ok = verify.subprocess.run(
            [sys.executable, "scripts/generate_lists.py", "--write"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False,
        )
        self.assertEqual(completed_ok.returncode, 0)
        self.assertIn("GENERATION PASSED", completed_ok.stdout)

    def test_workflows_pin_actions_and_restrict_tokens(self) -> None:
        import re
        workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
        expected_min = 3 if (ROOT / ".github" / "hooks" / "pre-commit").is_file() else 2
        self.assertGreaterEqual(len(workflows), expected_min)
        for wf in workflows:
            text = wf.read_text(encoding="utf-8")
            self.assertIn("permissions:\n  contents: read", text, wf.name)
            self.assertIn("persist-credentials: false", text, wf.name)
            uses_refs = re.findall(r"uses:\s*([^\s#]+)", text)
            self.assertTrue(uses_refs, wf.name)
            for ref in uses_refs:
                self.assertRegex(ref, r"^[^@]+@[0-9a-f]{40}$", f"{wf.name}: {ref}")
            self.assertNotIn("3780f8a00b6c718f3811fb4c75c5fa5b22a8ef75", text, f"{wf.name}: invalid setup-uv SHA")

    @unittest.skipUnless(
        (ROOT / "AGENTS.md").is_file(),
        "instruction files are intentionally excluded from the downstream pinned source copy",
    )
    def test_instruction_hygiene_and_strict_claude_pointer(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(agents.splitlines()), 100)
        self.assertLessEqual(len(agents.encode("utf-8")), 24576)
        claude = ROOT / "CLAUDE.md"
        if claude.exists():
            raw = claude.read_bytes()
            self.assertNotIn(b"\r", raw, "CLAUDE.md must use LF")
            self.assertEqual(raw.decode("utf-8").splitlines(), ["@AGENTS.md"])
        for forbidden in ("CLAUDE.local.md", "AGENTS.override.md"):
            self.assertFalse((ROOT / forbidden).exists(), forbidden)


    def test_scripts_and_tests_specify_utf8_encoding_explicitly(self) -> None:
        import ast

        missing: list[str] = []
        for directory in ("scripts", "tests"):
            for path in sorted((ROOT / directory).rglob("*.py")):
                tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                        continue
                    kws = {k.arg: k.value for k in node.keywords}
                    if node.func.attr in ("read_text", "write_text") and "encoding" not in kws:
                        missing.append(f"{path.relative_to(ROOT)}:{node.lineno} {node.func.attr}()")
                    if (
                        isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "subprocess"
                        and node.func.attr == "run"
                        and ("text" in kws or "universal_newlines" in kws)
                        and "encoding" not in kws
                    ):
                        missing.append(f"{path.relative_to(ROOT)}:{node.lineno} subprocess.run(text=True)")
        self.assertEqual(missing, [], f"Missing explicit encoding=: {missing}")


if __name__ == "__main__":
    unittest.main()
