FROM python:3.12-slim

# Устанавливаем системные зависимости
# postgresql-client нужен для команды psql (опционально)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY certs/ ./certs/
COPY app/auth/ ./auth/
COPY . .

# Создаем пользователя для безопасности (не запускаем от root)
RUN useradd -m -u 1000 user && chown -R user:user /app
USER user

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]