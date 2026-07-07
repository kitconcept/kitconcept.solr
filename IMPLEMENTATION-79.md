# AI Search (RAG) — Implementation Plan

Ticket: [#79](https://github.com/kitconcept/kitconcept.solr/issues/79)
Companion document: [SPECIFICATION-79.md](./SPECIFICATION-79.md)

The plan is organized in phases so that each phase ends in something
demonstrable and measurable. Phases 1–4 constitute the MVP; Phase 5 is the
quality pass that decides the remaining tuning questions with data.

Integration points reference the current codebase (2.0.0 alpha series).

## Phase 0 — Planning and decisions (this ticket)

- [x] Research: Solr vector/hybrid capabilities, chunking practice, RAG
      evaluation standards, demo corpus options (results folded into the
      specification).
- [x] Specification draft (SPECIFICATION-79.md).
- [ ] Review the specification with the team; close open questions **1**
      (chunk storage), **3** (embedding model / German) and **7** (demo
      corpus) — these block Phases 1–2.
- [ ] Confirm access to the kitconcept Ollama server (URL, credentials,
      available models) and that `nomic-embed-text`(-v2-moe) is served.

## Phase 1 — Retrieval foundation (backend)

Goal: a question typed into a REST call returns permission-trimmed, ranked
documents via vector search. No LLM answer yet. This is the riskiest layer,
so it goes first and gets measured first.

- [ ] **1.1 Ollama client module** (`backend/src/kitconcept/solr/llm/`):
      thin HTTP client for `POST /api/embed` (batched, `num_ctx: 8192`,
      task prefixes `search_document:` / `search_query:`) and
      `POST /api/chat` (Phase 3). Explicit timeouts; typed errors;
      no third-party LLM framework dependency.
- [ ] **1.2 Configuration plumbing**: registry records on
      `IKitconceptSolrSettings` (`backend/src/kitconcept/solr/interfaces.py`
      + `profiles/default/registry/`): `rag_enabled`, model names, `topK`,
      chunking parameters. Env vars for endpoint URL + token, wired through
      `docker-compose.yml` like `COLLECTIVE_SOLR_HOST`.
- [ ] **1.3 Chunking**: split extracted block text (reusing the traversal in
      `backend/src/kitconcept/solr/indexers/text.py`) into ~500-token
      structure-aware chunks with 10–15% overlap.
- [ ] **1.4 Index-time embedding**: hook after document assembly for
      `collective.solr` so each indexed object also writes its chunk
      documents (sibling docs with `parent_uid`, denormalized `Title`,
      `path`, `allowedRolesAndUsers`, `Language`) with `content_vector`
      populated. Schema updates in `solr/etc/conf/schema.xml` (chunk fields);
      delete/unindex removes chunks; embedding-endpoint failure logs and
      skips vectors without failing the save. Record model name in the
      index for reindex detection.
- [ ] **1.5 Full-reindex support**: make `solr-activate-and-reindex`
      populate vectors using batched `/api/embed` calls.
- [ ] **1.6 Retrieval service** `@rag-search` (retrieval part only, staged
      behind the toggle): embed query (`search_query:` prefix), run
      `{!knn f=content_vector topK=K}` with the same `fq` security/path/
      language filters as `SolrSearch` (`services/solr.py` —
      `security_filter()` composes as knn pre-filter), collapse chunk hits
      to parent documents, return ranked sources.
- [ ] **1.7 Tests**: unit tests for chunker and client (mocked HTTP);
      integration test against the docker-compose stack with a fake/pinned
      embedding server (deterministic vectors) so CI needs no GPU/model.
- [ ] **1.8 Dev stack**: add an `ollama` service (or a lightweight mock) to
      `docker-compose-dev.yml`; Makefile targets; document local setup.

Demo at end of phase: `curl` the endpoint, see sensible documents ranked for
a natural-language question on a local site.

## Phase 2 — Demo corpus, golden questions, retrieval evaluation

Goal: an objective measure of retrieval quality; also the demo site asset.
Can start in parallel with Phase 1 (only its evaluation step depends on 1).

- [ ] **2.1 Demo corpus**: generate the synthetic fictional-organization
      corpus (~50–150 docs, LLM-generated with agents, human-reviewed for
      internal consistency; language per open question 7). Import into a
      local site; export via `plone.exportimport` and ship as demo-site data
      in the product (per the kickoff: a kitconcept.solr example site,
      useful beyond this feature).
- [ ] **2.2 Golden question set**: 30–50 `question / expected sources /
      reference answer` triples in-repo (JSON/YAML). Bootstrapped with a
      generator + personas, manually culled; include CRAG-style variety and
      explicitly unanswerable questions.
- [ ] **2.3 Retrieval evaluation script** (`scripts/` or `backend/tools/`):
      run the golden set against `@rag-search` retrieval, report
      Recall@5/10, MRR, nDCG@10 (`ranx`). Makefile target; optional CI job.
- [ ] **2.4 Baseline run**: record baseline numbers; sanity-check against
      plain BM25 `@solr` results for the same questions (this comparison
      feeds open question 2, pure-vector vs hybrid).

Demo at end of phase: an evaluation report ("Recall@10 = X on N questions")
on a reproducible demo site.

## Phase 3 — Answer generation (backend)

Goal: `@rag-search` returns `{answer, sources}`.

- [ ] **3.1 Prompt template**: fixed instruction template (answer only from
      the provided context; match the question's language; say "no answer
      found in the documentation" when applicable; refer to sources).
      Stored server-side, overridable via registry.
- [ ] **3.2 Generation call**: send question + matched chunks (+ parent
      title/URL) to the general LLM; compose the response object; structured
      errors for timeout/unavailable/not-configured.
- [ ] **3.3 Model bake-off**: try the candidate models on the kitconcept
      Ollama server against the golden set; pick the MVP default (open
      question 5).
- [ ] **3.4 Tests**: service tests with a mocked generation endpoint
      (deterministic canned answers); error-path tests.

Demo at end of phase: full RAG loop over REST on the demo site.

## Phase 4 — Frontend (Volto modal UI)

Goal: the user-facing MVP in `@kitconcept/volto-solr`.

- [ ] **4.1 Short UX spec**: states (idle/loading/answer/error/disabled),
      keyboard behavior (⌘K open, Esc close), AI-disclaimer copy, relation
      to the existing search bar (open question 8). Wireframe level; review
      with the team before building.
- [ ] **4.2 Redux plumbing**: `actions/ragsearch/` + `reducers/ragsearch/`
      calling `@rag-search` (pattern: existing `actions/solrsearch/`).
- [ ] **4.3 Modal component**: command-palette modal
      (`components/theme/`…): input, loading state, answer panel with
      disclaimer, source list reusing the existing result-item rendering
      from `SolrSearch`; graceful fallback link to classic search on error;
      hidden entirely when the backend reports not-configured.
- [ ] **4.4 Tests**: Jest component tests; one Cypress acceptance flow
      against a mocked backend answer.
- [ ] **4.5 i18n** for all new strings (existing i18n setup).

Demo at end of phase: ⌘K on the demo site → ask → answer + sources. **This
is the MVP.**

## Phase 5 — Quality pass and evaluation tier 2

Goal: decide the data-driven open questions; make quality trustworthy.

- [ ] **5.1 Answer evaluation (RAGAS)**: faithfulness + answer relevancy on
      the golden set, judge LLM on the same Ollama server; one-time human
      calibration of the judge on a labeled sample.
- [ ] **5.2 Hybrid retrieval, if the numbers demand it**: client-side RRF
      (BM25 + knn, k=60) inside `@rag-search`; re-run the Phase 2 report to
      confirm the gain. Designed to be swapped for Solr's native RRF
      combiner when 9.11/10.1 ships.
- [ ] **5.3 Tuning knobs pass**: `topK`, chunk size/overlap, prompt wording
      — one iteration guided by the metrics, not more (MVP discipline).
- [ ] **5.4 Acceptance thresholds**: fix the release criteria (proposal in
      spec §7) with the measured baseline; wire the retrieval evaluation
      into CI as a regression gate.

## Phase 6 — Post-MVP roadmap (tracked, not scheduled)

- Community LLM-connector add-on integration (requires upstream support for
  the kitconcept Ollama server) → any-provider support.
- Control-panel UI for kitconcept.solr configuration incl. AI credentials.
- Multi-turn conversation; streaming answers; query rewriting; re-ranking;
  attachments in the modal; model benchmarking across providers.
- Multilingual optimization (per-language analyzers already exist for
  keyword search; embedding side per open question 3).

## Risks and mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Pure-vector retrieval quality insufficient on real corpora | wrong sources → wrong answers | Phase 2 measures it early; hybrid RRF is a bounded, planned fallback (5.2) |
| Ollama server latency/availability | slow saves, hanging searches | strict timeouts everywhere; indexing never fails on embedding errors; frontend error state falls back to classic search |
| Long-document embedding truncation (`num_ctx` default 2048) | silently bad vectors | chunking keeps inputs ~500 tokens; client always sets `num_ctx`; test asserts prefix+ctx behavior |
| Embedding model change invalidates index | broken search after model swap | model name recorded at index time; mismatch triggers/reports reindex need |
| LLM hallucinates sources or answers beyond context | trust damage | prompt constraints; unanswerable questions in golden set; faithfulness metric in 5.1; UI disclaimer |
| CI cannot run models | untestable feature | all CI tests run against mocked/deterministic endpoints; model-dependent evaluation is a separate opt-in job |
| Editing latency from synchronous embedding | editor complaints | short timeout + skip-on-failure; batched full reindex; async queue is the documented plan B |

## Suggested working order (tight MVP path)

Decisions 1/3/7 → 1.1–1.2 → 1.3–1.4 → 1.6 → 2.1–2.4 (overlapping) → 3.1–3.2
→ 4.1–4.3 → 5.1/5.4, with 1.7/3.4/4.4 tests accompanying their phases. Each
phase lands as one or more reviewed PRs referencing #79; towncrier news
fragments per PR as usual.
