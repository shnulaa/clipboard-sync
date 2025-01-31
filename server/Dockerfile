# 使用官方 Python 运行时作为父镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 将当前目录的内容复制到容器的工作目录中
COPY ./ .

# 安装依赖项
RUN pip install --no-cache-dir -r requirements.txt

# 暴露应用运行的端口
EXPOSE 5000

# 定义环境变量
ENV FLASK_APP=app.py

# 启动命令
CMD ["python", "app.py"]