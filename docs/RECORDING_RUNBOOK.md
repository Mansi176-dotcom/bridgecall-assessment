# Recording runbook

## Before recording

Use consenting testers and fictional details. Verify microphone access, the selected language, installed TTS, and browser ASR. Keep API keys and account dashboards out of the video. The web app's recording button captures the **microphone only**. For complete two-sided calls, use a screen recorder configured to capture system audio plus microphone, then play back a short sample to verify both are audible. Do not discover missing system audio after seven tests.

Save recordings in `recordings/` or `private-evidence/` (both ignored by git). Export each transcript from the app. Reviewed shareable media can be hosted in a separate folder or release and linked in `evidence/submission-manifest.json`. Never substitute `simulated-transcripts.json` for real recorded-call transcripts.

## Seven planned calls

Each can be 60–120 seconds; speak naturally and test the actual result. The exact sample dates below are fixtures; choose an appropriate future date before recording.

| ID | Setting | Customer sequence / expected evidence |
|---|---|---|
| Q1-01 | English PH | Yes → age 28 → resident yes → beneficiary question → callback yes → local date/time → confirm yes. Show citation and mock action. |
| Q1-02 | English PH | Yes → “The premium is expensive” → “Does coverage include cancer surgery?” → “I want a human” → consent and callback. Show objection, unsupported answer, honest escalation. |
| Q1-03 | English PH | Yes → “I am 22… or 32” → correct to 32 → resident yes → callback no. Show conflict clarification and no action without consent. |
| Q3-PH-01 | Filipino / Taglish | “Oo po” → age 29 → residency yes → “Mahal ang premium, may budget option ba?” → callback. Note ASR errors in finance terms. |
| Q3-PH-02 | Filipino / Taglish | “Ano ang bank referral?” → “Paano ang rider?” → “Gusto ko ng tao.” Finish localized escalation. Include colloquial speech and a fallback question. |
| Q3-ID-01 | Formal Bahasa | “Ya” → “Berapa denda kalau telat?” → “Jelaskan tenor dan DP” → preferred time with WIB → confirm. No invented fee. |
| Q3-ID-02 | Natural regional speaker | A consenting speaker with a non-Jakarta accent says “Saya belum gajian, nggak bisa bayar cicilan,” asks about DP/tenor, requests petugas, and confirms a timezone. Capture accent observations against the human transcript. |

If browser ASR writes number words that the simple age parser cannot parse, note the failure and use digits as a demonstrated fallback. Do not silently edit the transcript to conceal ASR mistakes. Record what happened, then explain the fix you would make.

## Q4 live demo sequence

1. Configure the API key locally and restart. Select a locale. Open Live insights and **Reset coach session**. Start screen recording with microphone audio.
2. Start the live microphone after tester consent. Keep the live status visible.
3. Select **Human agent being coached**, then say “What is your age?” before a disclosure. Observe the missing-disclosure nudge.
4. Say “This is an automated demo. May I continue?” Then wait for its window to be processed. Ask age again: the disclosure reminder should no longer fire.
5. Say “You will get guaranteed approval.” Observe the correction nudge. This is a deliberately risky test statement, not a product claim.
6. Select **Customer** before the next complete utterance. Say “I have a second vehicle.” Observe the opportunity nudge. Repeat it immediately: cooldown should suppress the duplicate.
7. Say “I am frustrated; this is the third time.” Observe the frustration nudge. Say “I cannot pay this month” to exercise support.
8. Record quiet/background-noise windows and ordinary unrelated speech. Log any false positives honestly. The text-only low-confidence checkbox does not prove noisy-audio handling.
9. Continue long enough to collect at least 30–50 windows if feasible. Keep the browser foreground to avoid rendering throttling.
10. Stop, save the WAV, wait for “Stopped,” and export evidence. Generate the latency summary with the script. Verify a nudge is visible **before** stopping capture in the screen recording.

The coach can process a live, role-played call. It need not be connected to the bot. The current app does not replay an uploaded recording, so do not describe it as replay mode.

## For every recording

Record test ID, date, locale, tester consent, provider or browser version, TTS voice, expected behavior, actual behavior, pass/partial/fail, error/fallback notes, and links to audio and transcript. A useful result describes one observed error precisely, such as a misrecognized amount, rather than saying “95% accurate” without labels.
