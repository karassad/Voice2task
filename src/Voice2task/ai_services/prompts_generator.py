import os
from datetime import datetime, timedelta
import uuid

import pytz


class PromptsGenerator:

    def __init__(self):
        self.time_zone = 'Europe/Moscow'
        self.prompts_dir = os.path.dirname(os.path.abspath(__file__))

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

    def _load_prompt_template(self, filename):
        file_path = os.path.join(self.prompts_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()


    def event_prompt(self):

        date_context = self._generate_date_context()
        specific_instructions = self._load_prompt_template('specific_instructions_event.txt')

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
                            
                            {specific_instructions}
    
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

    def google_meet_prompt(self, google_meet_block: bool = False):
        date_context = self._generate_date_context()
        unic_id_for_google_meet = str(uuid.uuid4())
        specific_instructions = self._load_prompt_template('specific_instructions_meet.txt')

        system_prompt = f"""
                                Ты - умный ассистент, который преобразует текст пользователя в структурированное JSON-событие для Google Calendar. 
                                Ты создаешь только Google Meet события.

                                {date_context}

                                - Текущее время: {datetime.now().astimezone(pytz.timezone('Europe/Moscow')).strftime('%H:%M')}
                                - Если не указана дата, используй сегодняшнюю.
                                - Если указан день недели, но не указано конкретное число, используй ближайшую дату этого дня недели.
                                - Если время окончания указано до времени начала, то время начала оставь прежним, а время окончания сделай через час от времени начала.
                                - Если время не указано, установи событие с 9:00 до 10:00 утра того дня (дня недели), который указан. 
                                - Если ни время, ни дата не указаны, установи событие с 9:00 до 10:00 утра сегодняшнего дня.
                                - Всегда возвращай 'start' и 'end' как объекты с 'dateTime' в формате ISO 8601, включая часовой пояс.
                                - Часовой пояс для всех событий - '{self.time_zone}'.
                                
                                {specific_instructions}

                                Словарь временных интервалов для помощи в определении времени:
                                - Утро: с 6:00 до 12:00
                                - День: с 12:00 до 18:00
                                - Вечер: с 18:00 до 23:00
                                - Ночь: с 23:00 до 6:00
                                - Первая половина дня: с 9:00 до 15:00
                                - Вторая половина дня: с 15:00 до 22:00

                                Формат вывода должен быть строго JSON. Вот пример:

                                {{
                                    "summary": "Название google meet",
                                    "start": {{
                                        "dateTime": "YYYY-MM-DDTHH:MM:SS+03:00",
                                        "timeZone": "Europe/Moscow"
                                    }},
                                    "end": {{
                                        "dateTime": "YYYY-MM-DDTHH:MM:SS+03:00",
                                        "timeZone": "Europe/Moscow"
                                    }},
                                    "conferenceData":{{
                                        "createRequest": {{
                                            "requestId": "{unic_id_for_google_meet}",
                                            "conferenceSolutionKey": {{
                                                "type": "hangoutsMeet"
                                            }}
                                        }}
                                    }},
                                    "attendees": [
                                        {{"email": "attendee1@example.com"}},
                                        {{"email": "attendee2@example.com"}}
                                    ]
                                }}
                                """

        return system_prompt
