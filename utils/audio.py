import subprocess

"""
Аудио-утилита для конвертации .ogg → .wav с помощью ffmpeg.
"""


def convert_ogg_to_wav(input_path: str, output_path: str):
    """
           convert_ogg_to_wav(input_path, output_path) — преобразует аудиофайл
    """
    subprocess.run([
        r'C:\Users\kladm\Python study\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe',
        "-y", "-i", input_path,
        "-ar", "16000",  # частота дискретизации
        "-ac", "1",      # моно
        output_path
    ], check=True)
