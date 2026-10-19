# Validation · 19 October 2026

## Executed and passed

- `python3 tools/build.py`: 27 generated pages from 7 content sources.
- `python3 tools/check.py`: exact source slug coverage, body equality, full-text index equality, previous/next order, all internal links and fragments, unique page IDs, semantic viewport/language/navigation/study structure, closed sample answers, case presence/substance, absence of remote scripts.
- `python3 -m unittest discover -s tools -p 'test_*.py'`: 7 arithmetic tests covering unit conversion, shortener namespace/storage/load, bucket load, scheduler headroom, analytics cells/storage, feature-serving budgets, booking and regional calculations, backlog/sensitivity.
- `python3 -m unittest discover -s labs -p 'test_*.py'`: 6 tests covering idempotent reservation retries/payload mismatch/invalid quantity, bucket boundary/cap/clock regression, stale-worker fencing and numerical units.
- `python3 labs/design.py`: retry, refill and stale-worker examples passed.
- `node tools/test_app.js`: search full text/case folding/reset, study storage isolation, definition click/Enter/Space/Escape and aria-controls passed in a controlled DOM model.
- `node --check app.js`: syntax passed.

## Independent review

A separate review pass read all foundations and twelve cases and recomputed their principal numerical examples. Fixes applied: scoped payment idempotency and one live attempt per order; scheduler cancellation boundary; revocation-aware cache lifetime; retained cache version fence; distinction between queue bookkeeping and successful effects; appointment reschedule lock ordering; escrow stock safety versus regional durability; source consistency checks; accessible definition relation; search initial-fetch race; prerequisite wording and narrative name consistency.

Source claims distinguish synthetic assumptions, vendor-specific behavior, platform-authored advice and LeetCode community anecdotes. Technical references were checked during authoring against primary documentation. Interview dialogues, prompts and solutions are original.

## Initial publication limits

The browser tool reported “No browser is available.” No empirical desktop/mobile, screen-reader or real-browser behavior checks were possible. App tests use a small controlled DOM model, not a browser. Responsive layout, semantic markup and no-JavaScript reading fallbacks are implemented; visual quality is not asserted as tested. No load tests, real distributed failure tests, third-party integrations or cloud services were exercised. Labs model boundaries and cannot prove production safety. External references are dated author checks, not continuous link monitoring.

Initial deployment verified: GitHub Pages reported built for db83fd2a4daee2624b44b34572c74c83ca92a17b; all 27 public pages and three required assets returned HTTP 200.

No GitHub workflow file is present; publication uses built static files and branch-based Pages. Deployment verification is recorded in the task outcome after GitHub reports a build and the live HTTP response is checked.

## Audio publication checks

The audio plan covers every substantive source section on all 27 course pages (229 section tracks), including all 12 foundation chapters, all 12 full interview walkthroughs, orientation, practice and glossary. Spoken adaptations preserve the teaching prose and use original explanations of all 29 exact code/diagram blocks. Equations and common units/acronyms are verbalized. Catalog and source hashes identify changed, new, missing or stale content; unregistered content sources or unmapped code fail closed.

Local Kokoro generation is pinned in `audio/engine.json`, with one CPU thread, offline model access and per-section checkpoints. Each completed section records text-consumption checks, sample counts, peak/RMS, timing, model/voice hashes and media fingerprint. Encoding and an independent final decode/astats/silence/duration pass check actual media. These are automated integrity checks, not proof of pronunciation accuracy or listening quality. The prior voice sample was approved for expansion; no end-to-end human listening pass is claimed.

Player tests use media/DOM doubles: explicit Play, opt-in continuation, final/missing-track stop, pause/stop races, silent reload and exact-position resume, throttled persistence, speed/seek bounds, storage denial/corruption, unavailable media, Media Session handling and known/unknown section deep links. A browser surface became available during audio work. Local real-browser checks passed explicit Play with readyState 4, natural section and chapter continuation, Pause, speed 1.25, silent reload, selected-section/preference persistence, resume at the saved 5.88-second position, Stop to 0, disabled Play for a missing recording, and a real media 404 fixture stopping with an explicit recovery message. A delayed native-pause event no longer overwrites terminal error/Stop messages. The temporary fixture was removed. Desktop and 390×844 listening layout were visually inspected; the mobile page width matched 390px with no page overflow. An appointment case also fit 390px; code/diagrams scroll within their own 350px containers. Temporary viewport override was reset. Screen readers, actual iOS devices, background/lock-screen behavior and a complete human listening/pronunciation pass remain untested.

GitHub workflow permissions are unavailable and have not been expanded. `tools/verify_audio.sh` is the reproducible local publication gate; branch-based GitHub Pages remains the host.

Final audio corpus: **229/229 sections across 27 pages, 4.77 hours**. All recording IDs are versioned by spoken content and engine; migration preserved every media file without resynthesis. Original teaching sources are unchanged. The final publication gate runs full media decoding plus 19 tooling/arithmetic tests, 6 lab tests, search/study tests and 15 player behavior groups. See [the full audio coverage matrix](../audio/COVERAGE.md).
