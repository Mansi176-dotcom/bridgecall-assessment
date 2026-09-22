# Limitations and production plan

## Implemented and locally checked

The local web app loads; a typed voice-desk question returns a source-cited answer; a text coaching input displays the expected opportunity nudge; audio latency remains blank in text mode. The 27 automated checks, 14 retrieval cases, and 20 nudge fixtures pass on the development machine. These checks cover only the described test conditions.

## Not yet validated or complete

- **Required evidence:** no real call audio, two-sided recordings, native-speaker feedback, Indonesian regional-accent results, or walkthrough video is supplied yet. Provider-backed live ASR is implemented but has not been exercised with an account.
- **Business input:** all approved content and qualification rules are fictional. No employer-provided business script or website was available. Real documents may change both flow and retrieval behavior.
- **Speech:** browser ASR exposes no stable provider/model identification. Installed TTS voices vary. Full multilingual word-number normalization, barge-in, full-duplex turn-taking, and automatic diarization are absent.
- **Dialogue:** this is a narrow state machine and lexical answer selector. It handles demonstrated exact intent phrases, not arbitrary conversation. English number words below 100 are normalized; other spoken age formats may need digits. Corrections outside the age stage, compound intents, ambiguous callback dates, and negation deserve more coverage.
- **Handoff:** mock callback records live in session memory and exported JSON. No adviser is contacted; no phone number, CRM, calendar, payment flow, or eligibility decision is connected.
- **Knowledge:** pattern-based PII masking is incomplete. Saved HTML/CSV/text/JSON are exercised; optional PDF extraction is not. No OCR, multilingual embedding index, version-history service, general contradiction resolution, or dynamic crawling is present.
- **Nudges:** phrase rules miss semantic variants. Confidence is not calibrated for provider audio. Silence filtering does not solve noisy ASR hallucinations. Topic tracking only follows matched signals; no general sentiment classifier exists.
- **Live audio:** four-second windows can split words. ScriptProcessor runs on the UI thread. Queues are bounded but failed windows are not retried automatically; stale advice is less useful than a visible error. ASR should be tested under slow networks and outages.
- **Deployment:** loopback only, ephemeral local token, no user accounts or durable storage. The standard-library server is not an internet-facing production host. There is no public hosted demo URL. The GitHub repository is public; its local demo still requires running the backend.

## Next steps in order

1. Replace fictional material with approved business sources, resolve conflicting policy statements, and add adversarial/held-out retrieval cases.
2. Run all planned recordings, native-speaker reviews, and regional-accent comparisons. Measure ASR errors on numbers and finance terms; tune dialogue from observed failures.
3. Replace browser voice services with a controlled ASR/TTS stack and language-specific model/voice configuration. Add number normalization and safe repair questions before moving to richer generation.
4. Use AudioWorklet or a streaming telephony bridge, contextual ASR across window boundaries, automatic channel attribution, and explicit backpressure/circuit breakers.
5. Add durable session/action storage, idempotent real CRM delivery, authentication, audit history, secrets management, encryption, retention, access control, and consent records.
6. Evaluate semantic retrieval and signal models against the deterministic baseline. Add a model only where it improves a measured failure without increasing unsupported answers or false alerts.
7. Load-test the complete path at 10× concurrency. Report P50/P95, dropped windows, cost per call-minute, ASR rate limits, and usefulness at arrival.

No native-language or regulatory compliance claim is made. Market-specific wording, disclosures, consent practices, collection conduct, and product statements require qualified local review before a real deployment.
