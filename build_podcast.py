"""Build podcast episodes from podcast/scripts/*.txt with local Kokoro TTS.

Script format: lines starting with "A:" or "B:" are spoken turns, "#" lines are
comments. A "# title: ..." line sets the mp3 title shown on the lock screen.

Usage:
    python build_podcast.py                 # build episodes whose mp3 is missing or older than the script
    python build_podcast.py lecture1 --force

Needs: pip install kokoro-onnx lameenc
Model files (not in the repo): set KOKORO_DIR, default C:/Users/nepet/tools/kokoro
with kokoro-v1.0.int8.onnx and voices-v1.0.bin.
"""
import os
import sys
import time
from pathlib import Path

import lameenc
import numpy as np
from kokoro_onnx import Kokoro

ROOT = Path(__file__).parent
SCRIPTS = ROOT / "podcast" / "scripts"
AUDIO = ROOT / "podcast"
KOKORO_DIR = Path(os.environ.get("KOKORO_DIR", "C:/Users/nepet/tools/kokoro"))

VOICES = {"A": "af_heart", "B": "am_michael"}
SPEED = 1.0
PAUSE_SECONDS = 0.35
BITRATE = 64


def parse(path):
    turns = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        speaker, text = line.split(":", 1)
        turns.append((speaker.strip(), text.strip()))
    return turns


def build(name, kokoro, force=False):
    script = SCRIPTS / f"{name}.txt"
    out = AUDIO / f"{name}.mp3"
    if out.exists() and not force and out.stat().st_mtime > script.stat().st_mtime:
        print(f"{name}: up to date")
        return
    start = time.time()
    pieces = []
    sample_rate = 24000
    for speaker, text in parse(script):
        audio, sample_rate = kokoro.create(text, voice=VOICES[speaker], speed=SPEED, lang="en-us")
        pieces.append(audio)
        pieces.append(np.zeros(int(sample_rate * PAUSE_SECONDS), dtype=audio.dtype))
    audio = np.concatenate(pieces)
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes()

    encoder = lameenc.Encoder()
    encoder.set_bit_rate(BITRATE)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(1)
    encoder.set_quality(2)
    out.write_bytes(encoder.encode(pcm) + encoder.flush())

    minutes = len(audio) / sample_rate / 60
    print(f"{name}: {minutes:.1f} min audio, built in {time.time() - start:.0f} s")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    names = args or sorted(p.stem for p in SCRIPTS.glob("*.txt"))
    kokoro = Kokoro(str(KOKORO_DIR / "kokoro-v1.0.int8.onnx"), str(KOKORO_DIR / "voices-v1.0.bin"))
    for name in names:
        build(name, kokoro, force)
    write_registry()


def write_registry():
    """Write _podcast-data.html (window.STA520_EPISODES) for _podcast.html."""
    import json

    episodes = []
    for script in sorted(SCRIPTS.glob("*.txt"), key=lambda p: p.stem):
        mp3 = AUDIO / f"{script.stem}.mp3"
        if not mp3.exists():
            continue
        title = script.stem
        for line in script.read_text(encoding="utf-8").splitlines():
            if line.startswith("# title:"):
                title = line.split(":", 1)[1].strip()
        minutes = round(mp3.stat().st_size * 8 / (BITRATE * 1000) / 60)
        episodes.append({"id": script.stem, "title": title, "minutes": minutes})
    (ROOT / "_podcast-data.html").write_text(
        "<script>window.STA520_EPISODES = " + json.dumps(episodes, ensure_ascii=False) + ";</script>\n",
        encoding="utf-8",
    )
    print(f"registry: {len(episodes)} episodes")


if __name__ == "__main__":
    main()
