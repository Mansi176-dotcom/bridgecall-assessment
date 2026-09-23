"""Audio-in/audio-out synthetic sessions: TTS -> actual ASR -> real Agent -> TTS.
These are synthetic test sessions, not human calls or telephony recordings.
"""

import argparse, json, time, re
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel
from app.kb import KnowledgeBase, ROOT
from app.agent import Agent
from scripts.evaluate import SCENARIOS
from scripts.media_helpers import synthesize, save_mp3, RATE


def edit_distance(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        row = [i]
        for j, y in enumerate(b, 1):
            row.append(min(row[-1] + 1, prev[j] + 1, prev[j - 1] + (x != y)))
        prev = row
    return prev[-1]


def words(text):
    return re.findall(r"\w+", text.casefold())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cache", default=".media-cache")
    p.add_argument("--models", default=".model-cache")
    p.add_argument("--model", default="base")
    p.add_argument("--output", default="evidence/audio")
    args = p.parse_args()
    model = WhisperModel(
        args.model,
        device="cpu",
        compute_type="int8",
        cpu_threads=4,
        download_root=args.models,
    )
    kb = KnowledgeBase()
    out = ROOT / args.output
    out.mkdir(parents=True, exist_ok=True)
    summary = []
    for name, (market, locale, inputs) in SCENARIOS.items():
        report_path = out / (name + ".json")
        if report_path.exists():
            summary.append(json.loads(report_path.read_text())["summary"])
            continue
        lang = {"en-PH": "en", "fil-PH": "tl", "id-ID": "id"}[locale]
        agent = Agent(kb, market, locale)
        chunks = []
        events = []
        position = 0.0
        distance = 0
        word_count = 0

        def append_audio(text, role):
            nonlocal position
            audio, _ = synthesize(text, lang, args.cache)
            start = position
            chunks.extend([audio, np.zeros(int(0.3 * RATE), dtype="float32")])
            position += len(audio) / RATE + 0.3
            return {
                "speaker": role,
                "start_s": round(start, 3),
                "end_s": round(position - 0.3, 3),
                "text": text,
            }

        opening = agent.respond("")
        events.append(append_audio(opening["assistant"], "assistant"))
        for reference in inputs:
            audio, path = synthesize(reference, lang, args.cache)
            start = time.perf_counter()
            segments, _ = model.transcribe(
                str(path),
                language=lang,
                beam_size=1,
                condition_on_previous_text=False,
                temperature=0,
            )
            recognized = " ".join(x.text.strip() for x in segments).strip()
            asr_ms = (time.perf_counter() - start) * 1000
            event = append_audio(reference, "customer")
            event.update({"reference": reference, "asr": recognized, "asr_ms": asr_ms})
            events.append(event)
            ref, hyp = words(reference), words(recognized)
            distance += edit_distance(ref, hyp)
            word_count += len(ref)
            response = agent.respond(recognized)
            event = append_audio(response["assistant"], "assistant")
            event.update(
                {
                    "state": response["state"],
                    "citation": response["citation"],
                    "action": response["action"],
                }
            )
            events.append(event)
            print(
                name, reference, "=>", recognized, "=>", response["state"], flush=True
            )
        expected_end = "closed" if name == "Q1-03-conflict" else "done"
        item = {
            "id": name,
            "evidence_type": "synthetic_audio_loop_not_human_call",
            "language": locale,
            "final_state": agent.state,
            "expected_final_state": expected_end,
            "flow_verdict": "pass" if agent.state == expected_end else "partial",
            "reference_words": word_count,
            "word_errors": distance,
            "wer": distance / max(1, word_count),
            "duration_s": round(position, 2),
            "recording": name + ".mp3",
            "asr_model": "faster-whisper/" + args.model + " CPU int8 beam_size=1",
            "tts": "gTTS 2.5.4, language " + lang,
            "native_speaker_review": False,
        }
        save_mp3(np.concatenate(chunks), out / (name + ".mp3"))
        report = {"summary": item, "events": events}
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        summary.append(item)
        print("SAVED", name, item["flow_verdict"], flush=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print("ALL AUDIO SESSIONS SAVED", flush=True)


if __name__ == "__main__":
    main()
