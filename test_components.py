"""
Bileşen testleri - mikrofon/hoparlör gerektirmez.
Her API ve modül ayrı ayrı doğrulanır.
"""
import asyncio
import sys
import os
import tempfile
import numpy as np
from scipy.io import wavfile

sys.stdout.reconfigure(encoding="utf-8")

PASS = "[OK]"
FAIL = "[FAIL]"


def section(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print("=" * 50)


# ── 1. Import testi ──────────────────────────────────
section("1. Modül importları")

try:
    import groq, edge_tts, sounddevice, scipy, dotenv, webrtcvad
    print(f"{PASS} Ortak paketler yüklü")
except ImportError as e:
    print(f"{FAIL} Eksik paket: {e}")
    sys.exit(1)

try:
    import pygame
    print(f"{PASS} pygame yüklü (Windows TTS oynatma)")
except ImportError:
    print(f"[--] pygame yok (RPi'de beklenen durum, mpg123 kullanılır)")


# ── 2. Config testi ──────────────────────────────────
section("2. Yapılandırma")

from config import GROQ_API_KEY, STT_MODEL, LLM_MODEL, TTS_VOICE, AUDIO_INPUT_DEVICE

if GROQ_API_KEY:
    print(f"{PASS} GROQ_API_KEY yüklü ({GROQ_API_KEY[:8]}...)")
else:
    print(f"{FAIL} GROQ_API_KEY eksik — .env dosyasını kontrol edin")
    sys.exit(1)

print(f"{PASS} STT modeli : {STT_MODEL}")
print(f"{PASS} LLM modeli : {LLM_MODEL}")
print(f"{PASS} TTS sesi   : {TTS_VOICE}")
print(f"{PASS} Giriş cihazı: {AUDIO_INPUT_DEVICE if AUDIO_INPUT_DEVICE is not None else 'sistem varsayılanı'}")


# ── 3. VAD testi ─────────────────────────────────────
section("3. VAD (webrtcvad)")

try:
    import webrtcvad
    vad = webrtcvad.Vad(2)
    # 30ms frame @ 16kHz = 480 örnek = 960 byte
    silence_frame = bytes(960)
    result = vad.is_speech(silence_frame, 16000)
    print(f"{PASS} webrtcvad başlatıldı, sessizlik testi: {'konuşma' if result else 'sessizlik'} (beklenen: sessizlik)")
except Exception as e:
    print(f"{FAIL} VAD hatası: {e}")


# ── 4. LLM testi ─────────────────────────────────────
section("4. LLM (Groq API)")

from agent.llm import get_response

try:
    history = [{"role": "user", "content": "Merhaba! Tek cümleyle kendini tanıt."}]
    response = get_response(history)
    print(f"{PASS} Yanıt alındı:")
    print(f"     {response}")
except Exception as e:
    print(f"{FAIL} LLM hatası: {e}")


# ── 5. TTS testi ─────────────────────────────────────
section("5. TTS (edge-tts — ses dosyası oluşturma)")

async def test_tts():
    import edge_tts
    communicate = edge_tts.Communicate("Merhaba, sistem testi başarılı.", TTS_VOICE)
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp_path = tmp.name
    tmp.close()
    await communicate.save(tmp_path)
    size = os.path.getsize(tmp_path)
    os.unlink(tmp_path)
    return size

try:
    size = asyncio.run(test_tts())
    print(f"{PASS} Ses dosyası oluşturuldu ({size:,} byte)")
except Exception as e:
    print(f"{FAIL} TTS hatası: {e}")


# ── 6. STT testi ─────────────────────────────────────
section("6. STT (Groq Whisper — sentetik ses)")

from agent.stt import transcribe_audio

try:
    sr = 16000
    t = np.linspace(0, 1, sr, dtype=np.float32)
    tone = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wavfile.write(tmp.name, sr, tone)
    tmp.close()
    result = transcribe_audio(tmp.name)
    print(f"{PASS} Whisper API erişilebilir")
    print(f"     Transkripsiyon: '{result}' (sinüs dalgası için boş beklenir)")
except Exception as e:
    print(f"{FAIL} STT hatası: {e}")


# ── 7. Ses cihazları ─────────────────────────────────
section("7. Ses cihazları")

import sounddevice as sd
try:
    inp = sd.query_devices(kind="input")
    print(f"{PASS} Varsayılan giriş: {inp['name']}")
except Exception as e:
    print(f"{FAIL} Giriş cihazı bulunamadı: {e}")

try:
    out = sd.query_devices(kind="output")
    print(f"{PASS} Varsayılan çıkış: {out['name']}")
except Exception as e:
    print(f"{FAIL} Çıkış cihazı bulunamadı: {e}")


# ── Özet ─────────────────────────────────────────────
section("Test tamamlandı")
print("Tüm bileşenler hazırsa 'python main.py' ile başlatabilirsiniz.\n")
