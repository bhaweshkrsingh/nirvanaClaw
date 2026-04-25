#!/usr/bin/env python3
"""
Whisper transcription script for OpenClaw.
Called by OpenClaw with the audio file path as the first argument.
Prints the transcript to stdout.

Requirements: faster-whisper
  pip install faster-whisper

Usage (by OpenClaw via openclaw.json):
  python whisper_transcribe.py <audio_file_path>
"""
import sys
from faster_whisper import WhisperModel

if len(sys.argv) < 2:
    print("", end="")
    sys.exit(0)

audio_path = sys.argv[1]

model = WhisperModel("small", device="cpu", compute_type="int8")
segments, _ = model.transcribe(audio_path, beam_size=5)
text = " ".join(seg.text.strip() for seg in segments).strip()
print(text)
