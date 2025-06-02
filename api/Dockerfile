FROM python:3.11-slim

WORKDIR /app

# 코드 및 모델 복사
COPY api/app.py /app/
COPY api/requirements.txt /app/
COPY api/best_resnet18.pt /app/
COPY api/abnormal_company_rf_model.pkl /app/
COPY api/abnormal_company_vectorizer.pkl /app/

# 라이브러리 설치
RUN apt-get update && apt-get install -y gcc && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]