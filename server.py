import os
import logging
import sys
from multiprocessing import Process
import subprocess
import uvicorn
import threading

logging.basicConfig(
    level=logging.INFO,  # или DEBUG если нужно
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# настройка логов
logger = logging.getLogger(__name__)

def start_api():
    logger.info("🚀 Запускаем FastAPI сервер на 0.0.0.0:8080")
    uvicorn.run("auth.main:app", host="0.0.0.0", port=8080)

def stream_output(pipe, level):
    for line in iter(pipe.readline, ''):
        if line:
            logger.log(level, line.strip())

def start_bot():
    logger.info("🤖 Запускаем Telegram-бота...")
    env = os.environ.copy()
    env["PYTHONPATH"] = "."

    try:
        process = subprocess.Popen(
            ["python", "tg_bot/bot.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        threading.Thread(target=stream_output, args=(process.stdout, logging.INFO), daemon=True).start()
        threading.Thread(target=stream_output, args=(process.stderr, logging.ERROR), daemon=True).start()

        process.wait()
        logger.info("⛔ Бот завершился.")
    except Exception as e:
        logger.exception("❌ Ошибка при запуске бота:")


if __name__ == "__main__":
    logger.info("📦 Запуск приложения с двумя процессами (API + BOT)")
    p1 = Process(target=start_api)
    p2 = Process(target=start_bot)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
