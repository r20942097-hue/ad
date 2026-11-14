import hashlib
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import audit_upstream


class UpstreamAuditTests(unittest.TestCase):
    def test_domain_boundaries_and_exception_roles(self):
        profiles = {'rule_sets': {'ads': {'rules': ['||ads.example^$third-party']}}}
        record = {'repository': 'owner/repo', 'path': 'ads.txt', 'url': 'https://github.com/owner/repo/blob/pin/ads.txt'}
        lines = ['! ads.example is a comment', '||ads.example^', '@@||cdn.ads.example^$domain=site.example', '||notads.example^', '||ads.example.evil^']
        rows = audit_upstream.audit(profiles, [(record, lines)])
        self.assertEqual([r['role'] for r in rows[0]['references']], ['classification', 'exception'])
        self.assertEqual(rows[0]['review'], '例外参照あり・個別確認')
        self.assertEqual(profiles['rule_sets']['ads']['rules'], ['||ads.example^$third-party'])

    def test_absence_is_reported_as_unknown(self):
        profiles = {'rule_sets': {'ads': {'rules': ['||ads.example^$third-party']}}}
        self.assertIn('未判定', audit_upstream.audit(profiles, [])[0]['review'])

    def test_changed_snapshot_is_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            record = {'repository': 'owner/repo', 'commit': 'a' * 40, 'path': 'ads.txt', 'sha256': hashlib.sha256(b'original').hexdigest()}
            target = root / 'owner__repo' / record['commit'] / 'ads.txt'
            target.parent.mkdir(parents=True)
            target.write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError, 'changed pinned snapshot'):
                audit_upstream.verified_sources(root, {'files': [record]})

    def test_unsafe_snapshot_path_is_rejected(self):
        with TemporaryDirectory() as tmp:
            for bad_path in ('../escape', '/outside.txt', 'dir//file.txt'):
                with self.subTest(bad_path=bad_path):
                    record = {'repository': 'owner/repo', 'commit': 'a' * 40, 'path': bad_path, 'sha256': '0' * 64}
                    with self.assertRaisesRegex(ValueError, 'unsafe snapshot path'):
                        audit_upstream.verified_sources(Path(tmp), {'files': [record]})
            for bad_rec in (
                {'repository': 'owner/..', 'commit': 'a' * 40, 'path': 'ads.txt', 'sha256': '0' * 64},
                {'repository': 'owner/repo', 'commit': 'a' * 40, 'path': 'ads.txt', 'sha256': 'not-sha256'},
            ):
                with self.subTest(bad_rec=bad_rec):
                    with self.assertRaisesRegex(ValueError, 'invalid snapshot identity'):
                        audit_upstream.verified_sources(Path(tmp), {'files': [bad_rec]})

    def test_symlinked_cache_and_report_paths_are_rejected(self):
        import contextlib
        import io
        from unittest.mock import patch
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache = root / 'cache'
            report = root / 'report.json'
            cache.mkdir()
            orig_is_symlink = Path.is_symlink

            with patch.object(Path, 'is_symlink', autospec=True, side_effect=lambda p: p == cache or orig_is_symlink(p)):
                with self.assertRaisesRegex(ValueError, 'symlink in snapshot cache'):
                    audit_upstream.verified_sources(cache, {'files': []})

            err = io.StringIO()
            with (
                patch.object(sys, 'argv', ['audit_upstream.py', '--cache', str(cache), '--report', str(report)]),
                patch.object(Path, 'is_symlink', autospec=True, side_effect=lambda p: p == report or orig_is_symlink(p)),
                contextlib.redirect_stderr(err),
            ):
                self.assertEqual(audit_upstream.main(), 1)
            self.assertIn('symlink output path is forbidden', err.getvalue())

            report_dir = root / 'reports'
            report_dir.mkdir()
            nested_report = report_dir / 'report.json'
            err = io.StringIO()
            with (
                patch.object(sys, 'argv', ['audit_upstream.py', '--cache', str(cache), '--report', str(nested_report)]),
                patch.object(Path, 'is_symlink', autospec=True, side_effect=lambda p: p == report_dir or orig_is_symlink(p)),
                contextlib.redirect_stderr(err),
            ):
                self.assertEqual(audit_upstream.main(), 1)
            self.assertIn('symlink output path is forbidden', err.getvalue())

            profiles_path = audit_upstream.ROOT / 'filter-profiles.json'
            err = io.StringIO()
            with (
                patch.object(sys, 'argv', ['audit_upstream.py', '--cache', str(cache), '--report', str(report)]),
                patch.object(Path, 'is_symlink', autospec=True, side_effect=lambda p: p == profiles_path or orig_is_symlink(p)),
                contextlib.redirect_stderr(err),
            ):
                self.assertEqual(audit_upstream.main(), 1)
            self.assertIn('symlink input metadata is forbidden', err.getvalue())

    def test_malformed_snapshots_and_profiles_rejected_and_main_accepts_argv(self):
        import json
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, 'invalid snapshot manifest'):
                audit_upstream.verified_sources(root, {'files': 'not-a-list'})
            with self.assertRaisesRegex(ValueError, 'invalid snapshot identity'):
                audit_upstream.verified_sources(root, {'files': ['bad-entry']})

            for bad_profiles, msg in (
                ({'rule_sets': []}, 'invalid filter profiles'),
                ({'rule_sets': {'ads': {'rules': 'not-a-list'}}}, 'invalid rule set: ads'),
                ({'rule_sets': {'ads': {'rules': ['not-a-rule']}}}, 'unsupported rule in profile'),
            ):
                with self.subTest(msg=msg):
                    with self.assertRaisesRegex(ValueError, msg):
                        audit_upstream.audit(bad_profiles, [])

            cache = root / 'cache'
            report = root / 'report.json'
            cache.mkdir()
            with self.assertRaises(ValueError):
                audit_upstream.verified_sources(cache, {'files': [{'repository': 'owner/repo', 'commit': 'a' * 40, 'path': 'missing.txt', 'sha256': '0' * 64}]})
            orig_read = Path.read_text
            fake_profiles = json.dumps({'version': '20261011.1', 'rule_sets': {'ads': {'rules': ['||example.com^$third-party']}}})
            fake_snapshots = json.dumps({'reviewed_at': '2026-11-09', 'files': []})
            from unittest.mock import patch
            def fake_read_text(path_self, *args, **kwargs):
                if path_self == audit_upstream.ROOT / 'filter-profiles.json':
                    return fake_profiles
                if path_self == audit_upstream.ROOT / 'verification/upstream-snapshots.json':
                    return fake_snapshots
                return orig_read(path_self, *args, **kwargs)
            import contextlib, io
            with patch.object(Path, 'read_text', autospec=True, side_effect=fake_read_text), contextlib.redirect_stdout(io.StringIO()):
                rc = audit_upstream.main(['--cache', str(cache), '--report', str(report)])
            self.assertEqual(rc, 0)
            self.assertTrue(report.is_file())


if __name__ == '__main__':
    unittest.main()
