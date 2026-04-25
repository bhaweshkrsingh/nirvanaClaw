# nirvanaClaw 🦞🎙️

> 2-way WhatsApp voice interface for [OpenClaw](https://github.com/openclaw/openclaw) — fully local, zero API cost, zero data leakage.

**Send a WhatsApp voice note. Get a voice reply back. Your AI agent. Your infrastructure. Your data.**

---

## Why nirvanaClaw?

As of April 2026, no public project implements a true 2-way voice interface to OpenClaw over WhatsApp. Every existing VoiceClaw project requires a dedicated app, a browser UI, or a separate voice channel (Telegram, Discord, WebSocket). nirvanaClaw uses WhatsApp — already on your phone — as the voice interface.

| Feature | nirvanaClaw | Other VoiceClaw projects |
|---------|-------------|--------------------------|
| Channel | WhatsApp (your existing number) | Browser, Telegram, Discord, custom app |
| App to install | None | Yes |
| STT | Local Whisper (CPU) | Cloud APIs or local |
| LLM | Self-hosted via vLLM | OpenAI / Anthropic / cloud |
| TTS | Microsoft Edge TTS (free) | OpenAI TTS, ElevenLabs, etc. |
| API cost | $0 | Variable |
| Data leaves your infra | Never | Often |

**What makes this unique:**

- **No app to install** — WhatsApp is already on your phone; your personal number is the UI
- **No new UI to maintain** — the channel is your existing personal number, paired once via QR
- **Fully local inference** — Whisper STT on your server, LLM on your home server via Tailscale/VPN, Edge TTS free with no API key
- **Zero data leakage** — Qwen3.6-35B-A3B runs locally via vLLM; personal conversations never leave your infrastructure and are never sent to an external LLM
- **Persistent memory** — OpenClaw's agent workspace carries context across all conversations
- **Surprisingly lean hardware** — the entire gateway + STT pipeline runs on a 2-vCPU / 8GB RAM VM (AWS Lightsail), proving enterprise-grade voice AI doesn't require expensive GPU infrastructure

---

## Architecture

```
iPhone WhatsApp
        │ voice note (.ogg) or text
        ▼
OpenClaw Gateway (port 18789)
        ├── STT: whisper_transcribe.py  (faster-whisper small, CPU)
        │         └─ transcript text
        ├── LLM: Qwen3.6-35B via vLLM  (your home server / self-hosted)
        │         └─ text reply
        └── TTS: Microsoft Edge TTS    (en-US-AriaNeural, free, no API key)
                  └─ voice reply .ogg → back to WhatsApp
```

All inference is local. OpenClaw is the glue — it handles WhatsApp Web protocol, STT dispatch, agent session, and TTS reply.

---

## Prerequisites

- **OpenClaw** v2026.4.23+ — `sudo npm install -g openclaw` (requires Node.js 22+)
- **Python 3.10+** with a virtualenv
- **faster-whisper** — `pip install faster-whisper`
- **vLLM** running an OpenAI-compatible model (or any OpenAI-compatible LLM endpoint)
- **ffmpeg** — `sudo apt install ffmpeg` (needed by faster-whisper for audio decoding)
- A WhatsApp account on your phone

---

## Setup

### 1. Clone this repo

```bash
git clone https://github.com/bhaweshkrsingh/nirvanaClaw.git
cd nirvanaClaw
pip install -r requirements.txt
```

### 2. Place transcription script

```bash
cp whisper_transcribe.py ~/whisper_transcribe.py
chmod +x ~/whisper_transcribe.py
```

The script will auto-download the Whisper `small` model (~460MB) on first run.

### 3. Configure OpenClaw

```bash
cp openclaw.json.example ~/.openclaw/openclaw.json
```

Edit `~/.openclaw/openclaw.json` and replace:
- `<YOUR_VLLM_HOST>` — IP/hostname of your vLLM server
- `<YOUR_USER>` — your Linux username
- `+1XXXXXXXXXX` — your WhatsApp phone number (with country code)
- Generate a gateway token: `openssl rand -hex 24`

### 4. Install systemd service

```bash
mkdir -p ~/.config/systemd/user
cp systemd/openclaw-gateway.service ~/.config/systemd/user/
# Edit the service file: replace <YOUR_USER> with your username
nano ~/.config/systemd/user/openclaw-gateway.service

systemctl --user daemon-reload
systemctl --user enable --now openclaw-gateway

# Allow service to persist after logout
loginctl enable-linger $USER
```

### 5. Pair WhatsApp

```bash
openclaw channels login --channel whatsapp
```

Scan the QR code with your iPhone (WhatsApp → Settings → Linked Devices → Link a Device).

### 6. Test it

Send yourself a voice note on WhatsApp. You should receive:
1. A text reply (the transcript + LLM response)
2. A voice reply (TTS audio)

---

## Files

| File | Purpose |
|------|---------|
| `whisper_transcribe.py` | CLI STT script — called by OpenClaw per voice message |
| `whisper_server.py` | Optional standalone HTTP STT server (port 9876, OpenAI-compatible) |
| `openclaw.json.example` | OpenClaw config template |
| `systemd/openclaw-gateway.service` | systemd user service for auto-start |
| `requirements.txt` | Python dependencies |

---

## Useful commands

```bash
# Gateway status
systemctl --user status openclaw-gateway

# Restart gateway
systemctl --user restart openclaw-gateway

# Live logs
journalctl --user -u openclaw-gateway -f

# Full debug log
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log
```

---

## Key config lessons

- `agents.defaults.sandbox.mode` must be `"off"` if Docker is not installed — any other mode causes a fatal error
- `tools.media.audio.models[].args` must include `"{{MediaPath}}"` — without it the audio path is never passed to the script
- Stop OpenClaw before hand-editing `openclaw.json` — it rewrites the config on shutdown and will overwrite your changes
- `messages.tts.auto: "inbound"` means TTS reply is sent only when the incoming message was a voice note (not for text messages)

---

## Hardware tested on

- **CPU:** Intel Xeon Platinum 8259CL @ 2.50GHz (2 vCPU)
- **RAM:** 8GB + 16GB swap
- **OS:** Ubuntu 24.04 LTS
- **Node:** v22.22.2
- **Python:** 3.12

Whisper `small` transcription takes ~5–10s on this hardware. The LLM response time depends on your vLLM host.

---

## Credits

Built by [Bhawesh Singh](https://github.com/bhaweshkrsingh) / [ideaNirvana LLC](https://ideanirvana.com)

Powered by:
- [OpenClaw](https://github.com/openclaw/openclaw) — the AI agent gateway
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — local STT
- [Qwen3.6-35B](https://huggingface.co/Qwen) via [vLLM](https://github.com/vllm-project/vllm) — local LLM
- Microsoft Edge TTS — free neural voice synthesis

---

## License

MIT
