# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI Talking Robot** is a Turkish-language conversational AI assistant powered by free APIs from Groq and Microsoft Edge.

| Component | Technology | Why |
|---|---|---|
| **STT** | Groq Whisper (`whisper-large-v3-turbo`) | Free, extremely fast speech-to-text |
| **LLM** | Groq LLaMA (`llama-3.3-70b-versatile`) | Free tier, high quality responses |
| **TTS** | Microsoft Edge Neural (`tr-TR-AhmetNeural`) | Free, natural-sounding Turkish voice |
| **Audio** | `webrtcvad` (WebRTC VAD) | Voice Activity Detection for hands-free recording |

## Architecture

The codebase is organized as a **linear pipeline**: microphone → VAD detection → Groq Whisper (transcribe) → Groq LLaMA (respond) → edge-tts (speak) → repeat.

**Key design decisions:**
- **No manual input required**: `utils/audio.py` uses Voice Activity Detection (VAD) to automatically detect speech start/stop. User speaks whenever ready—no button pressing.
- **Conversation history**: `main.py` maintains `conversation_history` (list of `{"role": "user"|"assistant", "content": ...}` dicts) sent to LLM for context-aware responses.
- **Cross-platform audio playback**: `agent/tts.py` abstracts playback—pygame on Windows, mpg123 on Raspberry Pi.
- **Graceful degradation**: VAD has tunable aggressiveness; if it fails, the app continues (returns empty text, skips TTS).

## File Structure

```
agent/
  ├── llm.py              # Groq chat completions, appends system prompt
  ├── stt.py              # Groq Whisper transcription
  └── tts.py              # edge-tts speech synthesis + platform-specific playback
utils/
  └── audio.py            # VAD-powered continuous recording, no manual intervention
main.py                   # Event loop, conversation history, exit word detection
config.py                 # All API keys, model names, voice, device IDs
test_components.py        # Comprehensive component validation (no hardware needed)
```

## Common Commands

**Setup & run (Windows):**
```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements-windows.txt
copy .env.example .env
# Edit .env, add your GROQ_API_KEY from console.groq.com
python main.py
```

**Setup & run (Raspberry Pi):**
```bash
chmod +x setup_rpi.sh
./setup_rpi.sh             # Installs system packages, venv, deps, lists audio devices
source .venv/bin/activate
python main.py
```

**Test all components (no hardware/microphone required):**
```powershell
python test_components.py
```
Validates imports, config, VAD, LLM, TTS, STT APIs, and audio device detection.

**List audio devices (find USB mic ID for RPi):**
```powershell
python list_devices.py
```
Then set `AUDIO_INPUT_DEVICE = <ID>` in `config.py`.

**Configure audio input/output:**
Edit `config.py`:
- `AUDIO_INPUT_DEVICE`: Device index from `list_devices.py` (None = system default)
- `TTS_VOICE`: `"tr-TR-AhmetNeural"` (male) or `"tr-TR-EmelNeural"` (female)
- VAD settings in `utils/audio.py`: `_VAD_AGGRESSIVENESS`, `_SILENCE_TIMEOUT`, `_MIN_SPEECH_FRAMES`

## Key Implementation Details

### Voice Activity Detection (`utils/audio.py`)

- Runs continuously in `stream.read()` loop, processing 30ms frames (480 samples @ 16 kHz).
- Detects speech via `webrtcvad.Vad.is_speech()`.
- Buffers pre-speech audio (`_PRE_BUFFER_FRAMES`) for natural start timing.
- Records until silence exceeds `_SILENCE_TIMEOUT` (default 1.5s).
- Returns `None` if fewer than `_MIN_SPEECH_FRAMES` detected (noise rejection).
- **Do not call manually**—`main.py` calls `record_with_vad()` in the event loop.

### LLM Context Management (`main.py` & `agent/llm.py`)

- `conversation_history` is a list of message dicts, persisted across the session.
- `get_response(conversation_history)` prepends `SYSTEM_PROMPT` from `config.py` and sends to Groq.
- System prompt enforces Turkish responses and spoken-format output (no markdown).
- History grows unbounded—for long sessions, consider truncating old messages or summarizing.

### Cross-Platform Playback (`agent/tts.py`)

- `speak(text)` is async; returns after TTS file is saved.
- `_play(path)` dispatches: Windows → `pygame.mixer`, Linux/RPi → `mpg123` subprocess.
- Main loop sleeps 0.4s after TTS to avoid speaker feedback triggering VAD.

### Error Handling

- STT/LLM/TTS exceptions caught in `main.py` loop—prints error, continues listening.
- Empty transcriptions (VAD returns `None` or STT yields empty string) skip LLM and TTS.
- Graceful exit: exit words (`"çıkış"`, `"exit"`, etc.) trigger farewell and break.

## Environment Setup

Requires `.env` file with single variable:
```
GROQ_API_KEY=sk_xxx...
```
Get free key from [console.groq.com](https://console.groq.com).

Dependencies:
- `groq`: Whisper + LLaMA APIs
- `edge-tts`: Text-to-speech synthesis
- `sounddevice`: Audio I/O
- `scipy`: WAV file writing
- `webrtcvad-wheels`: Voice activity detection
- `pygame` (Windows only): Audio playback on Windows
- `mpg123` (RPi only): Audio playback on Linux, installed by `setup_rpi.sh`

## Testing

`test_components.py` does **not** require a microphone or speakers. It validates:
1. All imports (groq, edge-tts, sounddevice, webrtcvad, scipy, pygame if Windows)
2. Config loading and GROQ_API_KEY presence
3. VAD initialization on a silence frame
4. LLM API connectivity (sends test query)
5. TTS MP3 generation (does not play)
6. STT API connectivity (sends synthetic sine wave)
7. Audio device detection

Use this to validate setup before running `main.py`.

## Deployment Notes

**Raspberry Pi specifics:**
- `setup_rpi.sh` installs `portaudio19-dev`, `mpg123`, `alsa-utils` via apt.
- After USB mic is plugged in, run `python list_devices.py` and set `AUDIO_INPUT_DEVICE` in `config.py`.
- If no audio output, check `amixer set Master 80%` and `amixer set Capture 80%`.
- For headless/systemd service, `setup_rpi.sh` offers optional systemd setup.

**Rate limits:**
- Groq APIs have free-tier rate limits (very generous). If you hit them, backoff is automatic in the SDK.

## Future Considerations

- **Conversation history length**: Currently unbounded; for long sessions, consider summarization or rolling context.
- **Latency**: Groq APIs are fast; bottleneck is typically TTS generation and network.
- **Multi-language support**: System prompt is hardcoded for Turkish; to add languages, parameterize `LANGUAGE` and `SYSTEM_PROMPT` based on a config flag.
