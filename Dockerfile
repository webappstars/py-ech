FROM python:3.11-slim
ENV TZ=Asia/Shanghai
RUN apt-get update && apt-get install -y curl wget && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY app.py /app/app.py
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x /app/app.py
EXPOSE 3000
EXPOSE 3001
ENV PORT=3000
ENV WSPORT=3001
ENV TOKEN=""
ENV ARGO_AUTH=""
ENV ARGO_DOMAIN=""
ENV CUSTOM_DNS=""
ENV ECH_LOG=ech.log
ENV ARGO_LOG=argo.log
CMD ["python3", "/app/app.py"]
