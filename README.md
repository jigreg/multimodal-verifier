# 영양제 분류 통합 서비스

---

## Demo

- 👉 [https://skk.devsecoops.xyz](https://skk.devsecoops.xyz)

---

## 주요 기능

1. **웹페이지 분석**  
   - URL 입력 → 텍스트/이미지 추출 → 이미지 분류 API 연동
2. **제품명 기반 식약처 인증 확인**  
   - 제품명 입력 → CSV 기반 인증 여부 및 업소명(회사명) 확인
3. **외국계 기업 분류**  
   - 회사명/대표자명/주소 입력 → API로 예측 결과 반환

---

## 빠른 시작

### Docker Compose로 한 번에 실행

```bash
cd app
docker-compose up --build
```

- Streamlit UI: [http://localhost:8501](http://localhost:8501)
- FastAPI API: [http://localhost:8000](http://localhost:8000)

---

## 환경/의존성

- Python 3.10 이상 권장
- 모든 의존성은 Docker 이미지 빌드시 자동 설치됨
- 주요 패키지:  
  `streamlit`, `fastapi`, `torch`, `torchvision`, `pillow`,  
  `selenium`, `beautifulsoup4`, `pandas`, `webdriver-manager` 등

---

## 데이터/모델 파일

- `foreign_company_classifier_v2.h5` : 외국계 기업 분류 모델
- `best_resnet18.pt` : 이미지 분류 모델 (api/image 폴더 등 위치)

---

## 문의

- 이메일: jigreg@g.skku.edu
- 또는 깃허브 이슈 등록
