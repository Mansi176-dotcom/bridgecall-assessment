"""Optional tools for reproducible, explicitly synthetic audio fixtures."""

import hashlib
import subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
import imageio_ffmpeg
from gtts import gTTS

RATE = 16000


def synthesize(text, language, cache):
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256((language + "\n" + text).encode()).hexdigest()[:24]
    mp3 = cache / (key + ".mp3")
    wav = cache / (key + ".wav")
    if not wav.exists():
        if not mp3.exists():
            gTTS(text, lang=language, timeout=30).save(str(mp3))
        subprocess.run(
            [
                imageio_ffmpeg.get_ffmpeg_exe(),
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(mp3),
                "-ar",
                str(RATE),
                "-ac",
                "1",
                str(wav),
            ],
            check=True,
        )
    audio, rate = sf.read(wav, dtype="float32")
    assert rate == RATE
    return audio, wav


def save_mp3(audio, path):
    path = Path(path)
    wav = path.with_suffix(".wav")
    sf.write(wav, audio, RATE, subtype="PCM_16")
    subprocess.run(
        [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(wav),
            "-b:a",
            "96k",
            str(path),
        ],
        check=True,
    )
    wav.unlink()
