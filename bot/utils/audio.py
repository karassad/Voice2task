import subprocess
import os

"""
Аудио-утилита для конвертации .ogg → .wav с помощью ffmpeg.
"""

FFMPEG = os.getenv("FFMPEG_PATH", "ffmpeg") #второй арг - значение по умолчанию

def convert_ogg_to_wav(input_path: str, output_path: str):
    """
           convert_ogg_to_wav(input_path, output_path) — преобразует аудиофайл
    """
    subprocess.run([
        FFMPEG,
        "-y", "-i", input_path,
        "-ar", "16000",  # частота дискретизации
        "-ac", "1",      # моно
        output_path
    ], check=True)
