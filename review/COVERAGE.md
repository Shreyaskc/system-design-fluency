# Coverage ledger · 19 October 2026

The course has 27 generated reading pages: orientation, 12 foundations, 12 complete worked cases, practice and glossary. There are no placeholder chapters. This is a substantial architecture course and practice resource; it is not a complete substitute for operating distributed systems or specialist study.

## Requested curriculum

| Requirement | Teaching source / destination | Evidence and scope |
|---|---|---|
| Sequenced prerequisites and paths | `content/start.json`, foundations 1–4 | Eight-week beginner, four-week builder and diagnostic principal paths; exit artifacts; Python/SQL prerequisites stated |
| Requirements, constraints, method | `requirements-method.html` | Invariant, risks, measurable goals, scope, time boxes, failure-first reasoning |
| Capacity with units | `capacity-estimates.html`, every case | Average/peak, logical/physical storage, bandwidth, skew, Little's law, backlog and sensitivity |
| One-machine and networking | `networking-api.html` | Process/thread/event-loop, pools, DNS/TLS/HTTP, deadline, durable acknowledgment and uncertain outcomes |
| Data/API contracts | `storage-transactions.html`, case schemas | Keys, constraints, indexes, query shape, cursor pagination, write amplification |
| Transactions/concurrency | storage, networking and LLD chapters; booking/payment cases | Lost update, write skew, confirm/expiry race, unknown external result; enforcement points |
| Caching | `caching.html`, shortener/feed | Cache-aside, stampede, cold start, version fence, authorization, bounded staleness |
| Replication/consistency/consensus | `replication-consensus.html` | Leader/follower, failover, linearizability vs serializability, quorum limits, Raft and CAP caveats |
| Partitioning | `partitioning.html`, feed/analytics | Ownership, hash/range, skew, hot keys, migration and cross-shard work |
| Messaging/streams | `messaging-streams.html`, scheduler/analytics | Outbox, replay, acknowledgments, duplicate effects, event-time/lateness, backpressure |
| Reliability/observability | `reliability-security.html`, cases | SLI/SLO, error budgets, tail latency, overload, recovery, restore vs replication |
| Security | reliability and all case boundaries | Resource/tenant authorization, untrusted upload inputs, cache/index privacy, webhook verification, retention |
| Regional evolution/cost | `regions-evolution-cost.html`, `multi-region-inventory.html` | RPO/RTO, fencing, regional partition, symbolic cost drivers, staged migration and rollback |
| HLD/LLD | start, `lld-python.html`, booking/rate/scheduler/payments | Architecture boundaries connected to atomic transitions and interfaces |
| Code/design exercises | `labs/design.py`, foundation disclosures | Executable reservation retry, token bucket and fenced-worker models; broader design exercises are prose tasks |
| Principal reasoning | `principal-decisions.html`, regional capstone | Ownership, risk prioritization, reversal cost, migration, evidence that changes a decision |
| Navigable practice and assessment | `practice.html`, all cases | Closed sample answers, failure probes, rubrics, independent study completion |
| Glossary definitions | `glossary.html`, inline definitions | Original technical definitions, plain-English meanings, analogies with stated limits and concrete examples; no-JS glossary plus mouse/touch/keyboard controls |
| Interview-platform interpretation | `practice.html` | Exact public LeetCode Discuss/Hello Interview/employer references; anecdotes and platform advice labeled; no frequency claims |

## Complete interview cases

Every case contains an exact original prompt, clarifying questions and assumed answers, measurable goals, worked capacity numbers, API/schema, labeled text diagram, end-to-end design, correctness/failure deep dives, alternatives, operations/cost/evolution, concealed practice, follow-ups and strong/weak rubric. Each includes a short candidate/interviewer exchange in addition to the teaching solution.

| Case | Primary decision | Deliberate boundary |
|---|---|---|
| Short links | Identifier uniqueness, read cache and revocation | Click analytics approximate; no production malware classifier implementation |
| Feed | Push/pull fanout, skew and visibility | Chronological baseline; relevance extension discussed |
| Chat | Durable send vs delivery/read | One-to-one baseline, not a complete E2E encryption protocol |
| Media | Resumable bytes and publication state | Scanning/transcoding isolation discussed, codecs not implemented |
| Search | Derived index, version ordering and rebuild | Relevance metrics discussed, no search engine implementation |
| Rate limiter | Atomic bucket and failure policy | Abuse protection vs durable entitlement explicitly separated |
| Job scheduler | Claim, lease, fencing and effects | External exactly-once promise requires receiver cooperation |
| Reservations/payments | Inventory invariant and ambiguous provider result | No provider integration or financial/legal compliance advice |
| Analytics | Event time, replay and provisional counts | Dashboard scope distinct from settlement correctness |
| Feature serving | Freshness, skew, eligibility and fallback | Elective serving architecture, not a model-training course |
| Appointment booking | Local correctness before distribution | Conditional transition, atomic two-slot extension |
| Regional inventory | Consistency/availability and tested recovery | RPO=0 scoped to declared failure model; minority refuses writes |

## Honest remaining gaps

- Browser surface was unavailable. Desktop/mobile rendering, real keyboard/screen-reader behavior and visual overflow have not been empirically checked. Responsive CSS and semantic structure are implemented and structurally checked.
- Labs are deterministic teaching models. They do not simulate real distributed consensus, network partitions, database failover or load. SQL reservation tests use an in-memory single connection and do not prove multi-process race freedom.
- Architecture exercises include full reasoned answers, but most are not executable end-to-end services. No benchmarks, cloud deployments or chaos experiments were run.
- Consensus proofs, storage-engine internals, operating-system scheduling, sophisticated search ranking, cryptographic protocols and production payment compliance require further specialist work. References provide starting points; the course makes no certification or interview guarantee.
- Technical sources were checked during authoring; link reachability is not a guarantee that future vendor behavior remains unchanged. No copyrighted paid courses or question banks were used.
