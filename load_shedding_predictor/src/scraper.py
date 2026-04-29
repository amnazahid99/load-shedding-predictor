"""
Web scraper for LESCO load shedding data.
Can be used to scrape real data or load from custom CSV.
"""

import pandas as pd
from pathlib import Path
from typing import Optional


def scrape_lesco_data() -> pd.DataFrame:
    """
    Scrape LESCO load shedding data from website.
    Returns DataFrame with columns: date, zone, outage_start, outage_end, outage_hours, temperature, humidity
    """
    raise NotImplementedError("Web scraping not implemented. Use load_from_csv() instead.")


def load_from_csv(filepath: str) -> pd.DataFrame:
    """
    Load load shedding data from CSV file.

    Args:
        filepath: Path to CSV file

    Returns:
        DataFrame with load shedding data
    """
    df = pd.read_csv(filepath)
    required_cols = ['date', 'zone', 'outage_hours']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


def save_raw_data(df: pd.DataFrame, output_path: Optional[str] = None) -> str:
    """
    Save raw data to CSV.

    Args:
        df: DataFrame to save
        output_path: Optional output path. If None, saves to data/raw/load_shedding_data.csv

    Returns:
        Path where data was saved
    """
    if output_path is None:
        output_path = Path(__file__).parent.parent / "data" / "raw" / "load_shedding_data.csv"
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return str(output_path)


if __name__ == "__main__":
    print("Use load_from_csv() to load data from a CSV file.")
    print("Example:")
    print("  from scraper import load_from_csv")
    print("  df = load_from_csv('path/to/your/data.csv')")