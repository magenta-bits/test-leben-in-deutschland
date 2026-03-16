import re
import subprocess
import tempfile
import os
import wave
import tarfile
import urllib.request
from pathlib import Path

from piper import PiperVoice

VOICE_DIR = Path.home() / ".local/share/piper-voices"
ONNX_PATH = VOICE_DIR / "de-thorsten-low.onnx"
MODEL_URL = "https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-de-thorsten-low.tar.gz"


def ensure_voice():
    if not ONNX_PATH.exists():
        VOICE_DIR.mkdir(parents=True, exist_ok=True)
        tar_path = VOICE_DIR / "de-thorsten-low.tar.gz"
        print("Downloading German voice model...")
        urllib.request.urlretrieve(MODEL_URL, tar_path)
        with tarfile.open(tar_path) as t:
            t.extractall(VOICE_DIR)
        tar_path.unlink()
        print("Voice model ready.")


def clean_markdown(text):
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)  # headings
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)                 # bold
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)       # hr
    text = re.sub(r'\n{3,}', '\n\n', text)                       # extra newlines
    return text.strip()


ensure_voice()

with open('german_summary_for_reading.md', 'r', encoding='utf-8') as f:
    clean = clean_markdown(f.read())

print("Loading voice model...")
voice = PiperVoice.load(str(ONNX_PATH))

with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
    wav_path = tmp.name

print("Synthesizing audio...")
with wave.open(wav_path, 'wb') as wav_file:
    voice.synthesize_wav(clean, wav_file)

subprocess.run(['lame', '-q', '3', wav_path, 'german_summary.mp3'], check=True, capture_output=True)
os.unlink(wav_path)
print("Saved german_summary.mp3")
