# Knowledge-base design

## Inputs and collection

`data/raw/business.json` holds the manually reviewed fictional business records. `website.html` models a saved business page with navigation/footer clutter and synthetic contact information. `form.csv` models structured form fields. The duplicate, unapproved, and broken files exercise ingestion controls deliberately; they are not accidental repository defects.

The app processes local snapshots instead of crawling arbitrary websites. For a real website: obtain the permitted pages, record the original URL and retrieval date, save immutable HTML, then run the extractor and reviewer. JavaScript-only pages need a rendered snapshot. Tables should be extracted with row/column headers preserved. This prototype preserves CSV field names and values; it does not reconstruct complex HTML tables.

HTML parsing excludes navigation, headers, footers, scripts, and styles. Text is Unicode-normalized for tokenization and whitespace-normalized during extraction. Identical or near-identical token sets with Jaccard similarity ≥ 0.88 are marked duplicate. The structured source carries ISO dates, canonical categories, and language-specific answers. An extraction failure records its source and error type instead of silently disappearing.

The optional PDF branch uses `pypdf.PdfReader` and page text extraction. It flags empty text for OCR/manual review. No PDF or OCR extraction was evaluated in this package; add representative PDFs and install/test `pypdf` before claiming that coverage. Scanned documents, columns, merged cells, and footnotes need additional layout-aware processing.

## Publishing and privacy

Reviewed `business.json` entries become approved records. Other extracted material is staged in `review_queue.json` for explicit human review. Suspicious promises and instruction-like text are quarantined. No automatic conflict resolution rewrites a policy. Conflicting material remains unpublished until the owner chooses an authoritative version.

Regex redaction masks emails, long phone/identifier-like sequences, and explicitly labeled names. It does not provide comprehensive PII protection: unlabeled names, addresses, and spoken PII can survive. Production needs entity detection, an allowlisted schema, access controls, encrypted storage, deletion policy, and an audit trail. The provided PII examples are synthetic, use the reserved `.invalid` domain, and are not customer data.

## Schema

| Field | Purpose |
|---|---|
| `record_id` | Business identifier + locale, stable across rebuilds |
| `market`, `language` | Strict retrieval partition |
| `title`, `category`, `keywords` | Taxonomy and search vocabulary |
| `content` | One approved, directly speakable answer |
| `source` | File plus exact JSON pointer or section |
| `source_sha256` | Hash of the complete source snapshot |
| `content_sha256` | Hash of the published answer |
| `version`, `effective_date` | Explicit version and ISO source date |
| `authority`, `status` | Fictional approved demo / approval boundary |
| `pii_redacted` | Whether masking changed the approved answer |

A sample record can be inspected in `data/processed/records.json`. There are 23 locale-specific records across product, qualification, FAQ, policy, objection, and action categories.

## Chunking, indexing, retrieval

One short policy/FAQ answer is one chunk; a rule and its caveat stay together. There is no overlapping fixed-token slicing in this small corpus. Longer real documents should be chunked by section with heading context and explicit table units, and split only after preserving conditions/exclusions.

The index is an in-memory term-frequency representation rebuilt from the reviewed source. A small explicit normalization map groups `miss`/`missing` with `missed`, `premiums` with `premium`, and `lapses` with `lapse`. This fixes an observed UI failure without claiming general morphological coverage. Common question words are removed. Ranking uses BM25-style inverse document frequency, length normalization, k1 = 1.2, and b = 0.75. Locale and market filtering happen before ranking. A minimum score of 1.25 plus overlap with the record's domain vocabulary gates the answer; explicit unsupported-topic checks demonstrate abstention. These are prototype heuristics, not calibrated confidence or general hallucination protection.

Embeddings are intentionally not used. With this tiny reviewed corpus, lexical search is reproducible and works without an embedding account. The cost is weak paraphrase recall and dependence on curated local vocabulary. A production successor should evaluate multilingual dense retrieval plus lexical ranking on held-out questions, with a reranker and contradiction-aware source precedence. Choose thresholds from actual error costs, not this small fixture set.

Citations carry the exact record ID, JSON pointer, version, and content hash. They demonstrate provenance, not automatic correctness. Updating the source requires a version bump and a regenerated index; the current tool records hashes but does not implement a version-history database or effective-date arbitration.

## Evaluation

Run `python3 -m scripts.evaluate`. The output includes 14 questions, retrieved passages, source references, lexical matches, expected topics, answer selection, and verdicts. Product, policy, qualification, FAQ, objection, and unsupported questions are represented. Tests resolve every approved answer back to its source. Review the full JSON to spot incorrect supporting passages even when a top-result test passes.
