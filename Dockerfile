# 使用轻量 Python 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制应用和依赖
COPY app.py /app/app.py
COPY requirements.txt /app/requirements.txt

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置非 root 用户
RUN useradd -m appuser
USER appuser

# 暴露端口
EXPOSE 3000

# 启动应用
CMD ["python", "/app/app.py"]
