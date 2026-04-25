# I Built a 2-Way WhatsApp Voice Interface for My AI Agent — Fully Local, Zero API Cost

*By Bhawesh Singh, Principal Agentic AI Engineer | ideaNirvana LLC*

---

I talk to my AI agent over WhatsApp now. Not by typing — by sending voice notes. And it talks back.

No app to install. No browser to open. No cloud API bill at the end of the month. My personal WhatsApp number is the UI. My own server is the brain. Every word stays inside my infrastructure.

Here's how I built it, why it matters, and how you can replicate it in an afternoon.

---

## The Problem with Every Other Voice AI Project

OpenClaw has over 80,000 GitHub stars. It's one of the most powerful self-hosted AI agent platforms available. But until now, there was no clean way to talk to it with your voice from your phone.

I searched through 25+ public repositories named "VoiceClaw" on GitHub. Every single one fell into one of these buckets:

- **Requires a dedicated app** — something you have to install, maintain, and remember to open
- **Requires a browser** — a WebSocket UI on a specific port, only works on your local network
- **Only handles async voice notes** — Telegram bots that transcribe but don't reply with voice
- **Requires a separate channel** — Discord bots, Telegram bots, custom PWAs
- **Needs cloud APIs** — OpenAI Realtime, Gemini Live, ElevenLabs — all with per-minute billing

One project's README literally said: *"OpenClaw has 80,000+ GitHub stars, but there's no proper real-time voice interface with gateway integration."*

So I built it. Over WhatsApp. In a single session.

---

## The Insight: WhatsApp Is Already There

The key insight was simple: **I already have WhatsApp on my iPhone**. Billions of people do. WhatsApp supports voice notes natively — you press and hold the microphone, speak, release, and it sends an `.ogg` audio file.

OpenClaw already has a WhatsApp channel plugin. It can receive those `.ogg` files. The missing pieces were:

1. A way to transcribe the audio locally (STT)
2. A way to send a voice reply back (TTS)

That's it. Everything else — the LLM, the memory, the agent session — OpenClaw handles.

---

## The Architecture

```
iPhone WhatsApp
        │  voice note (.ogg) or text message
        ▼
OpenClaw Gateway  (AWS Lightsail, 2 vCPU / 8GB RAM)
        ├── STT: faster-whisper small model, CPU, ~5-10s
        │         └─ transcript text
        ├── LLM: Qwen3.6-35B-A3B via vLLM  (home server, self-hosted)
        │         └─ text reply
        └── TTS: Microsoft Edge TTS, en-US-AriaNeural, FREE
                  └─ voice reply .ogg → back to WhatsApp
```

Three components. All local. All free.

---

## What Makes This Different

### No app. No new UI.
Your WhatsApp number is the interface. You already have it. You've been using it for years. You know how to send a voice note. That's the entire learning curve.

### Zero API cost.
- **STT:** faster-whisper runs on CPU. The `small` model is 460MB and fits comfortably on 8GB RAM.
- **LLM:** Qwen3.6-35B-A3B runs on my home server via vLLM, accessed over Tailscale VPN. Not a single token goes to OpenAI or Anthropic.
- **TTS:** Microsoft Edge TTS is built into OpenClaw. It uses the same neural voice engine as your Windows PC narrator — free, no API key, surprisingly good quality.

The running cost is my AWS Lightsail instance: **$10/month**. That's the entire infrastructure bill.

### Zero data leakage.
This is the one I care about most. When you talk to ChatGPT or Claude via voice, your words travel to a cloud server, get processed, and a response comes back. That data is logged, used for training, and subject to the privacy policies of those companies.

With nirvanaClaw, your voice note hits your server, gets transcribed on your server, sent to your own LLM on your own home server, and the reply is synthesized and sent back — all within infrastructure you control. **Your conversations never leave your infrastructure.**

### Persistent memory.
OpenClaw maintains an agent workspace across all conversations. It knows your name, your preferences, your context. Text a question, voice note a follow-up — it's all the same session.

### Lean hardware.
The entire gateway runs on a **2-vCPU Intel Xeon @ 2.50GHz with 8GB RAM** — a $10/month AWS Lightsail instance. This is not a GPU rig. This is not a beefy home server. This is the smallest practical Linux VM you can rent.

Enterprise-grade voice AI doesn't require expensive GPU infrastructure.

---

## The Tech Stack

| Component | Technology | Cost |
|-----------|-----------|------|
| Agent gateway | OpenClaw v2026.4.23 | Free / open source |
| WhatsApp channel | OpenClaw built-in plugin | Free |
| Speech-to-text | faster-whisper (small model, CPU) | Free |
| Large language model | Qwen3.6-35B-A3B via vLLM | Free (self-hosted) |
| Text-to-speech | Microsoft Edge TTS (AriaNeural) | Free |
| Server | AWS Lightsail 2 vCPU / 8GB | ~$10/month |
| VPN (home server access) | Tailscale | Free tier |

---

## How It Works — Step by Step

1. I press and hold the microphone button in WhatsApp and say something
2. WhatsApp sends the voice note as a `.ogg` (Opus codec) file
3. OpenClaw receives it via the WhatsApp Web protocol
4. OpenClaw calls `whisper_transcribe.py` with the audio file path
5. faster-whisper transcribes it to text in ~5–10 seconds on CPU
6. The transcript goes to the Qwen3.6-35B LLM on my home server
7. The LLM generates a response
8. OpenClaw passes the response text to Microsoft Edge TTS
9. Edge TTS synthesizes a voice reply as an audio file
10. OpenClaw sends the audio back to my WhatsApp as a voice note

The whole round trip takes about 15–25 seconds. Not real-time, but perfectly natural for an async voice conversation — the same rhythm as leaving a voicemail and getting one back.

---

## The Config That Makes It Work

The entire magic lives in `~/.openclaw/openclaw.json`. The three critical sections:

**STT — invoke whisper as a CLI command:**
```json
"tools": {
  "media": {
    "audio": {
      "enabled": true,
      "models": [{
        "type": "cli",
        "command": "/usr/bin/python3",
        "args": ["/home/ubuntu/whisper_transcribe.py", "{{MediaPath}}"]
      }]
    }
  }
}
```

**TTS — Microsoft Edge neural voice, reply only when a voice note was received:**
```json
"messages": {
  "tts": {
    "auto": "inbound",
    "provider": "microsoft",
    "providers": {
      "microsoft": { "voice": "en-US-AriaNeural" }
    }
  }
}
```

**LLM — self-hosted Qwen via vLLM:**
```json
"models": {
  "providers": {
    "genlab": {
      "baseUrl": "http://YOUR_HOME_SERVER:8001/v1",
      "apiKey": "none",
      "models": [{ "id": "qwen3.6-35b", "api": "openai-completions", "input": ["text"] }]
    }
  }
}
```

That's the entire voice pipeline. Three JSON blocks.

---

## Lessons Learned (The Hard Way)

A few things that tripped me up and will save you time:

**1. `sandbox.mode` must be `"off"` if Docker isn't installed.**
OpenClaw defaults to a sandboxed agent mode that requires Docker. Without Docker, every message fails silently with `Embedded agent failed before reply`. Set `agents.defaults.sandbox.mode: "off"` first.

**2. `{{MediaPath}}` must be in the args array.**
OpenClaw injects the audio file path via template variable. If you forget it, the script is called with no argument and returns empty — no error, just silent failure.

**3. Stop OpenClaw before editing the config file.**
OpenClaw rewrites `openclaw.json` on shutdown. If you edit it while the gateway is running and then stop the gateway, your edits are overwritten. Always `systemctl --user stop openclaw-gateway` first.

**4. Node.js 22+ is required.**
OpenClaw will not install on Node 18. Upgrade first via NodeSource.

---

## Get It

Everything is open source at:

**https://github.com/bhaweshkrsingh/nirvanaClaw**

The repo includes:
- `whisper_transcribe.py` — the STT script
- `openclaw.json.example` — config template with all placeholders documented
- `systemd/openclaw-gateway.service` — auto-start on reboot
- `requirements.txt` — Python dependencies
- Full setup guide in the README

If you have OpenClaw installed and a self-hosted LLM endpoint, you can have this running in under an hour.

---

## What's Next

A few things I'm thinking about building on top of this:

- **Wake-word over WhatsApp** — detect specific phrases and trigger actions automatically
- **Multi-language support** — faster-whisper supports 99 languages; the config is one line change
- **Tool use via voice** — ask it to check your calendar, search the web, run code
- **Group chat support** — extend the `allowFrom` list and let a team share one agent

If you build on this, I'd love to hear about it. Drop a comment, open an issue, or find me on LinkedIn.

---

## About the Author

**Bhawesh Singh** is a Principal Agentic AI Engineer and founder of **ideaNirvana LLC**, where he builds agentic AI systems that work within your infrastructure — not someone else's cloud.

- Medium: [@b_k_singh](https://medium.com/@b_k_singh)
- GitHub: [github.com/bhaweshkrsingh](https://github.com/bhaweshkrsingh)
- LinkedIn: [linkedin.com/in/bhawesh-singh](https://www.linkedin.com/in/bhawesh-singh/)
- Company: [ideanirvana.com](https://ideanirvana.com)

---

*If this was useful, star the repo at [github.com/bhaweshkrsingh/nirvanaClaw](https://github.com/bhaweshkrsingh/nirvanaClaw) — it helps others find it.*
