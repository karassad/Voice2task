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
class Transcriber:

    def __init__(self, model_size: str = 'tiny', device: str = 'cpu', compute_type: str = "int8"):
        """
            Инициализирует модель для распознавания речи.
        """
        os.environ["PATH"] += os.pathsep + r"C:\Users\kladm\Python study\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin"
        # Загружаем модель один раз при старте
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, file_path: str) -> str:
        """
            Распознаёт речь из аудиофайла и возвращает строку.
        """
        segments, _ = self.model.transcribe(file_path, language="ru")
        return " ".join(segment.text for segment in segments)
