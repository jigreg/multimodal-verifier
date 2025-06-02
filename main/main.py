import streamlit as st
st.set_page_config(page_title="제품 인증 분석기", layout="wide")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO
import pandas as pd
import requests
import time
from selenium.webdriver.chrome.service import Service

# 중고나라 URL 확인
def is_joongna_url(url: str) -> bool:
    return "joongna.com" in url

# Selenium 기반 텍스트/이미지 추출
def extract_with_selenium(url: str):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    text = soup.get_text(separator=' ', strip=True)

    img_urls = []
    for img in soup.find_all('img'):
        src = img.get('src')
        if src and not src.startswith('data:'):
            full_url = urljoin(url, src)
            img_urls.append(full_url)

    return text, img_urls

# 인증 제품 리스트 및 업소명 매핑 불러오기
@st.cache_data
def load_certified_product_info(csv_path: str):
    df = pd.read_csv(csv_path)
    product_to_company = dict(zip(df['제품명'].dropna().astype(str).str.strip(), df['업소명'].dropna().astype(str).str.strip()))
    certified_set = set(product_to_company.keys())
    return certified_set, product_to_company

# CSV 로드
CSV_PATH = "./data.csv"
certified_products, product_to_company = load_certified_product_info(CSV_PATH)

# === Streamlit UI 시작 ===
st.title("영양제 분류 통합 서비스")

# === 1. 웹페이지 텍스트/이미지 추출 및 이미지 분석 ===
st.header("1. 웹페이지 텍스트/이미지 추출 및 이미지 분석")
url = st.text_input("🔗 분석할 URL 입력", value="https://web.joongna.com/product/208924084")

if st.button("분석 시작", key="analyze") and url:
    # 이전 분석 결과 초기화
    st.session_state["text"] = ""
    st.session_state["img_urls"] = []
    for i in range(6):
        st.session_state.pop(f"img_result_{i}", None)

    is_joongna = is_joongna_url(url)
    if not is_joongna:
        st.warning("⚠️ 중고나라 URL이 아닙니다.")
    else:
        with st.spinner("페이지 분석 중..."):
            text, img_urls = extract_with_selenium(url)
            st.session_state["text"] = text
            st.session_state["img_urls"] = img_urls

# 세션에서 분석 결과 불러오기
text = st.session_state.get("text", "")
img_urls = st.session_state.get("img_urls", [])

if text:
    st.subheader("📜 텍스트 추출")
    st.write(text[:100] + ("..." if len(text) > 1000 else ""))

if img_urls:
    st.subheader("🖼️ 이미지 미리보기 및 이미지 분석")
    cols = st.columns(3)
    for i, img_url in enumerate(img_urls[:6]):
        with cols[i % 3]:
            st.image(img_url, caption=f"Image {i+1}", use_container_width=False, width=200)
            btn_key = f"analyze_img_{i}"
            if st.button(f"이 이미지 분석", key=btn_key):
                response = requests.get(img_url)
                if response.status_code == 200:
                    file_obj = BytesIO(response.content)
                    file_obj.name = "image.jpg"
                    api_response = requests.post(
                        "http://api:8000/classify-image",
                        files={"file": ("image.jpg", file_obj, "image/jpeg")}
                    )
                    if api_response.ok:
                        result = api_response.json()
                        st.session_state[f"img_result_{i}"] = f"분석 결과: {result.get('result')}"
                    else:
                        st.session_state[f"img_result_{i}"] = f"API 호출 실패: {api_response.status_code} {api_response.text}"
                else:
                    st.session_state[f"img_result_{i}"] = f"이미지 다운로드 실패: {response.status_code}"

            # 버튼 아래에 항상 결과 메시지 출력
            result_msg = st.session_state.get(f"img_result_{i}", "")
            if result_msg:
                st.info(result_msg)

# === 2. 제품명 기반 식약처 인증 확인 ===
st.header("2. 제품명 기반 식약처 인증 확인")
product_name = st.text_input("제품명을 입력하세요 (예: 시아플렉스)", key="product_name")
if st.button("제품 인증 확인", key="certify") and product_name:
    product_name_lower = product_name.strip().lower()
    matched = [(prod, comp) for prod, comp in product_to_company.items() if product_name_lower in prod.lower()]
    if matched:
        msg = "\n".join([f"\n✅ 식약처 인증 제품: {prod} (업소명: {comp})" for prod, comp in matched])
        st.session_state["certify_result"] = msg
    else:
        st.session_state["certify_result"] = "❌ 식약처 인증되지 않은 제품입니다."

# 항상 결과 메시지 출력
if "certify_result" in st.session_state:
    if "✅" in st.session_state["certify_result"]:
        st.success(st.session_state["certify_result"])
    else:
        st.error(st.session_state["certify_result"])

# === 3. 정상 기업 및 원료 분류(판매자) ===
st.title("🇰🇷 정상 기업 및 원료 분류")
st.write("회사명과/또는 사용 원료명을 입력하면, 신고업체 여부를 예측합니다.")

# === 입력 항목 ===
company_name = st.text_input("회사명", placeholder="예: 코스맥스바이오")

ingredient_input = st.text_area(
    "원료명 (쉼표로 구분)", 
    placeholder="예: 은행잎추출물, 프락토올리고당, 밀크씨슬추출물"
)

# === 처리 ===
if st.button("예측 실행"):
    # 입력 정리
    ingredients = [
        i.strip() for i in ingredient_input.split(",") if i.strip()
    ] if ingredient_input else None

    if not company_name and not ingredients:
        st.warning("회사명 또는 원료명을 하나 이상 입력해주세요.")
    else:
        payload = {
            "company_name": company_name,
            "ingredients": ingredients
        }

        try:
            response = requests.post("http://api:8000/predict", json=payload, timeout=10)
            if response.ok:
                result = response.json()
                st.success(f"🧠 예측 결과: {result['prediction']} (확률: {result['confidence']})")
                st.code(f"입력 문장: {result['input']}", language="text")
            else:
                st.error(f"API 요청 실패: {response.status_code} {response.text}")
        except Exception as e:
            st.error(f"API 연결 오류: {e}")