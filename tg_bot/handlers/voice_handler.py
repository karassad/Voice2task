import json
import os.path
import logging

from telegram import Update, Voice
from telegram.ext import ContextTypes

from tg_bot.utils.transcriber import transcribe_audio
from tg_bot.utils.audio import convert_ogg_to_wav
from tg_bot.utils.gpt_parser import parse_task_to_event
from tg_bot.utils.oauth import generate_google_auth_url
from tg_bot.config import TOKENS_DIR

from calendar_client import GoogleCalendar

logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

RAILWAY_DOMAIN = "https://web-production-25e89.up.railway.app"

"""
Обработчик голосовых сообщений Telegram-бота
Если пользователь авторизован — создаёт событие
Если нет — отправляет ссылку на авторизацию 
"""
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("handle_voice вызван")
    logger.debug(f"Update data: {update}")

    user_id = update.effective_user.id
    token_path = os.path.join(TOKENS_DIR, f"token_{user_id}.json")

    logger.info(f"user_id = {user_id}")
    logger.info(f"Проверяем наличие токена: {token_path}")

    if not os.path.exists(token_path):
        try:
            logger.info("🔐 Пользователь не авторизован. Генерируем ссылку...")
            auth_url = generate_google_auth_url(user_id)
            logger.info("🔗 Ссылка на авторизацию сгенерирована: %s", auth_url)

            await update.message.reply_text(
                f"Чтобы я мог сохранить задачу в твой Google Календарь, перейди по ссылке и авторизуйся:\n{auth_url}"
            )

        except Exception:
            logger.exception(f"❌ Ошибка при генерации OAuth-ссылки (user_id={user_id}):")
            await update.message.reply_text("❌ Ошибка при генерации ссылки авторизации.")
        return

    try:
        logger.info("✅ Токен найден, продолжаем обработку...")

        voice: Voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        await file.download_to_drive('voice.ogg')

        logger.info("🎙️ Голосовое сообщение скачано")

        convert_ogg_to_wav("voice.ogg", "voice.wav")
        logger.info("🎛️ Файл сконвертирован в WAV")

        text = transcribe_audio("voice.wav")
        await update.message.reply_text(f"Распознанный текст:\n{text}")

        logger.info("🧠 Распознанный текст: %s", text)

        event = parse_task_to_event(text)
        formatted = json.dumps(event, indent=2, ensure_ascii=False)

        logger.info("📦 Event object: %s", event)

        calendar = GoogleCalendar(user_id)
        created_event = calendar.add_event_to_primary(event)
        link = created_event.get('htmlLink')

        await update.message.reply_text(
            f"📅 Задача из текста:\n<pre>{formatted}</pre>\n\n✅ Добавлено в календарь:\n{link}",
            parse_mode="HTML"
        )

    except Exception:
        logger.exception("❌ Ошибка при создании события:")
        await update.message.reply_text("Ошибка при создании события.")
