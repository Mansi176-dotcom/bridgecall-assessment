# Bridgecall — assessment submission

**Candidate:** Mansi Birhman  
**Repository:** [Mansi176-dotcom/bridgecall-assessment](https://github.com/Mansi176-dotcom/bridgecall-assessment)

A local prototype connecting traceable business knowledge, localized conversation flows, and call-coaching logic. This index identifies the included work and the evidence that remains outstanding.

## Review links

| Material | Location |
|---|---|
| Overview and setup | [README](README.md) |
| Requirement-by-requirement guide | [Reviewer guide](docs/REVIEW_GUIDE.md) |
| Seven application screenshots | [Screenshot gallery](docs/SCREENSHOTS.md) |
| Architecture and conversation state | [Architecture](docs/ARCHITECTURE.md) |
| KB schema, ingestion, retrieval, and citations | [Knowledge-base design](docs/KNOWLEDGE_BASE.md) |
| Localization examples and voice configuration | [Localization](docs/LOCALIZATION.md) |
| Streaming design, nudge controls, and timing definitions | [Live insights](docs/LIVE_INSIGHTS.md) |
| Reproducible text evaluation | [Results](evidence/RESULTS.md) |
| Retrieved passages, source references, and verdicts | [Retrieval details](evidence/retrieval-results.json) |
| Known limitations and production plan | [Limitations](docs/LIMITATIONS.md) |
| Continuous integration | [GitHub Actions](https://github.com/Mansi176-dotcom/bridgecall-assessment/actions/workflows/tests.yml) |

## Included and verified

- Source code, environment-variable template, sample data, local setup, and documentation.
- 23 approved locale-specific knowledge records with source references and hashes.
- 27 automated tests; 14 retrieval/abstention fixtures; 20 nudge fixtures.
- Actual browser screenshots of typed interactions in English, Filipino/Taglish, and Indonesian.
- Explicit consent, unsupported-answer fallback, and mock callback behavior.
- Optional live microphone transcription integration and latency export implementation.

The test counts describe small authored regression sets. The screenshots and simulated transcripts are not evidence of actual calls, ASR accuracy, or regional-accent performance. Live transcription is implemented but has not been validated against the provider in this package.

## Outstanding assessment evidence

The three Q1 call recordings, two calls per Q3 market, walkthrough video, native-speaker/regional-accent evaluation, provider-backed live-audio latency, and real-audio false-positive measurements are not included. Consequently, this package does not yet satisfy the full assessment requirements.

Business content is fictional because no business source pack was supplied. The callback is a local mock; it does not connect to a person or book an appointment. The public repository is accessible, but the application itself runs locally and is not a hosted calling endpoint.

Use the [recording runbook](docs/RECORDING_RUNBOOK.md) and [submission checklist](docs/SUBMISSION.md) to complete those items. The [evidence manifest](evidence/submission-manifest.json) keeps missing results explicit.
