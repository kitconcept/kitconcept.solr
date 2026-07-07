# AI Search (RAG) — Specification

Ticket: [#79](https://github.com/kitconcept/kitconcept.solr/issues/79)
Status: draft for discussion
Companion document: [IMPLEMENTATION-79.md](./IMPLEMENTATION-79.md)

## 1. Goals

Enhance `kitconcept.solr` with an AI-powered search feature based on **RAG
(Retrieval-Augmented Generation)**, targeted at sites with large amounts of
long-form documentation (the primary driver is the kitconcept intranet
distribution, where users need to quickly find answers inside abundant
organizational documentation and fact-check them against the source pages).

The user-facing goal, as a user story:

> As a user, I can ask a question in natural language. I get a natural-language
> answer to my question, together with the list of documents within the site
> that the answer was based on.

Design goals derived from that:

- **Trustable answers.** The answer is always accompanied by its source
  documents, so it can be fact-checked. The retrieval layer respects the
  existing permission model — a user can never get an answer derived from
  content they are not allowed to see.
- **Part of the product, off by default.** The feature ships inside
  `kitconcept.solr` (backend) and `@kitconcept/volto-solr` (frontend), not as a
  separate plugin. It activates only when an LLM endpoint is configured; sites
  that do not configure it are unaffected.
- **Measurable quality.** "It works" is defined by an evaluation harness
  (golden question set + retrieval metrics + answer grading), not by anecdote.

## 2. MVP scope

The MVP is the smallest version that actually works end to end:

1. **Single-turn.** One question → one answer + source list. No conversation
   memory, no follow-up questions. A new question is a new query.
2. The response contains exactly two things beyond a normal search response:
   the **summary answer** and the **source documents** (which are ordinary
   Solr results).
3. **One model provider.** The MVP connects to a single Ollama-compatible
   server (the kitconcept Ollama server) using two models:
   an **embedding model** (`nomic-embed-text`) and a **general-purpose LLM**
   for answer synthesis. No provider abstraction, no model switching UI.
4. **Configuration without UI.** Endpoint URL, credentials and model names are
   set in the kitconcept.solr configuration (Plone registry + environment
   variables, see §5). No control-panel UI in the MVP.
5. **Minimal modal UI.** A command-palette style (⌘K) modal with a question
   input, an answer panel and the source result list (see §6).
6. **Demo site + evaluation.** An example content corpus shipped as
   export/import data, a golden set of questions, and scripts that measure
   retrieval and answer quality (see §7).

### Explicitly out of scope for the MVP (post-MVP roadmap)

- Multi-turn chat / conversation context.
- Admin/control-panel UI for AI configuration (long-term we want a UI for
  kitconcept.solr configuration in general; the AI credentials are a prime
  candidate).
- Integration with the community LLM-connector add-on. Long-term we commit to
  using it (it gives us any-provider support); it first needs support for the
  kitconcept Ollama setup. For the MVP we connect directly.
- Attaching files/context to a query, search-mode toggles, suggested actions
  in the modal.
- Streaming/token-by-token answer display (nice to have; the MVP may render
  the answer only when complete).
- Answer quality tuning beyond the initial evaluation pass (re-ranking models,
  semantic chunking, query rewriting, multilingual optimization).

## 3. Architecture overview

```
                       ┌──────────────────────────────────────────┐
                       │                Volto (React)             │
                       │   ⌘K modal → question                    │
                       └───────────────┬──────────────────────────┘
                                       │ GET/POST @rag-search?q=...
                       ┌───────────────▼──────────────────────────┐
                       │        Plone / kitconcept.solr           │
                       │  1. embed(question)  ──────────────────────────┐
                       │  2. Solr retrieval (knn [+ BM25/RRF])    │      │
                       │  3. build prompt(question, top docs)     │      │
                       │  4. LLM completion  ───────────────────────────┤
                       │  5. return {answer, sources[]}           │      │
                       └───────────────┬──────────────────────────┘      │
                                       │ {!knn f=content_vector}         │
                       ┌───────────────▼─────────────┐   ┌───────────────▼─────────────┐
                       │        Solr 9.10            │   │   Ollama server (kitconcept) │
                       │  content_vector (768, HNSW) │   │  /api/embed  nomic-embed-text│
                       │  existing keyword fields    │   │  /api/chat   general LLM     │
                       └─────────────────────────────┘   └──────────────────────────────┘
```

Two distinct LLM endpoints are involved (same Ollama server):

- **Embedding endpoint** — used at *indexing time* (vectorize content) and at
  *query time* (vectorize the user's question). Ollama `POST /api/embed`,
  which batches inputs and returns L2-normalized vectors.
- **Generation endpoint** — used at *query time only*: receives one prompt
  containing (a) the user's question, (b) the retrieved document texts, and
  (c) fixed instructions ("answer the question based only on these documents,
  cite which documents you used"), and returns the summary answer.

### Existing groundwork

The Solr schema (since 2.0.0a14) already defines the vector field — currently
unpopulated and unqueried:

- `solr/etc/conf/schema.xml`: field type `knn_vector_768`
  (`solr.DenseVectorField`, `vectorDimension="768"`,
  `similarityFunction="dot_product"`) and field `content_vector`.
- `nomic-embed-text` produces 768-dim vectors; `/api/embed` returns them
  normalized, so `dot_product` is equivalent to cosine similarity here.

### Retrieval design

- Query-time vector search uses Solr's `{!knn f=content_vector topK=K}` query
  parser (available since Solr 9.0; we ship 9.10).
- **Security filtering keeps working**: when the knn query is the main query,
  Solr applies `fq` filters as HNSW *pre-filters* — the existing
  `allowedRolesAndUsers` trimming, path and language filters compose correctly
  with vector search.
- **Hybrid search** (BM25 + vector, fused with Reciprocal Rank Fusion) is the
  industry-standard remedy for pure-vector weaknesses (exact names, codes,
  jargon; BEIR shows dense retrieval underperforms BM25 out-of-domain).
  Native RRF lands in Solr 9.11/10.1 ([SOLR-17319]) which is **not released
  yet**, so if/when we need hybrid we fuse client-side (two Solr requests,
  `score = Σ 1/(60 + rank)`), which is drop-in replaceable by the native
  combiner later. The MVP starts with pure knn retrieval and the evaluation
  harness decides whether hybrid is required (see §8 open question 2).

[SOLR-17319]: https://issues.apache.org/jira/browse/SOLR-17319

### Indexing design

- Embeddings are computed **on the Plone side** (client of Ollama), not via
  Solr's built-in LLM module: the module doesn't support Ollama as a provider
  and cannot add the task prefixes `nomic-embed-text` requires
  (`search_document: …` for content, `search_query: …` for questions —
  skipping them measurably degrades retrieval).
- **Chunking**: embedding a whole long document produces a "blurry" vector.
  State of the art for long-form documentation is structure-aware chunking:
  split on headings/blocks at roughly **500 tokens per chunk with 10–15%
  overlap**, merging tiny fragments. Volto blocks give us structural
  boundaries for free (the existing block-text indexer already walks them).
- Chunk storage in Solr — see §8 open question 1; the recommended model is
  chunks as **sibling documents** (`parent_uid` + denormalized title/path/
  security fields), grouped back to parent documents at query time
  (parent-document retrieval: match a chunk, show the parent as the source).

## 4. Functional specification

### New REST endpoint: `@rag-search`

- Registered like the existing `@solr` service
  (`backend/src/kitconcept/solr/services/`).
- Request: the question string, plus optional standard search parameters
  (`path_prefix`, `lang`) reused from `@solr`.
- Behavior: embed question → retrieve top-K chunks/documents (security
  trimmed) → collapse to parent documents → prompt LLM → respond.
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
- If the feature is not configured, the endpoint returns 501/`not configured`
  and the frontend never offers the AI mode.
- Timeouts are mandatory on both Ollama calls; the endpoint must never hang a
  Plone thread indefinitely.

### Indexing behavior

- On indexing/reindexing a content object, its extracted text (the existing
  `SearchableText`/block text path) is chunked and embedded, and the chunks
  are written to Solr alongside the document.
- On delete/unindex, chunks are removed with the parent.
- A full-reindex path exists (`solr-activate-and-reindex`) and must populate
  vectors; the embedding model name is recorded so a model change forces a
  reindex.
- If the embedding endpoint is unavailable at indexing time, indexing of the
  document must still succeed (log + skip vectors) — search availability must
  not depend on the AI stack.

## 5. Configuration

Two layers, consistent with how kitconcept.solr is configured today:

- **Plone registry** (`IKitconceptSolrSettings`,
  `backend/src/kitconcept/solr/interfaces.py` + GenericSetup profile):
  feature toggle (per the epic: "as Admin I can turn it on or off"), model
  names, prompt template override, `topK`, chunk size parameters.
- **Environment variables** (secrets / deployment-specific): Ollama base URL
  and API credentials (e.g. `KITCONCEPT_SOLR_LLM_URL`,
  `KITCONCEPT_SOLR_LLM_TOKEN`), following the existing
  `COLLECTIVE_SOLR_HOST`/`COLLECTIVE_SOLR_BASE` pattern in
  `docker-compose.yml`. Credentials must not live in the registry (they end
  up in exported site configuration).

No UI in the MVP. The feature counts as **enabled** when the toggle is on and
the endpoint variables are present.

## 6. Search UI (Volto)

MVP: a **modal search** (command-palette pattern, as in e.g. the Tailwind
docs ⌘K dialog), replacing/augmenting the current search entry point in
`@kitconcept/volto-solr`:

- Opened via keyboard shortcut (⌘K / Ctrl-K) and via the search icon.
- One text input. Submitting triggers `@rag-search`.
- Result view: answer panel (with a visible "AI-generated — verify against
  the sources" hint) above the source document list (reusing the existing
  result-item rendering).
- Loading state while the LLM answers (several seconds); error state falls
  back to a link to the classic search.
- The classic `@solr` search remains fully functional and unchanged.

A short UX specification (wireframe-level: states, keyboard behavior, copy)
is a deliverable of the implementation phase — the modal is deliberately
minimal but the pattern is chosen because it extends naturally (mode toggles,
attachments) post-MVP.

## 7. Demo site, example questions, evaluation

How we know the results are "good", aligned with current industry practice:

### Demo corpus

A demo/example site is shipped with the product as export/import data (also
useful beyond this feature). Recommended content, based on a license/quality
survey:

- **Primary: a synthetic fictional-organization corpus** (~50–150 documents:
  HR policies, IT procedures, onboarding guides, org structure), generated
  with an LLM and human-reviewed. Two decisive advantages: no license burden,
  and **no training-data contamination** — the answer LLM cannot answer from
  memory, so a correct, correctly-sourced answer proves the retrieval
  actually works. (Established practice; cf. EnterpriseRAG-Bench, OrgForge.)
- **Alternative/supplement: a curated subset of the GitLab Handbook**
  (CC BY-SA 4.0, real intranet-genre content, English) — believable, but
  contaminated (it is in every LLM's training data), so evaluation must check
  *sources*, not just answer text.
- German content (relevant for the target market): note that
  `nomic-embed-text` is English-trained; the multilingual variant is
  `nomic-embed-text-v2-moe` (also 768-dim, Apache-2.0, on Ollama). See §8
  open question 3. Public-domain German federal law texts
  (github.com/bundestag/gesetze) are a safe authentic supplement;
  `deepset/germanquad` (CC BY 4.0) provides a ready German corpus+QA set for
  pipeline benchmarking.

### Golden question set

- **30–50 questions to start** (growing later toward 100+), stored in the
  repo as `question / expected source document(s) / reference answer`
  triples.
- Question types follow the CRAG taxonomy: simple factual, comparison,
  aggregation, multi-hop, and questions with **no answer in the corpus**
  (the system should say so rather than hallucinate).
- Bootstrapped with a generator (RAGAS `TestsetGenerator` with personas —
  "new employee", "HR admin"), then **manually reviewed and culled**; plus
  hand-written terse real-user-style queries.

### Metrics — two tiers

1. **Retrieval metrics** (deterministic, no LLM, cheap — CI-able): run the
   golden questions against the retrieval endpoint and compute
   **Recall@5/10, MRR, nDCG@10** (`ranx` or `pytrec_eval`). This directly
   answers "are the correct source documents found?" — the MVP success
   criterion from the kickoff ("we actually get the documents that make
   sense for that question").
2. **Answer metrics** (LLM-as-judge, run on demand/nightly): **faithfulness**
   (is every claim grounded in the retrieved sources?) and **answer
   relevancy**, via **RAGAS** (Apache-2.0, vendor-neutral, any judge LLM —
   can use the same Ollama server). Judge scores are calibrated against a
   one-time human-labeled sample before being trusted for trend-tracking.

MVP acceptance target (proposal, to be confirmed once baseline numbers
exist): Recall@10 ≥ 0.8 on the golden set for answerable questions, and no
hallucinated sources; answers for unanswerable questions must decline.

## 8. Open questions / decisions still to be made

Ordered by how early they block implementation. Each has a recommended
default from the research phase.

1. **Chunk storage model in Solr.** (a) chunks as sibling documents with
   `parent_uid` + denormalized security fields, parent-collapse at query
   time — flexible, works on Solr 9.x, plays well with Plone's per-object
   reindexing; (b) nested child documents/block-join — poor fit (atomic
   block reindexing conflicts with Plone; knn-through-block-join is Solr
   10.x); (c) MVP-minimal: no chunks at all — one truncated-document vector
   in the existing `content_vector` field, accepting blurry retrieval on
   long documents. **Recommendation: (a)**; (c) is acceptable only as a
   phase-1 stepping stone. *Blocks Phase 1.*
2. **Pure vector vs. hybrid retrieval in the MVP.** Hybrid (client-side RRF)
   is the industry default and the likely end state, but it doubles the
   query path. **Recommendation: implement pure knn first, keep the query
   layer factored so client-side RRF is a bounded add-on in the quality
   phase, decided by golden-set numbers.** *Decided by Phase 5 data.*
3. **Embedding model / multilinguality.** `nomic-embed-text` (English) vs
   `nomic-embed-text-v2-moe` (multilingual incl. German, same 768 dims).
   If German content is in MVP scope, v2-moe from the start avoids a full
   reindex later; requires confirming it is available on the kitconcept
   Ollama server. **Recommendation: confirm German requirements now; prefer
   v2-moe if the server can host it.** *Blocks Phase 1 (index format).*
4. **Embedding at indexing time: synchronous vs. queued.** Synchronous (in
   the indexer/subscriber) is simple but adds an HTTP call per document to
   every save and couples editing latency to the Ollama server. A queue
   (async worker) is more robust but more moving parts. **Recommendation:
   synchronous with a short timeout and skip-on-failure for the MVP; batch
   endpoint for full reindexes. Revisit if editing latency hurts.**
5. **Generation model choice.** Which general-purpose LLM on the kitconcept
   Ollama server (quality vs. latency; answer language must follow the
   question language). Needs a quick bake-off on the golden set. *Phase 3.*
6. **Similarity function.** Schema says `dot_product`; nomic via `/api/embed`
   returns normalized vectors, so it is equivalent to cosine. Keep
   `dot_product` (no change) unless we switch to a model with unnormalized
   outputs. *Effectively decided; recorded for the record.*
7. **Demo corpus language and content** (see §7): synthetic fictional org
   (which language(s)?) vs GitLab Handbook subset. **Recommendation:
   synthetic, English first unless German is required for the first demo.**
   *Blocks Phase 2.*
8. **UX details of the modal**: trigger points (does it fully replace the
   search bar?), mobile behavior, wording of the AI disclaimer, behavior
   when the feature is disabled. Needs the short UX spec. *Blocks Phase 4.*
9. **Chunk-level vs document-level context for the LLM prompt**: send parent
   documents or the matched chunks (parent-document retrieval suggests:
   retrieve by chunk, prompt with chunk + surrounding context, cite parent).
   **Recommendation: prompt with matched chunks (+ title/URL), cite
   parents.** *Phase 3.*

## 9. References

Research summaries behind the recommendations (full reports in the planning
ticket):

- Solr dense vector search: https://solr.apache.org/guide/solr/latest/query-guide/dense-vector-search.html
- Solr native RRF (unreleased, 9.11/10.1): https://issues.apache.org/jira/browse/SOLR-17319
- RRF (Cormack et al. 2009): https://dl.acm.org/doi/10.1145/1571941.1572114
- BEIR benchmark (dense vs BM25 out-of-domain): https://github.com/beir-cellar/beir
- nomic-embed-text (prefixes, /api/embed, num_ctx): https://ollama.com/library/nomic-embed-text · https://docs.ollama.com/capabilities/embeddings
- nomic-embed-text-v2-moe (multilingual): https://ollama.com/library/nomic-embed-text-v2-moe
- Chunking practice: https://www.firecrawl.dev/blog/best-chunking-strategies-rag · https://weaviate.io/blog/chunking-strategies-for-rag
- RAGAS (metrics + testset generation): https://docs.ragas.io/
- Retrieval metrics tooling: https://github.com/cvangysel/pytrec_eval · https://github.com/AmenRa/ranx
- Golden-set / eval practice: https://hamel.dev/blog/posts/evals-faq/
- CRAG question taxonomy: https://arxiv.org/abs/2406.04744
- RAGBench (CC BY 4.0): https://huggingface.co/datasets/galileo-ai/ragbench
- GitLab Handbook license: https://about.gitlab.com/blog/our-handbook-is-open-source-heres-why/
- GermanQuAD: https://huggingface.co/datasets/deepset/germanquad
- German law corpus: https://github.com/bundestag/gesetze
