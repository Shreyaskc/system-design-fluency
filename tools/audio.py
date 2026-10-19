"""Deterministic section narration, incremental local Kokoro generation and coverage gate."""
from pathlib import Path
from html.parser import HTMLParser
import argparse, hashlib, html, json, os, re, subprocess, sys, tempfile, time
ROOT=Path(__file__).resolve().parents[1]
ORDER=['start','foundations','cases-a','cases-b','cases-extra','practice','glossary']
REV='f3ff3571791e39611d31c381e3a41a3af07b4987'
MODEL_SHA='496dba118d1a58f5f3db2efc88dbdc216e0483fc89fe6e47ee1f2c53f18ad1e4'
VOICE_SHA='0ab5709b8ffab19bfd849cd11d98f75b60af7733253ad0d67b12382a102cb4ff'
def sha(data):return hashlib.sha256(data).hexdigest()
def save(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n');tmp.replace(path)
class Speech(HTMLParser):
 def __init__(self):super().__init__();self.out=[]
 def handle_data(self,data):self.out.append(data)
 def handle_starttag(self,tag,attrs):
  if tag in ['p','li','summary','tr','h2','h3','details']:self.out.append('\n\n')
  if tag in ['td','th']:self.out.append(' ; ')
  if tag=='br':self.out.append(' ')
  if tag=='sup':self.out.append(' to the power ')
 def handle_endtag(self,tag):
  if tag in ['p','li','summary','tr','h2','h3']:self.out.append('.\n\n')
def speak(raw,mapping):
 def code(m):
  key=sha(m.group().encode());assert key in mapping,'Missing authored code/diagram narration '+key
  return '<p>'+html.escape(mapping[key])+'</p>'
 raw=re.sub(r'<pre\b[^>]*>.*?</pre>',code,raw,flags=re.S)
 inline_explanations={
  'available = min(B, old_tokens + r × dt)': 'the available token count is the smaller of bucket capacity B and the old token count plus refill rate r multiplied by elapsed time delta t',
  'sellable - reserved - sold >= requested_quantity': 'sellable stock minus reserved stock minus already sold stock must be at least the requested quantity',
  'UPDATE inventory SET available=available-:q, version=version+1 WHERE sku=:sku AND available>=:q': 'atomically update the inventory row for the requested item: subtract quantity q from available stock and increase the version by one, but only if that same row currently has at least q units available. Check that exactly one row changed, and commit the reservation and request result in the same transaction'
 }
 def inline(m):
  visible=html.unescape(re.sub('<[^>]*>','',m.group(1)))
  return html.escape(inline_explanations[visible]) if visible in inline_explanations else m.group()
 raw=re.sub(r'<code>(.*?)</code>',inline,raw,flags=re.S)
 p=Speech();p.feed(raw);s=''.join(p.out)
 replacements={'→':' leads to ','←':' comes from ','×':' times ','≈':' approximately ','≤':' at most ','≥':' at least ','−':' minus ','λ':' lambda ','μ':' mu ','≠':' not equal to ','%':' percent','/second':' per second','/s':' per second','/day':' per day','ms':' milliseconds','GB':' gigabytes','MB':' megabytes','KB':' kilobytes','TB':' terabytes','p99':'99th percentile','p95':'95th percentile','SQL':'sequel','API':'A P I','HTTP':'H T T P','TTL':'T T L','CPU':'C P U','RPO':'R P O','RTO':'R T O','SLO':'S L O','SLI':'S L I'}
 for a,b in replacements.items():
  if a.isalnum():s=re.sub(r'\b'+re.escape(a)+r'\b',b,s)
  else:s=s.replace(a,b)
 s=re.sub(r'(\d+)\^(\d+)',r'\1 to the power \2',s)
 s=re.sub(r'(?<=\d)\s*/\s*(?=\d)',' divided by ',s)
 s=s.replace('>=',' at least ').replace('<=',' at most ').replace(' + ',' plus ').replace(' - ',' minus ').replace(' > ',' greater than ').replace(' < ',' less than ').replace(' = ',' equals ')
 s=s.replace('`','').replace('•',' ').replace('·',' ').replace('&',' and ')
 s=re.sub(r'\.{2,}','.',s);s=re.sub(r' *\n *','\n',s)
 s='\n\n'.join(re.sub(r'\s+',' ',q).strip(' .;')+'.' for q in s.split('\n\n') if q.strip(' .;\n'))
 # Keep synthesis paragraphs bounded without omitting sentences.
 out=[]
 for para in s.split('\n\n'):
  parts=re.split(r'(?<=[.!?])\s+',para);current=''
  for part in parts:
   if len((current+' '+part).split())>100 and current:out.append(current);current=''
   current=(current+' '+part).strip()
  if current:out.append(current)
 return '\n\n'.join(out)+'\n'
def expected():
 mapping=json.loads((ROOT/'audio/code-narration.json').read_text());items=[]
 assert {p.stem for p in (ROOT/'content').glob('*.json')}==set(ORDER), 'Register all new content sources in ORDER'
 bodies=[c['body'] for name in ORDER for c in json.loads((ROOT/'content'/f'{name}.json').read_text())]
 blocks={sha(raw.encode()) for body in bodies for raw in re.findall(r'<pre\b[^>]*>.*?</pre>',body,re.S)}
 assert set(mapping)==blocks,'Missing or orphan code/diagram narration: review exact source hashes'
 for name in ORDER:
  for c in json.loads((ROOT/'content'/f'{name}.json').read_text()):
   assert re.fullmatch(r'[a-z0-9][a-z0-9-]*',c['slug']),'Unsafe chapter slug'
   raw=c['body']
   if c['slug']=='glossary':
    chunks=re.findall(r'<details>.*?</details>',raw,re.S)
    if chunks:chunks[0]=raw.split('<details>',1)[0]+chunks[0]
   else:chunks=re.split(r'(?=<h2\b)',raw)
   for i,chunk in enumerate(chunks,1):
    if not chunk.strip():continue
    heading=re.search(r'<(?:h2|summary)[^>]*>(.*?)</(?:h2|summary)>',chunk,re.S)
    title=html.unescape(re.sub('<[^>]*>','',heading.group(1))) if heading else 'Introduction'
    text=speak('<p>'+html.escape(c['title']+' . '+title)+'</p>'+chunk,mapping)
    engine='Kokoro-82M-v1-af_heart-speed1-rules1'
    ident=c['slug']+'-'+sha((text+'\0'+engine).encode())[:12]
    items.append(dict(id=ident,title=title,chapter=c['slug'],chapterTitle=c['title'],chapterUrl=c['slug']+'.html',transcript=f'audio/transcripts/{ident}.txt',text=text,source_sha256=sha(chunk.encode()),transcript_sha256=sha(text.encode()),engine=engine))
 assert len({q['id'] for q in items})==len(items),'Duplicate narration identities'
 return items
def catalog():
 p=ROOT/'audio/catalog.json';return json.loads(p.read_text()) if p.exists() else {'version':1,'tracks':[]}
def _sync():
 old={q['id']:q for q in catalog()['tracks']};tracks=[]
 by_content={(q['chapter'],q.get('source_sha256'),q.get('transcript_sha256'),q.get('engine')):q for q in old.values()}
 for item in expected():
  text=item.pop('text');path=ROOT/item['transcript'];path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
  previous=old.get(item['id']) or by_content.get((item['chapter'],item['source_sha256'],item['transcript_sha256'],item['engine']),{})
  fresh=all(previous.get(k)==item[k] for k in ['source_sha256','transcript_sha256','engine'])
  item.update({k:previous[k] for k in ['src','duration','sha256','provenance'] if fresh and k in previous})
  item.setdefault('src',None);item.setdefault('duration',None);tracks.append(item)
 save(ROOT/'audio/catalog.json',{'version':1,'tracks':tracks});return tracks

def sync():
 import fcntl
 with open(ROOT/'.audio-work.lock','w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  return _sync()

def validate(require=True,decode=False):
 items=expected();actual=catalog()['tracks'];assert [q['id'] for q in actual]==[q['id'] for q in items],'Stale source coverage; run sync'
 missing=[]
 for e,a in zip(items,actual):
  for k in ['source_sha256','transcript_sha256','engine']:assert e[k]==a.get(k),(a['id'],'stale '+k)
  assert (ROOT/a['transcript']).read_text()==e['text'],(a['id'],'transcript stale')
  if not a.get('src'):missing.append(a['id']);continue
  asset=(ROOT/a['src']).resolve();assert asset.is_relative_to((ROOT/'audio/media').resolve()) and asset.exists()
  assert sha(asset.read_bytes())==a['sha256'],(a['id'],'asset hash')
  provenance=(ROOT/a['provenance']).resolve();assert provenance.is_relative_to((ROOT/'audio/provenance').resolve())
  meta=json.loads(provenance.read_text());assert meta['transcript_sha256']==e['transcript_sha256']
  assert meta['source_sha256']==e['source_sha256'] and meta['model_sha256']==MODEL_SHA and meta['voice_sha256']==VOICE_SHA and meta['model_revision']==REV,(a['id'],'stale provenance')
  assert abs(meta['duration']-a['duration'])<.01
  assert meta['grapheme_complete'] and meta['peak']>.001 and meta['rms']>.001
  assert .8 < len(e['text'].split())/a['duration'] < 6,(a['id'],'duration/word rate')
  if decode:
   decoded=subprocess.run(['ffmpeg','-hide_banner','-i',str(asset),'-af','astats=metadata=0:reset=0,silencedetect=noise=-45dB:d=4','-f','null','-'],check=True,capture_output=True,text=True)
   assert 'silence_start' not in decoded.stderr,(a['id'],'decoded long silence')
   rms=re.findall(r'RMS level dB: ([-\d.]+)',decoded.stderr)
   assert rms and float(rms[-1])>-60,(a['id'],'decoded silence')
   probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,channels,sample_rate','-of','json',str(asset)],text=True))
   streams=probe['streams'];assert len(streams)==1 and streams[0]['codec_name']=='aac' and streams[0]['channels']==1 and streams[0]['sample_rate']=='24000',(a['id'],'unexpected encoding')
   duration=float(probe['format']['duration'])
   assert abs(duration-a['duration'])<.2,(a['id'],'encoded duration mismatch')
 print(f'Audio coverage {len(actual)-len(missing)}/{len(actual)} sections; {len(set(q["chapter"] for q in actual))} chapters; {sum(q.get("duration") or 0 for q in actual)/3600:.2f} hours',flush=True)
 if require:assert not missing,'Missing audio: '+', '.join(missing[:10])
 return missing

def report():
 validate(require=False)
 tracks=catalog()['tracks'];chapters={}
 for q in tracks:chapters.setdefault(q['chapter'],[]).append(q)
 lines=['# Audio coverage', '', f"Recorded sections: {sum(bool(q.get('src')) for q in tracks)} / {len(tracks)}. All workload examples remain synthetic teaching assumptions.", '', '| Chapter | Sections recorded | Duration |','|---|---:|---:|']
 for name,items in chapters.items():
  seconds=sum(q.get('duration') or 0 for q in items)
  lines.append(f"| {items[0]['chapterTitle']} | {sum(bool(q.get('src')) for q in items)}/{len(items)} | {seconds/60:.1f} minutes |")
 total=sum(q.get('duration') or 0 for q in tracks)
 lines+=['',f'Total narration: {total/3600:.2f} hours. Voice: Kokoro-82M v1.0 af_heart, local CPU, one thread.', '', 'The catalog pins per-section source, transcript and media hashes. Provenance records text consumption and signal checks. The publication gate independently decodes media and checks signal, long silence and duration. These checks do not prove pronunciation or instructional quality.', '', 'Player behavior and mobile layout were checked in a local in-app browser. Physical iOS, screen readers and background/lock-screen behavior remain untested.']
 (ROOT/'audio/COVERAGE.md').write_text('\n'.join(lines)+'\n')
 print('Wrote audio/COVERAGE.md')

def reusable(item):
 try:
  asset=(ROOT/item['src']).resolve();provenance=(ROOT/item['provenance']).resolve()
  if not asset.is_relative_to((ROOT/'audio/media').resolve()) or not provenance.is_relative_to((ROOT/'audio/provenance').resolve()):return False
  if sha(asset.read_bytes())!=item['sha256']:return False
  meta=json.loads(provenance.read_text())
  return meta['transcript_sha256']==item['transcript_sha256'] and meta['source_sha256']==item['source_sha256'] and meta['model_sha256']==MODEL_SHA and meta['voice_sha256']==VOICE_SHA and meta['grapheme_complete'] and abs(meta['duration']-item['duration'])<.01
 except (KeyError,TypeError,ValueError,OSError):return False

def generate(model_dir,limit=None):
 os.environ['HF_HUB_OFFLINE']='1';os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN']='1'
 import fcntl
 lock=open(ROOT/'.audio-work.lock','w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 import numpy as np, soundfile as sf, torch
 from kokoro import KModel,KPipeline
 torch.set_num_threads(1);torch.set_num_interop_threads(1)
 model_dir=Path(model_dir)
 engine=json.loads((ROOT/'audio/engine.json').read_text())
 assert sha((model_dir/'config.json').read_bytes())==engine['files']['config.json']
 from importlib.metadata import version
 for package,pinned in engine['packages'].items():assert version(package)==pinned,(package,'generation environment differs from audio/engine.json')
 assert sha((model_dir/'kokoro-v1_0.pth').read_bytes())==MODEL_SHA
 assert sha((model_dir/'voices/af_heart.pt').read_bytes())==VOICE_SHA
 model=KModel(repo_id='hexgrad/Kokoro-82M',config=str(model_dir/'config.json'),model=str(model_dir/'kokoro-v1_0.pth')).to('cpu').eval()
 pipeline=KPipeline(lang_code='a',repo_id='hexgrad/Kokoro-82M',model=model,device='cpu')
 voice=torch.load(model_dir/'voices/af_heart.pt',weights_only=True,map_location='cpu')
 tracks=_sync();count=0
 for item in tracks:
  if reusable(item):continue
  started=time.monotonic();text=(ROOT/item['transcript']).read_text();parts=[];segments=[];complete=True
  for paragraph in text.strip().split('\n\n'):
   generated=[];graphemes=[]
   with torch.inference_mode():
    for g,p,audio in pipeline(paragraph,voice=voice,speed=1.0):
     assert audio is not None;generated.append(audio.detach().cpu().numpy());graphemes.append(g)
   assert generated,(item['id'],'empty synthesis')
   # Kokoro may normalize punctuation; all alphanumeric text must be accounted for.
   norm=lambda s:re.sub(r'[^\w]','',s).lower()
   assert norm(''.join(graphemes))==norm(paragraph),(item['id'],'unconsumed text',paragraph,''.join(graphemes))
   wave=np.concatenate(generated);assert np.isfinite(wave).all()
   segments.append({'text_sha256':sha(paragraph.encode()),'samples':len(wave)})
   parts.extend([wave,np.zeros(6000,dtype=np.float32)])
  wave=np.concatenate(parts[:-1]);duration=len(wave)/24000;peak=float(np.max(np.abs(wave)));rms=float(np.sqrt(np.mean(wave**2)))
  assert .8<len(text.split())/duration<6 and peak>.001 and rms>.001
  digest=item['transcript_sha256'][:12];name=f'{item["id"]}-{digest}.m4a';dest=ROOT/'audio/media'/name
  with tempfile.TemporaryDirectory(prefix='sdf-audio-') as work:
   wav=Path(work)/'track.wav';encoded=Path(work)/'track.m4a';sf.write(wav,wave,24000,subtype='PCM_16')
   subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-c:a','aac','-b:a','64k','-movflags','+faststart',str(encoded)],check=True)
   subprocess.run(['ffmpeg','-v','error','-i',str(encoded),'-f','null','-'],check=True)
   # Long silent gaps indicate malformed synthesis; short sentence pauses remain.
   probe=subprocess.run(['ffmpeg','-hide_banner','-i',str(encoded),'-af','silencedetect=noise=-45dB:d=4','-f','null','-'],capture_output=True,text=True,check=True)
   assert 'silence_start' not in probe.stderr,(item['id'],'long silence')
   dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(encoded.read_bytes())
  meta=dict(backend='Kokoro-82M v1.0',model_revision=REV,model_sha256=MODEL_SHA,voice='af_heart',voice_sha256=VOICE_SHA,threads=1,sample_rate=24000,speed=1.0,transcript_sha256=item['transcript_sha256'],source_sha256=item['source_sha256'],duration=duration,peak=peak,rms=rms,grapheme_complete=complete,segments=segments,generation_seconds=time.monotonic()-started)
  provenance=f'audio/provenance/{item["id"]}-{digest}.json';save(ROOT/provenance,meta)
  item.update(src='audio/media/'+name,duration=duration,sha256=sha(dest.read_bytes()),provenance=provenance)
  save(ROOT/'audio/catalog.json',{'version':1,'tracks':tracks});count+=1
  print(f'COMPLETE {item["id"]} {duration:.1f}s in {meta["generation_seconds"]:.1f}s [{sum(bool(q.get("src")) for q in tracks)}/{len(tracks)}]',flush=True)
  if limit and count>=limit:break
 validate(require=False)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['sync','status','generate','validate','report']);p.add_argument('--model-dir',default=os.getenv('KOKORO_MODEL_DIR'));p.add_argument('--limit',type=int);p.add_argument('--decode',action='store_true');p.add_argument('--watch',action='store_true');a=p.parse_args()
 if a.action=='sync':print('Synced',len(sync()),'sections')
 elif a.action=='status':
  validate(require=False)
  if a.watch:
   while True:
    current=catalog()['tracks'];done=[q for q in current if q.get('src')]
    print(f'PROGRESS {len(done)}/{len(current)} sections; {sum(q["duration"] for q in done)/60:.1f} minutes; latest {done[-1]["id"] if done else "none"}',flush=True)
    if len(done)==len(current):validate();break
    time.sleep(30)
 elif a.action=='validate':validate(decode=a.decode)
 elif a.action=='report':report()
 else:
  if not a.model_dir:p.error('--model-dir or KOKORO_MODEL_DIR required')
  generate(a.model_dir,a.limit)
