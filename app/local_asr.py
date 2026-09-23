"""Optional local Whisper adapter. Audio stays on this machine after model download."""

import io
import os
import threading
import time

_MODEL = None
_MODEL_LOCK = threading.Lock()


def model():
    global _MODEL
    with _MODEL_LOCK:
        if _MODEL is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise ValueError(
                    "Install requirements-audio.txt to enable local ASR."
                ) from exc
            _MODEL = WhisperModel(
                os.environ.get("LOCAL_ASR_MODEL", "base"),
                device="cpu",
                compute_type="int8",
                cpu_threads=4,
                download_root=os.environ.get("ASR_MODEL_CACHE", ".model-cache"),
            )
    return _MODEL


def transcribe_local(audio, language):
    started = time.perf_counter()
    asr = model()
    segments, _ = asr.transcribe(
        io.BytesIO(audio),
        language=language,
        beam_size=1,
        condition_on_previous_text=False,
        vad_filter=False,
        temperature=0,
    )
    text = " ".join(segment.text.strip() for segment in segments).strip()
    return text, (time.perf_counter() - started) * 1000
