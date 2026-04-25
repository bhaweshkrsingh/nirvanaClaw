#!/usr/bin/env python3
"""
Local Whisper transcription server — OpenAI-compatible /audio/transcriptions endpoint.
Uses faster-whisper with the 'small' model. Runs on port 9876.

Not used by OpenClaw directly (OpenClaw calls whisper_transcribe.py as a CLI).
Available for other integrations that need an HTTP STT endpoint.

Requirements: faster-whisper flask
  pip install faster-whisper flask
"""
import os
import tempfile
from flask import Flask, request, jsonify
from faster_whisper import WhisperModel

app = Flask(__name__)

# Load model once at startup (CPU, int8 quantized for speed on 8GB RAM)
model = WhisperModel("small", device="cpu", compute_type="int8")


@app.route("/audio/transcriptions", methods=["POST"])
def transcribe():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    audio_file = request.files["file"]
    language = request.form.get("language", None)

    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        audio_file.save(tmp.name)
        tmp_path = tmp.name

    try:
        segments, _ = model.transcribe(tmp_path, language=language, beam_size=5)
        text = " ".join(seg.text.strip() for seg in segments).strip()
    finally:
        os.unlink(tmp_path)

    return jsonify({"text": text})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9876)
