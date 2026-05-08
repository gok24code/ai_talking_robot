import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# STT: Groq Whisper - ücretsiz, son derece hızlı
STT_MODEL = "whisper-large-v3-turbo"

# LLM: Groq LLaMA - ücretsiz tier
LLM_MODEL = "llama-3.3-70b-versatile"

# TTS: Microsoft Edge Neural - ücretsiz, yüksek kalite Türkçe ses
TTS_VOICE = "tr-TR-AhmetNeural"  # Erkek ses; alternatif: "tr-TR-EmelNeural"

LANGUAGE = "tr"
SAMPLE_RATE = 16000
CHANNELS = 1

# Ses cihazı indeksleri (None = sistem varsayılanı)
# Cihaz listesi için: python list_devices.py
AUDIO_INPUT_DEVICE = None   # Örn: USB mikrofon için 1
AUDIO_OUTPUT_DEVICE = None  # Şu an kullanılmıyor (mpg123 sistem default kullanır)

SYSTEM_PROMPT = (
    "You are a helpful conversational AI assistant speaking Turkish. "
    "Keep responses concise and natural for spoken conversation. "
    "Avoid markdown, bullet points, or special characters since your response will be converted to speech. "
    "Respond in Turkish at all times."
)
