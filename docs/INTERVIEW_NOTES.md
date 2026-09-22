# Be ready to explain your own submission

The assessment explicitly rewards AI-tool usage and independent thinking. You do not need to disguise assistance. You do need to understand, test, and take responsibility for the submitted code. Natural writing comes from concrete decisions and observed failures, not hiding how a draft was produced.

## Seven questions to rehearse

**Why not put the FAQs in a system prompt?**
The business answer is retrieved from versioned records. The same source is inspectable in the UI and attached to the response. Conversation prompts handle turns and consent, not the policy knowledge.

**Is this RAG?**
It is retrieval-grounded response selection. It does not use a generative answer model. An ASR model converts live audio to text; deterministic logic retrieves an approved answer or produces a fallback. Calling it LLM RAG would overstate the implementation.

**Why no vector database?**
The corpus has 23 language-specific chunks. Lexical search is sufficient for a baseline, cheap to run, and easy to inspect. It misses paraphrases. A larger corpus needs a held-out comparison before adopting embeddings and a reranker.

**How do you know it doesn't invent policy details?**
It returns reviewed text instead of generating new business claims. That reduces invention, but it can still retrieve the wrong passage or inherit a bad source. Source review, gating, and evaluation matter; “zero hallucinations” would be too strong.

**Is the nudge pipeline actually live?**
The microphone is cut into rolling windows while recording continues. Each is transcribed and analyzed before the session stops. Prove this with the live recording and timing export. Text-entry tests alone do not answer this question.

**How is latency measured?**
A monotonic browser clock measures capture-window start to display. Server monotonic durations measure provider round trip and rule processing. The app never subtracts server wall time from browser wall time. Four seconds of buffering belongs in the reported total.

**What is the weakest part?**
Answer from your observed test results. Before audio testing, the honest answer is that multilingual ASR, regional-accent handling, native TTS availability, and live-audio latency have not been validated. Afterwards, name a precise observed failure and the repair you would prioritize.

## Thirty-minute ownership exercise

1. Trace a beneficiary question through `web/app.js`, `/api/turn`, `Agent.respond`, and `KnowledgeBase.answer`.
2. Change one approved FAQ, increase its version, regenerate, and verify the new source hash/citation.
3. Add a negative nudge example that should not fire. Explain any false alert and improve the rule.
4. Change the fictional age rule and predict which boundary checks will fail.
5. Reproduce the complete callback path, including a declined confirmation.
6. Explain which components make external requests and where secrets are loaded.

Only claim changes or observations you actually made. In an AI-usage question, a candid answer can be: “I used AI assistance for scaffolding and review. I validated [specific parts], changed [actual changes], and can explain the remaining limitations.” Fill those details from your work; don't memorize invented ownership claims.
