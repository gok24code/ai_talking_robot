#!/bin/bash
# Raspberry Pi kurulum scripti — tam otomatik, soru sormaz
# Desteklenen: Raspberry Pi OS Bookworm / Bullseye (64-bit önerilir)
# Test edildi: RPi 4, RPi 5

set -e

VENV_DIR=".venv"
SERVICE_NAME="ai-robot"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==================================================="
echo "   AI Konuşma Robotu - Raspberry Pi Kurulumu"
echo "==================================================="

# Root olarak çalıştırılmamalı
if [ "$EUID" -eq 0 ]; then
    echo "HATA: Root olarak çalıştırmayın. sudo gereken komutlar otomatik çağrılır."
    exit 1
fi

# ─── 1. Sistem bağımlılıkları ───────────────────────────────────────────────
echo ""
echo "[1/5] Sistem paketleri kuruluyor..."
sudo apt-get update -qq
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    portaudio19-dev \
    libportaudio2 \
    mpg123 \
    alsa-utils \
    2>&1 | grep -vE "^(Hit|Get|Reading|Building|Calculating)" || true
echo "      Sistem paketleri hazır."

# Kullanıcıyı audio grubuna ekle (servis olarak çalışmak için gerekli)
sudo usermod -aG audio "$USER"
echo "      Kullanıcı '$USER' audio grubuna eklendi."

# ─── 2. Python sanal ortamı ─────────────────────────────────────────────────
echo ""
echo "[2/5] Python sanal ortamı oluşturuluyor..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip -q
echo "      Sanal ortam hazır."

# ─── 3. Python bağımlılıkları ───────────────────────────────────────────────
echo ""
echo "[3/5] Python paketleri kuruluyor..."
pip install -r requirements.txt -q
echo "      Python paketleri hazır."

# ─── 4. .env yapılandırması ─────────────────────────────────────────────────
echo ""
echo "[4/5] Yapılandırma kontrol ediliyor..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo ""
    echo "  UYARI: .env dosyası oluşturuldu."
    echo "  Groq API anahtarınızı girin ve tekrar çalıştırın:"
    echo ""
    echo "    nano $PROJECT_DIR/.env"
    echo ""
    exit 0
fi
echo "      .env mevcut."

# ─── 5. Systemd servisi ─────────────────────────────────────────────────────
echo ""
echo "[5/5] Systemd servisi kuruluyor..."

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=AI Konusma Robotu
After=network-online.target sound.target
Wants=network-online.target

[Service]
Type=simple
User=${USER}
WorkingDirectory=${PROJECT_DIR}
ExecStart=${PROJECT_DIR}/${VENV_DIR}/bin/python ${PROJECT_DIR}/main.py
Restart=on-failure
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}.service"
echo "      Servis kuruldu ve etkinleştirildi: ${SERVICE_NAME}.service"

# ─── Ses cihazları bilgisi ──────────────────────────────────────────────────
echo ""
echo "==================================================="
echo "   Kurulum tamamlandı!"
echo "==================================================="
echo ""
echo "  Ses cihazlarını görmek için:"
echo "    source ${VENV_DIR}/bin/activate && python list_devices.py"
echo ""
echo "  Gerekirse config.py'de mikrofon ID'sini ayarlayın:"
echo "    AUDIO_INPUT_DEVICE = <ID>"
echo ""
echo "  Şimdi başlatmak için:"
echo "    sudo systemctl start ${SERVICE_NAME}"
echo ""
echo "  Servis durumu:"
echo "    sudo systemctl status ${SERVICE_NAME}"
echo ""
echo "  Logları izlemek için:"
echo "    journalctl -u ${SERVICE_NAME} -f"
echo ""
echo "  NOT: Audio grubu değişikliğinin geçerli olması için"
echo "       oturumu kapatıp açın veya RPi'yi yeniden başlatın."
echo ""
