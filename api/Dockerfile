FROM python:3.11-slim

WORKDIR /app

COPY api/app.py /app/
COPY api/requirements.txt /app/
COPY bert_model /app/bert_model/
COPY foreign_company_classifier_v2.h5 /app/
COPY api/best_resnet18.pt /app/

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]