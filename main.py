import asyncio

from agent.llm import get_response
from agent.stt import transcribe_audio
from agent.tts import speak
from utils.audio import record_with_vad

EXIT_WORDS = {"çıkış", "exit", "quit", "kapat", "bitir"}

BANNER = """
╔══════════════════════════════════════╗
║        AI Konuşma Robotu             ║
║  STT: Groq Whisper  |  TTS: edge-tts ║
╚══════════════════════════════════════╝
Konuşmaya başlayın — Enter'a gerek yok.
Durdurmak için Ctrl+C.
"""


async def main() -> None:
    print(BANNER)

    conversation_history: list = []

    while True:
        try:
            print("Dinliyorum...")
            audio_path = record_with_vad()

            if not audio_path:
                continue  # gürültü / çok kısa ses → tekrar dinle

            print("Analiz ediliyor...")
            user_text = transcribe_audio(audio_path)

            if not user_text:
                continue

            print(f"Siz: {user_text}")

            if any(word in user_text.lower() for word in EXIT_WORDS):
                farewell = "Görüşürüz!"
                print(f"AI: {farewell}")
                await speak(farewell)
                break

            conversation_history.append({"role": "user", "content": user_text})

            print("Düşünüyor...")
            response = get_response(conversation_history)
            print(f"AI: {response}\n")

            conversation_history.append({"role": "assistant", "content": response})

            await speak(response)

            # TTS bittikten sonra kısa bekleme — hoparlör yankısının VAD'ı
            # tetiklemesini önler
            await asyncio.sleep(0.4)

        except KeyboardInterrupt:
            print("\nGörüşürüz!")
            break
        except Exception as e:
            print(f"Hata: {e}\n")
            continue


if __name__ == "__main__":
    asyncio.run(main())
