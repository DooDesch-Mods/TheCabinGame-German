"""Validate a release tag and render one changelog section for each store."""
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def render(tag, output):
    if not re.fullmatch(r'v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', tag):
        raise ValueError(f'release tag must be exactly vX.Y.Z: {tag}')
    version = tag[1:]
    metadata = json.loads((ROOT / 'package.json').read_bytes())
    if version != metadata['version']:
        raise ValueError(f'tag {version} differs from verified candidate {metadata["version"]}')
    text = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    headings = list(re.finditer(r'^## \[([^\]]+)\].*$', text, re.M))
    selected = [i for i, heading in enumerate(headings) if heading[1] == version]
    if len(selected) != 1:
        raise ValueError(f'expected exactly one changelog section for {version}, found {len(selected)}')
    index = selected[0]
    section = text[headings[index].end():headings[index+1].start() if index+1 < len(headings) else len(text)].strip()
    if not section or re.search(r'\b(TODO|TBD|placeholder)\b', section, re.I):
        raise ValueError('release notes are empty or contain a placeholder')
    bbcode, plain = [], []
    in_list, count = False, 0
    for line in section.splitlines():
        if line.startswith('- '):
            item = line[2:]
            if len(item) >= 200:
                raise ValueError(f'changelog bullet exceeds 199 characters: {item}')
            if not in_list:
                bbcode.append('[list]')
                in_list = True
            count += 1
            if count > 5:
                raise ValueError('more than five bullets in one changelog section')
            bbcode.append('[*]' + item)
            plain.append('- ' + item)
        else:
            if in_list:
                bbcode.append('[/list]')
                in_list = False
            if line.startswith('### '):
                count = 0
                bbcode.append('[b]' + line[4:] + '[/b]')
                plain.append(line[4:])
            elif line.strip():
                raise ValueError(f'unsupported changelog format: {line}')
    if in_list:
        bbcode.append('[/list]')
    output.mkdir(exist_ok=True, parents=True)
    for suffix, content in [('md', section), ('bbcode', '\n'.join(bbcode)), ('txt', '\n'.join(plain))]:
        (output / f'release-notes.{suffix}').write_text(content + '\n', encoding='utf-8')
    print(f'PASS: {tag}; Markdown, Nexus BBCode and plain changelog written to {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tag')
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    render(args.tag, args.output)
