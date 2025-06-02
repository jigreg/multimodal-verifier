from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from PIL import Image
import torch
from torchvision import transforms, models
import joblib
import io
from typing import Optional, List

app = FastAPI()

# 2. 이미지 모델 로드
def load_image_model():
    model = models.resnet18(pretrained=False)
    num_ftrs = model.fc.in_features
    model.fc = torch.nn.Linear(num_ftrs, 2)
    model.load_state_dict(torch.load("./best_resnet18.pt", map_location=torch.device("cpu")))
    model.eval()
    return model

image_model = load_image_model()

image_preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])
# 모델 및 벡터라이저 로딩
text_model = joblib.load("abnormal_company_rf_model.pkl")
vectorizer = joblib.load("abnormal_company_vectorizer.pkl")

# 새로운 요청 스키마
class PredictRequest(BaseModel):
    ingredients: Optional[List[str]] = None
    company_name: Optional[str] = None

@app.post("/predict")
def predict(data: PredictRequest):
    if not data.ingredients and not data.company_name:
        return {"error": "ingredients 또는 company_name 중 하나 이상 입력해주세요."}

    # 입력 텍스트 결합
    ingredients = data.ingredients if data.ingredients else []
    if isinstance(ingredients, str):
        ingredients = [ingredients]

    company_name = data.company_name if data.company_name else ""
    combined_text = ' '.join(ingredients + [company_name])

    # 예측
    vector = vectorizer.transform([combined_text])
    prob = text_model.predict_proba(vector)[0]
    label = int(prob[1] > 0.5)

    return {
        "input": combined_text,
        "prediction": "신고업체" if label == 1 else "정상업체",
        "confidence": round(prob[label], 4)
    }

# ===== 이미지 분류 엔드포인트 =====
@app.post("/classify-image")
async def classify_image(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    input_tensor = image_preprocess(image).unsqueeze(0)

    with torch.no_grad():
        output = image_model(input_tensor)
        _, predicted = torch.max(output, 1)

    label = "Yes" if predicted.item() == 1 else "No"
    return {"result": label}

# ===== 헬스 체크 =====
@app.get("/health")
def health_check():
    return {"status": "ok"}