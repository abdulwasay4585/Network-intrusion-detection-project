from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import pickle
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import tensorflow as tf

app = FastAPI(title="NetPulse API")

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = 'models/packet_loss_model.keras'
SCALER_PATH = 'models/scaler.pkl'

model = None
scaler = None

def load_resources():
    global model, scaler
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        model = tf.keras.models.load_model(MODEL_PATH)
        with open(SCALER_PATH, 'rb') as f:
            scaler = pickle.load(f)
        print("Model and Scaler loaded successfully.")
    else:
        print("Model or Scaler not found. Please run train_model.py first.")

@app.on_event("startup")
async def startup_event():
    load_resources()

class PredictionRequest(BaseModel):
    hour: int
    day_of_week: int
    is_weekend: int
    lag_1: float
    lag_2: float
    rolling_3: float

class PredictionResponse(BaseModel):
    predicted_dropped_packets: float

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    if model is None or scaler is None:
        load_resources()
        if model is None or scaler is None:
            raise HTTPException(status_code=503, detail="Model not loaded. Check server logs.")

    try:
        input_data = pd.DataFrame({
            'hour': [request.hour],
            'day_of_week': [request.day_of_week],
            'is_weekend': [request.is_weekend],
            'lag_1': [request.lag_1],
            'lag_2': [request.lag_2],
            'rolling_3': [request.rolling_3]
        })
        
        input_scaled = scaler.transform(input_data)
        prediction = model.predict(input_scaled)
        predicted_val = float(prediction[0][0])
        
        # Predicted value shouldn't be negative
        predicted_val = max(0, predicted_val)
        
        return PredictionResponse(predicted_dropped_packets=predicted_val)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve frontend
@app.get("/")
def read_index():
    return FileResponse('index.html')

# Mount other static files (css, js)
# Note: Ensure these files are in the same directory as app.py for this to work simply
# Or put them in a 'static' folder and mount that.
# Since they are in the root, we can just serve them as needed or mount root (risky).
# Better to serve them explicitly or move them.
# I'll just serve them explicitly for simplicity here.

@app.get("/style.css")
def read_style():
    return FileResponse('style.css')

@app.get("/script.js")
def read_script():
    return FileResponse('script.js')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
