"""
Model training with time-series split for tomorrow's outage prediction.
"""

import sys
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

sys.path.insert(0, str(Path(__file__).parent))
from features import process_features

FEATURE_COLS = [
    'zone_encoded', 'day_of_week', 'temperature', 'temp_bin',
    'lag_1', 'lag_2', 'lag_3', 'lag_7',
    'rolling_7', 'rolling_14'
]
TARGET_COL = 'target_tomorrow'

def load_processed_data(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)

def train_model_ts(data_path: str, model_save_path: str, n_splits=5):
    """
    Train models using time-series cross-validation.
    Returns best model and metrics.
    """
    df = load_processed_data(data_path)
    # Ensure chronological order
    df = df.sort_values(['zone_encoded', 'date'])
    X = df[FEATURE_COLS]
    y = df[TARGET_COL]
    
    tscv = TimeSeriesSplit(n_splits=n_splits)
    
    models = {
        'XGBoost': XGBRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1
        ),
        'RandomForest': RandomForestRegressor(
            n_estimators=200, max_depth=10, random_state=42, n_jobs=-1
        )
    }
    
    best_model = None
    best_score = float('inf')
    best_name = None
    metrics_summary = {}
    
    for name, model in models.items():
        print(f"\nTraining {name} with TimeSeriesSplit...")
        fold_mae = []
        fold_rmse = []
        fold_r2 = []
        
        for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_val)
            
            mae = mean_absolute_error(y_val, y_pred)
            rmse = np.sqrt(mean_squared_error(y_val, y_pred))
            r2 = r2_score(y_val, y_pred)
            
            fold_mae.append(mae)
            fold_rmse.append(rmse)
            fold_r2.append(r2)
            print(f"  Fold {fold+1}: MAE={mae:.4f}, RMSE={rmse:.4f}, R2={r2:.4f}")
        
        avg_mae = np.mean(fold_mae)
        avg_rmse = np.mean(fold_rmse)
        avg_r2 = np.mean(fold_r2)
        metrics_summary[name] = {'mae': avg_mae, 'rmse': avg_rmse, 'r2': avg_r2}
        print(f"{name} average: MAE={avg_mae:.4f}, RMSE={avg_rmse:.4f}, R2={avg_r2:.4f}")
        
        if avg_mae < best_score:
            best_score = avg_mae
            best_model = model
            best_name = name
    
    # Retrain best model on all data
    print(f"\nBest model: {best_name} (MAE={best_score:.4f})")
    best_model.fit(X, y)
    joblib.dump(best_model, model_save_path)
    print(f"Model saved to {model_save_path}")
    
    # Feature importance (for XGBoost)
    if hasattr(best_model, 'feature_importances_'):
        importance = dict(zip(FEATURE_COLS, best_model.feature_importances_))
        print("\nFeature importances:")
        for k, v in sorted(importance.items(), key=lambda x: x[1], reverse=True):
            print(f"  {k}: {v:.4f}")
    
    return best_model, metrics_summary

def main():
    project_root = Path(__file__).parent.parent
    raw_path = project_root / "data" / "raw" / "load_shedding_data.csv"
    processed_path = project_root / "data" / "processed" / "processed_data.csv"
    model_path = project_root / "artifacts" / "final_model.joblib"
    
    print("Processing features with target shift...")
    process_features(str(raw_path), str(processed_path))
    
    print("\nTraining models with time-series split...")
    model, metrics = train_model_ts(str(processed_path), str(model_path))
    
    print("\nTraining completed.")
    return model, metrics

if __name__ == "__main__":
    main()