# Базовий образ Python
FROM python:3.11-slim

# Встановлення робочої директорії
WORKDIR /app

# Копіювання файлу вимог
COPY requirements.txt .

# Встановлення залежностей
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання коду
COPY src/ ./src/

# Команда для запуску сервера
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
