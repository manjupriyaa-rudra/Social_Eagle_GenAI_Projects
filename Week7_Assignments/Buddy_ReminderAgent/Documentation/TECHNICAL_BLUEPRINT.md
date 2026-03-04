# Buddy Voice Agent — Technical Blueprint

## 1. Project Overview

Buddy is a real-time voice assistant designed for household task management, built on the LiveKit Agents framework. It combines speech recognition, natural language processing, text-to-speech synthesis, and real-time audio analysis into a single conversational agent.

The system targets three primary use cases for a home kitchen environment: counting pressure cooker whistles via audio frequency detection, managing time-based reminders for appliances like geysers and clothes dryers, and scheduling date-specific event reminders. Secondary capabilities include music recommendations and news retrieval.

## 2. Architecture

### 2.1 High-Level Flow

```
User speaks
    ↓
[Silero VAD] — detects voice activity
    ↓
[Deepgram Nova-3 STT] — streaming transcription (~200ms)
    ↓
[LiveKit Turn Detector] — semantic end-of-turn detection (~25ms)
    ↓
[OpenAI GPT-4o-mini LLM] — intent + response generation (~600ms)
    ↓ (may trigger function tools)
[Function Tools] — set_timer, start_whistle_monitor, etc.
    ↓
[Cartesia Sonic TTS] — streaming speech synthesis (~300ms)
    ↓
User hears response
```

Target end-to-end latency: 1.5-2.0 seconds.

### 2.2 Component Architecture

```
┌─────────────────────────────────────────────┐
│                LiveKit Room                  │
│  (WebRTC media transport)                   │
├─────────────────────────────────────────────┤
│              AgentSession                    │
│  ┌─────────┐ ┌──────────┐ ┌──────────────┐ │
│  │Silero   │ │Turn      │ │Noise         │ │
│  │VAD      │ │Detector  │ │Cancellation  │ │
│  └────┬────┘ └────┬─────┘ └──────────────┘ │
│       ↓           ↓                         │
│  ┌─────────────────────────────────────┐    │
│  │     Voice Pipeline                   │    │
│  │  STT → LLM → TTS                   │    │
│  │  (Deepgram) (OpenAI) (Cartesia)     │    │
│  └────────────┬────────────────────────┘    │
│               ↓                             │
│  ┌─────────────────────────────────────┐    │
│  │     Function Tools                   │    │
│  │  • set_timer        • get_news      │    │
│  │  • set_event_reminder               │    │
│  │  • start_whistle_monitor            │    │
│  │  • suggest_music    • list_timers   │    │
│  │  • cancel_timer     • get_today_date│    │
│  │  • stop_whistle_monitor             │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │     Background Tasks (asyncio)       │    │
│  │  • Timer coroutines                  │    │
│  │  • Event reminder coroutines         │    │
│  │  • Whistle listener (sounddevice)    │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

## 3. Technology Stack Details

### 3.1 LiveKit Agents Framework (v1.4.4)

The orchestration layer. Manages the WebRTC session, audio routing, and the STT-LLM-TTS pipeline. Handles interruptions, turn-taking, and streaming automatically. We use `AgentSession` (v1.x API) with `Agent` class for tool registration and system instructions.

Key configuration:
- `AgentSession` with VAD, STT, LLM, TTS, and turn detection
- `@function_tool` decorator for LLM-callable tools
- `RunContext[AgentData]` for shared state across tools
- `session.say()` for direct TTS (bypasses LLM)
- `session.generate_reply()` for LLM-driven responses

### 3.2 Deepgram Nova-3 (STT)

Streaming speech-to-text with 25ms endpointing. Chosen over OpenAI Whisper for significantly lower latency in real-time conversations. Nova-3 provides smart formatting (numbers, dates) and punctuation, which helps the turn detector work accurately.

Configuration: `model="nova-3"`, `language="en"`, `endpointing_ms=25`, `smart_format=True`, `punctuate=True`

### 3.3 OpenAI GPT-4o-mini (LLM)

Handles intent recognition, tool selection, and response generation. Chosen for its balance of speed and capability — fast enough for voice (TTFT ~600ms) while handling complex multi-tool scenarios like parsing "remind me tomorrow at 3pm" into correct date/time parameters.

The system prompt is kept minimal (under 50 tokens) to reduce TTFT.

### 3.4 Cartesia Sonic (TTS)

Streaming text-to-speech that begins producing audio from the first few words without waiting for the full response. Approximately 3x faster time-to-first-byte than OpenAI TTS-1. Uses a friendly female voice preset.

Configuration: `model="sonic-2024-10-19"`, `voice="79a125e8-cd45-4c13-8a67-188112f4dd22"`

### 3.5 Silero VAD

Lightweight voice activity detection running locally. Detects when the user starts and stops speaking. Configured with aggressive settings for fast response: `min_silence_duration=0.2s`, `activation_threshold=0.25`.

### 3.6 LiveKit Multilingual Turn Detector

A custom open-weights language model (~400MB) that adds semantic understanding on top of VAD. Instead of just detecting silence, it analyzes the transcription to determine if the user has finished their thought. This prevents premature responses when users pause mid-sentence.

Runs on CPU with ~25ms inference time.

### 3.7 NumPy + SoundDevice (Audio Analysis)

Used for the whistle detection feature. SoundDevice captures raw audio from the microphone, and NumPy performs FFT analysis to identify the whistle's frequency signature.

Detection pipeline: audio capture (0.3s chunks at 16kHz) → FFT → frequency band energy extraction → ratio comparison → consecutive confirmation → cooldown check.

### 3.8 LiveKit Server (Docker)

Self-hosted WebRTC media server. Routes audio between the user's device and the agent. In development, runs locally via Docker on ports 7880 (HTTP), 7881 (TCP), 7882 (UDP).

## 4. Feature Implementation Details

### 4.1 Timer System

Timers are stored in `AgentData.active_timers` dictionary. Each timer launches an `asyncio.create_task()` that sleeps for the specified duration, then triggers an alert. The alert uses a dual approach: `session.say()` first (fast, direct to TTS), followed by `session.generate_reply()` as a fallback to re-engage the audio pipeline if it went idle during a long sleep.

Supports both minutes and seconds parameters. Multiple timers run concurrently.

### 4.2 Event Reminders

Similar to timers but anchored to specific dates/times. The `get_today_date` tool provides current date context to the LLM, which then calculates the correct ISO date string for `set_event_reminder`. The reminder coroutine calculates the delay in seconds from `datetime.now()` to the target datetime.

### 4.3 Whistle Detection

The whistle detector runs as a background asyncio task alongside the voice agent. Key parameters were determined through a calibration process using `calibrate_whistle.py`, which records 8 seconds of actual cooker whistle audio and identifies peak frequencies via FFT analysis.

Detection uses a ratio-based approach: the energy in the whistle frequency band (5000-7500 Hz) must exceed a minimum threshold AND be at least 3x the average energy in non-whistle frequencies. Two consecutive positive detections are required to confirm a whistle, with a 2.5-second cooldown between counts.

Challenge: The whistle listener and the agent's audio pipeline both use the microphone, causing resource contention. Mitigated by adding brief pauses before TTS announcements to let the pipeline settle.

### 4.4 News Retrieval

Uses the NewsAPI free tier to fetch Indian top headlines. Implemented as an async HTTP request with a 4-second timeout. Falls back gracefully to suggesting news apps if the API is unavailable.

### 4.5 Music Suggestions

A lookup-based tool mapping moods to curated Illayaraja song lists. Provides playback guidance for YouTube and Google Assistant.

## 5. Latency Optimization Strategy

### 5.1 Model Selection

Each model was chosen specifically for minimum latency:

| Stage | Slow Option | Fast Option (Chosen) | Savings |
|-------|-------------|---------------------|---------|
| STT | OpenAI Whisper (~800ms) | Deepgram Nova-3 (~200ms) | ~600ms |
| TTS | OpenAI TTS-1 (~1500ms) | Cartesia Sonic (~300ms) | ~1200ms |
| Turn | VAD only (~400ms silence wait) | Semantic detector (~100ms) | ~300ms |

### 5.2 Pipeline Optimizations

- Ultra-fast VAD endpointing (0.2s silence threshold)
- Deepgram 25ms endpointing (detects end of phrase quickly)
- Minimal system prompt (fewer tokens = faster LLM TTFT)
- Compact tool docstrings (less context for LLM to process)
- `session.say()` for alerts (bypasses LLM entirely)
- Streaming TTS (audio starts before full response is generated)

### 5.3 Measured Latency Breakdown (Typical)

| Stage | Time |
|-------|------|
| VAD end-of-speech | ~200ms |
| STT final transcript | ~200ms |
| Turn detection | ~25ms |
| LLM TTFT | ~600ms |
| TTS TTFB | ~300ms |
| **Total e2e** | **~1.5-2.0s** |

## 6. State Management

All runtime state is stored in the `AgentData` class, passed to every tool via `RunContext[AgentData]`:

```
AgentData:
  active_timers: dict       # {timer_id: {task, display, set_at}}
  timer_counter: int        # Auto-incrementing timer ID
  event_reminders: dict     # {event_id: {event, datetime}}
  event_counter: int        # Auto-incrementing event ID
  whistle_listening: bool   # Is whistle monitor active?
  whistle_target: int       # Number of whistles to count
  whistle_count: int        # Current whistle count
  whistle_task_name: str    # What to do when target reached
  last_whistle_time: float  # Timestamp for cooldown
```

State is in-memory only and resets when the agent restarts. For production persistence, this could be backed by Redis or a database.

## 7. Error Handling

- `@session.on("error")` handler logs errors without crashing the session
- Timer/event alerts use try/except around `session.say()` with `generate_reply()` fallback
- News API has a 4-second timeout with graceful fallback
- Whistle listener wraps the entire loop in try/except to prevent background task crashes
- Network errors (API connection drops) are logged but don't kill the session

## 8. Future Enhancements

**Phone Deployment:** Build a web frontend using LiveKit's React SDK or deploy as a Progressive Web App. Connect to the agent via WebRTC for real-time voice from any device.

**Native Tamil Voice:** Integrate Google Cloud TTS Chirp 3 for high-quality Tamil speech synthesis. The agent instructions can be updated to respond in Tamil while keeping the same tool architecture.

**Persistent State:** Add Redis or SQLite to persist timers and reminders across agent restarts.

**Wake Word Detection:** Add always-on listening with a wake word ("Hey Buddy") so the agent can run continuously without needing to be in an active conversation.

**Multi-Room Support:** Deploy multiple agents for different rooms in the house, each with its own context and capabilities.

## 9. Development Commands

```bash
# Start LiveKit server (Docker)
docker run --rm -p 7880:7880 -p 7881:7881 -p 7882:7882/udp livekit/livekit-server --dev

# Download required models (first time only)
python agent.py download-files

# Run in console mode (local mic/speaker)
python agent.py console

# Run in dev mode (connect via browser playground)
python agent.py dev

# Calibrate whistle detection
python calibrate_whistle.py

# Test microphone
python -c "import sounddevice; print(sounddevice.query_devices())"
```
