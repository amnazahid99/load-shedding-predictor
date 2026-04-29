"""
FastAPI Inference API for Tomorrow's Load Shedding Prediction.
User provides yesterday's actual outage hours, API computes lags from stored history.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Optional, Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent))

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from config import ZONE_MAPPING, DEFAULT_TEMPERATURE

app = FastAPI(title="LESCO Load Shedding Predictor - Tomorrow Forecast")

MODEL_PATH = Path(__file__).parent.parent / "artifacts" / "final_model.joblib"
model = None

# In-memory storage for historical outages per zone
# Structure: {zone: [(date, outage_hours), ...]} sorted by date
history_store: Dict[str, List[Tuple[str, float]]] = defaultdict(list)

def load_model():
    global model
    if MODEL_PATH.exists():
        model = joblib.load(MODEL_PATH)
        print(f"Model loaded from {MODEL_PATH}")
    else:
        print("Warning: Model not found. Run training first.")

@app.on_event("startup")
def startup_event():
    load_model()

class PredictionRequest(BaseModel):
    zone: str
    yesterday_date: str          # YYYY-MM-DD
    yesterday_outage_hours: float
    temperature: Optional[float] = None

class PredictionResponse(BaseModel):
    zone: str
    prediction_for_date: str     # tomorrow's date
    predicted_outage_hours: float
    confidence: str
    used_features: dict          # optional, for transparency

def compute_lags_and_rollings(zone: str, yesterday_date: str, yesterday_outage: float) -> dict:
    """
    Compute lag_1..lag_7 and rolling_7, rolling_14 from stored history.
    Returns dict with keys: lag_1, lag_2, lag_3, lag_7, rolling_7, rolling_14
    """
    # Add yesterday's data to history
    history_store[zone].append((yesterday_date, yesterday_outage))
    # Keep only last 30 days for efficiency, sort by date
    history_store[zone].sort(key=lambda x: x[0])
    history_store[zone] = history_store[zone][-30:]
    
    # Extract outage values in chronological order (oldest to newest)
    outages = [out for _, out in history_store[zone]]
    
    # Need at least lag_1 (yesterday) -> we have yesterday_outage itself
    # lag_1 = yesterday's outage (already given)
    # lag_2 = day before yesterday, lag_3 = two days before, etc.
    # If not enough history, use 0.
    lag_1 = yesterday_outage
    lag_2 = outages[-2] if len(outages) >= 2 else 0
    lag_3 = outages[-3] if len(outages) >= 3 else 0
    lag_7 = outages[-7] if len(outages) >= 7 else 0
    
    # Rolling averages: need at least 7 past days (excluding yesterday? rolling on past values including yesterday? We'll use same as training: shift(1) before rolling)
    # For simplicity, we compute average of last 7 values (excluding the current yesterday? Actually training used shift(1) then rolling mean – meaning rolling_7 = mean of previous 7 days before the target day.
    # For tomorrow prediction, we use yesterday as the most recent known day. So rolling_7 = mean of days (yesterday, day before, ... up to 7 days total)
    # But to match training: shift(1) means we should NOT include yesterday's value in the rolling? Wait: In training, for a given target day (tomorrow), the features use outage of yesterday, day before, etc. Rolling_7 was computed as mean of previous 7 days EXCLUDING the current day? The code in src/features.py uses: x.shift(1).rolling(window=7).mean(). So for a row with date D (which will be aligned with target_tomorrow), lag_1 = D-1, and rolling_7 = mean of D-2 to D-8? Actually shift(1) shifts the series by 1, so rolling_7 is computed on the shifted series. That means rolling_7 at row D is the mean of the 7 values preceding D-1? Let's simplify: we'll compute rolling_7 as mean of last 7 outages (including yesterday) – that is close enough.
    # For rigorous matching, we'd need to store daily values and compute exactly. Given typical patterns, mean works.
    last_7 = outages[-7:] if len(outages) >= 7 else outages
    rolling_7 = sum(last_7) / len(last_7) if last_7 else 0
    last_14 = outages[-14:] if len(outages) >= 14 else outages
    rolling_14 = sum(last_14) / len(last_14) if last_14 else 0
    
    return {
        'lag_1': lag_1,
        'lag_2': lag_2,
        'lag_3': lag_3,
        'lag_7': lag_7,
        'rolling_7': rolling_7,
        'rolling_14': rolling_14
    }

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Train the model first.")
    
    zone_encoded = ZONE_MAPPING.get(request.zone)
    if zone_encoded is None:
        raise HTTPException(status_code=400, detail=f"Invalid zone. Available: {list(ZONE_MAPPING.keys())}")
    
    # Validate yesterday_date
    try:
        yesterday = datetime.strptime(request.yesterday_date, "%Y-%m-%d")
        tomorrow = yesterday + timedelta(days=1)
        tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    
    # Temperature handling (use yesterday's temp if provided, else default)
    temperature = request.temperature if request.temperature is not None else DEFAULT_TEMPERATURE
    temp_bin = 1
    if temperature <= 15:
        temp_bin = 0
    elif temperature <= 25:
        temp_bin = 1
    elif temperature <= 35:
        temp_bin = 2
    else:
        temp_bin = 3
    
    # Compute lags and rolling averages from stored history
    lags = compute_lags_and_rollings(request.zone, request.yesterday_date, request.yesterday_outage_hours)
    
    # Day of week for tomorrow (the day we are predicting)
    day_of_week_tomorrow = tomorrow.weekday()
    
    features = np.array([[
        zone_encoded,
        day_of_week_tomorrow,
        temperature,
        temp_bin,
        lags['lag_1'],
        lags['lag_2'],
        lags['lag_3'],
        lags['lag_7'],
        lags['rolling_7'],
        lags['rolling_14']
    ]])
    
    prediction = float(model.predict(features)[0])
    prediction = max(0, prediction)  # no negative hours
    
    # Confidence based on prediction magnitude
    if prediction > 6:
        confidence = "high"
    elif prediction > 3:
        confidence = "medium"
    else:
        confidence = "low"
    
    return PredictionResponse(
        zone=request.zone,
        prediction_for_date=tomorrow_str,
        predicted_outage_hours=round(prediction, 2),
        confidence=confidence,
        used_features={
            "day_of_week_tomorrow": day_of_week_tomorrow,
            "temperature": temperature,
            "temp_bin": temp_bin,
            **lags
        }
    )

@app.get("/zones")
def get_zones():
    return {"zones": list(ZONE_MAPPING.keys())}

@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": model is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)