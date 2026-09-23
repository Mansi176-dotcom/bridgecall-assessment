"""Evaluate published Javanese-accented Indonesian against matched standard speech.
Original audio stays in --work and MUST NOT be redistributed in this repository.
"""

import argparse, hashlib, io, json, time, urllib.request, zipfile
from pathlib import Path
from faster_whisper import WhisperModel
from app.kb import ROOT
from scripts.run_audio_evaluation import words, edit_distance

BASE = "https://raw.githubusercontent.com/s-sakti/data_indsp_news_lvcsr/main/"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--work", required=True)
    p.add_argument("--models", default=".model-cache")
    p.add_argument("--model", default="base")
    p.add_argument("--output", default="evidence/regional-accent-results.json")
    args = p.parse_args()
    work = Path(args.work)
    work.mkdir(parents=True, exist_ok=True)
    archives = {}
    for key, url in [
        ("Ind006", BASE + "speech/Ind0/Ind006.zip"),
        ("Ind003", BASE + "speech/Ind0/Ind003.zip"),
        ("transcripts", BASE + "text/all_transcript.zip"),
    ]:
        path = work / (key + ".zip")
        if not path.exists():
            path.write_bytes(urllib.request.urlopen(url, timeout=60).read())
        archives[key] = zipfile.ZipFile(path)
    paths = {
        s: {
            Path(x).stem.rsplit("news_", 1)[-1]: x
            for x in archives[s].namelist()
            if x.endswith(".wav")
        }
        for s in ("Ind006", "Ind003")
    }
    chosen = []
    refs = {}
    for num in sorted(set(paths["Ind006"]) & set(paths["Ind003"])):
        reference = " ".join(
            x.strip()
            for x in archives["transcripts"]
            .read("all_transcript/news_" + num + ".txt")
            .decode()
            .splitlines()
            if not x.startswith("|")
        )
        if len(reference.split()) >= 8:
            chosen.append(num)
            refs[num] = reference
        if len(chosen) == 3:
            break
    model = WhisperModel(
        args.model,
        device="cpu",
        compute_type="int8",
        cpu_threads=4,
        download_root=args.models,
    )
    results = []
    for speaker, accent in [
        ("Ind006", "Javanese-accented Indonesian (source label J)"),
        ("Ind003", "Standard Indonesian (source label U)"),
    ]:
        for num in chosen:
            member = paths[speaker][num]
            data = archives[speaker].read(member)
            started = time.perf_counter()
            segments, _ = model.transcribe(
                io.BytesIO(data),
                language="id",
                beam_size=1,
                temperature=0,
                condition_on_previous_text=False,
            )
            hyp = " ".join(s.text.strip() for s in segments)
            elapsed = (time.perf_counter() - started) * 1000
            a, b = words(refs[num]), words(hyp)
            distance = edit_distance(a, b)
            results.append(
                {
                    "speaker_id": speaker,
                    "accent": accent,
                    "archive_url": BASE + "speech/Ind0/" + speaker + ".zip",
                    "archive_member": member,
                    "audio_sha256": hashlib.sha256(data).hexdigest(),
                    "reference": refs[num],
                    "hypothesis": hyp,
                    "reference_words": len(a),
                    "word_errors": distance,
                    "wer": distance / len(a),
                    "asr_ms": elapsed,
                }
            )
            print(speaker, num, hyp, flush=True)
    summary = {}
    for speaker in ("Ind006", "Ind003"):
        rows = [r for r in results if r["speaker_id"] == speaker]
        n = sum(r["reference_words"] for r in rows)
        errors = sum(r["word_errors"] for r in rows)
        summary[speaker] = {
            "utterances": len(rows),
            "reference_words": n,
            "errors": errors,
            "aggregate_wer": errors / n,
        }
    out = {
        "evidence_type": "real_human_corpus_playback_ASR_test_not_interactive_financial_call",
        "source": "https://github.com/s-sakti/data_indsp_news_lvcsr",
        "citation": "Sakriani Sakti et al. (2008), Development of Indonesian Large Vocabulary Continuous Speech Recognition System within A-STAR Project, TCAST, pp. 19–24.",
        "license": "CC BY-NC-SA 4.0; source additionally requests no public dataset copies without permission. Original media are not redistributed.",
        "selection": "First three shared utterance IDs in ascending order with at least eight reference words; selected before ASR.",
        "model": "faster-whisper 1.2.1 / "
        + args.model
        + " / CPU int8 / beam_size 1 / language id",
        "normalization": "Unicode word tokens, casefold; no number normalization",
        "limitations": "One speaker per accent, three matched news sentences each, clean studio speech. No finance-call realism, native-speaker review, or population-level accent conclusion.",
        "summary": summary,
        "results": results,
    }
    (ROOT / args.output).write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
