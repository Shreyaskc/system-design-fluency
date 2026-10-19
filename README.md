# System Design Fluency

A practical, sequenced course in system design: request traces and concurrency first, distributed architecture next, then twelve original worked interviews and failure probes. Follow a fictional neighborhood marketplace from a single database to global and AI-assisted services. All workload numbers are explicit educational assumptions.

**[Start the course](https://shreyaskc.github.io/system-design-fluency/)** · [Practice](https://shreyaskc.github.io/system-design-fluency/practice.html) · [Glossary](https://shreyaskc.github.io/system-design-fluency/glossary.html) · [Coverage and limitations](review/COVERAGE.md)

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

Python 3.10+ and Node.js are sufficient; no third-party packages.

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
