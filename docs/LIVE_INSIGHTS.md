# Live insights: mechanism and measurement

## What qualifies as live here

The browser captures a microphone continuously and cuts it into independent approximately four-second PCM16 WAV windows. Each complete WAV is transcribed over HTTP while later audio is still being captured. Nudges render as each response arrives, before the live session ends. This is rolling-window ASR, not token-level streaming ASR or post-call upload. Four seconds of capture delay is included in reported timing. Short final windows are sent on stop.

Text entry goes to a separate endpoint and carries `mode: text_only`. The checked-in scripted transcripts and signal timings cannot establish Q4 audio success. A screen recording and exported `live_audio` observations are required.

The microphone path uses a browser ScriptProcessorNode for a minimal dependency-free prototype. It runs on the UI thread and is deprecated. An AudioWorklet and a real streaming provider connection are production improvements. Independent WAV windows avoid the invalid-container problem caused by treating arbitrary MediaRecorder fragments as standalone files, but may split words and lose context.

## Signals and control

| Signal | Trigger example | Response |
|---|---|---|
| Missing disclosure | Agent asks age without prior demo disclosure | Introduce the automated demo before screening |
| Risky promise | Agent says “guaranteed approval” | Correct the statement and refer to verified terms |
| Payment difficulty | “belum gajian”, “cannot pay” | Acknowledge and offer support review |
| Frustration | “third time”, “kesal” | Pause, acknowledge, offer human assistance |
| Missed opportunity | “second vehicle”, “motor kedua”, “anak ko” | Ask permission to explore the additional need |
| Buying signal | “want to apply” | Proceed to screening without promises |
| Callback | “hubungi besok” | Confirm date, time, timezone, consent |

These are transparent phrase rules, not broad emotion recognition. Topic labels update on matched signals. Sarcasm, indirect concerns, complex negation, and within-window multiple topics can be missed. Coaching text is for the reviewer/agent and is currently English; customer-facing fallback language stays localized.

Controls: explicit text-test confidence floor 0.75; ambiguous/noise markers; pre-ASR RMS silence threshold 0.008; 25-second per-rule cooldown; 20-second expiry; one active nudge per topic, with higher priority able to replace lower; role-specific compliance rules; short-range negation checks; a three-window waiting queue; duplicate chunk IDs rejected on the server; a five-minute recording cap in the UI.

The transcription adapter does not return calibrated ASR confidence. The value passed to rules for audio is not an accuracy estimate; exports mark confidence unavailable. The RMS filter cannot distinguish all noise from speech. Testing actual noisy recordings is essential.

## Clock definitions

All user-visible end-to-end timing uses the browser's monotonic clock. Server component durations use the server's monotonic clock; absolute timestamps across machines are never subtracted.

- **Capture to display:** start of the audio window → two animation frames after the response and nudges are inserted. Includes capture, queue wait, upload, provider time, signal detection, and UI scheduling. It approximates paint completion; background tab throttling can inflate it.
- **ASR:** server request start → parsed transcription response. Includes provider/network time, not microphone capture.
- **Signal:** start/end of rule processing.
- **LLM:** 0 ms, `llm_used: false`. No LLM runs in this path.
- **Delivery residual:** browser request-to-display minus measured total server duration. Includes upload/download and browser work; it is not a pure network measurement.
- **`window_ms`:** capture-start to send; includes queue/base64 overhead. Do not interpret it as exact voiced duration.

The UI shows P50/P95 of all completed live audio windows, including windows without a nudge. The exported report also supports nudge-bearing-window percentiles. Dropped, suppressed, and failed windows are separate observations and must be counted, not hidden as successful low-latency samples.

Run at least 30–50 windows under the same conditions, retain raw rows, and report sample size and network/browser/provider settings. Use `python3 -m scripts.summarize_live PATH_TO_EXPORTED_JSON` to generate a latency report. If there are no actual live audio rows, the script refuses to produce audio metrics.

## Quality evidence

The checked-in 20 text cases contain 10 positive and 10 negative/noisy fixtures. Their measured confusion matrix is in `evidence/summary.json`. They are regression tests, not an independent estimate of call-level precision. The package makes no measured real-audio false-positive or accent-quality claim.

For the live run, label each window with an expected signal, compare the display with the reference, then report TP, FP, TN, and FN. Also record duplicate/late alerts and whether a nudge remained useful by arrival. A signal fired on a misrecognized word is still a false positive.

## At 10× load

A four-second window produces approximately 15 ASR requests/minute per continuously active call, before silence suppression. Ten such calls can produce about 150 requests/minute. This is workload arithmetic, not a measured capacity claim. The local threaded server and in-memory sessions are not a scale architecture.

Move capture off the UI thread, stream audio through a session-aware gateway, bound concurrency per tenant, apply backpressure before queues become stale, and keep expiring state in a shared store. Use persistent authenticated sessions, metrics for dropped windows, encrypted storage with retention, regional processing decisions, and a provider outage circuit breaker. Benchmark noise, overlapping speakers, accents, and request limits before scaling.
