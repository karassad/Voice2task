
import logging

from google import genai
from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler

from src.Voice2task.ai_services.prompts_generator import PromptsGenerator
from src.Voice2task.config import GEMINI_API_KEY
from src.Voice2task.tg_services.message_utils.message_send_logic import send_new_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiParser:

    def __init__(self):
        self.gemini_api_key = GEMINI_API_KEY


    async def parse_user_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """
        Парсит текст с помощью Gemini API.
        :param text: Текст для парсинга.
        :return: json формат задачи для календаря
        """
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        user_message = text
        logger.info(f"Received task from user {user_id} ({user_name}): '{user_message}'")


        try:
            google_meet_block = context.user_data.pop('google_meet_block', False)
            prompts_generator = PromptsGenerator()
            logger.info(google_meet_block)

            #решаем созадть гугл мит или обычное событие
            if not google_meet_block:
                logger.info(f'промпт для события')
                prompt = prompts_generator.event_prompt()
            else:
                logger.info(f'промпт для созвона')
                prompt = prompts_generator.google_meet_prompt()

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





