FROM python:3.11-slim

WORKDIR /app

# Installer les outils nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt 2>&1 || pip install --no-cache-dir numpy pandas

COPY scripts/ ./scripts/
COPY .env .env

CMD ["python", "scripts/main.py"]
