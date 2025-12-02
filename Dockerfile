FROM python:3.11-slim

ENV TZ=Asia/Shanghai

RUN apt-get update && apt-get install -y curl wget && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app.py /app/app.py
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x /app/app.py

EXPOSE 3000

ENV CUSTOM_DNS="1.1.1.1"

CMD ["python3", "/app/app.py"]
