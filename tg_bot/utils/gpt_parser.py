import json
import os
from openai import OpenAI
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta
import re #для работы с регулярными выражениями

load_dotenv()

client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))

def extract_json_from_response(text: str) -> dict:
    try:
        json_str = re.search(r'\{[\s\S]+?\}', text).group(0)
        # Удаляем JS-подобные комментарии, чтобы получить валидный JSON
        cleaned = re.sub(r'//.*', '', json_str)
        return json.loads(cleaned)
    except Exception as e:
        print("Не удалось извлечь JSON из ответа:")
        print(text)
        raise e


def parse_task_to_event(text: str) -> str:
    """
    Отправляет текст в локальную LLM (через Ollama) и получает структуру события в JSON-формате.
    """
    print("GPT INPUT:", text)
    today_str = datetime.today().strftime('%Y-%m-%d')

    prompt = f"""
    Сегодня {today_str}.

    Из следующего текста создай событие в календаре. Ответ ДОЛЖЕН быть только в виде JSON, без пояснений. Не пиши ничего, кроме JSON.

    Пример:
    {{
      "title": "Название события",
      "start": "2025-06-05T15:00:00",
      "end": "2025-06-05T16:00:00",
      "description": "по желанию",
      "reminder_minutes": 10
    }}

    Вот текст задачи:
    {text}
    """

    print("Отправляем запрос в Ollama...")

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "mistral",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "temperature": 0.3
        },
        timeout=120
    )

    print("RAW RESPONSE:")
    print(response.text)

    try:
        data = json.loads(response.text)
        return extract_json_from_response(data["message"]["content"])
    except Exception as e:
        print("Ошибка при разборе JSON:")
        raise e


# Тест запуска
if __name__ == "__main__":
    result = parse_task_to_event("Напомни мне завтра в 9 утра совещание по проекту")
    print(result)
