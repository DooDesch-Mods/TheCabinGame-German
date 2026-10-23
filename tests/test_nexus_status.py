"""Read current Main versions and the flat dependency API response."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('nexus_status', Path(__file__).resolve().parents[1] / 'tools/nexus_status.py')
status = importlib.util.module_from_spec(spec)
spec.loader.exec_module(status)

class NexusStatusTests(unittest.TestCase):
    def test_current_version_and_flat_requirements(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'nexus.json').write_text(json.dumps({'mod_id': '13', 'game_id': '10562', 'file_id': '42', 'page_id': '13', 'initial_version': '0.2.0'}))
            (root / 'package.json').write_text(json.dumps({'version': '0.2.1'}))
            answers = [
                {'data': {'mods': [{'id': '13', 'game_id': '10562', 'status': 'published'}]}},
                {'data': {'mod_files': [{'id': '42'}]}},
                {'data': {'versions': [{'id': '99', 'version': '0.2.1', 'category': 'main', 'file': {'id': '42'}, 'allow_mod_manager_download': True}]}},
                {'dependency_definitions': [{'ranges': [{'min_version': {'id': '54'}}]}]},
            ]
            class Response:
                def __init__(self, body): self.body = body
                def __enter__(self): return self
                def __exit__(self, *args): return False
                def read(self): return json.dumps(self.body).encode()
            with patch.object(status, 'ROOT', root), patch.dict(os.environ, {'NEXUSMODS_API_KEY': 'fixture'}), patch.object(status.urllib.request, 'urlopen', side_effect=[Response(a) for a in answers]):
                status.main()
            receipt = json.loads((root / 'dist/nexus-status.json').read_text())
            self.assertEqual(receipt['version'], '0.2.1')
            self.assertEqual(receipt['dependencies'], answers[-1]['dependency_definitions'])
            self.assertTrue(receipt['download_flags']['allow_mod_manager_download'])
            self.assertFalse(receipt['write_attempted'])
