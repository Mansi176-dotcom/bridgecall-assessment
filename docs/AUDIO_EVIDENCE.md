# Audio evidence — recordings, measurements, and failures

The recordings below are **synthetic audio-in/audio-out sessions**, not human phone calls. Customer TTS passes through actual faster-whisper base ASR; the recognized words drive the real Agent; its response is synthesized. Dialogue tracks concatenate turns and exclude computation pauses, so they do not demonstrate conversational latency. The independent browser replay measures actual elapsed time.

## Watch first

- [Narrated walkthrough (MP4)](../evidence/video/walkthrough.mp4) · [direct download](https://raw.githubusercontent.com/Mansi176-dotcom/bridgecall-assessment/main/evidence/video/walkthrough.mp4) · [transcript](../evidence/video/walkthrough-transcript.md) · [captions](../evidence/video/walkthrough.vtt). Narration is synthetic, not the candidate's recorded voice.
- [Actual live UI capture (47-second MP4)](../evidence/video/live-demo.mp4) · [direct download](https://raw.githubusercontent.com/Mansi176-dotcom/bridgecall-assessment/main/evidence/video/live-demo.mp4). Frames were captured while the browser processed the real-time replay. The original playback WAV was muxed afterward; start alignment is approximate. This is a sampled screen capture, not continuous 30-fps capture.
- [Live screenshot](screenshots/08-live-audio.png), [raw observations](../evidence/live-replay.json), and [latency summary](../evidence/live-latency-summary.json).

## Recorded dialogue tests

Whisper base, CPU int8, beam size 1; gTTS 2.5.4 in English, Filipino (`tl`), or Indonesian. No native-speaker TTS quality rating was performed. A pass below means the expected terminal state was reached, not that every answer or intent was correct. JSON links contain both the original text and actual recognition, source citations, actions, and timeline positions. The PH-02 filename contains “human” because the scenario requests a human handoff; its speaker is synthetic.

| Scenario | Recording | Actual ASR + response log | Outcome |
|---|---|---|---|
| Q1-01-cooperative | [MP3](../evidence/audio/Q1-01-cooperative.mp3) | [JSON](../evidence/audio/Q1-01-cooperative.json) | pass — done |
| Q1-02-objection | [MP3](../evidence/audio/Q1-02-objection.mp3) | [JSON](../evidence/audio/Q1-02-objection.json) | pass — done |
| Q1-03-conflict | [MP3](../evidence/audio/Q1-03-conflict.mp3) | [JSON](../evidence/audio/Q1-03-conflict.json) | pass — closed |
| Q3-PH-01-taglish | [MP3](https://raw.githubusercontent.com/Mansi176-dotcom/bridgecall-assessment/9d0dec45bb0fa57d9e1024808c6a2b936f2ca813/evidence/audio/Q3-PH-01-taglish.mp3) | [JSON](../evidence/audio/Q3-PH-01-taglish.json) | partial — permission |
| Q3-PH-02-human | [MP3](../evidence/audio/Q3-PH-02-human.mp3) | [JSON](../evidence/audio/Q3-PH-02-human.json) | partial — consent |
| Q3-ID-01-formal | [MP3](../evidence/audio/Q3-ID-01-formal.mp3) | [JSON](../evidence/audio/Q3-ID-01-formal.json) | partial — time |
| Q3-ID-02-colloquial | [MP3](../evidence/audio/Q3-ID-02-colloquial.mp3) | [JSON](../evidence/audio/Q3-ID-02-colloquial.json) | partial — time |

### A failure that changed the implementation

Indonesian ASR expanded WIB/WITA into “waktu Indonesia Barat/Tengah.” The original parser only accepted abbreviations, leaving both callback flows in the time state. The parser now accepts the three spoken timezone names, with tests preserving explicit confirmation before any mock action.

- **Q3-ID-01-formal: pass**, final state `done`. [Rerun audio](../evidence/audio-after-fix/Q3-ID-01-formal.mp3) · [Rerun log](../evidence/audio-after-fix/Q3-ID-01-formal.json).
- **Q3-ID-02-colloquial: pass**, final state `done`. [Rerun audio](../evidence/audio-after-fix/Q3-ID-02-colloquial.mp3) · [Rerun log](../evidence/audio-after-fix/Q3-ID-02-colloquial.json).

The original failures are retained above. The colloquial run still misrecognizes finance terms and “mau petugas”; reaching a callback does not establish correct recognition of every intent. Filipino “oo” was heard as “Oh,” and spoken age/consent phrases were unreliable. Ambiguous audio does not count as consent. Those PH sessions remain partial; we did not rewrite failed transcripts into successes.

## Real-time replay: measured results

One 40-second run, 10 four-second windows, local macOS ARM64 CPU, faster-whisper 1.2.1/base/int8. Model loaded before replay; first inference initialization remains in the reported samples. Synthetic speech plus one non-speech noise window; manually labeled channels. Browser timing spans the start of each audio window through UI scheduling after the ASR response. It includes window accumulation and queue delay. Percentiles use nearest rank; with only 10 windows P95 is the maximum.

| Component | P50 | P95 |
|---|---:|---:|
| Audio window start → display | 4,911.40 ms | 8,727.40 ms |
| ASR | 877.36 ms | 4,658.61 ms |
| Signal rules | 0.062 ms | 2.673 ms |
| LLM | 0 ms (not used) | 0 ms (not used) |
| Delivery residual | 16.62 ms | 58.17 ms |

Component percentiles are independent and should not be added. Delivery residual includes transport, server overhead outside ASR/rules, and UI scheduling; it is not isolated network latency. The five nudge-bearing windows have P50 4,943 ms and P95 8,727.40 ms. The first nudge appeared about 8.73 seconds after replay start, before the 40-second audio ended.

Expected-versus-observed review: **TP 5, FN 1, TN 4, FP 0**. Duplicate opportunity advice was suppressed by cooldown. The missed payment-difficulty signal came from “I cannot pay this month” becoming “I cannot be this month.” Zero alerts on four negatives is not a reliable estimate of field false-positive rate. No windows were dropped or errored in this run. [Fixture](../data/demo/stream.json) records the expected rules before evaluation.

## Real human regional-accent playback

[INDspeech NEWS LVCSR](https://github.com/s-sakti/data_indsp_news_lvcsr) provides human Indonesian news recordings with source accent labels. Tested one Javanese-accented speaker (Ind006, source label J) and one standard speaker (Ind003, label U), three matched sentences per speaker selected before recognition. Each speaker has 28 reference word tokens. Javanese WER: **8/28 = 28.6%**; standard WER: **9/28 = 32.1%**.

[Full references, recognized words, audio hashes, archive paths, and timings](../evidence/regional-accent-results.json). This is actual human audio playback through ASR, not a synthesized accent. It is a tiny clean-news sample, not a finance call, an interactive regional-speaker test, native review, or evidence that one accent is easier. Original audio remains at its source; we do not redistribute the dataset, respecting the repository's additional request. Source license: CC BY-NC-SA 4.0. Citation: Sakti et al. (2008), Development of Indonesian Large Vocabulary Continuous Speech Recognition System within A-STAR Project, TCAST, pp. 19–24.

## Reproduce

Install `requirements-evidence.txt` in a Python 3.10+ virtual environment. Audio synthesis sends fictional scripts to Google Translate TTS; ASR runs locally after model download.

```bash
python -m scripts.run_audio_evaluation --cache .media-cache --models .model-cache
python -m scripts.evaluate_regional_accent --work .media-cache/accent --models .model-cache
python -m scripts.summarize_live evidence/live-replay.json
```

Existing dialogue JSON is reused; use `--output evidence/audio-new-run` to create fresh recordings with the current parser. Published `evidence/audio` preserves the pre-fix baseline. The regional script downloads source archives locally and never adds them to Git. Run the browser replay to collect a new real-time latency export; the summary command only analyzes an existing export.

## Remaining requirements

Human interactive calls, candidate-recorded narration, native-speaker review, reliable Filipino recognition, and regional-accent financial dialogue remain unverified. The corpus playback and synthetic dialogues are useful substitutes for development evidence, but do not satisfy all of those human evaluation requirements. Business content is fictional; callbacks are local mocks. No hosted calling endpoint is provided.
