from multiprocessing import Process
import uvicorn
import subprocess

def start_api():
    uvicorn.run("auth.main:app", host="0.0.0.0", port=8080)

import subprocess

def start_bot():
    print("📦 Запускаем Telegram-бота...")
    env = os.environ.copy()
    env["PYTHONPATH"] = "."  # корень проекта

    result = subprocess.run(
        ["python", "tg_bot/bot.py"],
        env=env,
        capture_output=True,
        text=True
    )
    print("🔚 Бот завершился.")
    print("stdout:\n", result.stdout)
    print("stderr:\n", result.stderr)

if __name__ == "__main__":
    p1 = Process(target=start_api)
    p2 = Process(target=start_bot)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
