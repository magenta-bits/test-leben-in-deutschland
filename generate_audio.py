import re
import subprocess
import tempfile
import os


def clean_markdown(text):
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)  # headings
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)                 # bold
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)       # hr
    text = re.sub(r'\n{3,}', '\n\n', text)                       # extra newlines
    return text.strip()


with open('german_summary_for_reading.md', 'r', encoding='utf-8') as f:
    raw = f.read()

clean = clean_markdown(raw)

with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_wav:
    wav_path = tmp_wav.name

try:
    # Generate WAV via espeak-ng (German voice)
    subprocess.run(
        ['espeak-ng', '-v', 'de', '-s', '140', '-w', wav_path, '--stdin'],
        input=clean.encode('utf-8'),
        check=True,
    )

    # Convert WAV to MP3 via lame
    subprocess.run(
        ['lame', '-q', '3', wav_path, 'german_summary.mp3'],
        check=True,
        capture_output=True,
    )

    print("Saved german_summary.mp3")
finally:
    os.unlink(wav_path)
