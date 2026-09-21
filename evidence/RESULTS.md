# Reproducible text evaluation

These results come from authored text fixtures. No recordings or ASR quality claims are implied.

| Check | Result |
|---|---|
| Retrieval + abstention | 13/13 |
| Nudge fixture checks | 20/20 |
| Nudge TP / FP / TN / FN | 10 / 0 / 10 / 0 |
| Signal-only latency P50 / P95 | 0.020 / 0.378 ms |
| Audio → display P50 / P95 | Not measured; run live audio |

## Retrieval cases

| Question | Selected record | Verdict |
|---|---|
| What coverage does the life insurance product provide? | ph-product-en-PH | correct |
| Who is eligible based on age? | ph-qualification-en-PH | correct |
| What happens if my policy lapses after a missed premium? | ph-lapse-en-PH | correct |
| What is a beneficiary? | ph-beneficiary-en-PH | correct |
| This is expensive and outside my budget | ph-budget-en-PH | correct |
| Mahal ang premium, may budget option ba? | ph-budget-fil-PH | correct |
| Ano ang bank referral? | ph-referral-fil-PH | correct |
| Kapan cicilan jatuh tempo? | id-payment-id-ID | correct |
| Berapa denda kalau telat? | id-penalty-id-ID | correct |
| Saya belum gajian, susah bayar | id-budget-id-ID | correct |
| Jelaskan tenor dan DP | id-tenor-id-ID | correct |
| Does coverage include cancer surgery? | ABSTAIN | correct |
| What is the weather in Manila? | ABSTAIN | correct |

Full retrieved chunks, scores, source references, and relevance explanations are in `retrieval-results.json`.

Small authored regression fixtures; not real-call accuracy, not ASR benchmarking, not live-audio evidence.
