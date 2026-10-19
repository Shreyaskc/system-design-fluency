"""Generate an accessible opt-in listening page from audio/catalog.json.

Integration: page(tracks(ROOT)) returns a main-content fragment; write_page(ROOT)
writes the complete standalone page. Catalog transcript fields are local paths.
"""
import html
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def local_file(root, value, label, audio_only=False):
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError(f'{label} must be a local relative path')
    path = Path(value)
    resolved = (root / path).resolve()
    boundary = (root / 'audio').resolve() if audio_only else root.resolve()
    if path.is_absolute() or not resolved.is_relative_to(boundary) or not resolved.is_file():
        raise ValueError(f'{label} missing or outside permitted directory: {value}')
    return resolved


def tracks(root=ROOT):
    root = Path(root).resolve()
    catalog = json.loads((root / 'audio/catalog.json').read_text())
    if catalog.get('version') != 1 or not isinstance(catalog.get('tracks'), list):
        raise ValueError('Expected catalog version 1 with a tracks list')
    result, ids = [], set()
    for record in catalog['tracks']:
        q = dict(record)
        if not isinstance(q.get('id'), str) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', q['id']) or q['id'] in ids:
            raise ValueError('Track IDs must be unique safe identifiers')
        ids.add(q['id'])
        for field in ('title', 'chapter'):
            if not isinstance(q.get(field), str) or not q[field].strip():
                raise ValueError(f'Missing {field} for {q["id"]}')
        local_file(root, q.get('chapterUrl'), 'Chapter')
        if q.get('src'):
            local_file(root, q['src'], 'Recording', audio_only=True)
        transcript_path = q.get('transcript')
        if q.get('src') and not transcript_path:
            raise ValueError('Published recordings require a matching transcript')
        q['transcriptPath'] = transcript_path
        q['transcript'] = local_file(root, transcript_path, 'Transcript', audio_only=True).read_text() if transcript_path else ''
        duration = q.get('duration')
        if duration is not None and (isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration <= 0):
            raise ValueError('Duration must be positive finite seconds or null')
        q['section'] = q.get('section') or q['chapter']
        q['chapterTitle'] = q.get('chapterTitle') or q['chapter']
        q['status'] = q.get('status') or ('Recording available' if q.get('src') else 'Recording not available')
        result.append(q)
    return result


def safe_json(value):
    return json.dumps(value, ensure_ascii=False).replace('<', r'\u003c').replace('>', r'\u003e').replace('&', r'\u0026')


def page(items):
    escape = lambda value: html.escape(str(value), quote=True)
    options = ''.join(f'<option value="{escape(q["id"])}">{escape(q.get("chapterTitle") or q["chapter"])} · {escape(q["title"])} — {escape(q["status"])}</option>' for q in items)
    fallback = ''.join('<li><a href="'+escape(q['chapterUrl'])+'">'+escape((q.get('chapterTitle') or q['chapter'])+' · '+q['title'])+'</a>' + (' · <a href="'+escape(q['src'])+'" download>Download recording</a>' if q.get('src') else ' · Recording unavailable') + ('<details><summary>Transcript</summary><p>'+escape(q['transcript']).replace('\n\n','</p><p>')+'</p></details>' if q['transcript'] else '')+'</li>' for q in items)
    count = sum(bool(q.get('src')) for q in items)
    return f'''<h1>Listen to System Design Fluency</h1>
<p class="lead">{count} recordings available across {len(items)} sections. Audio follows the course sequence; each recording has a matching transcript. Listen alongside the diagrams and code in the written lessons.</p>
<p>Choose a section, then Play or Resume. Continuous playback is optional. Reopening this page never starts sound. Pause or Stop cancels the current continuous run; selecting another section leaves it paused. Missing recordings stop the sequence rather than silently skipping material.</p>
<div id="listen-interactive" hidden><label for="audio-track">Section / chapter</label><select id="audio-track">{options}</select>
<h2 id="audio-title"></h2><p id="audio-status" role="status" aria-live="polite"></p><p id="audio-storage"></p>
<audio id="course-audio" controls preload="none" aria-label="System Design Fluency narration"></audio>
<div class="audio-actions"><button id="audio-play" type="button">Play</button> <button id="audio-resume" type="button">Resume</button> <button id="audio-pause" type="button">Pause</button> <button id="audio-stop" type="button">Stop</button> <button id="audio-next" type="button">Next section (paused)</button></div>
<label for="audio-speed">Playback speed</label><select id="audio-speed"><option value="0.5">0.5×</option><option value="0.75">0.75×</option><option value="1">1×</option><option value="1.25">1.25×</option><option value="1.5">1.5×</option><option value="1.75">1.75×</option><option value="2">2×</option><option value="2.5">2.5×</option><option value="3">3×</option></select>
<label><input id="audio-continue" type="checkbox"> Continue to next section or chapter</label>
<p id="audio-position"></p><p><a id="audio-lesson" target="_blank" rel="noopener">Read this lesson (new tab)</a> · <a id="audio-download" hidden download>Download recording</a></p>
<details><summary>Matching transcript</summary><div id="audio-transcript" style="white-space:pre-wrap"></div></details>
<details><summary>Use a local recording</summary><p>Choose audio for the selected section. The file stays in this browser tab and is never uploaded. Choose it again after reopening to resume its saved position.</p><label for="audio-file">Local audio file</label><input id="audio-file" type="file" accept="audio/*"></details></div>
<p>Synthetic narration: Kokoro-82M v1.0, af_heart. Original teaching scripts and spoken code explanations. <a href="audio/ATTRIBUTION.md">Audio attribution and model sources</a>.</p>
<p>Selected section, position, speed and continuous-play preference are stored only in this browser when storage is available. Clearing site data removes them. Study completion uses separate storage. Background and lock-screen playback depend on the browser and operating system.</p>
<noscript><p>Interactive playback and saved positions require JavaScript. Available downloads and transcripts follow.</p></noscript>
<details><summary>All recordings and transcripts</summary><ol>{fallback}</ol></details>
<script id="audio-data" type="application/json">{safe_json(items)}</script><script src="podcast.js" defer></script>'''


def course_navigation(root=ROOT):
    import importlib.util
    spec=importlib.util.spec_from_file_location("course_switcher",Path(__file__).with_name("course_switcher.py"))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.course_navigation(root)


def write_page(root=ROOT,check=False):
    root = Path(root).resolve()
    body = page(tracks(root))
    document = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Listen · System Design Fluency</title><link rel="stylesheet" href="style.css"><link rel="stylesheet" href="courses.css"></head><body><a class="skip" href="#main">Skip to listening controls</a><header><a class="brand" href="index.html">System Design Fluency</a>{course_navigation(root)}</header><main id="main">{body}</main></body></html>'''
    destination = root / 'listen.html'
    if check:
        assert destination.exists() and destination.read_text()==document, "Stale listen.html; rebuild after source/audio changes"
    else:
        destination.write_text(document)
    return destination


if __name__ == '__main__':
    print(write_page())
