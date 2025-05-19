import streamlit as st
import requests
from PIL import Image

st.title("영양제 분류 통합 서비스")

# --- 외국계 기업 분류 UI ---
st.header("외국계 기업 분류")
company = st.text_input("회사명")
ceo = st.text_input("대표자명")
address = st.text_input("주소")
if st.button("기업 분류 예측"):
    if not (company or ceo or address):
        st.warning("하나 이상의 정보를 입력하세요.")
    else:
        response = requests.post(
            "http://api:8000/predict",
            json={"company": company, "ceo": ceo, "address": address}
        )
        if response.ok:
            result = response.json()
            st.write(f"예측 결과: {result.get('label')} (확률: {result.get('probability')})")
        else:
            st.error("API 요청 실패")

# --- 영양제 이미지 분류 UI ---
st.header("영양제 이미지 분류")
uploaded_file = st.file_uploader("이미지를 업로드하세요", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="업로드된 이미지", use_container_width=True)
    if st.button("이미지 분류"):
        files = {"file": uploaded_file.getvalue()}
        response = requests.post("http://api:8000/classify-image", files=files)
        if response.ok:
            result = response.json()
            st.markdown(f"### 👉 결과: **{result.get('result')}**")
        else:
            st.error("API 요청 실패")