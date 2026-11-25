"""Boundary and negative-control regression tests for subscription metadata."""
import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_subscription_contract import BASE, PUBLIC, check, check_path


class ContractBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in PUBLIC:
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            license_name = 'GPL-3.0-only' if name.startswith('v2/') else 'CC0-1.0'
            p.write_text('[Adblock Plus 2.0]\n! Title: Test\n! License: ' + license_name +
                         '\n! Homepage: https://github.com/r20942097-hue/s\n! Subscription: ' +
                         BASE + name + '\nexample.org##.test\n', encoding='utf-8')

    def rewrite(self, name, old, new):
        p = self.root / name
        text = p.read_text(encoding='utf-8')
        self.assertEqual(text.count(old), 1)
        p.write_text(text.replace(old, new, 1), encoding='utf-8')

    def test_wrong_file_type_has_specific_diagnosis(self):
        p = self.root / 'ad.txt'
        p.unlink()
        p.mkdir()
        self.assertEqual(check_path(self.root, 'ad.txt'), ['missing subscription file or wrong file type'])

    def test_invalid_utf8_rejected(self):
        (self.root / 'ad.txt').write_bytes(b'\xff\xfe')
        self.assertEqual(check_path(self.root, 'ad.txt'), ['file unreadable as UTF-8'])

    def test_title_required_nonempty_unique(self):
        for name, replacement in zip(PUBLIC[:3], ['', '! Title:   \n', '! Title: A\n! Title: B\n']):
            with self.subTest(name=name):
                self.rewrite(name, '! Title: Test\n', replacement)
                self.assertIn('title metadata missing or duplicated', check_path(self.root, name))

    def test_homepage_required_unique_correct(self):
        old = '! Homepage: https://github.com/r20942097-hue/s\n'
        for name, replacement in zip(PUBLIC[:3], ['', '! Homepage: https://example.invalid/\n', old + old]):
            with self.subTest(name=name):
                self.rewrite(name, old, replacement)
                self.assertIn('homepage metadata mismatch', check_path(self.root, name))

    def test_optional_subscription_if_present_must_be_correct(self):
        self.rewrite('ad-ubo.txt', BASE + 'ad-ubo.txt', 'https://example.invalid/')
        self.assertIn('subscription URL metadata mismatch', check_path(self.root, 'ad-ubo.txt'))

    def test_metadata_scan_boundary(self):
        # Characterizes the current 45-line scan limit; revisit if the contract changes.
        for line, expected in [(45, False), (46, True)]:
            with self.subTest(line=line):
                p = self.root / 'ad.txt'
                p.write_text('[Adblock Plus 2.0]\n! License: CC0-1.0\n'
                             '! Homepage: https://github.com/r20942097-hue/s\n'
                             '! Subscription: ' + BASE + 'ad.txt\n' +
                             '! filler\n' * (line - 5) + '! Title: Test\n', encoding='utf-8')
                self.assertEqual('title metadata missing or duplicated' in check_path(self.root, 'ad.txt'), expected)

    def test_each_public_path_individually_required(self):
        for name in PUBLIC:
            with self.subTest(name=name):
                p = self.root / name
                original = p.read_bytes()
                try:
                    p.unlink()
                    result = check(self.root)
                    self.assertEqual(result['status'], 'FAIL')
                    self.assertEqual(set(result['issues']), {name})
                finally:
                    p.write_bytes(original)

    def test_duplicate_required_subscription_rejected(self):
        for name in (n for n in PUBLIC if n != 'ad-ubo.txt'):
            with self.subTest(name=name):
                field = '! Subscription: ' + BASE + name + '\n'
                self.rewrite(name, field, field + field)
                self.assertIn('missing or changed subscription URL metadata', check_path(self.root, name))

if __name__ == '__main__':
    unittest.main()
