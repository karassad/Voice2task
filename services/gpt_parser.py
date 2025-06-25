import json
import os
from openai import OpenAI
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta
import re #для работы с регулярными выражениями


class TaskParser:

    def __init__(self, model_url = "http://localhost:11434/api/chat", model_name: str = "mistral", temperature: float = 0.3):
        self.model_url = model_url
        self.model_name = model_name
        self.temperature = temperature

    def _extract_json(self, text: str) -> dict:
        try:
            json_str = re.search(r'\{[\s\S]+?\}', text).group(0)
            # Удаляем JS-подобные комментарии, чтобы получить валидный JSON
            cleaned = re.sub(r'//.*', '', json_str)
            return json.loads(cleaned)
        except Exception as e:
            print("Не удалось извлечь JSON из ответа:")
            print(text)
            raise e

    def parse(self, text: str) -> dict:
        """
        Отправляет текст в локальную LLM (через Ollama) и получает структуру события в JSON-формате.
        """

        today_str = datetime.today().strftime('%Y-%m-%d')

        prompt = f"""
        Сегодняшняя дата: {today_str}
        Из этого текста создай структуру события для календаря в формате JSON 
        (не добавляй никаких пояснений или комментариев внутри JSON):
        Время указывай в локальной зоне (Москва).

        "{text}"

        Формат:
        {{
          "title": "Название события",
          "start": "2025-06-05T15:00:00",
          "end": "2025-06-05T16:00:00",
          "description": "по желанию",
          "reminder_minutes": 10
        }}
        """

        response = requests.post(
            self.model_url,
            json={
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "temperature": self.temperature
            }
        )

        print("RAW RESPONSE:")
        print(response.text)

        try:
            data = json.loads(response.text)
            return self._extract_json(data["message"]["content"])
        except Exception as e:
            print("Ошибка при разборе JSON:")
            raise e




