"""Regression checks for the public filter repository's local guard."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".github" / "hooks" / "pre-commit"


def _find_posix_bash() -> str | None:
    """Locate a working non-WSL POSIX bash executable, if available."""
    candidates: list[str] = []
    if git_bin := shutil.which("git"):
        git_path = Path(git_bin).resolve()
        for base in git_path.parents[:3]:
            for rel in ("bin/bash.exe", "usr/bin/bash.exe"):
                candidate = base / rel
                if candidate.is_file():
                    candidates.append(str(candidate))
    if path_bash := shutil.which("bash"):
        resolved = Path(path_bash).resolve().as_posix().casefold()
        if not resolved.endswith("/windows/system32/bash.exe"):
            candidates.append(path_bash)
    for candidate in dict.fromkeys(candidates):
        try:
            probe = subprocess.run([candidate, "-c", "exit 0"], capture_output=True, check=False)
        except OSError:
            continue
        if probe.returncode == 0:
            return candidate
    return None


@unittest.skipUnless(HOOK.is_file(), "local hook is intentionally excluded from the downstream pinned source copy")
class PublicPreCommitScopeTests(unittest.TestCase):
    def run_staged(
        self,
        filename: str,
        payload: bytes,
        origin: str = "https://github.com/r20942097-hue/ad.git",
    ) -> subprocess.CompletedProcess[str]:
        bash_bin = _find_posix_bash()
        if bash_bin is None:
            self.skipTest("working POSIX bash executable is unavailable in this environment")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "core.autocrlf", "false"], check=True)
            subprocess.run(
                ["git", "-C", str(root), "remote", "add", "origin", origin],
                check=True,
            )
            (root / filename).write_bytes(payload)
            subprocess.run(["git", "-C", str(root), "add", filename], check=True)
            return subprocess.run(
                [bash_bin, str(HOOK)], cwd=root, capture_output=True,
                text=True, encoding="utf-8", errors="replace", check=False,
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

    def test_hook_supports_renamed_repos_and_portable_python(self) -> None:
        hook = HOOK.read_text(encoding="utf-8")
        self.assertIn("py=$(command -v python3 || command -v python || py -3 -c", hook)
        self.assertNotIn("/workspace/tools/bin", hook)
        self.assertIn('[ "$repo" = s ] || [ "$repo" = ad ]', hook)
        self.assertIn('[ "$repo" = faaff ] || [ "$repo" = 01 ]', hook)
        self.assertNotIn("*.ts|", hook)

    def test_personal_paths_blocked_for_both_s_and_ad(self) -> None:
        for origin in (
            "https://github.com/r20942097-hue/s.git",
            "https://github.com/r20942097-hue/ad.git",
        ):
            with self.subTest(origin=origin):
                result = self.run_staged("rplay_helper.user.js", b"// user script\n", origin=origin)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("personal-only path", result.stderr)

    def test_gitattributes_enforces_lf_for_hooks_and_filter_lists(self) -> None:
        attrs_path = ROOT / ".gitattributes"
        self.assertTrue(attrs_path.is_file(), ".gitattributes missing")
        attrs = attrs_path.read_text(encoding="utf-8")
        self.assertIn("* text=auto eol=lf", attrs)
        self.assertIn(".github/hooks/* text eol=lf", attrs)
        self.assertIn("*.txt text eol=lf", attrs)

    def test_instruction_entrypoints_and_templates_are_consistent(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for ref in ("[CLAUDE.md](CLAUDE.md)", "[.cursor/rules/agents.mdc](.cursor/rules/agents.mdc)", "[.github/copilot-instructions.md](.github/copilot-instructions.md)"):
            self.assertIn(ref, agents)

        self.assertLessEqual(len(agents.splitlines()), 100)
        self.assertLessEqual(len(agents.encode("utf-8")), 24576)
        self.assertFalse((ROOT / "CLAUDE.local.md").exists())
        self.assertFalse((ROOT / "AGENTS.override.md").exists())

        claude_lines = [ln.strip() for ln in (ROOT / "CLAUDE.md").read_text(encoding="utf-8").splitlines()]
        self.assertIn("@AGENTS.md", claude_lines)
        self.assertLessEqual(len(claude_lines), 6)

        for rel in ("CLAUDE.md", ".cursor/rules/agents.mdc", ".github/copilot-instructions.md"):
            content = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("AGENTS.md", content)
            self.assertIn("No separate rules here.", content)

        pr_tpl = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
        self.assertIn("python scripts/check_subscription_contract.py --json", pr_tpl)
        self.assertIn("01（旧 faaff）", pr_tpl)

        issue_tpl = (ROOT / ".github" / "ISSUE_TEMPLATE" / "ai-task.yml").read_text(encoding="utf-8")
        self.assertIn("id: high_impact", issue_tpl)
        self.assertNotIn("id: approval", issue_tpl)

    def test_markdown_relative_links_and_dependabot_codeql_group(self) -> None:
        import re
        from urllib.parse import unquote
        link_re = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
        fence_re = re.compile(r"^\s*(```|~~~)")
        inline_code_re = re.compile(r"(`+).*?\1")
        tracked = subprocess.run(
            ["git", "-c", "core.quotePath=false", "-C", str(ROOT), "ls-files", "*.md", "*.mdc"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout.splitlines()
        self.assertIn(".cursor/rules/agents.mdc", tracked)
        root_resolved = ROOT.resolve()
        for rel_doc in tracked:
            doc = ROOT / rel_doc
            in_fence = False
            for no, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), 1):
                if fence_re.match(line):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                for target in link_re.findall(inline_code_re.sub("", line)):
                    if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("#"):
                        continue
                    rel = unquote(target.split("#", 1)[0])
                    if not rel:
                        continue
                    self.assertNotIn("\\", target, f"{rel_doc}:{no}: backslash in link {target}")
                    resolved = (ROOT / rel.lstrip("/")) if rel.startswith("/") else (doc.parent / rel)
                    self.assertTrue(
                        resolved.resolve().is_relative_to(root_resolved) and resolved.exists(),
                        f"{rel_doc}:{no}: broken link -> {target}",
                    )

        dependabot = (ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")
        self.assertIn("codeql-action:", dependabot)
        self.assertIn('"github/codeql-action*"', dependabot)


if __name__ == "__main__":
    unittest.main()
