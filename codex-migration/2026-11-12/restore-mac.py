#!/usr/bin/env python3
"""Restore the archived user skills without executing their scripts or overwriting existing skills."""
from pathlib import Path, PurePosixPath
import argparse,hashlib,json,shutil,sys,tempfile,zipfile,urllib.request

BASE='https://raw.githubusercontent.com/haonanz295-dev/portfolio/main/codex-migration/2026-11-12/'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--bundle',type=Path,help='Local folder containing skills-backup.zip and files-sha256.json')
 p.add_argument('--apply',action='store_true',help='Copy missing skills; default is dry run')
 p.add_argument('--target',type=Path,default=Path.home()/'.agents/skills')
 a=p.parse_args()
 if sys.platform!='darwin' and a.apply:raise SystemExit('Apply is intended for macOS only; use dry run here.')
 with tempfile.TemporaryDirectory(prefix='codex-restore-') as tmp:
  tmp=Path(tmp);folder=a.bundle or tmp
  if not a.bundle:
   for n in ['bundle-index.json','files-sha256.json']:
    print('Downloading',n);urllib.request.urlretrieve(BASE+n,folder/n)
   index=json.loads((folder/'bundle-index.json').read_text(encoding='utf-8'))
   with (folder/'skills-backup.zip').open('wb') as out:
    for part in index['parts']:
     name=part['name']
     if '/' in name or '\\' in name or not name.startswith('skills-backup.zip.part-'):raise SystemExit('Invalid part name')
     print('Downloading',name);urllib.request.urlretrieve(BASE+name,folder/name)
     data=(folder/name).read_bytes()
     if hashlib.sha256(data).hexdigest()!=part['sha256']:raise SystemExit('Part checksum mismatch')
     out.write(data)
   if hashlib.sha256((folder/'skills-backup.zip').read_bytes()).hexdigest()!=index['zip_sha256']:raise SystemExit('Archive checksum mismatch')
  expected=json.loads((folder/'files-sha256.json').read_text(encoding='utf-8'))
  checks={x['path']:x for x in expected}
  with zipfile.ZipFile(folder/'skills-backup.zip') as z:
   if len(z.namelist())!=len(set(z.namelist())) or set(z.namelist())!=set(checks):raise SystemExit('Archive file list mismatch')
   for name in z.namelist():
    rel=PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or rel.parts[0]!='skills' or '\\' in name:raise SystemExit('Unsafe archive path')
    data=z.read(name)
    if hashlib.sha256(data).hexdigest()!=checks[name]['sha256']:raise SystemExit('Checksum mismatch: '+name)
    dest=tmp/'unpacked'/Path(*rel.parts);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
  source=tmp/'unpacked/skills'; count=0;existing=[]
  for skill in sorted(source.iterdir()):
   if not skill.is_dir():continue
   dest=a.target/skill.name
   if dest.exists():existing.append(skill.name);continue
   print(('INSTALL ' if a.apply else 'WOULD INSTALL ')+skill.name)
   if a.apply:
    a.target.mkdir(parents=True,exist_ok=True);shutil.copytree(skill,dest)
   count+=1
  print('Copied' if a.apply else 'Planned',count,'top-level folders; existing folders skipped:',len(existing))
  if existing:print('SKIPPED:',', '.join(existing))
  print('Restart Codex and verify skill discovery. Plugins, OAuth, Python/Node dependencies and macOS permissions require separate setup.')
if __name__=='__main__':main()
