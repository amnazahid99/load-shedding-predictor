# LESCO Load Shedding Predictor

AI-powered machine learning solution to predict daily power outage hours for various zones in Lahore, Pakistan.

## Project Overview

This project predicts load shedding (planned power outages) hours for different zones in Lahore using historical data and machine learning. It consists of:

- **Backend**: FastAPI inference API
- **Frontend**: Next.js + Tailwind CSS web interface
- **Model**: XGBoost regressor for prediction

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, Python 3.12 |
| Frontend | Next.js, React, Tailwind CSS |
| ML Model | XGBoost, scikit-learn |
| Data Processing | Pandas, NumPy |

## Project Structure

```
load_shedding_predictor/
├── backend/           # FastAPI Inference API
│   ├── main.py        # API endpoints
│   └── features.py    # Zone mapping & config
├── src/               # Training & Data Processing
│   ├── train.py       # Model training
│   ├── features.py    # Feature engineering
│   ├── scraper.py     # Data collection
│   └── classifier.py  # Helper utilities
├── frontend/          # Next.js Web App
├── data/              # Raw & processed data
│   ├── raw/
│   └── processed/
└── artifacts/         # Trained model
```

## Features

- Predict outage hours for 23 Lahore zones
- Temperature-aware predictions
- Confidence levels (low/medium/high)
- RESTful API with health checks
- Interactive web UI

## Supported Zones

Gulberg, Model Town, Cantt, Shalimar, Samanabad, Allama Iqbal Town, Data Gunj Baksh, Ravi Road, Shahalam, Mughalpura, Outfall Road, Nishtar Town, Wahdat Colony, Sabzazar, Yunus Road, Cantonment, Johar Town, Wapda Town, Muslim Town, Kahnpur, Shahpur, Harbanspura, Ferozewala

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+

### Installation

```bash
# Backend dependencies
pip install fastapi uvicorn xgboost scikit-learn pandas joblib

# Frontend dependencies
cd frontend && npm install
```

### Training the Model

```bash
cd load_shedding_predictor
python -m src.train
```

### Running the API

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Running the Frontend

```bash
cd frontend
npm run dev
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/predict` | POST | Make prediction |
| `/zones` | GET | List available zones |
| `/model/info` | GET | Model information |

## API Usage

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "zone": "Gulberg",
    "date": "2025-04-15",
    "temperature": 25
  }'
```

**Response:**
```json
{
  "zone": "Gulberg",
  "date": "2025-04-15",
  "predicted_outage_hours": 3.33,
  "confidence": "medium"
}
```

## Model Performance

- MAE: 0.85 hours
- RMSE: 1.01 hours
- R² Score: 0.65

## License

MIT License