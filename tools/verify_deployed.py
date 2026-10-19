"""Read-only exact-byte verification of the public branch-based Pages deployment."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen,Request
from urllib.parse import quote
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def main(base):
 catalog=json.loads((ROOT/'audio/catalog.json').read_text())['tracks']
 assert catalog and all(q.get('src') for q in catalog),'Complete local audio before checking deployment'
 files={p.name for p in ROOT.glob('*.html') if not p.name.startswith('.')}
 files.update(['app.js','podcast.js','style.css','search-index.json','courses.json','audio/catalog.json','audio/ATTRIBUTION.md','audio/COVERAGE.md','audio/engine.json','audio/licenses/Kokoro-Apache-2.0.txt'])
 for q in catalog:files.update([q['src'],q['transcript'],q['provenance']])
 def verify(name):
  local=(ROOT/name).resolve();assert local.is_relative_to(ROOT)
  expected=hashlib.sha256(local.read_bytes()).digest()
  with urlopen(base.rstrip('/')+'/'+quote(name,safe='/'),timeout=40) as response:
   assert response.status==200,(name,response.status)
   digest=hashlib.sha256();size=0
   while block:=response.read(1024*1024):digest.update(block);size+=len(block)
  assert digest.digest()==expected,(name,'deployed bytes differ')
  return size
 with ThreadPoolExecutor(max_workers=6) as pool:sizes=list(pool.map(verify,sorted(files)))
 first=catalog[0]['src'];request=Request(base.rstrip('/')+'/'+quote(first,safe='/'),headers={'Range':'bytes=0-1023'})
 with urlopen(request,timeout=30) as response:
  assert response.status==206,('Range response',response.status)
  assert response.read()==(ROOT/first).read_bytes()[:1024]
  content_range=response.headers.get('Content-Range')
 print(f'PASS: {len(files)} deployed pages/assets/transcripts/provenance files are byte-identical; {sum(sizes):,} bytes checked')
 print('PASS: audio HTTP206 byte-range response:',content_range)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--base',default='https://shreyaskc.github.io/system-design-fluency/');args=parser.parse_args();main(args.base)
