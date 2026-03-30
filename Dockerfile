FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "tele_main.py"]
```

**`requirements.txt`** — pin exact versions:
```
python-telegram-bot==20.7
yt-dlp==2024.12.23