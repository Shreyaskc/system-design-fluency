from pathlib import Path
import json,html

def course_navigation(root):
    data=json.loads((Path(root)/'courses.json').read_text())
    current=data['current']
    name=next(c['title'] for c in data['courses'] if c['id']==current)
    links=[]
    for c in data['courses']:
        active=c['id']==current
        href=('index.html' if current=='system-design-fluency' else '#home') if active else c['site']
        if active and current=='practical-engineering-fluency': href='#'
        attr=' aria-current="page"' if active else ''
        label=html.escape(c['title'])+(' · Current course' if active else '')
        links.append('<li><a href="'+html.escape(href,quote=True)+'"'+attr+'>'+label+'</a></li>')
    listen='<a class="suite-listen" href="listen.html">Listen to this course</a>' if current=='system-design-fluency' else ''
    return '<nav aria-label="Courses" class="suite-courses"><details><summary>Courses <span> / '+html.escape(name)+'</span></summary><ul>'+''.join(links)+'</ul></details>'+listen+'</nav>'

if __name__ == '__main__':
    import re,sys
    root=Path(__file__).resolve().parents[1]
    nav=course_navigation(root)
    data=json.loads((root/'courses.json').read_text())
    assert len(data['courses'])==6 and len({c['id'] for c in data['courses']})==6
    for page in root.glob('*.html'):
        original=page.read_text()
        updated=re.sub(r'<nav aria-label="Courses"[^>]*>.*?</nav>',lambda m:nav,original,flags=re.S)
        assert nav in updated, f'Missing course switcher: {page.name}'
        assert 'href="courses.css"' in updated
        if '--check' in sys.argv: assert original==updated, f'Stale course navigation: {page.name}'
        else: page.write_text(updated)
    print('PASS: six-course registry and all app-page switchers agree')
