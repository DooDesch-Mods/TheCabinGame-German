from pathlib import Path
import argparse
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1]
metadata=json.loads((ROOT/'package.json').read_bytes())
acceptance=json.loads((ROOT/'acceptance.json').read_bytes())
parser=argparse.ArgumentParser()
parser.add_argument('--candidate',action='store_true',help='build a local candidate without claiming runtime acceptance')
args=parser.parse_args()
version=metadata['version']+('-candidate' if args.candidate else '')
files=sorted(p for folder in ['Mods','Content'] for p in (ROOT/folder).rglob('*') if p.is_file())
bindings={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
if not args.candidate:
    assert metadata['version']==acceptance['version'],'version changed since runtime verification'
    assert acceptance['runtime_sha256']==bindings,'runtime changed since recorded verification'
    assert acceptance['ui_runtime_accepted'] and acceptance['audio_runtime_accepted'] and acceptance['radio_subtitle_playback_accepted'],'required release acceptance incomplete'
manifest={'mod':metadata['mod'],'version':version,'game_build':metadata['game_build'],'ue4ss':metadata['ue4ss'],'files':bindings,
          'acceptance_scope':'Local candidate; game verification pending' if args.candidate else acceptance['scope'],
          'full_gameplay_acceptance':False,'ui_runtime_accepted':not args.candidate,'audio_runtime_accepted':not args.candidate}
dist=ROOT/'dist'
dist.mkdir(exist_ok=True)
target=dist/(metadata['mod']+'-'+version+'.zip')
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    documents=['README.md','LICENSE.md','CHANGELOG.md','translations.de.json','CREDITS.md','INTRO.de.txt']
    for path in files+[ROOT/name for name in documents]:
        info=zipfile.ZipInfo(path.relative_to(ROOT).as_posix(),(2026,10,17,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        archive.writestr(info,path.read_bytes())
    info=zipfile.ZipInfo('README.manifest.json',(2026,10,17,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
    archive.writestr(info,json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
with zipfile.ZipFile(target) as archive:
    assert archive.testzip() is None,'ZIP CRC failure'
    for relative,digest in bindings.items():assert hashlib.sha256(archive.read(relative)).hexdigest()==digest
digest=hashlib.sha256(target.read_bytes()).hexdigest()
target.with_suffix('.sha256').write_text(digest+'  '+target.name+'\n',encoding='ascii')
print(f'confirmed ZIP: {target}; entries={len(files)+len(documents)+1}; sha256={digest}')

# Nexus uses game-root destinations and excludes the editable source documents.
nexus=dist/f"{metadata['mod']}_{version}_nexus.zip"
nexus_bindings={}
with zipfile.ZipFile(nexus,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for path in files:
        relative=path.relative_to(ROOT).as_posix()
        destination=('the_cabin_game/Binaries/Win64/ue4ss/'+relative if relative.startswith('Mods/')
                     else 'the_cabin_game/'+relative)
        info=zipfile.ZipInfo(destination,(2026,10,17,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
        archive.writestr(info,path.read_bytes())
        nexus_bindings[destination]=bindings[relative]
    for name in ['README.md','LICENSE.md','CHANGELOG.md','CREDITS.md']:
        info=zipfile.ZipInfo(name,(2026,10,17,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
        archive.writestr(info,(ROOT/name).read_bytes())
    nexus_manifest={**manifest,'files':nexus_bindings}
    info=zipfile.ZipInfo('README.manifest.json',(2026,10,17,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
    archive.writestr(info,json.dumps(nexus_manifest,ensure_ascii=False,indent=2)+'\n')
with zipfile.ZipFile(nexus) as archive:
    assert archive.testzip() is None,'Nexus ZIP CRC failure'
    for relative,digest in nexus_bindings.items():assert hashlib.sha256(archive.read(relative)).hexdigest()==digest
digest=hashlib.sha256(nexus.read_bytes()).hexdigest()
nexus.with_suffix('.sha256').write_text(digest+'  '+nexus.name+'\n',encoding='ascii')
print(f'confirmed Nexus ZIP: {nexus}; entries={len(nexus_bindings)+5}; sha256={digest}')
