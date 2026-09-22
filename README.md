# Bridgecall
### Grounded voice conversations, with evidence attached.

[![Core checks](https://github.com/Mansi176-dotcom/bridgecall-assessment/actions/workflows/tests.yml/badge.svg)](https://github.com/Mansi176-dotcom/bridgecall-assessment/actions/workflows/tests.yml)

[Reviewer guide](docs/REVIEW_GUIDE.md) · [Screenshots](docs/SCREENSHOTS.md) · [Test results](evidence/RESULTS.md) · [Architecture](docs/ARCHITECTURE.md)

![Bridgecall interface](docs/screenshots/00-overview.png)

Bridgecall is a local assessment prototype for Philippine life-insurance screening and Indonesian consumer-finance follow-up. It connects a reviewed knowledge base to a voice-capable conversation flow and a live call-coaching dashboard.

The useful part is inspectable: an answer carries a source record; a coaching nudge carries the phrase that triggered it; missing policy information produces a fallback.

**Current status:** runnable local implementation with passing text regression checks. Real call recordings, native-speaker/accent testing, provider-backed live-audio latency, and a walkthrough video are still required before submission. See [submission checklist](docs/SUBMISSION.md). Fictional business data is used because no actual business script or source pack was provided.

**Public repository:** https://github.com/Mansi176-dotcom/bridgecall-assessment

Screenshots are actual captures of the locally running application using typed inputs. They do not substitute for recorded calls or live-audio measurements.

## Run locally

Requires Python 3.9+ and a browser. No package installation is needed for the core workflow.

```bash
git clone https://github.com/Mansi176-dotcom/bridgecall-assessment.git
cd bridgecall-assessment
python3 -m app.server
```

Open **http://localhost:8765**. Keep the terminal running. The local URL is for your machine; it is not a public recruiter demo link.

1. In **Voice desk**, start a call. Type `yes`, `28`, `yes`, ask `What is a beneficiary?`, then finish the callback flow. Inspect the source citation and export the transcript.
2. Ask `Does coverage include cancer surgery?` to see an unsupported-answer fallback. Ask for a human to see the mock handoff path.
3. Choose Filipino/Taglish or Bahasa Indonesia and start a new call. **Speak one turn** uses browser ASR; responses use an installed language-matched TTS voice when available.
4. In **Knowledge explorer**, retrieve `What happens if I miss a premium?` and inspect the record, source, version, and hash.
5. In **Live insights**, run a text check with `I have a second vehicle`. This validates nudge logic only. The live microphone mode below is the audio pipeline.

## Enable live audio

```bash
cp .env.example .env
# Edit .env locally and set OPENAI_API_KEY. Never commit this file.
python3 -m app.server
```

Restart if the server was already running. This mode uses a paid external transcription service; use consenting testers and fictional details. Set the call language first, then open **Live insights**, reset the coach session, confirm consent, and start the microphone. Speak a complete sentence during a four-second window. The browser continues capturing while the previous window is transcribed.

Choose the speaker before speaking. This is manual speaker attribution, not automatic diarization. Stop to save a WAV, then export evidence after queued audio finishes. Save a screen recording that shows a nudge arriving while the session remains live. See [recording runbook](docs/RECORDING_RUNBOOK.md).

If ASR is not configured, live audio is disabled. The app never substitutes text simulation for an audio result. Browser ASR/TTS support and available voices vary; use a browser with SpeechRecognition support for Q1/Q3. The app reports missing TTS voices. Type input remains available for debugging.

## Reproduce the checks

```bash
python3 -m unittest discover -s tests -v
python3 -m scripts.evaluate
python3 -m scripts.check_submission
```

The last command intentionally fails until real media and sharing links are supplied. The first two produce/check local evidence without an API key.

| Evidence | Result | Scope |
|---|---|---|
| Core tests | 27 passing | Source resolution, consent, qualification, fallback, locale isolation, nudge controls |
| Retrieval and abstention | 14/14 | Authored questions; not an independent benchmark |
| Nudge rules | 20/20 | 10 positive and 10 negative/noisy text fixtures |
| Recorded calls / native speech quality | Pending | No ASR or accent quality claim |
| Live audio P50/P95 | Pending | Measured by the app after an actual audio run |

[Generated results](evidence/RESULTS.md) · [Full retrieval evidence](evidence/retrieval-results.json) · [Simulated text transcripts](evidence/simulated-transcripts.json)

## What is where

| Assessment | Implementation | Documentation |
|---|---|---|
| Q1: grounded voice | `app/agent.py`, Voice desk | [Flow and architecture](docs/ARCHITECTURE.md) |
| Q2: knowledge base | `app/kb.py`, `data/` | [KB design](docs/KNOWLEDGE_BASE.md) |
| Q3: localized bots | Locale-specific dialogue and records | [Localization and ASR plan](docs/LOCALIZATION.md) |
| Q4: live coaching | `app/nudges.py`, `app/server.py`, `web/app.js` | [Latency and controls](docs/LIVE_INSIGHTS.md) |
| Submission | Manifest, validator, recording scripts | [Checklist](docs/SUBMISSION.md), [walkthrough](docs/WALKTHROUGH.md) |

## Decisions worth discussing

- **Lexical retrieval before embeddings.** The small corpus is curated in each language. A BM25-style ranker is cheap, deterministic, and easy to inspect. It misses paraphrases; a larger corpus should be evaluated with hybrid retrieval.
- **Approved answer text before generation.** The agent speaks the retrieved passage and uses a state machine for consent. It cannot invent a premium, waiver, or benefit. Lexical retrieval can still select an irrelevant passage, so a domain gate and explicit abstention checks are included.
- **Rules before an LLM for nudges.** A small set of signals has auditable triggers and negligible local compute. Broader semantic detection remains future work. The audio ASR is the model-backed component; there is no hidden LLM in the coaching path.
- **Failure is visible.** Missing voices, unconfigured ASR, extraction errors, low-energy audio, queue overflow, and unsupported questions are surfaced.

This is not a production deployment: sessions are in memory, handoffs are mock records, PDF support needs the optional `pypdf` package and is not part of the tested corpus, and natural-language understanding is deliberately narrow. [Limitations and next steps](docs/LIMITATIONS.md).

## References

The optional transcription adapter follows the [official OpenAI audio transcription reference](https://developers.openai.com/api/reference/typescript/resources/audio/subresources/transcriptions/methods/create). Browser voice behavior uses [SpeechRecognition](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition) and [MediaRecorder](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder). These references support the integrations, not claims about observed speech quality.
