# 식의약 인증/분석(PILL-SQUAD) MCP 서버

## 1. 개요

이 프로젝트는 식의약 제품 인증, 판매자(국내/중국) 분류, 이미지/웹페이지 분석 등 다양한 식의약 데이터 분석을 위한 MCP 서버입니다.  
Cursor, Claude Desktop 등 MCP 호환 LLM에서 도구로 사용할 수 있습니다.

[![데모 영상 바로보기]](https://github.com/user-attachments/assets/6f74c8e6-2ec6-4479-8b11-bdb9a03f71a1)




---

## 2. 설치 및 준비

### 2-1. 저장소 클론

```bash
git clone --branch mcp https://github.com/jigreg/multimodal-verifier.git
cd mcp-server
```

### 2-2. uv 설치 (필수)

- **macOS**:  
  ```bash
  brew install uv
  혹은
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Windows**:  
  ```bash
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

### 2-3. 가상환경 및 의존성 설치

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
# 또는
uv pip install .
```

## 3. MCP 서버 실행

```bash
uv run main.py
```

- 서버가 정상 실행되면 MCP 호환 클라이언트(예: Claude Desktop)에서 도구 사용 가능

---

## 4. Claude Desktop 연동 방법

1. Claude Desktop 설치 및 최신 업데이트 ([공식 다운로드](https://claude.ai/download))
2. Settings → Developer → Edit Config에서 MCP 서버 등록

```json
{
  "mcpServers": {
    "pill-squad": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/사용자계정/경로/mcp-server",
        "run",
        "main.py"
      ]
    }
  }
}
```
- 경로는 본인 환경에 맞게 수정

3. Claude Desktop 재시작  
4. 채팅창에서 질문하기

---

## 5. 도구(Tools)별 상세 사용법

### 5-1. 판매자(회사) 외국계/국내 분류

- **도구명**: `predict_company_label`
- **설명**: 회사명, 대표자명, 주소를 기반으로 외국계 기업 여부 예측 (BERT로 학습한 자체 이미지 모델 API 활용)
- **파라미터**:
  - `company`: 회사명
  - `ceo`: 대표자명
  - `address`: 주소
- **반환**: 예측 결과 문자열

---

### 5-2. 식약처 인증 제품 확인

- **도구명**: `check_certified_product`
- **설명**: 제품명이 식약처 인증 제품인지 확인, 인증된 경우 업소명도 반환 (식약처에 등록된 데이터 비교)
- **파라미터**:
  - `product_name`: 제품명
- **반환**: 인증 결과 메시지

---

### 5-3. 이미지 분석

- **도구명**: `analyze_image`
- **설명**: 이미지 파일을 API로 전송하여 분석 결과 반환 (torch로 학습한 자체 이미지 모델 API 활용)
- **파라미터**:
  - `image_path`: 분석할 이미지 파일 경로
- **반환**: 분석 결과 문자열

---

### 5-4. 이미지 다운로드/스크린샷

- **도구명**: `download_image`
- **설명**: 셀레니움으로 이미지 URL에 접속, 스크린샷 저장 (`image/` 폴더)
- **파라미터**:
  - `url`: 이미지 URL
  - `save_path`: 저장 파일명(옵션)
- **반환**: 저장된 파일 경로

---

### 5-5. 웹페이지 이미지 URL 추출

- **도구명**: `crawl_image_urls_selenium`
- **설명**: Selenium으로 웹페이지에서 이미지 URL 목록 추출
- **파라미터**:
  - `page_url`: 웹페이지 URL
- **반환**: 이미지 URL 리스트

---

### 5-6. 웹페이지 텍스트 추출 및 인증 제품 포함여부 검사

- **도구명**: `extract_text_with_bs4`
- **설명**: BeautifulSoup으로 웹페이지 주요 텍스트 추출, 인증 제품명 포함여부 검사
- **파라미터**:
  - `page_url`: 웹페이지 URL
- **반환**: 텍스트 + 인증 제품 포함 여부 결과

---

## 6. 기타

- 로그/이미지 등은 `image/` 폴더에 저장됩니다.
- 데이터 파일(`data.csv`)이 반드시 필요합니다.
- 확장/개발: `main.py` 참고

---

**문의/기여**: jigreg@g.skku.edu 또는 머지 리퀘스트로 연락 바랍니다.
