"""Simple case-folded word error rate; no claim of native-language segmentation quality."""

import re, sys, json
from pathlib import Path


def words(text):
    return re.findall(r"\w+", text.casefold())


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python -m scripts.wer reference.txt hypothesis.txt")
    a, b = (words(Path(p).read_text()) for p in sys.argv[1:])
    if not a:
        raise SystemExit("Reference transcript is empty")
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        row = [i]
        for j, y in enumerate(b, 1):
            row.append(min(row[-1] + 1, prev[j] + 1, prev[j - 1] + (x != y)))
        prev = row
    print(
        json.dumps(
            {
                "reference_words": len(a),
                "hypothesis_words": len(b),
                "edit_distance": prev[-1],
                "wer": prev[-1] / len(a),
                "normalization": "Unicode word tokens and casefold; no number normalization",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
