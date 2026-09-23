"""Generate a deterministic 40-second synthetic call for real-time replay."""

import argparse, json
import numpy as np
import soundfile as sf
from app.kb import ROOT
from scripts.media_helpers import synthesize, RATE


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cache", default=".media-cache")
    args = p.parse_args()
    lines = [
        ("agent", "What is your age?", "missing_disclosure"),
        ("agent", "This is an automated demo.", None),
        ("agent", "You will get guaranteed approval.", "risky_promise"),
        ("customer", "I have a second vehicle.", "cross_sell"),
        ("customer", "I have a second vehicle.", None),
        ("customer", "I am frustrated. This is the third time.", "frustration"),
        ("customer", "I cannot pay this month.", "payment_difficulty"),
        ("customer", "Please call me tomorrow.", "callback"),
        ("customer", "Thank you for explaining.", None),
        ("customer", "", None),
    ]
    chunks = []
    windows = []
    for i, (speaker, text, expected) in enumerate(lines):
        if text:
            audio, _ = synthesize(text, "en", args.cache)
            if len(audio) > int(3.85 * RATE):
                raise ValueError(
                    "Fixture phrase exceeds window; shorten text, do not truncate speech: "
                    + text
                )
            chunk = np.pad(
                audio, (int(0.1 * RATE), 4 * RATE - len(audio) - int(0.1 * RATE))
            )
        else:
            chunk = (
                np.random.default_rng(42).normal(0, 0.012, 4 * RATE).astype("float32")
            )
        chunks.append(chunk)
        windows.append(
            {
                "index": i,
                "start_s": i * 4,
                "end_s": (i + 1) * 4,
                "speaker": speaker,
                "reference": text,
                "expected_rule": expected,
                "note": (
                    "Cooldown duplicate"
                    if i == 4
                    else "Seeded non-speech noise" if i == 9 else "Synthetic speech"
                ),
            }
        )
    out = ROOT / "data/demo"
    out.mkdir(parents=True, exist_ok=True)
    sf.write(out / "stream.wav", np.concatenate(chunks), RATE, subtype="PCM_16")
    (out / "stream.json").write_text(
        json.dumps(
            {
                "evidence_type": "synthetic_audio_fixture",
                "tts": "gTTS 2.5.4 / Google Translate speech, en; not a human voice recording",
                "window_seconds": 4,
                "windows": windows,
            },
            indent=2,
        )
    )
    print("Built 40-second replay fixture", flush=True)


if __name__ == "__main__":
    main()
