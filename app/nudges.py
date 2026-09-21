"""Conservative, explainable streaming signal rules; no generative model in latency path."""

import re, time, uuid

RULES = [
    (
        "risky_promise",
        "compliance",
        100,
        "agent",
        r"\b(guaranteed approval|guaranteed returns|pasti disetujui|pasti untung)\b",
        "Correct the claim. Explain that approval and benefits require verified terms.",
    ),
    (
        "payment_difficulty",
        "support",
        85,
        "customer",
        r"\b(cannot pay|can.t afford|missed salary|belum gajian|susah bayar|nggak bisa bayar|gak bisa bayar|walang pambayad|mahal)\b",
        "Acknowledge the payment concern; offer the approved adviser/support path. Do not promise a waiver.",
    ),
    (
        "frustration",
        "experience",
        90,
        "customer",
        r"\b(frustrated|angry|third time|stop repeating|nakakainis|kesal|berulang kali)\b",
        "Pause the script, acknowledge the concern, and offer human assistance.",
    ),
    (
        "cross_sell",
        "opportunity",
        50,
        "customer",
        r"\b(second vehicle|another vehicle|second motorcycle|motor kedua|mobil kedua|anak ko|new baby)\b",
        "Ask permission to explore the additional need with an adviser. No unverified offer or discount.",
    ),
    (
        "callback",
        "follow_up",
        60,
        "customer",
        r"\b(call me tomorrow|call back later|callback please|telepon besok|hubungi besok|tawag bukas)\b",
        "Confirm a local date, time, timezone, and callback consent.",
    ),
    (
        "buying_signal",
        "interest",
        45,
        "customer",
        r"\b(want to apply|ready to apply|interested in coverage|mau mengajukan|gusto kong kumuha)\b",
        "Confirm the need and move to screening; make no approval promise.",
    ),
]


class NudgeEngine:
    def __init__(self):
        self.last = {}
        self.disclosed = False
        self.active = {}
        self.history = []
        self.topic = None

    def process(self, text, speaker="customer", confidence=1.0, now=None):
        start = time.perf_counter()
        now = time.monotonic() if now is None else now
        self.active = {k: v for k, v in self.active.items() if v["expires_at"] > now}
        if confidence < 0.75 or re.search(
            r"\[inaudible\]|\[noise\]|not sure|maybe i heard", text, re.I
        ):
            return {
                "nudges": [],
                "suppressed": "low_confidence_or_ambiguous",
                "signal_ms": (time.perf_counter() - start) * 1000,
                "topic": self.topic,
            }
        if speaker == "agent" and re.search(
            r"automated demo|simulation|simulasi|automated assistant|automated na",
            text,
            re.I,
        ):
            self.disclosed = True
        proposals = []
        for rid, topic, priority, role, pattern, message in RULES:
            match = re.search(pattern, text, re.I)
            if speaker != role or not match:
                continue
            prefix = text[max(0, match.start() - 45) : match.start()].lower()
            if re.search(
                r"\b(no|not|never|without|isn.t|cannot promise|hindi|tidak|bukan)\b",
                prefix,
            ):
                continue
            # Reject hypothetical/reporting risk phrases instead of treating a quotation as an agent promise.
            if rid == "risky_promise" and re.search(
                r"you said|customer said|do not promise", text, re.I
            ):
                continue
            proposals.append((rid, topic, priority, message, match.group()))
        if (
            speaker == "agent"
            and not self.disclosed
            and re.search(
                r"\b(your age|your income|how old|usia|ilang taon)\b", text, re.I
            )
        ):
            proposals.append(
                (
                    "missing_disclosure",
                    "compliance",
                    95,
                    "Introduce the automated demo and obtain permission before screening.",
                    text,
                )
            )
        emitted = []
        for rid, topic, priority, message, evidence in sorted(
            proposals, key=lambda p: -p[2]
        ):
            self.topic = topic
            if now - self.last.get(rid, -1e10) < 25:
                continue
            existing = self.active.get(topic)
            if existing and existing["priority"] >= priority:
                continue
            item = {
                "id": str(uuid.uuid4()),
                "rule": rid,
                "topic": topic,
                "priority": priority,
                "message": message,
                "evidence": evidence,
                "confidence": confidence,
                "expires_at": now + 20,
                "ttl_ms": 20000,
            }
            self.last[rid] = now
            self.active[topic] = item
            emitted.append(item)
            self.history.append(item)
        return {
            "nudges": emitted,
            "topic": self.topic,
            "signal_ms": (time.perf_counter() - start) * 1000,
            "llm_ms": 0.0,
            "llm_used": False,
        }
