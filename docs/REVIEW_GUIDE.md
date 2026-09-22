# Bridgecall — reviewer guide

Bridgecall is a local prototype for grounded insurance screening, localized financial conversations, and live call coaching. The implementation and documentation are available for review; the required voice recordings and audio-validation evidence are not included in this version.

## Review in five minutes

1. Open the [screenshot gallery](SCREENSHOTS.md) to see the actual interface and outputs.
2. Follow the [README setup](../README.md#run-locally). The core app needs Python 3.9+ and no external packages.
3. Ask `What is a beneficiary?` and inspect the source citation. Ask `Does coverage include cancer surgery?` to see the fallback.
4. Inspect the [retrieval evidence](../evidence/retrieval-results.json) and [generated results](../evidence/RESULTS.md).
5. Read [architecture](ARCHITECTURE.md), [limitations](LIMITATIONS.md), and the requirement map below.

## Requirement map

| Area | Included implementation and evidence | Outstanding evidence / limits |
|---|---|---|
| Q1: grounded voice agent | Shared KB connection; browser voice controls; qualification/consent state machine; mock callback; citations; localized fallback; scripted text scenarios | Three recorded calls and observed voice quality; actual handoff is a mock |
| Q2: knowledge base | 23 approved locale-specific records; sample JSON, saved HTML, CSV, text; cleaning, deduplication, PII masking, quarantine; metadata and hashes; 14 retrieval/abstention checks | Actual employer sources were not provided; optional PDF branch is not tested; PII protection is pattern-based |
| Q3: native-language bots | PH English and Filipino/Taglish plus Indonesian scripts, reviewed demo answers, locale configuration, localized fallback, three-plus adaptation examples per market | Two recordings per market, real non-Jakarta accent observations, native-speaker review, actual ASR/TTS quality |
| Q4: live insights | Ongoing four-second WAV capture; optional provider transcription; per-window analysis; evidence-backed nudges; priorities, cooldown, expiry, bounded queue; component timing/export | Provider-backed audio test, measured audio P50/P95, live screen recording, real-audio false-positive analysis |
| Supporting materials | README; environment template; architecture diagram; test suite and CI; source/retrieval data; screenshot gallery; setup; limitations and production plan | Walkthrough video and final recording links |

## Verified results

- **27 automated tests pass.** Includes consent, qualification boundaries, spoken-age parsing, source resolution, locale isolation, fallback, and nudge controls.
- **14/14 retrieval and abstention cases pass.** Each output includes retrieved content, source, expected topic, and verdict.
- **20/20 authored nudge cases pass.** The set includes 10 positive and 10 negative/noisy text cases.
- **Seven browser screenshots** show actual typed interaction and visible outcomes.

These are small authored regression sets, not independent accuracy benchmarks. The timing in the checked-in results is text signal-processing latency only. Audio latency fields remain unmeasured rather than being filled with estimates.

## Key choices

Approved passages are returned directly to limit invented product claims. The state machine keeps consent explicit. A lexical baseline makes the small corpus easy to inspect and reproduce. Rule-based coaching exposes exactly which phrase caused a nudge. The tradeoffs are limited paraphrase handling, narrow intent recognition, and the need for actual speech evaluation before making quality claims.

Harbor Life and Nusantara Finance are fictional demo businesses. No real insurer, bank, lender, or customer data is represented. A callback creates a local mock record and does not contact an adviser.

## Reproduce

```bash
git clone https://github.com/Mansi176-dotcom/bridgecall-assessment.git
cd bridgecall-assessment
python3 -m unittest discover -s tests -v
python3 -m scripts.evaluate
python3 -m app.server
```

Open `http://localhost:8765` on the same machine. For microphone transcription, copy `.env.example` to `.env`, configure the API key locally, restart, and follow [the recording runbook](RECORDING_RUNBOOK.md). The public repository is not a hosted public calling endpoint.
