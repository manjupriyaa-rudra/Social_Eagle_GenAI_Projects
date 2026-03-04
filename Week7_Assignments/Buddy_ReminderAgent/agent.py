"""
Buddy - House Help Voice Agent (Low-Latency Optimized)
========================================================
Following LiveKit recommended stack:
  STT:  Deepgram Nova-3 (streaming, fastest STT)
  LLM:  OpenAI GPT-4o-mini (fast, good enough)
  TTS:  Cartesia Sonic-3 (fastest TTS, streams audio)
  Turn: LiveKit Turn Detector (semantic end-of-turn)
"""

import asyncio
import logging
import numpy as np
import sounddevice as sd
from datetime import datetime, timedelta

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, RunContext, function_tool
from livekit.plugins import openai, silero, deepgram, cartesia
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("buddy-agent")

# ── Whistle Detection Settings ──
WHISTLE_FREQ_LOW = 5000
WHISTLE_FREQ_HIGH = 7500
WHISTLE_THRESHOLD = 0.005
WHISTLE_MAGNITUDE_MIN = 15
SAMPLE_RATE = 16000
CHUNK_DURATION = 0.3
COOLDOWN_SECONDS = 2.5


class AgentData:
    def __init__(self):
        self.active_timers: dict[str, dict] = {}
        self.timer_counter: int = 0
        self.event_reminders: dict[str, dict] = {}
        self.event_counter: int = 0
        self.whistle_listening: bool = False
        self.whistle_target: int = 0
        self.whistle_count: int = 0
        self.whistle_task_name: str = ""
        self.last_whistle_time: float = 0


# ── Tools: Timers ──

@function_tool()
async def set_timer(context: RunContext[AgentData], task_description: str, minutes: float = 0, seconds: int = 0):
    """Set a timer. Args: task_description: what to remind. minutes: mins. seconds: secs."""
    total_seconds = (minutes * 60) + seconds
    if total_seconds <= 0:
        return "Please specify a time."
    display = f"{minutes} min" if minutes >= 1 else f"{int(total_seconds)} sec"
    ud = context.userdata
    ud.timer_counter += 1
    tid = f"t_{ud.timer_counter}"
    ud.active_timers[tid] = {"task": task_description, "display": display, "set_at": datetime.now().strftime("%H:%M")}
    logger.info(f"TIMER: '{task_description}' {display}")
    asyncio.create_task(_run_timer(context.session, ud, tid, task_description, total_seconds))
    return f"Timer set! '{task_description}' in {display}."


@function_tool()
async def set_event_reminder(context: RunContext[AgentData], event_description: str, date_str: str, time_str: str = "09:00"):
    """Set date/time reminder. Args: event_description: what. date_str: YYYY-MM-DD. time_str: HH:MM."""
    ud = context.userdata
    ud.event_counter += 1
    eid = f"e_{ud.event_counter}"
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        return "Bad date format."
    now = datetime.now()
    if dt <= now:
        return "That's in the past!"
    ud.event_reminders[eid] = {"event": event_description, "datetime": dt.strftime("%Y-%m-%d %H:%M")}
    delay = (dt - now).total_seconds()
    logger.info(f"EVENT: '{event_description}' at {dt}")
    asyncio.create_task(_run_event_reminder(context.session, ud, eid, event_description, delay))
    return f"Reminder set for '{event_description}' on {dt.strftime('%b %d %I:%M %p')}."


@function_tool()
async def list_timers(context: RunContext[AgentData]):
    """List active timers and reminders."""
    ud = context.userdata
    p = []
    for i in ud.active_timers.values(): p.append(f"Timer: {i['task']} ({i['display']})")
    for i in ud.event_reminders.values(): p.append(f"Event: {i['event']} ({i['datetime']})")
    if ud.whistle_listening: p.append(f"Whistle: {ud.whistle_count}/{ud.whistle_target}")
    return "\n".join(p) if p else "Nothing active."


@function_tool()
async def cancel_timer(context: RunContext[AgentData], task_description: str):
    """Cancel timer/reminder. Args: task_description: partial match."""
    ud = context.userdata
    for k, v in list(ud.active_timers.items()):
        if task_description.lower() in v["task"].lower():
            del ud.active_timers[k]; return f"Cancelled '{v['task']}'."
    for k, v in list(ud.event_reminders.items()):
        if task_description.lower() in v["event"].lower():
            del ud.event_reminders[k]; return f"Cancelled '{v['event']}'."
    return "No match found."


@function_tool()
async def get_today_date(context: RunContext[AgentData]):
    """Get today's date. Call before setting event reminders."""
    now = datetime.now()
    return f"Today: {now.strftime('%A %B %d %Y')} ({now.strftime('%Y-%m-%d')}). Tomorrow: {(now+timedelta(days=1)).strftime('%Y-%m-%d')}. Time: {now.strftime('%I:%M %p')}"


# ── Tools: Whistle ──

@function_tool()
async def start_whistle_monitor(context: RunContext[AgentData], whistle_count: int, task_description: str = "turn off the cooker"):
    """Listen for cooker whistles. Args: whistle_count: how many. task_description: what to do after."""
    ud = context.userdata
    if ud.whistle_listening:
        return f"Already listening! {ud.whistle_count}/{ud.whistle_target} so far."
    ud.whistle_listening = True; ud.whistle_target = whistle_count; ud.whistle_count = 0
    ud.whistle_task_name = task_description; ud.last_whistle_time = 0
    asyncio.create_task(_whistle_listener(context.session, ud))
    return f"Listening for {whistle_count} whistles!"


@function_tool()
async def stop_whistle_monitor(context: RunContext[AgentData]):
    """Stop whistle monitor."""
    ud = context.userdata
    if not ud.whistle_listening: return "Not running."
    ud.whistle_listening = False
    return f"Stopped. {ud.whistle_count}/{ud.whistle_target} detected."


# ── Tools: Music & News ──

@function_tool()
async def suggest_music(context: RunContext[AgentData], mood: str = "relaxed", song_request: str = ""):
    """Suggest songs. Args: mood: happy/sad/relaxed/energetic. song_request: specific request."""
    songs = {
        "happy": "Thendral Vandhu Theendum Podhu, Pudhu Vellai Mazhai",
        "sad": "Ennai Thalatta Varuvala, Sevvaanam",
        "relaxed": "Mandram Vandha Thendralukku, Thenpandi Cheemayile",
        "energetic": "Rakkamma Kaiya Thattu, Mukkala Mukkabula",
    }
    s = songs.get(mood.lower(), songs["relaxed"])
    r = f"For {mood} mood try: {s}. Search on YouTube or say 'Hey Google play' and the name."
    if song_request: r += f" You asked about '{song_request}' — search on YouTube!"
    return r


@function_tool()
async def get_news(context: RunContext[AgentData], topic: str = "headlines"):
    """Get news. Args: topic: headlines/sports/tech/business."""
    import aiohttp
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://newsapi.org/v2/top-headlines?country=in&pageSize=3&apiKey=demo", timeout=aiohttp.ClientTimeout(total=4)) as r:
                if r.status == 200:
                    data = await r.json()
                    titles = [a["title"] for a in data.get("articles", [])[:3] if a.get("title")]
                    if titles: return "Headlines: " + ". ".join(titles)
    except: pass
    return f"Couldn't fetch news. Check Google News or NDTV for '{topic}'."


# ── Background Tasks ──

async def _run_timer(session, ud, tid, task, total_seconds):
    logger.info(f"Timer waiting {total_seconds:.0f}s...")
    await asyncio.sleep(total_seconds)
    if tid not in ud.active_timers: return
    del ud.active_timers[tid]
    logger.info(f"TIMER FIRED: '{task}'")
    try: await session.say(f"Hey! Time's up! Please {task} now!")
    except Exception as e: logger.warning(f"say failed: {e}")
    await asyncio.sleep(2)
    await session.generate_reply(instructions=f"Remind: '{task}' is due! One short sentence.")


async def _run_event_reminder(session, ud, eid, event, delay):
    logger.info(f"Event waiting {delay:.0f}s...")
    await asyncio.sleep(delay)
    if eid not in ud.event_reminders: return
    del ud.event_reminders[eid]
    logger.info(f"EVENT FIRED: '{event}'")
    try: await session.say(f"Hey! Time to {event}!")
    except Exception as e: logger.warning(f"say failed: {e}")
    await asyncio.sleep(2)
    await session.generate_reply(instructions=f"Remind: '{event}' now! One short sentence.")


# ── Whistle Detection ──

def _detect_whistle(audio_chunk):
    level = np.abs(audio_chunk).mean()
    if level < WHISTLE_THRESHOLD: return False, 0.0
    fft = np.abs(np.fft.rfft(audio_chunk))
    freqs = np.fft.rfftfreq(len(audio_chunk), 1.0 / SAMPLE_RATE)
    wm = (freqs >= WHISTLE_FREQ_LOW) & (freqs <= WHISTLE_FREQ_HIGH)
    we = fft[wm].max() if wm.any() else 0
    te = fft[freqs >= 200].mean() if (freqs >= 200).any() else 1
    ratio = we / (te + 0.001)
    hit = (we > WHISTLE_MAGNITUDE_MIN) and (ratio > 3.0)
    if hit: logger.info(f"[WHISTLE] e={we:.1f} r={ratio:.1f}")
    return hit, ratio


async def _whistle_listener(session, ud):
    import time
    chunk = int(SAMPLE_RATE * CHUNK_DURATION)
    consec = 0
    try:
        while ud.whistle_listening:
            audio = sd.rec(chunk, samplerate=SAMPLE_RATE, channels=1, dtype='float32'); sd.wait()
            hit, _ = _detect_whistle(audio.flatten())
            consec = consec + 1 if hit else 0
            if consec >= 2:
                now = time.time()
                if now - ud.last_whistle_time > COOLDOWN_SECONDS:
                    ud.whistle_count += 1; ud.last_whistle_time = now; consec = 0
                    logger.info(f"WHISTLE #{ud.whistle_count}/{ud.whistle_target}")
                    if ud.whistle_count < ud.whistle_target:
                        await asyncio.sleep(1.0)
                        await session.say(f"Whistle {ud.whistle_count} of {ud.whistle_target}.")
                    if ud.whistle_count >= ud.whistle_target:
                        ud.whistle_listening = False
                        await asyncio.sleep(1.5)
                        await session.say(f"All {ud.whistle_target} whistles done! Please {ud.whistle_task_name} now!")
                        await asyncio.sleep(2)
                        await session.say(f"Reminder! {ud.whistle_task_name}!")
                        return
            await asyncio.sleep(0.05)
    except Exception as e:
        logger.error(f"Whistle error: {e}"); ud.whistle_listening = False


# ── Agent ──

BUDDY_INSTRUCTIONS = """You are Buddy, a friendly house help voice assistant.
Keep responses to 1 SHORT sentence. Be warm.
For event reminders, call get_today_date first.
Match task descriptions EXACTLY to what user asked.
When asked to sing, joke and use suggest_music.
When asked about news, use get_news."""


class BuddyAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=BUDDY_INSTRUCTIONS,
            tools=[set_timer, list_timers, cancel_timer, set_event_reminder,
                   get_today_date, start_whistle_monitor, stop_whistle_monitor,
                   suggest_music, get_news],
        )


# ── Entrypoint ──

async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    session = AgentSession[AgentData](
        # ── VAD: Silero (lightweight, runs locally) ──
        vad=silero.VAD.load(
            min_speech_duration=0.1,
            min_silence_duration=0.2,    # Very fast end-of-speech
            activation_threshold=0.25,
        ),

        # ── STT: Deepgram Nova-3 (streaming, ~200ms faster than Whisper) ──
        stt=deepgram.STT(
            model="nova-3",
            language="en",
            smart_format=True,
            punctuate=True,
            endpointing_ms=25,           # Ultra-fast endpointing
        ),

        # ── LLM: GPT-4o-mini (fast, with limited tokens) ──
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.7,
        ),

        # ── TTS: Cartesia Sonic (streaming, ~3x faster than OpenAI TTS) ──
        tts=cartesia.TTS(
            model="sonic-2024-10-19",
            voice="79a125e8-cd45-4c13-8a67-188112f4dd22",  # Friendly female
        ),

        # ── Turn Detection: Semantic (knows when user is done talking) ──
        turn_detection=MultilingualModel(),

        userdata=AgentData(),
    )

    @session.on("user_input_transcribed")
    def on_transcription(event):
        logger.info(f">>> USER: {event.transcript}")

    @session.on("error")
    def on_error(event):
        logger.error(f"Error: {event}")

    await session.start(room=ctx.room, agent=BuddyAgent())
    await session.generate_reply(instructions="Say only: 'Hey! I'm Buddy. What can I do for you?'")


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))