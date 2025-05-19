FROM python:3.10-slim

WORKDIR /app

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 설치
COPY requirements.txt .
COPY app.py .
COPY best_resnet18.pt .

# 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# streamlit 실행
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]