import whisper
import os
from faster_whisper import WhisperModel


"""
Модуль распознавания речи (ускоренная версия).

Использует оптимизированную модель faster-whisper:
- Tiny модель
- Работает на CPU с типом INT8
- Быстрее обычного whisper в 2–5 раз
"""

os.environ["PATH"] += os.pathsep + r"C:\Users\kladm\Python study\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin"

# Загружаем модель один раз при старте
model = WhisperModel("tiny", device="cpu", compute_type="int8")

def transcribe_audio(file_path: str) -> str:
    segments, _ = model.transcribe(file_path, language="ru")
    return " ".join(segment.text for segment in segments)
