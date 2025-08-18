import asyncio
import logging
from datetime import datetime, timedelta

import pytz
from google import genai
from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler

from src.Voice2task.config import GEMINI_API_KEY
from src.Voice2task.tg_services.message_utils.message_send_logic import send_new_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiParser:

    def __init__(self):
        self.gemini_api_key = GEMINI_API_KEY
        self.time_zone = 'Europe/Moscow'


    def _generate_date_context(self):
        '''
        Генерирует 30 дней контекста для Gemini API.
        Помогает АИ понимать относительные временные выражения.
        :return:
        '''

        now = datetime.now()
        today_date = now.strftime('%Y-%m-%d')
        tomorrow_date = (now + timedelta(days=1)).strftime('%Y-%m-%d')
        day_after_tomorrow_date = (now + timedelta(days=2)).strftime('%Y-%m-%d')

        date_context = [
            f'сегодня: {today_date}',
            f'завтра: {tomorrow_date}',
            f'послезавтра: {day_after_tomorrow_date}',
            f'список дат с указанием дня недели на следующие 30 дней: '
        ]

        for i in range(30):
            date = now + timedelta(days=i)

            #добавляем день недели к дате
            day_names = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
            day_name = day_names[date.weekday()]

            date_context.append(f'{date.strftime("%Y-%m-%d")} ({day_name})')

        return '\n'.join(date_context)


    def _generate_prompt(self):
        date_context = self._generate_date_context()

        system_prompt = f"""
                        Ты - умный ассистент, который преобразует текст пользователя в структурированное JSON-событие для Google Calendar.

                        {date_context}

                        - Текущее время: {datetime.now().astimezone(pytz.timezone('Europe/Moscow')).strftime('%H:%M')}
                        - Если не указана дата, используй сегодняшнюю.
                        - Если указан день недели, но не указано конкретное число, используй ближайшую дату этого дня недели.
                        - Если время окончания указано до времени начала, то время начала оставь прежним, а время окончания сделай через час от времени начала.
                        - Если время не указано, установи событие с 9:00 до 10:00 утра того дня (дня недели), который указан. 
                        - Если ни время, ни дата не указаны, установи событие с 9:00 до 10:00 утра сегодняшнего дня.
                        - Всегда возвращай 'start' и 'end' как объекты с 'dateTime' в формате ISO 8601, включая часовой пояс.
                        - Часовой пояс для всех событий - '{self.time_zone}'.

                        Словарь временных интервалов для помощи в определении времени:
                        - Утро: с 6:00 до 12:00
                        - День: с 12:00 до 18:00
                        - Вечер: с 18:00 до 23:00
                        - Ночь: с 23:00 до 6:00
                        - Первая половина дня: с 9:00 до 15:00
                        - Вторая половина дня: с 15:00 до 22:00

                        Формат вывода должен быть строго JSON. Вот пример:
                        {{
                            "summary": "Название события",
                            "start": {{
                                "dateTime": "YYYY-MM-DDTHH:MM:SS+03:00",
                                "timeZone": "Europe/Moscow"
                            }},
                            "end": {{
                                "dateTime": "YYYY-MM-DDTHH:MM:SS+03:00",
                                "timeZone": "Europe/Moscow"
                            }},
                            "attendees": [
                                {{"email": "attendee1@example.com"}},
                                {{"email": "attendee2@example.com"}}
                            ]
                        }}
                        """

        return system_prompt


    async def parse_user_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Парсит текст с помощью Gemini API.
        :param text: Текст для парсинга.
        :return: json формат задачи для календаря
        """
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        user_message = update.message.text
        logger.info(f"Received task from user {user_id} ({user_name}): '{user_message}'")


        try:
            prompt = self._generate_prompt()

            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f'Системный промпт: {prompt}, задача от пользователя: {user_message}'
            )

            # print(response.text)
            logger.info(f"Response from Gemini API: {response.text}")
            res = response.text

            await send_new_message(update, context, f"{res}")

            return ConversationHandler.END

        except Exception as e:
            logger.info(f"Error parsing user request with Gemini API for user {user_id}: {e}", exc_info=True)



#
#
# async def main():
#     g = GeminiParser()
#     await g.parse_user_request('Поставь встречу с Петей на завтра в 10 утра')
#
# if __name__ == "__main__":
#     asyncio.run(main())





