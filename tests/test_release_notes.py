"""Release failures must stop before a store upload can start."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('release_notes', Path(__file__).resolve().parents[1] / 'tools/release_notes.py')
notes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(notes)


class ReleaseNotesTests(unittest.TestCase):
    def setUp(self):
        workspace = Path(__file__).resolve().parents[1] / 'dist'
        workspace.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=workspace)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.original = notes.ROOT
        notes.ROOT = self.root
        self.addCleanup(setattr, notes, 'ROOT', self.original)
        (self.root / 'package.json').write_text(json.dumps({'version': '0.2.0'}), encoding='utf-8')
        self.write('## [0.2.0] - 2026-10-17\n\n### Added\n\n- Deutsches Radiointro.\n')

    def write(self, text):
        (self.root / 'CHANGELOG.md').write_text(text, encoding='utf-8')

    def test_bad_tags_and_unverified_version_are_refused(self):
        for tag in ['v1.2', 'vNext', 'v0.2.0-rc1', 'v00.2.0', 'v0.2.1']:
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                notes.render(tag, self.root / 'dist')
        self.assertFalse((self.root / 'dist').exists())

    def test_missing_duplicate_and_empty_notes_are_refused(self):
        for text in ['## [0.1.0]\n- Old.\n', '## [0.2.0]\n\n', '## [0.2.0]\n- One.\n## [0.2.0]\n- Two.\n']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.write(text)
                notes.render('v0.2.0', self.root / 'dist')

    def test_unsupported_markdown_is_refused(self):
        self.write('## [0.2.0]\n\n| Bad | Table |\n')
        with self.assertRaises(ValueError):
            notes.render('v0.2.0', self.root / 'dist')

    def test_store_formats_keep_the_same_player_text(self):
        target = self.root / 'dist'
        notes.render('v0.2.0', target)
        self.assertEqual((target / 'release-notes.bbcode').read_text(encoding='utf-8'), '[b]Added[/b]\n[list]\n[*]Deutsches Radiointro.\n[/list]\n')
        self.assertEqual((target / 'release-notes.txt').read_text(encoding='utf-8'), 'Added\n- Deutsches Radiointro.\n')


if __name__ == '__main__':
    unittest.main()
