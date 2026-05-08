import asyncio
import sys
import tempfile
import os
import edge_tts
from config import TTS_VOICE


async def speak(text: str) -> None:
    """Metni edge-tts ile sese çevirir ve çalar."""
    communicate = edge_tts.Communicate(text, TTS_VOICE)

    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp_path = tmp.name
    tmp.close()

    await communicate.save(tmp_path)
    _play(tmp_path)
    os.unlink(tmp_path)


def _play(path: str) -> None:
    if sys.platform == "win32":
        _play_pygame(path)
    else:
        _play_mpg123(path)


def _play_pygame(path: str) -> None:
    import pygame
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    import time
    while pygame.mixer.music.get_busy():
        time.sleep(0.05)
    pygame.mixer.music.unload()
    pygame.mixer.quit()


def _play_mpg123(path: str) -> None:
    """Raspberry Pi için mpg123 ile çalar (sudo apt install mpg123)."""
    import subprocess
    subprocess.run(["mpg123", "-q", path], check=True)
