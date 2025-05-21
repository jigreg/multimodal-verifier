import httpx
from mcp.server.fastmcp import FastMCP
import pandas as pd
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import os
from webdriver_manager.chrome import ChromeDriverManager

mcp = FastMCP("pill-squad")

# 외부 BERT API 주소를 입력하세요
BERT_API_URL = "https://api.devsecoops.xyz/predict"

# 이미지 분석 API 엔드포인트
IMAGE_API_URL = "https://api.devsecoops.xyz/classify-image"

@mcp.tool()
async def predict_company_label(company: str = "", ceo: str = "", address: str = "") -> str:
    """
    회사명, 대표자명, 주소를 기반으로 외국계 기업 여부를 예측합니다.

    Args:
        company: 회사명
        ceo: 대표자명
        address: 주소
    Returns:
        예측 결과 문자열 (예: "외국계 기업", "국내 기업" 등)
    """
    if not (company or ceo or address):
        return "하나 이상의 정보를 입력하세요."
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                BERT_API_URL,
                json={"company": company, "ceo": ceo, "address": address},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return f"예측 결과: {data.get('label')} (확률: {data.get('probability')})"
            else:
                return f"API 오류: {response.status_code} {response.text}"
        except Exception as e:
            return f"API 연결 오류: {e}"

@mcp.tool()
async def analyze_image(image_path: str) -> str:
    """
    이미지 파일을 외부 API로 전송하여 분석 결과를 반환합니다.

    Args:
        image_path: 분석할 이미지 파일 경로
    Returns:
        분석 결과 문자열
    """
    ext_to_mime = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".bmp": "image/bmp",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    try:
        path = Path(image_path)
        if not path.exists() or not path.is_file():
            return f"❌ 파일이 존재하지 않습니다: {image_path}"
        mime = ext_to_mime.get(path.suffix.lower(), "application/octet-stream")
        async with httpx.AsyncClient() as client:
            with open(path, "rb") as f:
                files = {"file": (path.name, f, mime)}
                response = await client.post(IMAGE_API_URL, files=files, timeout=30)
            if response.status_code == 200:
                return f"✅ 분석 결과: {response.text.strip()}"
            else:
                return f"❌ API 오류: {response.status_code} {response.text.strip()}"
    except Exception as e:
        return f"❌ 이미지 분석 중 예외 발생: {e}"

# === 제품 인증 도구 ===
CSV_PATH = "./data.csv"

def load_certified_product_info(csv_path: str):
    df = pd.read_csv(csv_path)
    product_to_company = dict(zip(
        df['제품명'].dropna().astype(str).str.strip(),
        df['업소명'].dropna().astype(str).str.strip()
    ))
    certified_set = set(product_to_company.keys())
    return certified_set, product_to_company

certified_products, product_to_company = load_certified_product_info(CSV_PATH)

@mcp.tool()
async def check_certified_product(product_name: str) -> str:
    """
    제품명이 식약처 인증 제품인지 확인합니다.

    Args:
        product_name: 확인할 제품명
    Returns:
        인증 결과 메시지
    """
    product_name_lower = product_name.strip().lower()
    matched = [
        (prod, comp)
        for prod, comp in product_to_company.items()
        if product_name_lower in prod.lower()
    ]
    if matched:
        msg = "\n".join([f"✅ 식약처 인증 제품: {prod} (업소명: {comp})" for prod, comp in matched])
        return msg
    else:
        return "❌ 식약처 인증되지 않은 제품입니다."

@mcp.prompt("제품 인증 정보 요청")
def product_cert_prompt():
    return """
아래 제품명이 식약처 인증 제품인지 확인하고, 인증된 경우 업소명도 함께 알려주세요.

제품명: {{product_name}}
"""

@mcp.prompt("판매자 분류 요청")
def company_classify_prompt():
    return """
아래 회사 정보(회사명, 대표자명, 주소)를 바탕으로 외국계 기업 여부를 예측해 주세요.

회사명: {{company}}
대표자명: {{ceo}}
주소: {{address}}
"""

@mcp.prompt("통합 제품/판매자 분석 요청")
def integrated_analysis_prompt():
    return """
아래 정보를 바탕으로
1) 제품이 식약처 인증 제품인지,
2) 판매자가 외국계 기업인지
각각 판별해 주세요.

제품명: {{product_name}}
회사명: {{company}}
대표자명: {{ceo}}
주소: {{address}}
"""

@mcp.prompt("이미지 분석 요청")
def analyze_image_prompt():
    return """
아래 이미지 파일을 분석해 주세요. 분석 결과를 요약해서 알려주세요.

이미지 파일 경로: {{image_path}}
"""

@mcp.prompt("이미지 크롤링 요청")
def crawl_image_urls_prompt():
    return """
아래 웹페이지에서 이미지 URL 목록을 모두 추출해 주세요.

웹페이지 URL: {{page_url}}
"""

@mcp.prompt("셀레니움 이미지 다운로드 요청")
def download_image_selenium_prompt():
    return """
아래 이미지 URL에 셀레니움으로 접속하여 이미지를 스크린샷으로 저장해 주세요.

이미지 URL: {{url}}
저장 경로(선택): {{save_path}}
"""

@mcp.prompt("웹페이지 이미지 일괄분석 요청")
def analyze_images_from_url_prompt():
    return """
아래 웹페이지에서 이미지를 모두 추출하여 다운로드하고, 각 이미지를 분석해 결과를 요약해 주세요.

웹페이지 URL: {{page_url}}
"""

@mcp.prompt("웹페이지 텍스트 추출 요청")
def extract_text_with_selenium_prompt():
    return """
아래 웹페이지에서 주요 텍스트만 추출해 주세요.

웹페이지 URL: {{page_url}}
"""

@mcp.tool()
async def download_image(url: str, save_path: str = None) -> str:
    """
    셀레니움으로 이미지 URL에 접속하여 이미지를 스크린샷으로 저장 (mcp-server/image/ 폴더 내)
    Args:
        url: 이미지 URL
        save_path: 저장 파일명(옵션)
    Returns:
        저장된 파일 경로
    """
    os.makedirs("image", exist_ok=True)
    if not save_path:
        filename = url.split("/")[-1].split("?")[0] or "downloaded.jpg"
        save_path = os.path.join("image", filename)
    else:
        save_path = os.path.join("image", os.path.basename(save_path))
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(url)
        time.sleep(2)
        # 전체 페이지 스크린샷 (이미지 태그만 캡처하려면 추가 로직 필요)
        driver.save_screenshot(save_path)
    finally:
        driver.quit()
    return save_path

@mcp.tool()
async def crawl_image_urls_selenium(page_url: str) -> list:
    """
    Selenium을 이용해 웹페이지에서 이미지 URL 목록 추출
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    # chromedriver 경로는 환경에 맞게 수정하세요!
    service = Service("/opt/homebrew/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(page_url)
    time.sleep(3)  # 동적 로딩 대기

    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    img_urls = [urljoin(page_url, img['src']) for img in soup.find_all("img") if img.get('src') and not img['src'].startswith('data:')]
    return img_urls

@mcp.tool()
async def extract_text_with_bs4(page_url: str) -> str:
    """
    requests+BeautifulSoup으로 웹페이지에서 주요 텍스트만 추출하고,
    텍스트 내에 식약처 인증 제품명이 포함되어 있는지 검사합니다.
    Args:
        page_url: 크롤링할 웹페이지 URL
    Returns:
        텍스트 + 인증 제품 포함 여부 결과
    """
    resp = requests.get(page_url)
    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator=' ', strip=True)
    if len(text) > 2000:
        text = text[:2000] + "..."
    # 인증 제품명 포함 여부 검사
    found = []
    text_lower = text.lower()
    for prod, comp in product_to_company.items():
        prod_lower = prod.lower()
        if prod_lower and prod_lower in text_lower:
            found.append(f"- {prod} (업소명: {comp})")
    if found:
        cert_result = "다음과 같은 제품이 등록되어 있습니다:\n" + "\n".join(found)
    else:
        cert_result = "❌ 텍스트 내에 식약처 인증 제품명이 포함되어 있지 않습니다."
    return f"[텍스트 추출 결과]\n{text}\n\n[식약처 인증 제품 검사]\n{cert_result}"

@mcp.prompt("웹페이지 텍스트(BS4) 추출 요청")
def extract_text_with_bs4_prompt():
    return """
아래 웹페이지에서 주요 텍스트만 추출해 주세요. (BeautifulSoup 사용)

웹페이지 URL: {{page_url}}
"""

if __name__ == "__main__":
    mcp.run(transport='stdio')
