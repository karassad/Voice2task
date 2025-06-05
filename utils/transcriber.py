import whisper
import os

"""
Модуль распознавания речи.

Использует модель Whisper от OpenAI:
- Загружает модель (base)
- Распознаёт речь из .wav файла
- Возвращает текст
"""

os.environ["PATH"] += os.pathsep + r"C:\Users\kladm\Python study\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin"
model = whisper.load_model('base')

def transcribe_audio(file_path: str) -> str:
    result = model.transcribe(file_path, language='ru')
    return result['text']
