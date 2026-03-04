# Buddy - House Help Voice Agent 🏠🎤

A real-time voice assistant built with **LiveKit Agents** that helps with everyday household tasks — counting cooker whistles, setting timers, scheduling reminders, and more.

## What Buddy Can Do

**Pressure Cooker Whistle Counting** — Listens for cooker whistles using audio frequency analysis and alerts you when the target count is reached. Uses FFT-based detection in the 5000-7500 Hz range with consecutive-detection confirmation to avoid false positives.

**Timer Reminders** — Set timers in minutes or seconds for tasks like switching off the geyser, drying clothes, or checking on food. Multiple timers run simultaneously as independent background tasks.

**Event/Date Reminders** — Schedule reminders for specific dates and times. Say "remind me about the LIC payment tomorrow at 10 AM" and Buddy calculates the exact datetime and alerts you when it's due.

**Music Suggestions** — Ask for song recommendations by mood (happy, sad, relaxed, energetic, devotional, nostalgic) with guidance on how to play them via YouTube or Google Assistant.

**News Headlines** — Fetch latest news headlines on demand.

**Conversational Companion** — Buddy responds in short, friendly English sentences optimized for voice interaction.

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | LiveKit Agents 1.4.4 (Python) | Voice agent orchestration |
| STT | Deepgram Nova-3 | Speech-to-text (streaming, ~200ms) |
| LLM | OpenAI GPT-4o-mini | Language understanding & responses |
| TTS | Cartesia Sonic | Text-to-speech (streaming, ~300ms) |
| VAD | Silero VAD | Voice activity detection |
| Turn Detection | LiveKit Multilingual Model | Semantic end-of-turn detection |
| Audio Analysis | NumPy + SoundDevice | Whistle frequency detection via FFT |
| Server | LiveKit Server (Docker) | WebRTC media routing |

## Prerequisites

- Python 3.11+
- Docker (for LiveKit server)
- API keys for: OpenAI, Deepgram, Cartesia

## Quick Start

### 1. Clone and set up

```bash
git clone <your-repo-url>
cd house-help-voice-agent
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### 2. Install dependencies

```bash
pip install livekit livekit-agents livekit-plugins-openai livekit-plugins-silero livekit-plugins-deepgram livekit-plugins-cartesia livekit-plugins-turn-detector python-dotenv sounddevice numpy aiohttp
```

### 3. Configure environment

Create a `.env` file:

```
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
OPENAI_API_KEY=your_openai_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
CARTESIA_API_KEY=your_cartesia_api_key
```

### 4. Start LiveKit server

```bash
docker run --rm -p 7880:7880 -p 7881:7881 -p 7882:7882/udp livekit/livekit-server --dev
```

### 5. Download model files

```bash
python agent.py download-files
```

### 6. Run

```bash
python agent.py console
```

Press `Ctrl+T` to switch between voice and text input mode.

## Project Structure

```
house-help-voice-agent/
├── agent.py                 # Main agent (all features integrated)
├── calibrate_whistle.py     # Whistle frequency calibration tool
├── .env                     # API keys (not committed)
├── venv/                    # Python virtual environment
└── README.md                # This file
```

## How Whistle Detection Works

1. Buddy records audio in 0.3-second chunks at 16kHz
2. Each chunk is analyzed using Fast Fourier Transform (FFT)
3. Energy in the whistle frequency band (5000-7500 Hz) is compared to background noise
4. A whistle is confirmed when 2 consecutive chunks show dominant whistle-band energy
5. A 2.5-second cooldown prevents double-counting the same whistle
6. After reaching the target count, Buddy announces urgently via TTS

To calibrate for your cooker, run `python calibrate_whistle.py` and update the frequency constants in `agent.py`.

## Latency Optimization

The agent follows LiveKit's recommended low-latency stack. Key optimizations applied:

- Deepgram Nova-3 with 25ms endpointing (streaming STT, no batch delay)
- Cartesia Sonic with streaming audio output (first byte in ~300ms)
- LiveKit semantic turn detector (knows when you're done talking, not just silent)
- Silero VAD with 0.2s silence threshold
- Minimal system prompt (fewer tokens for faster LLM response)
- `session.say()` for timer alerts (bypasses LLM, goes direct to TTS)
- `session.generate_reply()` as fallback for long-idle sessions

## Voice Commands (Examples)

| Say This | Buddy Does |
|----------|------------|
| "Set a timer for 15 minutes for the geyser" | Sets 15-minute timer |
| "Remind me in 30 seconds to check the rice" | Sets 30-second timer |
| "Remind me about the doctor appointment tomorrow at 3 PM" | Schedules date reminder |
| "Listen for 3 cooker whistles" | Starts whistle monitor |
| "Stop listening for whistles" | Stops whistle monitor |
| "What timers are running?" | Lists all active timers/reminders |
| "Cancel the geyser timer" | Cancels matching timer |
| "Suggest some relaxing songs" | Recommends music by mood |
| "What's the latest news?" | Fetches headlines |

## API Key Setup

| Service | Free Tier | Sign Up |
|---------|-----------|---------|
| OpenAI | Pay-as-you-go | https://platform.openai.com |
| Deepgram | $200 free credits | https://console.deepgram.com |
| Cartesia | Free tier available | https://play.cartesia.ai |
| LiveKit | Self-hosted (free) | https://docs.livekit.io |

## Troubleshooting

**Terminal corrupted after running console mode:** Close the terminal and open a new one. Run `chcp 65001` on Windows for UTF-8 encoding.

**Microphone not detected:** Check Windows Sound Settings → Input device. Ensure volume is not muted and level is above 0.

**Agent not responding to voice:** Press `Ctrl+T` to switch to text mode. If text works but voice doesn't, the mic is the issue.

**Whistle not detected:** Run `python calibrate_whistle.py` to check your cooker's whistle frequency and update the constants.

**High latency:** Ensure stable internet. Use wired ethernet if possible. Check terminal for `e2e` time — should be under 2 seconds with the optimized stack.

## License

MIT
