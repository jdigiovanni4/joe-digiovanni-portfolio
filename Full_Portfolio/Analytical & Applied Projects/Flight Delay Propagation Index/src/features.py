"""
features.py
-----------
All feature engineering for the Delay Propagation Index model.

Two main transformations:
  1. tail_chain_features  — lag the previous flight's arrival delay per aircraft (Tail_Number)
  2. airport_congestion   — rolling 60-min mean of arrival delays at the origin airport
"""

import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _time_to_minutes(x) -> int:
    """Convert an integer HHMM departure time (e.g. 830) to minutes from midnight."""
    s = str(int(x)).zfill(4)
    return int(s[:2]) * 60 + int(s[2:])


# ---------------------------------------------------------------------------
# Core transforms
# ---------------------------------------------------------------------------

def build_tail_chain(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sort by (Tail_Number, FlightDate, CRSDepTime) and lag ArrDelay one position
    within each aircraft's flight history.

    Adds columns
    ------------
    Prev_ArrDelay : float  — previous flight's arrival delay (minutes)
    Target_Delayed : int   — 1 if current ArrDelay > 15 minutes, else 0

    Drops the first flight of each aircraft (no prior chain available).
    """
    df = df.copy()
    df = df.sort_values(["Tail_Number", "FlightDate", "CRSDepTime"])
    df["Prev_ArrDelay"] = df.groupby("Tail_Number")["ArrDelay"].shift(1)
    df["Target_Delayed"] = (df["ArrDelay"] > 15).astype(int)
    df = df.dropna(subset=["Prev_ArrDelay"])
    return df.reset_index(drop=True)


def build_airport_congestion(df: pd.DataFrame, window: str = "60min") -> pd.DataFrame:
    """
    Compute a rolling mean of ArrDelay for flights departing from the same Origin
    within a trailing time window. Acts as a proxy for real-time airport congestion.

    Parameters
    ----------
    window : str
        Pandas offset alias for the rolling window (default '60min').

    Adds column
    -----------
    Airport_Congestion : float — rolling mean arrival delay at the origin (NaN → 0)
    Dep_Minutes        : int   — CRSDepTime converted to minutes from midnight
    """
    df = df.copy()
    df["Dep_Minutes"] = df["CRSDepTime"].apply(_time_to_minutes)

    # Build a proper datetime index so pandas rolling works on real time distances
    df["Time_Index"] = (
        pd.to_datetime(df["FlightDate"])
        + pd.to_timedelta(df["Dep_Minutes"], unit="m")
    )
    df = df.sort_values(["Origin", "Time_Index"]).set_index("Time_Index")

    df["Airport_Congestion"] = (
        df.groupby("Origin")["ArrDelay"]
        .rolling(window)
        .mean()
        .reset_index(level=0, drop=True)
        .fillna(0)
    )

    df = df.reset_index(drop=True)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full feature engineering pipeline in order."""
    df = build_tail_chain(df)
    df = build_airport_congestion(df)
    return df


FEATURE_COLS = ["Prev_ArrDelay", "Airport_Congestion", "Distance", "Dep_Minutes"]
TARGET_COL = "Target_Delayed"
