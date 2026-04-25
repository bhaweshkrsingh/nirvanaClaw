# LinkedIn Post

---

I built a 2-way voice interface for my AI agent over WhatsApp. Fully local. Zero API cost. Zero data leakage.

I press the microphone button in WhatsApp, say something, and my AI agent talks back — as a voice note. No app to install. No browser to open. My personal WhatsApp number is the UI.

I searched 25+ public "VoiceClaw" repos on GitHub before building this. Every single one required a dedicated app, a browser, or a paid cloud API. One README literally said: *"OpenClaw has 80,000+ stars but there's no proper voice interface with gateway integration."* So I built it.

The stack is entirely self-hosted:
- 🎙️ **STT** — faster-whisper running on CPU (no GPU needed)
- 🧠 **LLM** — Qwen3.6-35B on my home server via vLLM, accessed over Tailscale VPN
- 🔊 **TTS** — Microsoft Edge neural voices, built into OpenClaw, completely free
- 📱 **Channel** — WhatsApp, already on your phone

The whole thing runs on a 2-vCPU / 8GB RAM AWS Lightsail instance ($10/month). Your conversations never touch OpenAI, Anthropic, or any external LLM. Your data stays in your infrastructure — period.

I've open-sourced it as **nirvanaClaw** — named after my company ideaNirvana LLC.

🔗 GitHub: https://github.com/bhaweshkrsingh/nirvanaClaw
📖 Full writeup on Medium: [your Medium link here]

If you're running OpenClaw and a self-hosted LLM, you can have this working in under an hour. Drop a comment if you build on it — I'd love to see where this goes.

#AI #OpenSource #WhatsApp #VoiceAI #SelfHosted #LLM #AgenticAI #Privacy
