web: uvicorn auth.main:app --host=0.0.0.0 --port=8080
web: uvicorn auth.main:app --host=0.0.0.0 --port=${PORT:-8080}
worker: python bot/bot.py