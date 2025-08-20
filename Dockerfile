FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends     ca-certificates tzdata curl build-essential     && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Default to polling. For webhook, set USE_WEBHOOK=true and expose port.
ENV WEBAPP_HOST=0.0.0.0
ENV WEBAPP_PORT=8080

EXPOSE 8080

CMD ["python", "bot/main.py"]
