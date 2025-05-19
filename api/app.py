from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from bert_model.classifier import predict_label
from PIL import Image
import torch
from torchvision import transforms, models
import io

app = FastAPI()

class PredictRequest(BaseModel):
    company: str = ""
    ceo: str = ""
    address: str = ""

# 모델 로드 (최초 1회)
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

@app.post("/predict")
def predict(data: PredictRequest):
    label, prob = predict_label(data.company, data.ceo, data.address)
    if not label:
        return {"error": "하나 이상의 정보가 필요합니다."}
    return {"label": label, "probability": round(prob, 4)}

@app.get("/health")
def health_check():
    return {"status": "ok"}

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