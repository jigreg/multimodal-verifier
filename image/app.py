import streamlit as st
import torch
from torchvision import transforms, models
from PIL import Image

# 모델 로드
@st.cache_resource
def load_model():
    model = models.resnet18(pretrained=False)
    num_ftrs = model.fc.in_features
    model.fc = torch.nn.Linear(num_ftrs, 2)  # 출력 클래스 수를 2로 변경
    model.load_state_dict(torch.load("./best_resnet18.pt", map_location=torch.device("cpu")))
    model.eval()
    return model

model = load_model()

# 전처리
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# Streamlit UI
st.title("💊 영양제 분류기")
st.write("이미지를 업로드하면 영양제인지 아닌지 분류해줍니다.")

uploaded_file = st.file_uploader("이미지를 업로드하세요", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="업로드된 이미지", use_container_width=True)

    # 추론
    input_tensor = preprocess(image).unsqueeze(0)  # 배치 차원 추가
    with torch.no_grad():
        output = model(input_tensor)
        _, predicted = torch.max(output, 1)

    # 결과 출력
    label = "Yes ✅" if predicted.item() == 1 else "No ❌"
    st.markdown(f"### 결과: **{label}**")