import os
import logging
from multiprocessing import Process
import subprocess
import uvicorn

# настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_api():
    logger.info("🚀 Запускаем FastAPI сервер на 0.0.0.0:8080")
    uvicorn.run("auth.main:app", host="0.0.0.0", port=8080)

def start_bot():
    logger.info("🤖 Запускаем Telegram-бота...")
    env = os.environ.copy()
    env["PYTHONPATH"] = "."  # корень проекта

    result = subprocess.run(
        ["python", "tg_bot/bot.py"],
        env=env,
        capture_output=True,
        text=True
    )

    logger.info("⛔ Бот завершился.")
    if result.stdout:
        logger.info("📤 STDOUT:\n%s", result.stdout)
    if result.stderr:
        logger.error("📥 STDERR:\n%s", result.stderr)

if __name__ == "__main__":
    logger.info("📦 Запуск приложения с двумя процессами (API + BOT)")
    p1 = Process(target=start_api)
    p2 = Process(target=start_bot)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
