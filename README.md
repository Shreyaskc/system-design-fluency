# System Design Fluency

A practical, sequenced course in system design: request traces and concurrency first, distributed architecture next, then twelve original worked interviews and failure probes. Follow a fictional neighborhood marketplace from a single database to global and AI-assisted services. All workload numbers are explicit educational assumptions.

**[Start the course](https://shreyaskc.github.io/system-design-fluency/)** · **[Listen](https://shreyaskc.github.io/system-design-fluency/listen.html)** · [Practice](https://shreyaskc.github.io/system-design-fluency/practice.html) · [Glossary](https://shreyaskc.github.io/system-design-fluency/glossary.html) · [Coverage and limitations](review/COVERAGE.md)

## Study sequence

1. Requirements, interview method and capacity estimates.
2. Networking, APIs, concurrency, transactions and ambiguous outcomes.
3. Caching, replication, consensus, partitioning and messaging.
4. Reliability, security, SLOs, regional recovery, migration and cost.
5. Code-level state machines and principal decision practice.
6. URL shortener, feed, chat, uploads/media, search, rate limiter, scheduler, reservations/payments, streaming analytics AI feature serving, appointment booking and a multi-region inventory capstone.
7. Solve changed requirements without the sample answer; assess reasoning separately from reading completion.

The site supports full-text lesson search, previous/next navigation, answer disclosures, touch/keyboard definitions and local study checkboxes. All content remains readable without JavaScript. No external scripts, analytics, paid services or APIs. Nothing here guarantees interview results or establishes a universal hiring rubric.

## Build and verify

Core reading/build/labs need Python 3.10+ and Node.js, with no third-party Python packages. Audio media validation additionally needs FFmpeg; optional narration generation uses the separate pinned environment below.

```sh
python3 tools/build.py
python3 tools/check.py
python3 -m unittest discover -s labs -p 'test_*.py'
python3 labs/design.py
node tools/test_app.js
python3 -m http.server 8000
```

Open `http://localhost:8000`. Search needs an HTTP server; direct-file reading and ordinary navigation work without it. HTML is generated from `content/*.json`; edit sources and rebuild. Generated pages are committed so GitHub Pages can publish the `main` branch root without a custom workflow. No workflow permission or token scope expansion is required.

## Evidence and originality

Technical references are linked near the relevant lesson material, reviewed 19 October 2026. Interview-platform sources are evidence of their authors' guidance, not verified employer-wide scoring or question frequency. Community posts are labeled as such. Prompts, explanations, calculations, code and diagrams are original. No paid question bank was copied. Accessibility concepts—skip links, legible content, native answer disclosures and separate reading progress—were informed by the user-owned [AI Fluency](https://github.com/Shreyaskc/AI-Learning) reference, inspected read-only; its source files were not copied or modified.

No new license is asserted. Do not infer a third-party license grant from public availability. Labs are small educational models, not production-ready distributed implementations. See [validation evidence](review/VALIDATION.md) for what was and was not tested.

## Navigate the app

**Live site: https://shreyaskc.github.io/system-design-fluency/**

- **Start here** explains the beginner, experienced-builder and principal diagnostic paths. Follow the numbered course sequence; use Previous/Next to move through it.
- **Search** in Course sequence searches full lesson text. It needs an HTTP server; static reading works without JavaScript.
- **Cases** provide full prompts, assumed interviewer answers, calculations, diagrams, schemas, failures and rubrics. Solve before revealing samples; use the short spoken exchange to rehearse communication.
- **Practice** contains failure probes and self-assessment. Study checkboxes record reading, not mastery.
- **Glossary** provides precise definitions, plain meanings, analogies with limits and examples. Inline definitions also work with click/keyboard.
- **[Listen](https://shreyaskc.github.io/system-design-fluency/listen.html)** follows the same chapters as section recordings. Each chapter has a direct Listen link. Select a section, press Play or Resume, then opt into **Continue to next section or chapter** for a continuous run. Pause stops the run; Stop also resets the selected section position. Changing sections leaves playback paused. Native seeking and speed controls are available.
- Audio selection, per-section seconds, speed and continuation preference persist in the same browser when storage works. Reopening stays silent until Resume. Clearing site data removes progress; there is no account or cross-device sync. Missing/broken recordings stop playback with an explicit recovery message. Keep the Listen tab open when using a lesson in another tab. iOS/background/lock-screen behavior is browser-dependent and has not been tested.
- Recordings have matching transcripts and individual downloads. Code and diagrams are explained in speech, not read as punctuation. Written originals remain the authority for exact syntax. Narration is synthetic Kokoro `af_heart`; no Apple voice recording is published.

## Related courses

| Course | Live learning app | Source |
|---|---|---|
| System Design Fluency | https://shreyaskc.github.io/system-design-fluency/ | https://github.com/Shreyaskc/system-design-fluency |
| AI Fluency | https://shreyaskc.github.io/AI-Learning/ | https://github.com/Shreyaskc/AI-Learning |
| DSA Fluency | https://shreyaskc.github.io/dsa-fluency/ | https://github.com/Shreyaskc/dsa-fluency |

The shared Courses navigation is generated from `courses.json`; add a verified live course there to update reading and listening pages together. All three listed courses have verified live sites.

## Audio contributor workflow

Narration is generated locally, not by a paid API. `audio/catalog.json` records every source section, chapter, transcript/media fingerprints, duration and provenance. `audio/transcripts/` contains the exact spoken scripts; `audio/code-narration.json` contains original explanations of all visual code/diagram blocks, keyed by source-block SHA256. `tools/audio.py` deterministically prepares spoken text from the complete teaching prose, including worked solutions; it expands common units/acronyms and mathematical operators. The written lesson retains exact code, reference links and visual formatting.

After editing or adding content:

```sh
python3 tools/audio.py status             # reports missing; rejects stale source/transcript/catalog
python3 tools/audio.py status --watch     # optional checkpoint progress while generation runs
python3 tools/audio.py sync               # prepare transcripts; invalidate changed recordings
python3 tools/audio.py status
```

A new or changed `<pre>` block deliberately fails until its spoken explanation is authored in `audio/code-narration.json`. New chapters must be added to the ordered content sources in `tools/audio.py` and `tools/build.py`; the exact source-coverage checks prevent silent omission. Review the resulting transcripts before synthesis, including numbers, symbols, API semantics, concurrency order and security boundaries. They are listening adaptations, not permission to change the lesson's guarantees.

Generation requires Python 3.12, FFmpeg, the packages in `tools/audio-requirements.txt` (the complete verified Mac ARM environment is `audio/requirements-macos-arm64.lock`), and spaCy `en_core_web_sm` 3.8.0. Create your own virtual environment; do not change another contributor's environment. Install the spaCy model from the [official en_core_web_sm 3.8.0 release](https://github.com/explosion/spacy-models/releases/tag/en_core_web_sm-3.8.0). The exact verified package/configuration hashes are in `audio/engine.json`. Download the pinned public model snapshot `f3ff3571791e39611d31c381e3a41a3af07b4987` from https://huggingface.co/hexgrad/Kokoro-82M, including `config.json`, `kokoro-v1_0.pth`, and `voices/af_heart.pt`. Set the environment variable below to your snapshot directory. The generator verifies model and voice fingerprints and makes no network call in offline mode.

```sh
python3.12 -m venv .audio-venv
.audio-venv/bin/python -m pip install -r audio/requirements-macos-arm64.lock  # includes the official spaCy model and espeak support
# Download public files from the exact official snapshot; no token is needed.
.audio-venv/bin/python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='hexgrad/Kokoro-82M', revision='f3ff3571791e39611d31c381e3a41a3af07b4987', allow_patterns=['config.json','kokoro-v1_0.pth','voices/af_heart.pt'], local_dir='.audio-model', token=False)"
export KOKORO_MODEL_DIR="$PWD/.audio-model"  # or your already verified snapshot directory
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 HF_HUB_OFFLINE=1 HF_HUB_DISABLE_IMPLICIT_TOKEN=1 \
  .audio-venv/bin/python tools/audio.py generate --limit 1  # review one changed section
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 HF_HUB_OFFLINE=1 HF_HUB_DISABLE_IMPLICIT_TOKEN=1 \
  .audio-venv/bin/python tools/audio.py generate            # remaining missing/changed sections
sh tools/verify_audio.sh
```

One CPU thread and a file lock prevent competing writers in this checkout. Every complete section is encoded as mono 64 kbit/s AAC/M4A, decoded, checked for long silence/nonfinite output and plausible duration, then atomically added to the catalog. Interrupted runs resume from completed section checkpoints; an unfinished section is regenerated. Unchanged hashed assets are skipped. Playback IDs include the spoken-content/engine version: inserting or reordering other sections preserves unchanged IDs and positions; changed narration gets a new ID rather than resuming at a misleading old offset. Catalog migration reuses matching source/transcript/engine hashes without resynthesis. Versioned filenames avoid replacing cached media in place. Old unreferenced assets can be removed only after reviewing the catalog diff; do not remove current assets or provenance.

The gate rejects incomplete/stale narration, missing files, changed hashes, transcript mismatch and source coverage/order errors. Provenance checks include whether all paragraph text was consumed by the synthesizer. Automated checks cannot prove pronunciation or instructional quality; review representative output and changed technical passages by listening. Local real-browser Play/continuation/resume and 390px listening layout were checked. No physical iOS, screen-reader or background/lock-screen playback pass is claimed.

Commit source, spoken explanations, transcripts, current media/provenance, catalog and rebuilt HTML together, then run the gate before pushing. GitHub Pages publishes built files from the `main` branch root. A versioned local pre-push guard is provided. Enable it per checkout with `git config --local core.hooksPath .githooks`; it verifies audio and exact generated files without generating or rewriting them. This checkout enables the guard. New clones must opt in, and local hooks can be bypassed, so this is not a GitHub-side enforcement claim. No custom GitHub workflow is installed: the available OAuth authorization lacks workflow scope, and no scope expansion or alternate credential path is used. A future CI gate would require separately authorized workflow access; the documented local gate works now. See [audio attribution](audio/ATTRIBUTION.md) for model and license sources.

After GitHub reports the exact new `main` commit as built, run `python3 tools/verify_deployed.py`. It downloads the published pages, player assets, catalog, transcripts, recordings and provenance, compares every byte with the local build, and checks an HTTP 206 audio byte range. It is read-only and needs no token. A mismatch can indicate an incomplete/older deployment; inspect the Pages build before retrying.
