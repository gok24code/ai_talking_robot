import os
from groq import Groq
from config import GROQ_API_KEY, STT_MODEL, LANGUAGE

_client = Groq(api_key=GROQ_API_KEY)


def transcribe_audio(audio_path: str) -> str:
    """WAV dosyasını Groq Whisper ile metne çevirir."""
    with open(audio_path, "rb") as f:
        result = _client.audio.transcriptions.create(
            model=STT_MODEL,
            file=f,
            language=LANGUAGE,
        )
    os.unlink(audio_path)
    return result.text.strip()
