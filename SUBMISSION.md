# Bridgecall — assessment submission

**Candidate:** Mansi Birhman  
**Public repository:** https://github.com/Mansi176-dotcom/bridgecall-assessment

A local prototype joining source-cited business answers, Philippine and Indonesian conversation flows, and live coaching.

## Start here

1. [Walkthrough video](evidence/video/walkthrough.mp4) — synthetic narration explaining a design choice, an observed failure, and its correction.
2. [Audio evidence report](docs/AUDIO_EVIDENCE.md) — seven synthetic sessions, two Indonesian reruns, actual ASR observations, and real-human regional-accent corpus results.
3. [Live demo video](evidence/video/live-demo.mp4) — nudges appear during a real-time audio replay; [measured latency](evidence/live-latency-summary.json).
4. [Screenshot gallery](docs/SCREENSHOTS.md), [architecture](docs/ARCHITECTURE.md), [KB design](docs/KNOWLEDGE_BASE.md), and [setup](README.md).
5. [Text evaluation](evidence/RESULTS.md), [limitations](docs/LIMITATIONS.md), and [requirement map](docs/REVIEW_GUIDE.md).

## Verified scope

29 unit tests pass, with 14 retrieval/abstention and 20 nudge fixtures. The actual browser replay measured P50 4.91 s / P95 8.73 s from audio-window start to display over 10 windows. Five expected signals were detected, one was missed, and four negative windows produced no false alert. These are small authored tests, not production accuracy claims.

The recordings use synthetic speakers. The separate regional-accent test uses published human news speech, not an interactive financial call. Human call validation and native-speaker review remain outstanding. Filipino ASR failures are reported, not hidden. The narrated walkthrough uses synthetic narration rather than the candidate's voice. Fictional businesses and mock callbacks keep this a demonstration, not a deployed financial service.
