"""Reproducible fixture evaluation. No audio or native-speaker quality claims."""

import json, platform, time, math
from app.kb import KnowledgeBase, ROOT
from app.agent import Agent
from app.nudges import NudgeEngine

QUERIES = [
    (
        "What coverage does the life insurance product provide?",
        "PH",
        "en-PH",
        "ph-product",
    ),
    ("Who is eligible based on age?", "PH", "en-PH", "ph-qualification"),
    (
        "What happens if my policy lapses after a missed premium?",
        "PH",
        "en-PH",
        "ph-lapse",
    ),
    ("What is a beneficiary?", "PH", "en-PH", "ph-beneficiary"),
    ("This is expensive and outside my budget", "PH", "en-PH", "ph-budget"),
    ("Mahal ang premium, may budget option ba?", "PH", "fil-PH", "ph-budget"),
    ("Ano ang bank referral?", "PH", "fil-PH", "ph-referral"),
    ("Kapan cicilan jatuh tempo?", "ID", "id-ID", "id-payment"),
    ("Berapa denda kalau telat?", "ID", "id-ID", "id-penalty"),
    ("Saya belum gajian, susah bayar", "ID", "id-ID", "id-budget"),
    ("Jelaskan tenor dan DP", "ID", "id-ID", "id-tenor"),
    ("Does coverage include cancer surgery?", "PH", "en-PH", None),
    ("What is the weather in Manila?", "PH", "en-PH", None),
]
CASES = [
    ("customer", "I have a second vehicle", 1, "cross_sell"),
    ("agent", "You will get guaranteed approval", 1, "risky_promise"),
    ("agent", "What is your age?", 1, "missing_disclosure"),
    ("customer", "I am frustrated; this is the third time", 1, "frustration"),
    ("customer", "I cannot pay this month", 1, "payment_difficulty"),
    ("customer", "Please call me tomorrow", 1, "callback"),
    ("customer", "I want to apply", 1, "buying_signal"),
    ("customer", "Saya belum gajian", 1, "payment_difficulty"),
    ("customer", "Saya punya motor kedua", 1, "cross_sell"),
    ("customer", "Nakakainis, paulit ulit", 1, "frustration"),
    ("customer", "I have a second vehicle", 0.3, None),
    ("customer", "[noise] second vehicle", 1, None),
    ("customer", "maybe I heard second vehicle", 1, None),
    ("agent", "We do not promise guaranteed returns", 1, None),
    ("agent", "The customer said guaranteed approval", 1, None),
    ("customer", "Do you offer guaranteed approval?", 1, None),
    ("customer", "I do not have a second vehicle", 1, None),
    ("customer", "Thank you for explaining", 1, None),
    ("agent", "This is an automated demo", 1, None),
    ("customer", "I paid my installment yesterday", 1, None),
]
SCENARIOS = {
    "Q1-01-cooperative": (
        "PH",
        "en-PH",
        [
            "yes",
            "28",
            "yes",
            "What is a beneficiary?",
            "yes",
            "25 September at 3 pm",
            "yes",
        ],
    ),
    "Q1-02-objection": (
        "PH",
        "en-PH",
        [
            "yes",
            "The premium is expensive",
            "Does coverage include cancer surgery?",
            "I want a human",
            "yes",
            "25 September at 4 pm",
            "yes",
        ],
    ),
    "Q1-03-conflict": ("PH", "en-PH", ["yes", "22 or 32", "32", "yes", "no"]),
    "Q3-PH-01-taglish": (
        "PH",
        "fil-PH",
        [
            "oo",
            "29",
            "oo",
            "Mahal ang premium, may budget option ba?",
            "oo",
            "25 Setyembre alas tres ng hapon",
            "oo",
        ],
    ),
    "Q3-PH-02-human": (
        "PH",
        "fil-PH",
        [
            "oo",
            "Ano ang bank referral?",
            "Gusto ko ng tao",
            "oo",
            "26 Setyembre alas dos ng hapon",
            "oo",
        ],
    ),
    "Q3-ID-01-formal": (
        "ID",
        "id-ID",
        ["ya", "Berapa denda kalau telat?", "ya", "25 September jam 10 WIB", "ya"],
    ),
    "Q3-ID-02-colloquial": (
        "ID",
        "id-ID",
        [
            "iya",
            "Saya belum gajian, nggak bisa bayar cicilan",
            "Jelaskan tenor dan DP",
            "mau petugas",
            "ya",
            "26 September jam 9 WITA",
            "ya",
        ],
    ),
}


def percentile(values, p):
    return sorted(values)[max(0, math.ceil(len(values) * p) - 1)]


def main():
    kb = KnowledgeBase()
    out = ROOT / "evidence"
    out.mkdir(exist_ok=True)
    retrieval = []
    for q, m, l, expected in QUERIES:
        hits = kb.search(q, m, l)
        answer = kb.answer(q, m, l)
        got = answer["record_id"] if answer else None
        correct = (
            got is None
            if expected is None
            else bool(got and got.startswith(expected + "-"))
        )
        retrieval.append(
            {
                "question": q,
                "market": m,
                "language": l,
                "expected": expected,
                "retrieved": [
                    {
                        k: r[k]
                        for k in ("record_id", "source", "content", "score", "matched")
                    }
                    for r in hits
                ],
                "selected": got,
                "verdict": "correct" if correct else "incorrect",
                "relevance_explanation": (
                    "Expected abstention on unsupported content"
                    if expected is None
                    else "Expected topic: "
                    + expected
                    + "; lexical matches recorded above."
                ),
            }
        )
    nudge = []
    durations = []
    for speaker, text, confidence, expected in CASES:
        start = time.perf_counter()
        result = NudgeEngine().process(text, speaker, confidence)
        elapsed = (time.perf_counter() - start) * 1000
        durations.append(elapsed)
        actual = [n["rule"] for n in result["nudges"]]
        nudge.append(
            {
                "speaker": speaker,
                "text": text,
                "confidence": confidence,
                "expected": expected,
                "actual": actual,
                "pass": actual == ([expected] if expected else []),
                "signal_ms": elapsed,
            }
        )
    tp = sum(bool(r["expected"]) and r["expected"] in r["actual"] for r in nudge)
    fp = sum(not r["expected"] and bool(r["actual"]) for r in nudge)
    tn = sum(not r["expected"] and not r["actual"] for r in nudge)
    fn = sum(bool(r["expected"]) and r["expected"] not in r["actual"] for r in nudge)
    summary = {
        "evidence_type": "synthetic_text_fixtures_only",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "retrieval_correct": sum(r["verdict"] == "correct" for r in retrieval),
        "retrieval_total": len(retrieval),
        "nudge_cases": len(nudge),
        "nudge_pass": sum(r["pass"] for r in nudge),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "fixture_false_positive_rate": fp / max(1, fp + tn),
        "text_signal_latency_ms": {
            "p50": percentile(durations, 0.5),
            "p95": percentile(durations, 0.95),
        },
        "audio_asr_latency": None,
        "audio_end_to_end_latency": None,
        "native_speaker_validation": "not performed",
        "warning": "Small authored regression fixtures; not real-call accuracy, not ASR benchmarking, not live-audio evidence.",
    }
    (out / "retrieval-results.json").write_text(
        json.dumps(retrieval, indent=2, ensure_ascii=False)
    )
    (out / "nudge-results.json").write_text(
        json.dumps(nudge, indent=2, ensure_ascii=False)
    )
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    transcripts = {}
    for name, (m, l, turns) in SCENARIOS.items():
        a = Agent(kb, m, l)
        a.respond("")
        for text in turns:
            a.respond(text)
        transcripts[name] = {
            "evidence_type": "scripted_text_simulation_not_a_recorded_call",
            "market": m,
            "language": l,
            "turns": a.events,
        }
    (out / "simulated-transcripts.json").write_text(
        json.dumps(transcripts, indent=2, ensure_ascii=False)
    )
    lines = [
        "# Reproducible text evaluation",
        "",
        "These results come from authored text fixtures. No recordings or ASR quality claims are implied.",
        "",
        "| Check | Result |",
        "|---|---|",
        f"| Retrieval + abstention | {summary['retrieval_correct']}/{len(retrieval)} |",
        f"| Nudge fixture checks | {summary['nudge_pass']}/{len(nudge)} |",
        f"| Nudge TP / FP / TN / FN | {tp} / {fp} / {tn} / {fn} |",
        f"| Signal-only latency P50 / P95 | {summary['text_signal_latency_ms']['p50']:.3f} / {summary['text_signal_latency_ms']['p95']:.3f} ms |",
        "| Audio → display P50 / P95 | Not measured; run live audio |",
        "",
        "## Retrieval cases",
        "",
        "| Question | Selected record | Verdict |",
        "|---|---|",
    ]
    for r in retrieval:
        lines.append(
            f"| {r['question']} | {r['selected'] or 'ABSTAIN'} | {r['verdict']} |"
        )
    lines += [
        "",
        "Full retrieved chunks, scores, source references, and relevance explanations are in `retrieval-results.json`.",
        "",
        summary["warning"],
    ]
    (out / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(summary, indent=2))
    if summary["retrieval_correct"] != len(retrieval) or summary["nudge_pass"] != len(
        nudge
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
