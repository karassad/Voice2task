import json
import wave

from src.Voice2task.config import VOICE_TRANSCRIBER_PATH
from vosk import Model, KaldiRecognizer

class VoskTranscriber:

    def __init__(self, voice_transcriber_path = VOICE_TRANSCRIBER_PATH):
        self.model = Model(voice_transcriber_path)


    def transcribe_voice(self, file_path: str) -> str:

        wav_file = wave.open(file_path, 'rb') #r - read, b - binary

        if wav_file.getnchannels() != 1 or wav_file.getsampwidth() != 2 or wav_file.getframerate() != 16000:
            raise ValueError("Файл должен быть в формате WAV 16 kHz, моно, 16 бит.")

        recognizer = KaldiRecognizer(self.model, wav_file.getframerate())
        text = ""

        while True:
            data = wav_file.readframes(4000) #берем по 4000 фреймов (0.25 сек аудио)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                res = json.loads(recognizer.Result())
                text += res.get("text", "") + " "

        #обработка возможного короткого хвоста
        last_part = json.loads(recognizer.FinalResult())
        text += last_part.get("text", "")

        return text.strip()