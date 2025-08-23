FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл с зависимостями в рабочую директорию
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y ffmpeg

# Копируем весь исходный код проекта в рабочую директорию.
# Это включает все папки и файлы, видимые на вашем скриншоте.
COPY . .
ENV PYTHONPATH=/app/
# Открываем порт, на котором работает веб-сервер
EXPOSE 8080

# Команда для запуска приложения
CMD ["python", "src/Voice2task/main.py"]