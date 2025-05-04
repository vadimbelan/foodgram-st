# Базовый образ
FROM python:3.12
# Устанавливаем рабочую директорию
WORKDIR /app
# Копируем файл зависимостей и сразу ставим gunicorn и остальные пакеты
COPY requirements.txt /app/
RUN \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir gunicorn==20.1.0 && \
    python3 -m pip install --no-cache-dir -r requirements.txt
# Копируем весь код приложения
COPY . /app
# Команда запуска приложения
CMD ["gunicorn", "foodgram.wsgi", "--bind", "0:8000"]
