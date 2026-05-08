"""
Sistemdeki ses cihazlarını listeler.
config.py'deki AUDIO_INPUT_DEVICE değerini buradan öğrenebilirsiniz.
Kullanım: python list_devices.py
"""
import sounddevice as sd

devices = sd.query_devices()
print(f"\n{'ID':<4} {'Type':<7} {'Name'}")
print("-" * 60)
for i, d in enumerate(devices):
    kind = []
    if d["max_input_channels"] > 0:
        kind.append("IN")
    if d["max_output_channels"] > 0:
        kind.append("OUT")
    print(f"{i:<4} {'/'.join(kind):<7} {d['name']}")

print(f"\nDefault input : {sd.query_devices(kind='input')['name']}")
print(f"Default output: {sd.query_devices(kind='output')['name']}")
print("\nSet AUDIO_INPUT_DEVICE in config.py to your microphone's ID.")
