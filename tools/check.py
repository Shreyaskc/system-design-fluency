from pathlib import Path
from html.parser import HTMLParser
import json,re
R=Path(__file__).resolve().parents[1]
class Scan(HTMLParser):
 def __init__(self): super().__init__(); self.links=[];self.ids=[];self.stack=[]; self.details=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='a': self.links.append(a.get('href',''))
  if tag=='details':
   self.details+=1
   assert 'open' not in a or 'data-navigation' in a, 'Sample answer exposed by default'
pages=list(R.glob('*.html')); assert len(pages)>=24, len(pages)
for p in pages:
 s=Scan(); text=p.read_text();s.feed(text)
 assert len(s.ids)==len(set(s.ids)),p
 assert '<html lang="en">' in text and 'name="viewport"' in text
 for href in s.links:
  if href.startswith(('https:','http:','mailto:')):continue
  target,_,anchor=href.partition('#')
  dest=R/target if target else p
  assert dest.exists(),(p,href)
  if anchor: assert f'id="{anchor}"' in dest.read_text(),(p,href)
 assert 'data-study=' in text and 'aria-label="Lesson navigation"' in text
 assert not re.search(r'<script[^>]+src=["\']https?',text)
index=json.loads((R/'search-index.json').read_text()); assert len(index)==len(pages)
assert all((R/x['url']).exists() for x in index)
for name in ['cases-a','cases-b']:
 data=json.loads((R/'content'/f'{name}.json').read_text());assert len(data)==5
 for c in data:
  assert len(re.sub('<[^>]*>',' ',c['body']).split())>=650,(c['slug'],'too short')
  assert '<pre' in c['body'] and '<details' in c['body'],c['slug']
print(f'PASS: {len(pages)} pages, unique IDs, internal links, search index, case substance, accessibility structure')
expected=[]
for name in ['start','foundations','cases-a','cases-b','cases-extra','practice','glossary']:
 expected+=json.loads((R/'content'/f'{name}.json').read_text())
assert {p.stem for p in pages}=={c['slug'] for c in expected}
assert [x['url'] for x in index]==[c['slug']+'.html' for c in expected]
for i,c in enumerate(expected):
 page=(R/(c['slug']+'.html')).read_text()
 assert c['body'] in page,(c['slug'],'generated body differs from source')
 assert index[i]['text']==re.sub('<[^>]+>',' ',c['body'])
 if i:assert f'<a href="{expected[i-1]["slug"]}.html">← Previous</a>' in page
 if i+1<len(expected):assert f'<a href="{expected[i+1]["slug"]}.html">Next →</a>' in page
 if c in json.loads((R/'content/cases-extra.json').read_text()):
  assert '<pre' in c['body'] and '<details' in c['body']
  assert len(re.sub('<[^>]*>',' ',c['body']).split())>=650
print('PASS: exact source coverage, generated body/index consistency, next/previous sequence, extra cases')
glossary=json.loads((R/'content/glossary.json').read_text())[0]['body']
for label in ['Precise definition:','Plain English:','Analogy and its limit:','Concrete example:']:
 assert glossary.count(label)==25,(label,'missing definition layer')
foundation_text=(R/'content/foundations.json').read_text()
for label in ['Technical:','Plain English:','Analogy and limit:','Example:']:
 assert foundation_text.count(label)==10,(label,'missing inline layer')
print('PASS: 25 layered glossary entries and 10 layered inline definitions')
