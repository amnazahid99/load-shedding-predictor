"""
Feature engineering for load shedding prediction.
Target: tomorrow's outage hours (shifted -1 per zone).
All features use only past information.
"""

import pandas as pd
import numpy as np
from pathlib import Path

ZONE_MAPPING = {
    'Gulberg': 0, 'Model Town': 1, 'Cantt': 2, 'Shalimar': 3,
    'Samanabad': 4, 'Allama Iqbal Town': 5, 'Data Gunj Baksh': 6,
    'Ravi Road': 7, 'Shahalam': 8, 'Mughalpura': 9, 'Outfall Road': 10,
    'Nishtar Town': 11, 'Wahdat Colony': 12, 'Sabzazar': 13, 'Yunus Road': 14,
    'Cantonment': 15, 'Johar Town': 16, 'Wapda Town': 17, 'Muslim Town': 18,
    'Kahnpur': 19, 'Shahpur': 20, 'Harbanspura': 21, 'Ferozewala': 22
}

DEFAULT_TEMPERATURE = 20.0

def load_raw_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    return df

def create_zone_encoding(df: pd.DataFrame) -> pd.DataFrame:
    df['zone_encoded'] = df['zone'].map(ZONE_MAPPING)
    # handle unseen zones
    if df['zone_encoded'].isna().any():
        max_code = max(ZONE_MAPPING.values()) + 1
        df['zone_encoded'] = df['zone_encoded'].fillna(max_code).astype(int)
    return df

def create_day_of_week(df: pd.DataFrame) -> pd.DataFrame:
    df['day_of_week'] = df['date'].dt.dayofweek
    return df

def create_temperature_features(df: pd.DataFrame) -> pd.DataFrame:
    df['temperature'] = df['temperature'].fillna(DEFAULT_TEMPERATURE)
    df['temp_bin'] = pd.cut(
        df['temperature'],
        bins=[0, 15, 25, 35, 50],
        labels=[0, 1, 2, 3]
    ).astype(float).fillna(1)
    return df

def create_lag_features(df: pd.DataFrame, zone_col='zone_encoded', target_col='outage_hours', lags=None):
    if lags is None:
        lags = [1, 2, 3, 7]
    df = df.sort_values([zone_col, 'date']).copy()
    for lag in lags:
        df[f'lag_{lag}'] = df.groupby(zone_col)[target_col].shift(lag)
    return df

def create_rolling_features(df: pd.DataFrame, zone_col='zone_encoded', target_col='outage_hours'):
    df = df.sort_values([zone_col, 'date']).copy()
    df['rolling_7'] = df.groupby(zone_col)[target_col].transform(
        lambda x: x.shift(1).rolling(window=7, min_periods=1).mean()
    )
    df['rolling_14'] = df.groupby(zone_col)[target_col].transform(
        lambda x: x.shift(1).rolling(window=14, min_periods=1).mean()
    )
    return df

def create_target_tomorrow(df: pd.DataFrame, zone_col='zone_encoded', target_col='outage_hours'):
    """Shift target one day forward (tomorrow's outage)."""
    df = df.sort_values([zone_col, 'date']).copy()
    df['target_tomorrow'] = df.groupby(zone_col)[target_col].shift(-1)
    return df

def process_features(raw_data_path: str, output_path: str = None) -> pd.DataFrame:
    """Complete feature engineering pipeline, including target shift."""
    df = load_raw_data(raw_data_path)
    df = create_zone_encoding(df)
    df = create_day_of_week(df)
    df = create_temperature_features(df)
    df = create_lag_features(df)
    df = create_rolling_features(df)
    df = create_target_tomorrow(df)
    
    # Drop rows where target is NaN (last day of each zone) and where lags are NaN (first few days)
    df = df.dropna(subset=['target_tomorrow'])
    df = df.fillna(0)  # remaining NaNs in lags/rollings become 0
    
    if output_path:
        df.to_csv(output_path, index=False)
        print(f"Processed data saved to {output_path}")
    return df

def get_zone_list():
    return list(ZONE_MAPPING.keys())

if __name__ == "__main__":
    raw_path = Path(__file__).parent.parent / "data" / "raw" / "load_shedding_data.csv"
    processed_path = Path(__file__).parent.parent / "data" / "processed" / "processed_data.csv"
    df = process_features(str(raw_path), str(processed_path))
    print(f"Processed {len(df)} records. Columns: {list(df.columns)}")