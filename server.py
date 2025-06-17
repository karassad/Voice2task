# server.py
from multiprocessing import Process
import uvicorn

def start_api():
    uvicorn.run("auth.main:app", host="0.0.0.0", port=8080)

def start_bot():
    import bot  # это выполнит bot.py (где app.run_polling)

if __name__ == "__main__":
    p1 = Process(target=start_api)
    p2 = Process(target=start_bot)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
