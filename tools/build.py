from pathlib import Path
import json,html,re
ROOT=Path(__file__).resolve().parents[1]
chapters=[]
for name in ['start','foundations','cases-a','cases-b','cases-extra','practice','glossary']:
 p=ROOT/'content'/f'{name}.json'
 if p.exists(): chapters+=json.loads(p.read_text())
assert len({c['slug'] for c in chapters})==len(chapters)
nav=''.join(f'<li><a href="{c["slug"]}.html">{html.escape(c["title"])}</a></li>' for c in chapters)
for i,c in enumerate(chapters):
 links=(f'<a href="{chapters[i-1]["slug"]}.html">← Previous</a>' if i else '')+(f'<a href="{chapters[i+1]["slug"]}.html">Next →</a>' if i+1<len(chapters) else '')
 page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Practical system design learning with worked examples and interview reasoning"><title>{html.escape(c['title'])} · System Design Fluency</title><link rel="stylesheet" href="style.css"><script defer src="app.js"></script></head><body><a class="skip" href="#main">Skip to lesson</a><header><a class="brand" href="index.html">System Design Fluency</a><p>Build the reasoning. Trace the failure. Defend the tradeoff.</p></header><div class="layout"><aside><details data-navigation open><summary>Course sequence & search</summary><label for="search">Find a lesson</label><input id="search" type="search" placeholder="Try transactions or chat"><ol id="navigation">{nav}</ol></details></aside><main id="main"><p class="eyebrow">LESSON {i+1:02} / {len(chapters)} · ORIGINAL TEACHING EXAMPLES</p><h1>{html.escape(c['title'])}</h1>{c['body']}<section class="study"><label><input type="checkbox" data-study="{c['slug']}"> I studied this lesson</label><p>Stored only in this browser. Study completion is separate from mastery; demonstrate mastery by solving a changed problem without the sample answer.</p></section><nav class="pager" aria-label="Lesson navigation">{links}</nav><footer>Original course · Technical references reviewed 19 October 2026 · No interview outcome guarantee.</footer></main></div></body></html>'''
 (ROOT/f'{c["slug"]}.html').write_text(page)
(ROOT/'search-index.json').write_text(json.dumps([{'title':c['title'],'url':c['slug']+'.html','text':re.sub('<[^>]+>',' ',c['body'])} for c in chapters]))
print(f'Built {len(chapters)} lessons')
