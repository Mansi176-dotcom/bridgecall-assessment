# Walkthrough outline — target 5–7 minutes

Use this as a prompt, not a speech to read word-for-word. Replace the bracketed observations only after performing the tests. Do not say the audio pipeline was measured until it was.

**0:00–0:35 — Show the product first.**

“Bridgecall connects a small, reviewed knowledge base to a voice conversation and a live coaching view. I used fictional businesses because the source pack wasn't included. The behavior I wanted to get right was simple: answer from a traceable source, or say the information isn't available.”

**0:35–1:40 — Demonstrate Q1 and Q2 together.**

Start an English call, ask about a beneficiary, and show the citation. Open the retrieved record. Ask whether cancer surgery is covered, then request a human. Explain that the callback is a local mock action and requires consent and confirmation. Show one conflicting-age or opt-out case.

**1:40–2:25 — Explain the architecture and one tradeoff.**

Show the Mermaid diagram. Point out the shared KB, explicit conversation state, and separate audio-coaching route. Explain why the answer is an approved passage instead of a generated paraphrase, and where that becomes limiting. Mention the small corpus and the reason for lexical retrieval.

**2:25–3:30 — Show language behavior.**

Play brief excerpts from the PH and ID calls. Point out Taglish finance words, respectful tone, an Indonesian timezone confirmation, and a localized fallback. Describe the actual regional-speaker test and a concrete observed error. If a native TTS voice was unavailable, state that rather than presenting English TTS as native.

**3:30–4:50 — Demonstrate live nudges.**

With live status visible, speak a missed-disclosure or risky statement and a second-vehicle opportunity. Show nudges arriving before the session ends. Repeat the phrase to show cooldown. Open exported metrics and distinguish capture-to-display from provider round-trip time. Say the actual P50/P95 and sample size, not the text-rule timings.

**4:50–5:40 — Evidence and limitations.**

Show test results and one recording/transcript pair. Explain a false positive or failed case if one occurred. State that a small fixture suite is not production accuracy. Show the limits: fictional policy data, narrow dialogue, manual speaker attribution, installed voices, and no real CRM delivery.

**5:40–6:15 — What you would improve first.**

“I would first fix the failures observed in the real recordings: [specific error]. Then I'd improve streaming and add a durable action store. I'd evaluate semantic retrieval on a held-out set before replacing the current baseline.”

Avoid claims such as “production-ready,” “fluent in all accents,” “zero hallucinations,” or “100% accurate.” Show the behavior and evidence that support the narrower claim.
