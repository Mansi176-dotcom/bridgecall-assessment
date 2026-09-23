# Walkthrough transcript

Synthetic English narration; not a recording of the candidate.

## Bridgecall · engineering walkthrough

Bridgecall connects a reviewed knowledge base, localized conversation flows, and live coaching. This walkthrough uses synthetic narration. The application screenshots are actual captures. The evidence distinguishes generated audio, real time audio processing, and recordings of real people.

## Design choice · inspectable answers

One design choice is returning approved passages directly, instead of generating new financial product claims. Each supported answer has a source reference. Unsupported questions receive a fallback. A state machine keeps consent separate from qualification. This makes the prototype easy to inspect, with the tradeoff of narrow paraphrase handling.

## A failure and its correction

Audio testing found a concrete failure. The recognizer expanded W I B into waktu Indonesia Barat. The callback parser accepted the abbreviation but rejected the spoken phrase. The parser now accepts the three spoken Indonesian timezone names. Regression tests check that confirmation is still required. Original failed audio and corrected reruns are both retained.

## Real audio pipeline · measured in the browser

The companion live demo plays synthetic speech at real time speed. Every four second window passes through local Whisper before the browser displays a nudge. End to end latency was four point nine one seconds at the median, and eight point seven three seconds at the ninety fifth percentile, over ten windows. The capture interval is included. No language model is used for the nudge rules.

## Failures remain visible

Five expected signals were detected, one was missed, and four negative windows produced no alert. The missed signal came from hearing cannot pay as cannot be. Short Filipino consent words were also unreliable. The system keeps ambiguous speech out of the consent path. These are small authored tests, not claims of production accuracy.

## Regional accent · real published human speech

For a regional accent test, local Whisper transcribed published Indonesian news recordings: one Javanese accented speaker and one standard speaker, reading three matched sentences each. Word error rates were twenty eight point six and thirty two point one percent. This tiny sample cannot establish an accent ranking. The report links the original source and does not redistribute its recordings.

## Review the evidence

Start with the audio evidence report in the repository. It links seven synthetic dialogue recordings, the corrected Indonesian reruns, the live screen capture, and the regional accent results. Remaining work includes real interactive calls, native speaker review, stronger Filipino recognition, and deployment hardening. The business data is fictional and callbacks are local mocks.