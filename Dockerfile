FROM python:3.11.9-slim

WORKDIR /app

# Установка Poetry
RUN pip install --no-cache-dir poetry

# Копируем pyproject.toml и poetry.lock
COPY pyproject.toml poetry.lock ./  

# Конфигурируем Poetry: не создавать виртуальное окружение
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости через Poetry
RUN poetry install --only main --no-interaction --no-ansi --no-root

# Копируем исходный код
COPY . .

# (Опционально) Если используешь poetry build — убедись, что это нужно
# RUN poetry build --format wheel

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]