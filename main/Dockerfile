FROM python:3.10-slim

WORKDIR /app

# 시스템 패키지 설치 (Selenium + Chromium + 의존성)
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg2 ca-certificates \
    fonts-liberation libappindicator3-1 libasound2 \
    libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 \
    libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxrandr2 xdg-utils \
    libgbm-dev libgtk-3-0 chromium chromium-driver \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Chrome 환경 변수 설정
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 앱 소스 복사
COPY ../main/requirements.txt ./
COPY ../main/main.py ./main.py
COPY ../main/data.csv ./data.csv

# Python 패키지 설치
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

# Streamlit 실행
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]