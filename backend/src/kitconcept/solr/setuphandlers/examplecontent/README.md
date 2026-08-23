# German example content ("Deutsches Forschungszentrum für Nachhaltige Technologien")

A German-language test corpus for the AI search (RAG) feature (#79), in
[plone.exportimport](https://github.com/plone/plone.exportimport) format.

It is a curated copy of the fictional intranet demo site
`plone-intranet.kitconcept.io` (a research-institute intranet with
sections Aktuelles, Arbeitsthemen, Forschung, Services, Über uns):
409 content objects, 80 images, 7 example users.

## Usage

Create a site with German as the default language, import, then index:

```sh
DELETE_EXISTING=1 SITE_DEFAULT_LANGUAGE=de make create-site
make import-example-content
make solr-activate-and-reindex-with-rag-clear   # or without -with-rag
```

The site default language **must** be `de`; the importer downgrades the
language of every object to the site default when `de` is not among the
site's available languages.

## Example users

All users share the password `intranet-demo-2026` (fictional accounts,
demo purposes only).

| User | Role |
| --- | --- |
| a.becker, b.yilmaz, c.nguyen, d.schmidt, e.roth | Editors, Administrators group |
| j.halmbach | Site Administrator |
| f.meier | plain Member (no editing rights) |

`f.meier` is the reference user for permission-trimming tests: three
documents are in the `private` review state (Betriebsrat,
Gleichstellungsbeauftragte, and one unpublished news item) and must not
appear in search results or RAG answers for this user.

## Curation applied to the source site

- Dropped subtrees: `/test`, `/services/features/plone-cms` (including
  their images).
- Dropped comments (Discussion Items; separate exportimport format).
- Dropped images not referenced by any kept page.
- Raster images are the ~1200px "great" scale instead of the originals
  (228 MB → ~19 MB); SVGs are kept as-is.
- `preview_image_link` / `relatedItems` relations are shipped through
  `relations.json` (the relations importer runs after all content
  exists), so listing and teaser preview images work.
- Content links inside block data are in `resolveuid` form and stale
  embedded `image_scales` were stripped, so plone.restapi injects fresh
  image scales at serve time (the crawl's absolute URLs and foreign
  scale hashes produced broken images otherwise).
- Blocks of the source site's volto-light-theme / kitconcept add-ons
  are mapped to Volto core blocks so the corpus renders on the plain
  kitconcept.solr frontend: `introduction` → slate, `__button` → slate
  link, `highlight`/`banner` → image + slate heading, `slider` →
  gridBlock of teasers; purely decorative blocks (`separator`,
  `eventMetadata`, `eventCalendar`) are dropped. A native-blocks
  variant for the kitconcept.intranet distribution can be regenerated
  from the preserved source pipeline (`transform_corpus.py intranet`).
- Content types of the kitconcept.intranet distribution (17 Person,
  5 Organisational Unit, 3 Location objects) are **not part of this
  dump**: they cannot be exported from a site that does not have those
  types installed. Five institute subtrees under `/forschung/institute/`
  are therefore missing their container pages.
- Language normalized to German (the source site's language metadata
  was unreliable).

## Golden questions

`questions.json` holds ~20 hand-written German questions with expected
source documents, including two questions the corpus cannot answer (the
system must decline) and one permission-sensitive question. Verified
2026-07-14 against the live RAG stack: 19/19 answerable questions
retrieve an expected source, both unanswerable questions decline.

The import uses the stock `plone-importer` script of plone.exportimport
(see the make target). Caveat: the stock importer **crashes on content
whose portal type is not installed** on the target site (it aborts on
the first unknown type instead of skipping it). This dump contains only
standard types, so a plain kitconcept.solr site imports it cleanly.

For one-time operations on dumps that do contain uninstalled types —
e.g. re-importing the original intranet source tree with its Person,
Organisational Unit and Location objects — use the robust variant
instead, which skips such items with a report:
`make import-content-robust IMPORT_CONTENT_FOLDER=<path>`
(`scripts/import_content_robust.py`).
