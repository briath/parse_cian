FROM selenium/standalone-chrome:latest

# Переключаемся на root, чтобы ставить пакеты
USER root

# Устанавливаем Python и системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Ставим alias на python
RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

# Переменные окружения для Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH"

# Копируем requirements.txt отдельно для кеша
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY . .

# Создаем непривилегированного пользователя
RUN useradd -m appuser && chown -R appuser /app && chmod -R 755 /app
USER appuser
# Устанавливаем PYTHONPATH
ENV PYTHONPATH=/app
# Запуск FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
