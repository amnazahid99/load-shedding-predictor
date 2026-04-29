"""
Classifier utilities for load shedding prediction.
Provides helper functions for model inference.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple

from features import ZONE_MAPPING, DEFAULT_TEMPERATURE


def prepare_features(
    zone: str,
    date: str,
    temperature: float = None,
    lag_values: List[float] = None,
    rolling_values: Tuple[float, float] = None
) -> np.ndarray:
    """
    Prepare feature vector for prediction.

    Args:
        zone: Zone name
        date: Date string (YYYY-MM-DD)
        temperature: Temperature in Celsius
        lag_values: List of lag values [lag_1, lag_2, lag_3, lag_7]
        rolling_values: Tuple of (rolling_7, rolling_14)

    Returns:
        Feature array ready for model prediction
    """
    from datetime import datetime

    zone_encoded = ZONE_MAPPING.get(zone)
    if zone_encoded is None:
        raise ValueError(f"Unknown zone: {zone}")

    date_obj = datetime.strptime(date, "%Y-%m-%d")
    day_of_week = date_obj.weekday()

    temp = temperature if temperature is not None else DEFAULT_TEMPERATURE
    temp_bin = 1
    if temp <= 15:
        temp_bin = 0
    elif temp <= 25:
        temp_bin = 1
    elif temp <= 35:
        temp_bin = 2
    else:
        temp_bin = 3

    lags = lag_values if lag_values else [0, 0, 0, 0]
    rolling = rolling_values if rolling_values else (0, 0)

    features = np.array([[
        zone_encoded,
        day_of_week,
        temp,
        temp_bin,
        lags[0], lags[1], lags[2], lags[3],
        rolling[0], rolling[1]
    ]])

    return features


def classify_outage_severity(outage_hours: float) -> str:
    """
    Classify outage severity based on hours.

    Args:
        outage_hours: Predicted outage hours

    Returns:
        Severity classification: low, medium, high, critical
    """
    if outage_hours <= 2:
        return "low"
    elif outage_hours <= 4:
        return "medium"
    elif outage_hours <= 6:
        return "high"
    else:
        return "critical"


def get_zone_encoding(zone: str) -> int:
    """Get numeric encoding for a zone name."""
    return ZONE_MAPPING.get(zone)


def get_all_zones() -> List[str]:
    """Get list of all available zones."""
    return list(ZONE_MAPPING.keys())


if __name__ == "__main__":
    print("Available zones:")
    for zone, code in ZONE_MAPPING.items():
        print(f"  {zone}: {code}")