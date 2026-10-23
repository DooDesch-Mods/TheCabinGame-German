"""Read the configured Nexus parent and file group without changing them."""
from pathlib import Path
import json
import os
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def main():
    target = json.loads((ROOT / 'nexus.json').read_bytes())
    expected_version = json.loads((ROOT / 'package.json').read_bytes())['version']
    key = os.environ.get('NEXUSMODS_API_KEY')
    if not key:
        raise RuntimeError('NEXUSMODS_API_KEY is missing')

    def read(path, payload=None):
        request = urllib.request.Request('https://api.nexusmods.com/v3' + path,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={'apikey': key, 'accept': 'application/json', 'content-type': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                body = json.load(response)
        except urllib.error.HTTPError as error:
            raise RuntimeError(f'Nexus read {path}: HTTP {error.code}') from None
        except urllib.error.URLError as error:
            raise RuntimeError(f'Nexus read {path}: {str(error.reason).replace(key, "[redacted]")}') from None
        if not isinstance(body.get('data'), dict):
            raise RuntimeError(f'Nexus read {path}: missing data object')
        return body['data']

    parent = read('/mods/batch', {'mod_ids': [target['mod_id']]})['mods']
    if len(parent) != 1 or str(parent[0].get('id')) != target['mod_id'] or str(parent[0].get('game_id')) != target['game_id']:
        raise RuntimeError('Nexus parent identity differs')
    files = read(f"/mods/{target['mod_id']}/files")['mod_files']
    if len([row for row in files if str(row.get('id')) == target['file_id']]) != 1:
        raise RuntimeError('Nexus file group does not belong to this mod')
    versions = read(f"/mod-files/{target['file_id']}/versions")['versions']
    initial = [row for row in versions if row.get('version') == expected_version and row.get('category') == 'main']
    if len(initial) != 1 or str(initial[0].get('file', {}).get('id')) != target['file_id']:
        raise RuntimeError('Expected exactly one current Main version in the configured file group: ' + expected_version)
    report = {'mod_id': target['mod_id'], 'file_id': target['file_id'], 'page_id': target['page_id'],
              'status': parent[0].get('status'), 'initial_version_id': str(initial[0]['id']),
              'version': initial[0]['version'], 'files_in_parent': len(files), 'write_attempted': False,
              'download_flags': {key: initial[0][key] for key in ['allow_mod_manager_download', 'primary_mod_manager_download'] if key in initial[0]},
              'dependencies': read('/mod-file-versions/' + str(initial[0]['id']) + '/dependencies/ranges')['dependency_definitions']}
    output = ROOT / 'dist/nexus-status.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
