import json
import os.path

from telegram import Update, Voice
from telegram.ext import ContextTypes

from tg_bot.utils.transcriber import transcribe_audio
from tg_bot.utils.audio import convert_ogg_to_wav
from tg_bot.utils.gpt_parser import parse_task_to_event
from tg_bot.utils.oauth import generate_google_auth_url
from tg_bot.config import TOKENS_DIR

from calendar_client import GoogleCalendar



RAILWAY_DOMAIN = "https://web-production-25e89.up.railway.app"

"""
Обработчик голосовых сообщений Telegram-бота
Если пользователь авторизован — создаёт событие
Если нет — отправляет ссылку на авторизацию 
"""
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("handle_voice вызван")
    print(f"Update data: {update}")

    user_id = update.effective_user.id
    # token_path = f'tokens/token_{user_id}.json'
    token_path = os.path.join(TOKENS_DIR, f"token_{user_id}.json")

    print(f"user_id = {user_id}")
    print(f"Проверяем наличие токена: {token_path}")

    #чекаем авторизован ли пользователь
    # if not os.path.exists(token_path):
    #     auth_url = generate_google_auth_url(user_id)
    #     await update.message.reply_text(
    #         f"Чтобы я мог сохранить задачу в твой Google Календарь, перейди по ссылке и авторизуйся:\n\n{auth_url}"
    #     )
    #     return
    if not os.path.exists(token_path):
        try:
            print("🔐 Пользователь не авторизован. Генерируем ссылку...")
            auth_url = generate_google_auth_url(user_id)
            print("🔗 Ссылка на авторизацию сгенерирована:", auth_url)

            await update.message.reply_text(
                f"Чтобы я мог сохранить задачу в твой Google Календарь, перейди по ссылке и авторизуйся:\n\n{auth_url}"
            )
        except Exception as e:
            import traceback
            print("❌ Ошибка при генерации OAuth-ссылки:")
            print(f"user_id = {user_id}")
            traceback.print_exc()
            await update.message.reply_text("❌ Ошибка при генерации ссылки авторизации.")
        return

    try:
        print("✅ Токен найден, продолжаем обработку...")

        voice: Voice = update.message.voice
        file = await context.bot.get_file(voice.file_id) #Получаем ссылку на скачивание голосового файла
        await  file.download_to_drive('voice.ogg') #Скачиваем голосовое сообщение

        convert_ogg_to_wav("voice.ogg", "voice.wav")
        text = transcribe_audio("voice.wav")

        await  update.message.reply_text(f"Распознанный текст:\n{text}")

        print("🧠 Распознанный текст:", text)
        event = parse_task_to_event(text) #получчаем питон словарь
        formatted = json.dumps(event, indent=2, ensure_ascii=False) #преобразует его в отформатированную JSON-строку
        #Добавляем в Google Calendar
        print("📦 Event object:", event)
        # link = create_event(event, user_id)
        calendar = GoogleCalendar(user_id)
        created_event = calendar.add_event_to_primary(event)
        link = created_event.get('htmlLink')

        await update.message.reply_text(
            f"📅 Задача из текста:\n<pre>{formatted}</pre>\n\n✅ Добавлено в календарь:\n{link}",
            parse_mode="HTML"
        )

    except Exception as e:
        import traceback
        traceback.print_exc()  # покажет ошибку в консоли
        await update.message.reply_text("Ошибка при создании события.")