
---

## Demo
https://skk.devsecoops.xyz

## 주요 기능

1. **웹페이지 분석**
   - URL 입력 → 텍스트/이미지 추출 → 이미지 분류 API 연동

2. **제품명 기반 식약처 인증 확인**
   - 제품명 입력 → CSV 기반 인증 여부 및 업소명(회사명) 확인

3. **외국계 기업 분류**
   - 회사명/대표자명/주소 입력 → API로 예측 결과 반환

---

## 실행 방법

### 1. 도커(Docker)로 전체 서비스 실행

```bash
cd app
docker-compose up --build
```

- `streamlit`(메인 UI): http://localhost:8501
- `api`(FastAPI): http://localhost:8000

### 2. 개별 실행 (로컬)

#### (1) FastAPI 서버

```bash
cd app/api
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

#### (2) Streamlit UI

```bash
cd app/main
pip install -r ../streamlit/requirements.txt
streamlit run main.py
```

---

## 환경/의존성

- Python 3.10 이상 권장
- 주요 패키지: streamlit, fastapi, torch, torchvision, pillow, selenium, beautifulsoup4, pandas, webdriver-manager 등
- 자세한 버전은 각 requirements.txt 참고

---

## 데이터/모델 파일

- `foreign_company_classifier_v2.h5` : 외국계 기업 분류 모델
- `best_resnet18.pt` : 이미지 분류 모델 (api/image 폴더 등 위치)
- `data.csv` : 식약처 인증 제품 데이터 (main.py와 같은 폴더)

---

## 참고/기타

- Amazon Linux 등 서버 환경에서는 Chrome/Chromedriver 설치 필요 (README 내 설치법 참고)
- Streamlit, FastAPI, Docker 등 개별 실행도 가능
- 문의: [jigreg@g.skku.edu 또는 깃허브 이슈]
