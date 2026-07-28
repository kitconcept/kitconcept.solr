# AI Search (RAG) — Specification

Ticket: [#79](https://github.com/kitconcept/kitconcept.solr/issues/79)
Status: **decisions final** (team review 2026-07-09); implementation planned per
[IMPLEMENTATION-79.md](./IMPLEMENTATION-79.md)

## 1. Goals

Enhance `kitconcept.solr` with an AI-powered search feature based on **RAG
(Retrieval-Augmented Generation)**, targeted at sites with large amounts of
long-form documentation (the primary driver is the kitconcept intranet
distribution, where users need to quickly find answers inside abundant
organizational documentation and fact-check them against the source pages).

The user-facing goal, as a user story:

> As a user, I can ask a question in natural language. I get a natural-language
> answer to my question, together with the list of documents within the site
> that the answer is based on.

Design goals derived from that:

- **Trustable answers.** The answer is always accompanied by its source
  documents, so it can be fact-checked. The retrieval layer respects the
  existing permission model — a user can never get an answer derived from
  content they are not allowed to see.
- **Part of the product, off by default.** The feature ships inside
  `kitconcept.solr` (backend) and `@kitconcept/volto-solr` (frontend), not as a
  separate plugin. It activates only when an LLM endpoint is configured and the
  toggle is on; sites that do not configure it are unaffected.
- **Measurable quality.** The MVP ships with a small golden question set as
  smoke-level checks; the full evaluation harness is a post-MVP work item
  (see §7).

## 2. MVP scope

The MVP is the smallest version that actually works end to end. This is a
POC-grade scope: quality tooling and tuning are deliberately deferred.

1. **Single-turn.** One question → one answer + source list. No conversation
   memory, no follow-up questions. A new question is a new query.
2. The response contains exactly two things beyond a normal search response:
   the **summary answer** and the **source documents** (which are ordinary
   Solr results).
3. **One model provider, fixed models.** The MVP connects to the kitconcept
   LLM server (Ollama-compatible) using two models, both fixed:
   - embedding: **`nomic-embed-text-v2-moe`** (multilingual — chosen from the
     start so switching or mixing content languages never requires a full
     reindex; its 512-token sequence limit makes
     chunking mandatory and sets the chunk target to ~400 tokens);
   - generation: **`qwen3:14b`** (model comparison is a post-MVP task).
4. **Minimal configuration, no UI.** An **"AI search" toggle** plus the
   endpoint URL/token via environment variables; model names and tuning
   parameters are code defaults. The full configuration surface (registry
   records for models, topK, chunk size, prompt override) is post-MVP. See §5.
5. **One kind of chunking.** Two kinds of chunking have been identified for
   the intranet use case; the MVP implements one, with the design kept
   compatible with the second (post-MVP). See §8, open point 1.
6. **No new search UI in this repository for the MVP.** The search modal UX
   is developed separately in the kitconcept.intranet project; the RAG
   backend is developed and tested over REST (with a throwaway input box at
   most), and the finalized UX is integrated before the MVP ships. The
   "AI search" toggle means RAG does not unconditionally replace the normal
   search. See §6.
7. **Test corpus + smoke checks.** A German demo corpus with ~20
   hand-written questions with expected sources (see §7; German-first
   decided 2026-07-11, English later).

### Explicitly out of scope for the MVP (post-MVP roadmap)

- **Hybrid retrieval (BM25 + vector, RRF)** — deferred from the MVP by the
  re-scoping decision; it is the *first* post-MVP work item, and the query
  layer is factored so it is a bounded add-on. The pure-knn MVP results
  should confirm the deferral is acceptable (earlier experiments suggested
  pure vector search may not be sufficient — see §3).
- Full test pass (beyond minimal inline coverage accompanying the MVP PRs)
  and acceptance/CI wiring — acceptance tests are deferred until the real
  search UI is integrated, so they target that UI rather than a throwaway
  input box.
- Full evaluation harness (Recall@k/MRR, nDCG, RAGAS faithfulness/relevancy)
  — to be funded by client projects.
- Generation model comparison (`qwen3:14b` vs `qwen3.5:9b-q8_0` vs others).
- Full configuration surface (registry records) and an admin/control-panel
  UI for AI configuration.
- Multi-turn chat / conversation context; streaming answers.
- Integration with the community LLM-connector add-on. Long-term we commit
  to using it (it gives us any-provider support); it first needs support for
  the kitconcept Ollama setup. For the MVP we connect directly.
- Wiring the demo corpus dump into this repository's CI tests.
- English content rollout (German-first since 2026-07-11; the architecture
  is language-agnostic via the multilingual embedding model).

## 3. Architecture overview

```
                       ┌──────────────────────────────────────────┐
                       │                Volto (React)             │
                       │   search UI (external project) → question│
                       └───────────────┬──────────────────────────┘
                                       │ GET/POST @rag-search?q=...
                       ┌───────────────▼──────────────────────────┐
                       │        Plone / kitconcept.solr           │
                       │  1. embed(question)  ──────────────────────────┐
                       │  2. Solr retrieval ({!knn})              │      │
                       │  3. build prompt(question, top chunks)   │      │
                       │  4. LLM completion  ───────────────────────────┤
                       │  5. return {answer, sources[]}           │      │
                       └───────────────┬──────────────────────────┘      │
                                       │ {!knn f=content_vector}         │
                       ┌───────────────▼─────────────┐   ┌───────────────▼──────────────┐
                       │        Solr 9.10            │   │  kitconcept LLM server       │
                       │  content_vector (768, HNSW) │   │  /api/embed                  │
                       │  chunk sibling documents    │   │    nomic-embed-text-v2-moe   │
                       │  existing keyword fields    │   │  /api/chat   qwen3:14b       │
                       └─────────────────────────────┘   └──────────────────────────────┘
```

Two distinct LLM endpoints are involved (same server):

- **Embedding endpoint** — used at *indexing time* (vectorize content chunks)
  and at *query time* (vectorize the user's question). Ollama
  `POST /api/embed`, which batches inputs and returns L2-normalized vectors.
- **Generation endpoint** — used at *query time only*: receives one prompt
  containing (a) the user's question, (b) the retrieved chunk texts (with
  parent title/URL), and (c) fixed instructions ("answer the question based
  only on these documents, cite which documents you used"), and returns the
  summary answer.

### Existing groundwork

The Solr schema (since 2.0.0a14) already defines the vector field — currently
unpopulated and unqueried:

- `solr/etc/conf/schema.xml`: field type `knn_vector_768`
  (`solr.DenseVectorField`, `vectorDimension="768"`,
  `similarityFunction="dot_product"`) and field `content_vector`.
- `nomic-embed-text-v2-moe` produces 768-dim vectors; `/api/embed` returns
  them normalized, so `dot_product` is equivalent to cosine similarity here.
  **Decision: keep `dot_product`, no schema change.**

### Retrieval design

- Query-time vector search uses Solr's `{!knn f=content_vector topK=K}` query
  parser (available since Solr 9.0; we ship 9.10).
- **Security filtering keeps working**: when the knn query is the main query,
  Solr applies `fq` filters as HNSW *pre-filters* — the existing
  `allowedRolesAndUsers` trimming, path and language filters compose correctly
  with vector search.
- **Hybrid search** (BM25 + vector, fused with Reciprocal Rank Fusion) is the
  industry-standard remedy for pure-vector weaknesses (exact names, codes,
  jargon; BEIR shows dense retrieval underperforms BM25 out-of-domain), and
  earlier hands-on experiments on intranet content pointed the same way.
  It is nevertheless **deferred to post-MVP** by the re-scoping decision.
  Native RRF lands in Solr 9.11/10.1 ([SOLR-17319]) which is **not released
  yet**, so the post-MVP implementation fuses client-side (two Solr requests,
  `score = Σ 1/(60 + rank)`), drop-in replaceable by the native combiner
  later. The MVP query layer is factored so this is a bounded add-on.

[SOLR-17319]: https://issues.apache.org/jira/browse/SOLR-17319

### Indexing design

- Embeddings are computed **on the Plone side** (client of the LLM server),
  not via Solr's built-in LLM module: the module doesn't support Ollama as a
  provider and cannot add the task prefixes the nomic models require
  (`search_document: …` for content, `search_query: …` for questions —
  skipping them measurably degrades retrieval).
- **Chunking**: embedding a whole long document produces a "blurry" vector,
  and `nomic-embed-text-v2-moe`'s 512-token sequence limit makes chunking
  mandatory. Structure-aware chunking: split on headings/blocks at roughly
  **400 tokens per chunk with 10–15% overlap**, merging tiny fragments.
  Volto blocks give us structural boundaries for free (the existing
  block-text indexer already walks them). The embedding client must detect
  and log truncation rather than silently accept it.
- **Chunk storage (decided)**: chunks as **sibling documents** in Solr
  (`parent_uid` + denormalized title/path/security fields), grouped back to
  parent documents at query time (parent-document retrieval: match a chunk,
  show the parent as the source). Nested/block-join documents were rejected:
  atomic block reindexing conflicts with Plone's per-object indexing, and
  knn-through-block-join is Solr 10.x-only.
- **Index-time embedding is synchronous (decided)** with a short timeout;
  embedding failure must never fail the content save (log + skip vectors).
  An async queue is the documented plan B if editing latency hurts.

## 4. Functional specification

### New REST endpoint: `@rag-search`

- Registered like the existing `@solr` service
  (`backend/src/kitconcept/solr/services/`).
- Request: the question string, plus optional standard search parameters
  (`path_prefix`, `lang`) reused from `@solr`.
- Behavior: embed question → retrieve top-K chunks (security trimmed) →
  collapse to parent documents → prompt LLM with the matched chunks →
  respond.
- Response (shape, subject to refinement in implementation):

```json
{
  "answer": "Employees are entitled to at least 30 days of leave…",
  "sources": [ { "@id": "...", "title": "...", "description": "...", "snippet": "..." } ],
  "error": null
}
```

- Errors (LLM endpoint down, timeout, not configured) return a structured
  error so the frontend can degrade gracefully to normal search.
- If the feature is not configured/enabled, the endpoint returns a structured
  `not configured` response and the frontend never offers the AI mode.
- The prompt instructs the model to answer only from the provided context,
  answer in the language of the question, and decline explicitly when the
  answer is not found in the documentation.
- Timeouts are mandatory on both LLM calls; the endpoint must never hang a
  Plone thread indefinitely.

### Indexing behavior

- On indexing/reindexing a content object, its extracted text (the existing
  `SearchableText`/block text path) is chunked and embedded, and the chunks
  are written to Solr alongside the document.
- On delete/unindex, chunks are removed with the parent.
- A full-reindex path exists (`solr-activate-and-reindex`) and must populate
  vectors using batched `/api/embed` calls; the embedding model name is
  recorded so a model change forces a reindex.
- If the embedding endpoint is unavailable at indexing time, indexing of the
  document must still succeed (log + skip vectors) — search availability must
  not depend on the AI stack.

## 5. Configuration

MVP configuration is deliberately minimal:

- **"AI search" toggle** (Plone registry, `IKitconceptSolrSettings` in
  `backend/src/kitconcept/solr/interfaces.py` + GenericSetup profile) — per
  the epic requirement: "as Admin I can turn it on or off".
- **Endpoint URL + token via environment variables** (e.g.
  `KITCONCEPT_SOLR_LLM_URL`, `KITCONCEPT_SOLR_LLM_TOKEN`), following the
  existing `COLLECTIVE_SOLR_HOST`/`COLLECTIVE_SOLR_BASE` pattern in
  `docker-compose.yml`. Credentials must not live in the registry (they end
  up in exported site configuration).
- **Everything else is a code default**: model names
  (`nomic-embed-text-v2-moe`, `qwen3:14b`), topK, chunk size/overlap, prompt
  template.

Post-MVP: registry records for model names, topK, chunk size and prompt
override; longer-term an admin UI. The feature counts as **enabled** when the
toggle is on and the endpoint variables are present.

## 6. Search UI

**The search UX is not part of this repository's MVP scope.** The search
modal (command-palette pattern) is being designed and implemented separately
in the kitconcept.intranet project; the RAG feature integrates into it before
the MVP ships. Decisions that affect this repository:

- ~~There will be an **"AI search" toggle in the search UI**~~ **Revised
  (team discussion, 2026-07-23): no user-facing AI toggle.** The
  presentation follows the Google pattern instead: an **"AI" tab** shows
  the AI result alone, and the **"All" tab** shows the AI answer on top
  of the classic results. Planned as kitconcept.solr **tabs
  configuration**: two per-tab flags — "AI results" (the tab shows only
  the AI answer) and "AI on top" (the tab prepends the AI answer to its
  result list) — so any consumer (including kitconcept.intranet)
  composes the presentation freely. To be finalized and implemented
  after the UX has been seen live in kitconcept.intranet; until then the
  interim UI always shows the AI answer above the classic results.
  Unchanged: RAG does not replace the normal search; the classic `@solr`
  search remains fully functional.
- During backend development, testing happens over REST (optionally a
  throwaway input box); no acceptance tests are written against interim UI.
- The answer panel must carry a visible "AI-generated — verify against the
  sources" hint; error states fall back to the classic search.

## 7. Test corpus and quality checks

MVP-level (this is a POC — minimal by decision):

- **Corpus**: **German-first** (revised 2026-07-11, Timo — supersedes the
  earlier translate-to-English plan): a curated export of the fictional
  German intranet demo site `plone-intranet.kitconcept.io`, kept in German
  with no translation. Research confirmed no suitable open intranet-shaped
  corpus with ready-made questions exists (public QA datasets are
  Wikipedia/web-shaped; open handbooks have no questions), so an in-house
  corpus plus hand-written questions is the pragmatic and correct choice.
  The corpus ships in this repository as a plone.exportimport dump
  (`backend/src/kitconcept/solr/setuphandlers/examplecontent`, see its
  README for curation and usage); the English corpus comes later with
  expected-similar results (the embedding model is multilingual).
- **Questions**: ~20 hand-written German questions with expected source
  documents, stored alongside the corpus; used as smoke tests ("are the
  right documents found? does the answer decline when it should?").
- The demo site lives in the kitconcept.intranet project; making the same
  export/import dump also drive this repository's CI tests is post-MVP.

Post-MVP (client-funded): the full evaluation harness — golden set grown to
100+ questions (CRAG-style type coverage incl. unanswerable), retrieval
metrics (Recall@5/10, MRR, nDCG@10 via `ranx`/`pytrec_eval`) as a CI
regression gate, RAGAS faithfulness/answer-relevancy with a calibrated LLM
judge, and model comparisons.

## 8. Decisions record and open points

All major open questions from the draft phase have been decided (team review
2026-07-09):

| # | Question | Decision |
| --- | --- | --- |
| 1 | Chunk storage model in Solr | Sibling documents with `parent_uid` + denormalized security fields; parent-collapse at query time |
| 2 | Pure vector vs. hybrid in the MVP | **Hybrid deferred to post-MVP** (first follow-up item); MVP is pure knn, factored so RRF fusion is a bounded add-on |
| 3 | Embedding model / multilinguality | `nomic-embed-text-v2-moe` from the start; chunk target ~400 tokens (512-token limit) |
| 4 | Index-time embedding | Synchronous, skip-on-failure; async queue only if editing latency demands it |
| 5 | Generation model | `qwen3:14b` fixed for the MVP; comparison post-MVP |
| 6 | Similarity function | `dot_product` (existing schema, no change) |
| 7 | Demo corpus | **German-first** (revised 2026-07-11, Timo): the corpus stays German — no translation; German hand-written questions; the English corpus comes later. Corpus source: curated export of the fictional `plone-intranet.kitconcept.io` demo site, shipped in this repository as plone.exportimport data (`setuphandlers/examplecontent`). |
| 8 | Search UX | External (kitconcept.intranet search modal project); "AI search" toggle |
| 9 | Chunk vs. document context for the prompt | Prompt with matched chunks (+ parent title/URL), cite parents |
| 10 | Failure policy: hard error vs. graceful degradation | **Graceful degradation, applied consistently** (2026-07-13): toggle on without credentials = the feature silently reports unavailable (no error); AI service down = users fall back to the classic search instead of a hard error. The effective state is exposed to the client as `kitconcept.solr.rag_available` on the @site endpoint (registry toggle AND credentials), so the UI renders the right thing from the first paint. Recorded as revisitable: if operational practice shows silent degradation hides real misconfigurations, we can move toward hard errors. |

Resolved open point:

1. **The two kinds of chunking** (resolved 2026-07-14): the second kind
   is the block storage of the new Volto editor (Plate) - the rich
   text block carries a ``value`` list of editor nodes instead of the
   classic per-block fields. Detection is per block (the Plate block
   ``@type``), so both kinds coexist in the same site and even on the
   same page; the chunking logic is shared, only the reading differs.
   Based on plone.restapi's Plate support (the authoritative
   implementation of the storage); the provisional upstream block type
   name may change when the new editor settles - isolated in one
   constant. Covered by unit tests only for now: Plate pages cannot
   yet be produced manually, e2e tests follow when the editor
   settles.

Remaining open point:

1. **Facet/tab conditions and the AI search** — requirements question,
   **to be discussed with Dante and Timo in the review**. The classic
   search presents tabbed results per content type with facet conditions
   in selected tabs (e.g. the person search). Two distinct readings for
   the AI search:
   - *Facets as navigation over the results:* does **not** transfer — the
     source list is a small top-K evidence set justifying the answer, not
     an exhaustive listing to narrow down; filtering the evidence away
     would undermine the fact-checking contract.
   - *Facets/tabs as scope constraints on the question* (ask within a
     tab or facet selection, e.g. a department in the person search):
     transfers well and the architecture already supports it — the knn
     query composes any filter query as a pre-filter (as security, path
     and language do today). Adding tab/facet parameters to
     `@rag-search` is a bounded, additive change reusing the classic
     search's condition builders. Caveat: chunks do not denormalize
     `portal_type` or the facet fields, so scoped retrieval needs either
     those fields on the chunks (schema addition + reindex) or filtering
     at the parent-collapse step — a real design decision.
   Proposed MVP stance: whole-intranet scope (matches the single search
   box); scoped RAG as a follow-up once the modal UX (external search
   modal project) defines what scoping looks like.

## 9. References

Research summaries behind the recommendations (full reports in the planning
ticket):

- Solr dense vector search: https://solr.apache.org/guide/solr/latest/query-guide/dense-vector-search.html
- Solr native RRF (unreleased, 9.11/10.1): https://issues.apache.org/jira/browse/SOLR-17319
- RRF (Cormack et al. 2009): https://dl.acm.org/doi/10.1145/1571941.1572114
- BEIR benchmark (dense vs BM25 out-of-domain): https://github.com/beir-cellar/beir
- nomic embeddings (prefixes, /api/embed, num_ctx): https://docs.ollama.com/capabilities/embeddings
- nomic-embed-text-v2-moe (multilingual): https://ollama.com/library/nomic-embed-text-v2-moe
- Chunking practice: https://www.firecrawl.dev/blog/best-chunking-strategies-rag · https://weaviate.io/blog/chunking-strategies-for-rag
- RAGAS (metrics + testset generation): https://docs.ragas.io/
- Retrieval metrics tooling: https://github.com/cvangysel/pytrec_eval · https://github.com/AmenRa/ranx
- Golden-set / eval practice: https://hamel.dev/blog/posts/evals-faq/
- CRAG question taxonomy: https://arxiv.org/abs/2406.04744
- RAGBench (CC BY 4.0): https://huggingface.co/datasets/galileo-ai/ragbench
