FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg2 ca-certificates \
    fonts-liberation libappindicator3-1 libasound2 \
    libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 \
    libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxrandr2 xdg-utils \
    libgbm-dev libgtk-3-0 chromium chromium-driver \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# 환경변수 설정 (Selenium이 크롬 찾을 수 있도록)
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 애플리케이션 복사
COPY streamlit/app.py /app/
COPY streamlit/requirements.txt /app/

# 파이썬 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# Streamlit 실행
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]