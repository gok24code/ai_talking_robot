import collections
import tempfile

import numpy as np
import sounddevice as sd
import webrtcvad
from scipy.io import wavfile

from config import AUDIO_INPUT_DEVICE, SAMPLE_RATE

# VAD ayarları
_VAD_AGGRESSIVENESS = 2     # 0–3 (3 = gürültüye en dayanıklı)
_FRAME_MS = 30              # webrtcvad için geçerli: 10, 20, veya 30 ms
_SILENCE_TIMEOUT = 1.5      # Bu kadar sessizlik sonrası kayıt durur (saniye)
_MIN_SPEECH_FRAMES = 4      # Yanlış tetiklenmeyi önlemek için minimum konuşma frame sayısı
_PRE_BUFFER_FRAMES = 10     # Konuşma başlamadan önceki context frame sayısı


def record_with_vad() -> str | None:
    """
    Mikrofonu sürekli dinler; konuşma algılanınca kaydeder,
    sessizlik başlayınca durdurur. WAV dosya yolunu döndürür.
    Manuel hiçbir işlem gerektirmez.
    """
    vad = webrtcvad.Vad(_VAD_AGGRESSIVENESS)
    frame_size = int(SAMPLE_RATE * _FRAME_MS / 1000)
    silence_limit = int(_SILENCE_TIMEOUT * 1000 / _FRAME_MS)

    pre_buffer: collections.deque = collections.deque(maxlen=_PRE_BUFFER_FRAMES)
    recording: list[bytes] = []
    is_speaking = False
    silent_frames = 0
    speech_frames = 0

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        blocksize=frame_size,
        device=AUDIO_INPUT_DEVICE,
    ) as stream:
        while True:
            raw, _ = stream.read(frame_size)
            frame = bytes(raw)

            try:
                speech = vad.is_speech(frame, SAMPLE_RATE)
            except Exception:
                speech = False

            if speech:
                if not is_speaking:
                    is_speaking = True
                    recording.extend(pre_buffer)
                silent_frames = 0
                speech_frames += 1
                recording.append(frame)
            else:
                pre_buffer.append(frame)
                if is_speaking:
                    silent_frames += 1
                    recording.append(frame)
                    if silent_frames >= silence_limit:
                        break  # sessizlik süresi doldu → kayıt bitti

    if speech_frames < _MIN_SPEECH_FRAMES:
        return None  # çok kısa → gürültü, atla

    audio = np.frombuffer(b"".join(recording), dtype=np.int16)
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wavfile.write(tmp.name, SAMPLE_RATE, audio)
    tmp.close()
    return tmp.name
