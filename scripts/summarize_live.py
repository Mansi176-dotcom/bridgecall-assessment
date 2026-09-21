"""Summarize real browser-exported audio observations; reject text-only substitutes."""

import json, math, sys
from pathlib import Path


def p(values, q):
    return sorted(values)[max(0, math.ceil(len(values) * q) - 1)] if values else None


def main():
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python -m scripts.summarize_live exported-insights.json"
        )
    data = json.loads(Path(sys.argv[1]).read_text())
    rows = [r for r in data.get("metrics", []) if r.get("mode") == "live_audio"]
    if not rows:
        raise SystemExit(
            "No live_audio observations. Text simulations cannot produce an audio latency report."
        )
    result = {
        "source": Path(sys.argv[1]).name,
        "provider": data.get("provider"),
        "samples": len(rows),
        "nudge_bearing_samples": sum(r["nudge_count"] > 0 for r in rows),
        "units": "milliseconds",
        "latency": {},
    }
    for key in (
        "capture_to_display_ms",
        "asr_ms",
        "signal_ms",
        "llm_ms",
        "delivery_residual_ms",
    ):
        values = [r[key] for r in rows if r.get(key) is not None]
        result["latency"][key] = {
            "p50": p(values, 0.5),
            "p95": p(values, 0.95),
            "n": len(values),
        }
    values = [r["capture_to_display_ms"] for r in rows if r["nudge_count"] > 0]
    result["nudge_bearing_capture_to_display"] = {
        "p50": p(values, 0.5),
        "p95": p(values, 0.95),
        "n": len(values),
    }
    result["excluded_observations"] = {
        kind: sum(r.get("mode") == kind for r in data.get("observations", []))
        for kind in ("suppressed_audio", "dropped_audio", "audio_error", "text_only")
    }
    result["notes"] = (
        "LLM not used. Source observations must be checked against the live recording. This script verifies structure, not provenance. Silence/dropped/failed windows are excluded from successful-window percentiles."
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
