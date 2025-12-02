FROM python:latest

ENV TZ=Asia/Shanghai

RUN apt-get update && \
    apt-get install -y curl wget build-essential libffi-dev libssl-dev && \
    python3 -m pip install --upgrade pip setuptools wheel && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app.py requirements.txt ./
 

RUN pip install -r requirements.txt
RUN chmod +x /app/app.py

EXPOSE 3000

ENV CUSTOM_DNS="1.1.1.1"

CMD ["python3", "/app/app.py"]
