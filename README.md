# AI Konuşma Robotu

Groq API tabanlı, tamamen ücretsiz STT + LLM + TTS pipeline'ı ile çalışan sesli AI asistan.

| Bileşen | Teknoloji | Neden? |
|---|---|---|
| STT | Groq Whisper (`whisper-large-v3-turbo`) | Ücretsiz, son derece hızlı |
| LLM | Groq LLaMA (`llama-3.3-70b-versatile`) | Ücretsiz tier, yüksek kalite |
| TTS | Microsoft Edge Neural (`tr-TR-AhmetNeural`) | Ücretsiz, doğal Türkçe ses |

---

## Gereksinimler

- Python 3.10+
- Groq API anahtarı → [console.groq.com](https://console.groq.com)
- Mikrofon
- İnternet bağlantısı (Groq API + edge-tts için)

---

## Kurulum — Windows

```powershell
# 1. Depoyu klonla
git clone https://github.com/kullanici/ai_talking_robot.git
cd ai_talking_robot

# 2. Sanal ortam oluştur
python -m venv .venv
.venv\Scripts\activate

# 3. Bağımlılıkları kur
python -m pip install -r requirements-windows.txt

# 4. API anahtarını ayarla
copy .env.example .env
# .env dosyasını açıp GROQ_API_KEY değerini gir

# 5. Çalıştır
python main.py
```

---

## Kurulum — Raspberry Pi

**Donanım:** Raspberry Pi 4 / 5, USB mikrofon, USB hoparlör veya 3.5mm hoparlör

```bash
# 1. Depoyu klonla
git clone https://github.com/kullanici/ai_talking_robot.git
cd ai_talking_robot

# 2. Kurulum scriptini çalıştır (sistem paketleri + venv + bağımlılıklar)
chmod +x setup_rpi.sh
./setup_rpi.sh

# 3. Sanal ortamı etkinleştir ve çalıştır
source .venv/bin/activate
python main.py
```

Script şunları yapar:
- `portaudio19-dev`, `mpg123`, `alsa-utils` sistem paketlerini kurar
- Python sanal ortamı ve bağımlılıkları kurar
- `.env` dosyası yoksa oluşturur
- Mevcut ses cihazlarını listeler
- İsteğe bağlı systemd servisi kurar (otomatik başlatma)

### Ses cihazı seçimi (RPi)

USB mikrofon takıldıktan sonra:

```bash
python list_devices.py
```

Çıktıdaki mikrofon ID'sini `config.py`'e yazın:

```python
AUDIO_INPUT_DEVICE = 1  # USB mikrofon ID'niz
```

### ALSA ses seviyesi ayarı (RPi)

```bash
alsamixer          # Grafik arayüz ile ayarla
# veya
amixer set Master 80%
amixer set Capture 80%
```

---

## Kullanım

```
>>> Konuşmak için Enter'a basın...
Dinliyorum... (bitince Enter'a basın)
[Enter'a basın]
Siz: Merhaba, nasılsın?
AI: Merhaba! İyiyim, teşekkür ederim. Sana nasıl yardımcı olabilirim?
```

- **Enter** → kaydı başlat
- **Enter** (tekrar) → kaydı durdur ve işle
- **"Çıkış"** de veya **Ctrl+C** → programı kapat

---

## Yapılandırma

`config.py` dosyasından tüm ayarlar değiştirilebilir:

```python
TTS_VOICE = "tr-TR-AhmetNeural"   # Erkek ses
TTS_VOICE = "tr-TR-EmelNeural"    # Kadın ses

AUDIO_INPUT_DEVICE = None          # None = sistem varsayılanı
AUDIO_INPUT_DEVICE = 2             # Belirli mikrofon ID'si
```

---

## Proje Yapısı

```
ai_talking_robot/
├── main.py                  # Ana döngü
├── config.py                # Tüm ayarlar
├── list_devices.py          # Ses cihazı listesi
├── requirements.txt         # Ortak bağımlılıklar
├── requirements-windows.txt # Windows (pygame ekler)
├── setup_rpi.sh             # Raspberry Pi kurulum scripti
├── .env                     # API anahtarı (git'e gitmez)
├── .env.example             # Örnek .env şablonu
├── agent/
│   ├── stt.py               # Groq Whisper transkripsiyon
│   ├── llm.py               # Groq LLaMA yanıt üretimi
│   └── tts.py               # edge-tts ses sentezi
└── utils/
    └── audio.py             # Mikrofon kaydı
```

---

## Sorun Giderme

**Mikrofon algılanmıyor**
```bash
python list_devices.py
# Doğru ID'yi config.py'e yaz: AUDIO_INPUT_DEVICE = <ID>
```

**RPi'de ses çıkışı yok**
```bash
# mpg123 kurulu mu?
which mpg123 || sudo apt install mpg123

# Ses seviyesi sıfır mı?
amixer set Master 80%
```

**API hatası**
```
# .env dosyasındaki anahtarı kontrol et
cat .env
# Groq rate limit aşıldıysa birkaç saniye bekle
```
