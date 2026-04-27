"""
ingest.py
---------
Downloads and caches raw BTS On-Time Performance data.
Default: January 2023. Pass a different (year, month) tuple to pull another period.
"""

import io
import zipfile
import requests
import pandas as pd
from pathlib import Path

BTS_URL_TEMPLATE = (
    "https://transtats.bts.gov/PREZIP/"
    "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{year}_{month}.zip"
)

KEEP_COLS = [
    "FlightDate", "Tail_Number", "Origin", "Dest",
    "CRSDepTime", "DepTime", "DepDelay",
    "CRSArrTime", "ArrTime", "ArrDelay", "Distance",
]


def fetch_bts_data(year: int = 2023, month: int = 1, cache_dir: Path = Path("data")) -> pd.DataFrame:
    """
    Download one month of BTS On-Time data and return a trimmed DataFrame.

    Parameters
    ----------
    year, month : int
        The period to pull.
    cache_dir : Path
        Where to cache the raw CSV so repeated runs don't re-download.

    Returns
    -------
    pd.DataFrame with KEEP_COLS, rows dropped where Tail_Number / DepTime / ArrTime are null.
    """
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"bts_{year}_{month:02d}.csv"

    if cache_path.exists():
        print(f"[ingest] Loading from cache: {cache_path}")
        return pd.read_csv(cache_path, low_memory=False)

    url = BTS_URL_TEMPLATE.format(year=year, month=month)
    print(f"[ingest] Downloading: {url}")
    r = requests.get(url, timeout=120)
    r.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        df = pd.read_csv(z.open(z.namelist()[0]), low_memory=False)

    print(f"[ingest] Raw shape: {df.shape}")
    df = df[KEEP_COLS].dropna(subset=["Tail_Number", "DepTime", "ArrTime"])
    df.to_csv(cache_path, index=False)
    print(f"[ingest] Cached trimmed data to: {cache_path}")
    return df
