"""Completeness gate, not proof that media/links are correct or publicly accessible."""

import json, sys
from urllib.parse import urlparse
from app.kb import ROOT


def usable_url(value):
    u = urlparse(value or "")
    return (
        u.scheme == "https"
        and bool(u.netloc)
        and not any(
            x in value.lower()
            for x in ("placeholder", "your-link", "example.com", "replace-me")
        )
    )


def main():
    m = json.loads((ROOT / "evidence/submission-manifest.json").read_text())
    missing = []
    for field in ("human_call_validation", "native_speaker_review"):
        if not m.get(field):
            missing.append(field)
    for field in (
        "repository_url",
        "walkthrough_url",
        "live_demo_recording_url",
        "live_metrics_url",
        "asr_report_url",
    ):
        if not usable_url(m.get(field)):
            missing.append(field)
    if not m.get("links_checked_signed_out"):
        missing.append("signed-out accessibility check")
    for record in m["calls"]:
        for key in ("recording_url", "transcript_url", "result"):
            if not (
                usable_url(record.get(key))
                if key.endswith("_url")
                else record.get(key) in ("pass", "partial", "fail")
            ):
                missing.append(record["id"] + ": " + key)
        if record.get("requires_regional_accent") and not record.get(
            "accent_observations"
        ):
            missing.append(record["id"] + ": regional accent observations")
    if missing:
        print(
            "NOT READY — missing required evidence:\n"
            + "\n".join("- " + x for x in missing)
        )
        raise SystemExit(1)
    print(
        "Manifest complete. Manually verify every link, media content, claims, and evaluator access before sending."
    )


if __name__ == "__main__":
    main()
