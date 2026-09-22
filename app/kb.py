"""Traceable lexical retrieval. Only reviewed structured records may answer calls."""

import csv, hashlib, json, math, re, unicodedata
from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STOP = set(
    "a an the is are of to for in on this that it i my me can do does what how if when after happens your you ang po ng sa ano ba yang saya ini apa dan untuk please".split()
)


TERM_ALIASES = {
    "miss": "missed",
    "missing": "missed",
    "lapses": "lapse",
    "premiums": "premium",
}


def tokens(text):
    return [
        TERM_ALIASES.get(t, t)
        for t in re.findall(r"\w+", unicodedata.normalize("NFKC", text).lower())
        if t not in STOP
    ]


def redact(text):
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", "[EMAIL]", text)
    text = re.sub(r"(?<!\w)(?:\+?\d[\d ()-]{8,}\d)(?!\w)", "[PHONE_OR_ID]", text)
    text = re.sub(r"(?i)\b(name|nama|pangalan)\s*[:=]\s*[^\n,;]+", r"\1: [NAME]", text)
    return text


class MainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("nav", "footer", "header", "script", "style"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("nav", "footer", "header", "script", "style"):
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.parts.append(data.strip())


def ingest():
    raw = ROOT / "data/raw"
    processed = ROOT / "data/processed"
    processed.mkdir(exist_ok=True)
    records = []
    report = []
    seen = []
    # Curated source is the authority. Other extraction is staged for review, never auto-published.
    business = json.loads((raw / "business.json").read_text())
    for i, r in enumerate(business):
        date.fromisoformat(r["effective_date"])
        for lang, answer in r["answers"].items():
            content = redact(answer)
            digest = hashlib.sha256(content.encode()).hexdigest()
            records.append(
                {
                    **r,
                    "record_id": r["record_id"] + "-" + lang,
                    "language": lang,
                    "content": content,
                    "answers": None,
                    "source": f"data/raw/business.json#/{i}/answers/{lang}",
                    "source_sha256": hashlib.sha256(
                        (raw / "business.json").read_bytes()
                    ).hexdigest(),
                    "content_sha256": digest,
                    "pii_redacted": content != answer,
                    "status": "approved",
                }
            )
            seen.append(set(tokens(content)))
    staged = []
    for path in sorted(raw.iterdir()):
        if path.name == "business.json":
            continue
        try:
            if path.suffix == ".html":
                parser = MainText()
                parser.feed(path.read_text())
                parts = parser.parts
            elif path.suffix == ".csv":
                parts = [
                    " | ".join(f"{k}: {v}" for k, v in row.items())
                    for row in csv.DictReader(path.read_text().splitlines())
                ]
            elif path.suffix == ".json":
                parts = [json.dumps(json.loads(path.read_text()))]
            elif path.suffix == ".pdf":
                from pypdf import PdfReader

                parts = [page.extract_text() or "" for page in PdfReader(path).pages]
                if not any(p.strip() for p in parts):
                    raise ValueError("No text layer; OCR/manual review required")
            else:
                parts = path.read_text().split("\n\n")
            for index, part in enumerate(parts):
                content = redact(" ".join(part.split()))
                ts = set(tokens(content))
                if not ts:
                    continue
                duplicate = any(len(ts & s) / max(1, len(ts | s)) >= 0.88 for s in seen)
                suspicious = bool(
                    re.search(
                        r"ignore previous|password|guaranteed approval", content, re.I
                    )
                )
                status = (
                    "duplicate"
                    if duplicate
                    else "quarantined" if suspicious else "review_required"
                )
                report.append(
                    {
                        "source": path.name,
                        "section": index,
                        "status": status,
                        "pii_redacted": content != part,
                    }
                )
                if not duplicate:
                    staged.append(
                        {
                            "source": f"data/raw/{path.name}#section-{index}",
                            "content": content,
                            "status": status,
                        }
                    )
                    seen.append(ts)
        except Exception as exc:
            report.append(
                {
                    "source": path.name,
                    "status": "extraction_failed",
                    "error": type(exc).__name__,
                }
            )
    (processed / "records.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2)
    )
    (processed / "review_queue.json").write_text(
        json.dumps(staged, ensure_ascii=False, indent=2)
    )
    (processed / "ingestion_report.json").write_text(json.dumps(report, indent=2))
    return records


class KnowledgeBase:
    def __init__(self, records=None):
        self.records = records if records is not None else ingest()

    def search(self, query, market="PH", language="en-PH", limit=3):
        query_tokens = set(tokens(redact(query)))
        candidates = [
            r
            for r in self.records
            if r["market"] == market
            and r["language"] == language
            and r["status"] == "approved"
        ]
        docs = [
            Counter(tokens(r["title"] + " " + r["keywords"] + " " + r["content"]))
            for r in candidates
        ]
        avg = sum(map(lambda d: sum(d.values()), docs)) / max(1, len(docs))
        results = []
        for r, doc in zip(candidates, docs):
            score = 0.0
            matched = []
            for t in query_tokens:
                if t not in doc:
                    continue
                df = sum(t in d for d in docs)
                idf = math.log(1 + (len(docs) - df + 0.5) / (df + 0.5))
                tf = doc[t]
                score += (
                    idf
                    * tf
                    * 2.2
                    / (tf + 1.2 * (0.25 + 0.75 * sum(doc.values()) / max(1, avg)))
                )
                matched.append(t)
            if score > 0:
                results.append(
                    {**r, "score": round(score, 4), "matched": sorted(matched)}
                )
        return sorted(results, key=lambda x: (-x["score"], x["record_id"]))[:limit]

    def answer(self, query, market, language):
        hits = self.search(query, market, language)
        if not hits or hits[0]["score"] < 1.25:
            return None
        # A narrow deterministic intent gate prevents a lone generic word from authorizing an answer.
        domain = set(tokens(hits[0]["keywords"]))
        if not set(tokens(query)) & domain:
            return None
        # Do not answer unsupported specific pricing/benefit questions using a generic match.
        if re.search(
            r"cancer|diabetes|tax|deduct|surgery|cure|bitcoin|weather|cuaca|kanser|kanker",
            query,
            re.I,
        ):
            return None
        return hits[0]


if __name__ == "__main__":
    rows = ingest()
    print(f"Published {len(rows)} reviewed language-specific records.")
