# Submission checklist

**The current package is not yet a complete assessment submission.** Code, documentation, synthetic inputs, and text evaluations are included. The required recorded evidence, account-backed ASR checks, and accessible links still need to be completed.

## What is already included

- Runnable local web app with a shared KB and source-cited responses.
- Philippine English, Filipino/Taglish, and Indonesian dialogue settings.
- Explicit screening, conflict handling, unsupported-answer fallback, consent, and mock callback flow.
- JSON/HTML/CSV/text inputs; ingestion report, review queue, 22 approved records, schema, taxonomy, hashes, and retrieval evidence.
- Optional provider-backed live microphone transcription with nudge controls and timing export.
- Automated tests, text evaluations, simulated transcripts labeled as simulations, and GitHub Actions configuration.
- `.env.example`, setup instructions, architecture diagram, localization notes, known limitations, walkthrough outline, email draft, and interview preparation.

## Before replying to the recruiter

| Required item | Current status | Completion action |
|---|---|---|
| Actual business script / rules / sources | Not supplied | Obtain them if available, replace fictional content, rerun tests |
| Public/access-granted GitHub repository | Private draft; see repository link in README | Add reviewer access or make public after evidence review |
| Web calling interface | Local implementation | Verify microphone/TTS in a supported browser; share setup and preferably a working hosted implementation if time permits |
| Q1 three recorded calls | Missing | Run Q1-01 through Q1-03; include both sides, transcript, and actual result |
| Q2 retrieval evidence | Included | Review source matches and add actual business queries if sources change |
| Q3 two PH calls | Missing | Run PH-01 and PH-02 with code-switching and fallback |
| Q3 two ID calls + regional accent | Missing | Use a real consenting non-Jakarta regional speaker in ID-02 |
| ASR observations and TTS compromises | Missing | Complete the report from recordings; record exact errors |
| Q4 live audio recording and metrics | Missing | Run configured microphone pipeline; show nudges before stop; export P50/P95/component data |
| Real-audio false-positive review | Missing | Label real windows, report errors and sample size |
| Video walkthrough | Missing | Record the 5–7 minute outline after functional checks |
| Accessible links | Not checked | Test every URL in a signed-out/private browser |
| Reply in original email thread | Not sent | Paste the final reviewed email, preserving the thread |

Seven separate calls make coverage easy to audit. If you reuse recordings across Q1 and Q3, explicitly map each requirement to a time range and preserve each question's minimum coverage. Q4 may reuse call audio only if replayed at real-time speed through a working streaming path; this build uses live microphone input instead.

## Publish or update the repository

The prepared draft is private. In the existing checkout, use `git add`, `git commit`, and `git push` to update it. The full initialization commands below are only for creating a new repository elsewhere. Do not rerun `gh repo create` for an existing repository.

GitHub CLI authentication is available on the preparation machine. On another machine, authenticate yourself; do not paste tokens into the conversation or commit them.

```bash
gh auth login
cd /path/to/bridgecall
git init -b main
git add .
git status --short
# Inspect what will be committed, especially evidence and any new files.
git commit -m "Build grounded voice and live coaching assessment prototype"
gh repo create bridgecall-assessment --public --source=. --remote=origin --push
```

Use private visibility plus explicit reviewer access if the assessment contains confidential source material. The supplied fictional package is designed to be shareable. Do not publish real customer information, private assessment attachments, credentials, or unconsented voices. The `.gitignore` excludes local secrets and recording directories.

GitHub Pages cannot run this Python backend. Do not upload only the static UI and call that a working voice demo. A hosted deployment needs a proper application server, HTTPS, authentication/rate limits, and secret configuration. Until then, link the repository's local setup and a verified demo video. A recruiter cannot access your `localhost` URL.

## Organize evidence links

Recommended folder:

```text
01_walkthrough.mp4
02_calls/
  Q1-01.mp4 + Q1-01-transcript.json + Q1-01-result.md
  ... all seven planned tests
03_live_insights/
  live-demo.mp4 + call.wav + observations.json + latency-report.json
04_asr_review/
  language-and-accent-report.md + references/ + hypotheses/
```

Put verified URLs in `evidence/submission-manifest.json`. Run:

```bash
python3 -m scripts.check_submission
```

This validates required fields, not network access or audio authenticity. Open every final link while signed out. Check download/playback, sharing scope, expiry, filenames, matching transcripts, secret exposure, and whether both sides can be heard. Add the actual links near the top of README before publishing your final version.

## Suggested order for the remaining work

1. Run and understand the app. Confirm source data and scope with the assessment issuer if necessary.
2. Configure ASR and test a short microphone window before spending time recording full calls.
3. Resolve missing native voices and recruit the regional-accent tester early.
4. Record calls, write honest results, and calculate ASR and live metrics.
5. Record the walkthrough and replace pending manifest fields.
6. Publish, check links signed out, and send the reply in the original thread.

The assessment deadline is 48 hours from receipt; that receipt time was not provided. Calculate the actual deadline from the original email, not this package's creation date.
