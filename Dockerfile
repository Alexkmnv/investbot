FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y build-essential && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
