# AI Search (RAG) — Implementation Plan

Ticket: [#79](https://github.com/kitconcept/kitconcept.solr/issues/79)
Companion document: [SPECIFICATION-79.md](./SPECIFICATION-79.md)
Status: **approved plan** (team review 2026-07-09). Work is tracked in the
internal tracker (epic holds the itemized plan; step numbers below map to
individual tracker tickets). Work starts **after the 2.0 release**, which
proceeds in parallel.

The MVP path is **7.5 dev days** across three steps, followed by post-MVP
follow-ups. A **checkpoint after 5 dev days** re-evaluates the estimate and
updates the schedule if necessary.

## Step 0 — Planning (done)

- [x] Research: Solr vector/hybrid capabilities, chunking practice, RAG
      evaluation standards, demo corpus options.
- [x] Specification, team review, decisions (recorded in
      SPECIFICATION-79.md §8).
- [ ] Kick-off prerequisites:
      - access to the kitconcept LLM server (action item);
      - clarify the two kinds of chunking (input from Victor) — pick the MVP
        kind, keep the design compatible with the second;
      - 2.0 released, or a feature branch policy agreed.

## Step 1 — Foundations + Indexing (4.5d)

Goal: content gets chunked, embedded and indexed; the vector infrastructure
is live. This is the riskiest layer, so it goes first.

**Foundations (1.5d):**

- [x] **1.1 LLM client module** (`backend/src/kitconcept/solr/llm/`):
      thin HTTP client for `POST /api/embed` (batched, `num_ctx` set,
      task prefixes `search_document:` / `search_query:`, truncation
      detection) and `POST /api/chat` (used in Step 3). Explicit timeouts;
      typed errors; no third-party LLM framework dependency.
- [x] **1.2 Minimal configuration**: the "AI search" toggle as a registry
      record on `IKitconceptSolrSettings`
      (`backend/src/kitconcept/solr/interfaces.py` +
      `profiles/default/registry/`); endpoint URL + token as env vars wired
      through `docker-compose.yml` (pattern: `COLLECTIVE_SOLR_HOST`). Model
      names, topK, chunk parameters, prompt template: code defaults.
- [x] **1.3 Schema additions** for chunk sibling documents in
      `solr/etc/conf/schema.xml` (chunk fields: `parent_uid`, denormalized
      `Title`, `path`, `allowedRolesAndUsers`, `Language`;
      `content_vector` populated on chunks).

**Indexing (3d):**

- [x] **1.4 Chunking**: split extracted block text (reusing the traversal in
      `backend/src/kitconcept/solr/indexers/text.py`) into ~400-token
      structure-aware chunks with 10–15% overlap, merging tiny fragments.
      One kind of chunking (per the kick-off clarification); design kept
      compatible with the second kind.
- [x] **1.5 Index-time embedding**: hook after document assembly for
      `collective.solr` so each indexed object also writes its chunk
      documents with vectors — synchronous, short timeout,
      **skip-on-failure** (a save must never fail on embedding errors).
      Delete/unindex removes chunks. Record the embedding model name for
      reindex detection.
- [x] **1.6 Full-reindex support**: `solr-activate-and-reindex` populates
      vectors using batched `/api/embed` calls.
- [x] Minimal inline test coverage with the PRs (repo CI standards); the
      full test pass is post-MVP (Step P1).

Demo at end of step: indexed site content visible in Solr with chunk
documents and populated vectors.

### Implementation notes — Step 1 (design decisions made on the way)

- **Hook: own indexing queue processor, not `ISolrAddHandler` adders.**
  collective.solr queries its add handlers as *named* adapters by
  portal type, so a single adapter cannot intercept all types. Instead,
  `RagIndexProcessor` is registered as an `IIndexQueueProcessor`
  utility (`componentregistry.xml`) — Plone's indexing queue dispatches
  to every such utility, next to collective.solr's own processor, and
  the RAG processor shares the same Solr connection. The module path
  became `kitconcept/solr/rag/` (not `llm/` as sketched above): it
  holds config, client, chunker, extraction, processor and reindex.
- **Chunks are invisible to keyword search by construction.**
  `chunk_text`/`parent_title` are stored-only (not indexed); chunks
  carry none of the fields the `@solr` main query matches on. A
  defensive `-is_rag_chunk:true` filter query was added to `@solr`
  anyway.
- **Chunk lifecycle**: chunk UIDs are `<parent UID>#rag-<n>`; a text
  rebuild is delete-by-query + re-add (the chunk count may shrink).
  A `MAX_CHUNKS_PER_DOCUMENT = 100` safety cap guards against
  pathological documents (~40k tokens covered per document).
- **Workflow transitions don't re-embed.** An attribute-limited
  reindex that touches only metadata (`allowedRolesAndUsers`,
  `Language`, path) updates the denormalized chunk fields in place via
  Solr atomic updates; only text-affecting attributes trigger
  re-chunking/re-embedding.
- **Failure policy**: embedding errors log a warning and *keep* the
  previously indexed chunks (slightly stale beats absent); the content
  save itself never fails. Chunk cleanup on delete is gated on the
  registry toggle only, so it works while the endpoint is unconfigured.
- **Token sizing is heuristic** (4 chars/token, no tokenizer
  dependency): chunk target 1600 chars ≈ 400 tokens under the model's
  512-token limit; the client warns when an input still estimates over
  the limit.
- **Full reindex needs its own pass**: collective.solr's
  `@@solr-maintenance` talks to Solr directly and bypasses queue
  processors, so `reindex_helpers.reindex` now calls `reindex_rag`
  afterwards (no-op when the feature is off).
- **MVP text coverage**: title + description + Volto blocks. Binary
  content (File/Image) is extracted by Tika *inside* Solr — the text
  never passes through Plone, so it cannot be chunked/embedded here.
  Post-MVP follow-up.
- **Env overrides** `KITCONCEPT_SOLR_LLM_EMBED_MODEL`/`_CHAT_MODEL`
  exist besides the code defaults, to ease testing against different
  servers.
- **Verified end to end against real Solr + the kitconcept LLM server**
  (`tests/rag/test_e2e_live.py`, runs only when the LLM env vars are
  set): indexing a document creates chunk documents with real vectors
  through collective.solr's XML `update="set"` path; a `{!knn}` query
  with the embedded question retrieves the right chunk; deletion
  removes the chunks. Note: knn queries must be POSTed to Solr — the
  768-float vector exceeds GET URL limits.
- **kitconcept Genie (Open WebUI) endpoint constraints**: the server's
  API key allowlist permits exactly `/ollama/api/embed` and
  `/api/chat/completions`, so the client uses those as path defaults
  (env-overridable for plain Ollama), chat speaks the OpenAI format,
  and the embed model name needs its explicit `:latest` tag.

## Step 2 — Test corpus (0.5d)

Goal: content and questions to validate Step 3 against. Lands before or
together with Step 3.

- [x] **2.1 Corpus**: German-first (decision revised 2026-07-11, see spec
      §7/§8): curated export of the fictional `plone-intranet.kitconcept.io`
      demo site, shipped as a plone.exportimport dump in
      `backend/src/kitconcept/solr/setuphandlers/examplecontent`
      (409 objects, 80 images, 7 example users — see its README).
- [ ] **2.2 Questions**: ~20 hand-written German questions with expected
      source documents, stored alongside the corpus; includes questions
      whose answer is *not* in the corpus (the system should decline).

Post-MVP: the same export/import dump also drives this repository's CI
tests (see Step P2 overflow list).

### Implementation notes — Step 2 (corpus build, 2026-07-14)

How the dump was produced (pipeline preserved in
`~/work/kitconcept/solr/intranet-corpus-source/`: raw restapi crawl,
transform script, and the pre-import tree):

1. Crawled the live demo site over plone.restapi (`@search?fullobjects=1`;
   the site has no exportimport views installed), including folder
   orderings, `@users`, `@groups` and `@sharing`.
2. Transformed the crawl into plone.exportimport format with the curation
   listed in the corpus README (drops, ~1200px image scales instead of
   originals — 228 MB → 19 MB, language normalized to `de`,
   relation fields removed, comments out of scope).
3. Imported into a fresh local site created with `SITE_DEFAULT_LANGUAGE=de`
   via a one-off wrapper that skipped portal types not installed on the
   target site (17 Person, 5 Organisational Unit, 3 Location from the
   intranet distribution).
4. Re-exported with the official `plone-exporter` — that round-tripped
   dump is what ships (canonical field serializations, workflow history,
   hashed user passwords).

Importer decision — two tiers:

- **Daily workflow: the stock `plone-importer`** of plone.exportimport
  (`make import-example-content`) — the shipped dump contains only
  standard types, so no custom import code is needed. Caveat: the stock
  importer **crashes on content whose portal type is not installed**
  (aborts on the first unknown type instead of skipping).
- **One-time operations: `scripts/import_content_robust.py`**
  (`make import-content-robust IMPORT_CONTENT_FOLDER=<path>`) — the
  skip-unknown-types wrapper used during the corpus build (step 3
  above), kept for dumps that contain uninstalled types, e.g.
  re-importing the original intranet source tree. Long-term, this
  behavior is a candidate for an upstream plone.exportimport
  contribution (skip-and-report option).

Verified end to end: German site renders in Volto, RAG reindex embeds
489 chunks for 409 objects, German questions get grounded German answers
with correct sources, and permission trimming holds (private Betriebsrat
page appears in admin's sources, not in plain-member `f.meier`'s).

Corpus v2 (2026-07-22, after Balazs's manual review found rendering
problems): the crawl-form data broke the demo look on a plain Volto
frontend — three causes, all fixed in the transform (now
`transform_corpus.py [solr|intranet]` beside the preserved source):

1. Block data carried the source site's absolute URLs and embedded
   `image_scales` with foreign scale hashes → broken in-page images.
   Fixed by converting content links in blocks to `resolveuid` form and
   stripping embedded `image_scales`; plone.restapi then injects fresh
   scales at serve time.
2. `preview_image_link`/`relatedItems` had been dropped → missing
   listing/teaser preview images. Restored through `relations.json`
   (the relations importer runs after content, so targets resolve; the
   site's IIntIds utility works — the earlier crash was a commit
   OUTSIDE the site context, fixed in `import_content_robust.py`).
3. volto-light-theme / kitconcept blocks rendered as "Unknown Block".
   The `solr` variant maps them to core blocks (`introduction` → slate,
   `__button` → slate link, `highlight`/`banner` → image + slate
   heading, `slider` → gridBlock of teasers; decorative
   `separator`/`eventMetadata`/`eventCalendar` dropped). The `intranet`
   variant keeps native blocks for the later kitconcept.intranet demo
   site — decision: two regenerable dumps rather than one compromise
   dump.

Known limitations (acceptable for the MVP corpus):

- The intranet-only types (Persons — the `/kontakte` contacts, the five
  institute Organisational Units, Locations) are not in the dump; the
  full pre-import tree that still contains them is preserved with the
  pipeline (see above) for the eventual intranet-distribution demo site.
- The live site had no explicit local-role grants and no custom groups
  (verified via `@sharing`/`@groups`), so permission tests rest on the
  three `private`-state documents.
- Site-root `logo`/`footer_logo` are intranet-distribution fields and are
  not part of the dump.

## Step 3 — Query pipeline: retrieval endpoint + answer generation (2.5d)

Goal: `@rag-search` returns `{answer, sources}` end to end.

**Retrieval endpoint (1d):**

- [x] **3.1** New restapi service `@rag-search`
      (`backend/src/kitconcept/solr/services/`, staged behind the toggle):
      embed query (`search_query:` prefix), run
      `{!knn f=content_vector topK=K}` with the same `fq` security/path/
      language filters as `SolrSearch` (`services/solr.py` —
      `security_filter()` composes as knn pre-filter), collapse chunk hits
      to parent documents, return ranked sources.

**Answer generation (1.5d):**

- [x] **3.2 Prompt template**: fixed instruction template (answer only from
      the provided context; answer in the question's language; decline
      explicitly when no answer is found; refer to sources). Code default;
      registry override is post-MVP.
- [x] **3.3 Generation call**: send question + matched chunks (+ parent
      title/URL) to `qwen3:14b`; compose the `{answer, sources}` response;
      structured errors for timeout/unavailable/not-configured.
- [x] Validate against the Step 2 questions (smoke level: right documents
      found, declines when it should). Note: Step 2 (the proper corpus,
      internal ticket 459) was deferred by decision - validation ran
      against a minimal hand-made corpus; re-run once the corpus lands.

Demo at end of step: full RAG loop over REST on the demo corpus. **This is
the MVP backend.** The user-facing MVP completes when the search UI from the
kitconcept.intranet modal project integrates this endpoint (outside this
repository's estimates).

### Implementation notes — Step 3 (design decisions made on the way)

- **Pipeline extracted from the HTTP layer**: the logic lives in
  `rag/pipeline.py` (`run_rag_search`) with the prompt in
  `rag/prompt.py`; the restapi service is a thin wrapper. This keeps
  the pipeline testable with faked Solr/LLM and reusable by a future
  evaluation harness.
- **Structured errors with codes**: the response carries `error`
  (human readable) plus `error_code` (`not_configured`,
  `embedding_failed`, `generation_failed`, `solr_unavailable`) so the
  frontend can degrade to the classic search. A generation failure
  still returns the retrieved sources. Empty retrieval is NOT an
  error: `answer: null, sources: []`.
- **Sources are enriched parent documents**: one extra Solr query
  fetches parent metadata (`Title`, `Description`, `Type`); each
  source carries the best-ranked chunk's text as `snippet`. `@type`
  is Solr's friendly type name (e.g. "Page"), consistent with the
  classic search results.
- **Optional filters**: `path_prefix` and `lang` request parameters
  compose as additional pre-filter queries next to the security
  filter.
- **Model bake-off** (`qwen3:14b` vs alternatives) stays in the
  overflow list per the re-scoping; the model remains fixed.
- Observation from live testing on the minimal corpus: with only a
  handful of documents, `topK=5` spans the whole corpus, so weakly
  related sources appear below the top hit. On a realistic corpus a
  score threshold (`{!vectorSimilarity}` / `minReturn`) or a smaller
  source cutoff is worth evaluating - noted for the quality pass.

## Known issues (accepted for the MVP)

1. **The Solr tests and a local dev site share the Solr core.** The
   test compose project uses the fixed host port 8983 — the same port
   a dev Solr uses — and the test fixtures clear/recreate the index
   (`down -v` at session start, `maintenance.clear()` in the portal
   fixtures; the RAG live e2e tests behave exactly like the
   pre-existing service tests here). Consequences and workarounds:
   (a) stop the site's Solr before running the tests so the situation
   does not arise, or (b) if it has happened, no harm is done — simply
   reindex with `make solr-activate-and-reindex` before using the
   site again. A real fix (ephemeral host ports for the test project,
   wired into the test layer's `collective.solr.port`) is a **post-MVP
   improvement**, tracked in the overflow list.
2. **Weak sources on small corpora (topK semantics).** `{!knn topK=5}`
   returns the 5 *nearest* chunks unconditionally, so on a small
   corpus weakly related documents appear in the source list (answer
   quality is unaffected — the grounding prompt handles weak context;
   verified by the decline behavior). Accepted for now; **re-check
   with the real corpus** (internal ticket 459) and evaluate a
   similarity cutoff for displayed sources in the quality pass.

## Post-MVP follow-ups

**Step P1 — Hybrid RRF + tests (2d), first follow-up:**

- [ ] **P1.1 Hybrid retrieval (1d)**: BM25 (reusing the existing
      `SolrSearch` query building) + knn as two Solr requests, client-side
      Reciprocal Rank Fusion (k=60) in `@rag-search`; designed to be swapped
      for Solr's native RRF combiner when 9.11/10.1 ships. Hybrid was
      originally MVP scope (empirical signal that pure vector is not enough
      on intranet content); the pure-knn MVP results should confirm the
      deferral was acceptable — if not, this item moves up.
- [ ] **P1.2 Test pass (1d)**: unit tests (chunker, LLM client mocked) + one
      integration test against the docker-compose stack with deterministic
      mock endpoints (CI needs no GPU/model).

**Step P2 — Overflow tasks** (first candidates after that, or if time
remains):

| Work item | Est. |
| --- | --- |
| ~~Adapt chunking to the second kind~~ (done 2026-07-14: Plate block storage, per-block detection, unit-tested) | 1d |
| Shared export/import dump: same corpus drives the kitconcept.intranet demo site and this repository's CI tests | 0.5d |
| Generation model comparison (`qwen3:14b` vs `qwen3.5:9b-q8_0` vs others) on the test questions | 0.5d |
| Full configuration surface: registry records for model names, topK, chunk size, prompt override | 0.5d |
| Acceptance test flow + full CI wiring (after the search-UI integration, so acceptance tests target the real UI) | 1d |
| Separate Solr core/ports for tests vs. local dev site (see known issue 1) | 0.5d |

**Later roadmap** (tracked, not scheduled): full evaluation harness
(Recall@k/MRR/nDCG as CI regression gate, RAGAS faithfulness/relevancy with
calibrated judge — client-funded), admin configuration UI, community
LLM-connector add-on integration, multi-turn conversation, streaming
answers, query rewriting/re-ranking, German content rollout.

## Risks and mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Pure-vector retrieval quality insufficient (hybrid deferred) | wrong sources → wrong answers | Step 2 questions surface it immediately; hybrid RRF (P1.1) is a bounded, planned add-on and moves up if needed |
| LLM server latency/availability | slow saves, hanging searches | strict timeouts everywhere; indexing never fails on embedding errors; endpoint returns structured errors for graceful UI fallback |
| 512-token sequence limit of the embedding model | silently truncated, bad vectors | ~400-token chunks; client sets `num_ctx` and detects/logs truncation |
| Embedding model change invalidates index | broken search after model swap | model name recorded at index time; mismatch triggers/reports reindex need |
| LLM hallucinates sources or answers beyond context | trust damage | prompt constraints; decline-when-unanswerable tested by Step 2 questions; UI disclaimer |
| CI cannot run models | untestable feature | all CI tests run against mocked/deterministic endpoints; model-dependent checks are opt-in |
| Editing latency from synchronous embedding | editor complaints | short timeout + skip-on-failure; batched full reindex; async queue is the documented plan B |
| No stabilization buffer in the estimates | overruns land directly on the schedule | checkpoint after 5 dev days: re-evaluate the estimate, update the schedule if necessary |

## Working order

Kick-off prerequisites → Step 1 (foundations, then indexing) → Step 2
(overlapping) → Step 3 → checkpoint bookkeeping → P1 when scheduled. Each
step lands as one or more reviewed PRs referencing #79; towncrier news
fragments per PR as usual.
