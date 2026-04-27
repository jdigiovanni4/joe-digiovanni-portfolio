
import sys
sys.path.insert(0, "../src")

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Project modules
from ingest import fetch_bts_data
from features import engineer_features, FEATURE_COLS, TARGET_COL
from model import (
    time_split, train_models, evaluate,
    plot_roc_curves, plot_feature_importance, plot_delay_propagation_lift,
)

OUTPUT_DIR = Path("../outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

raw = fetch_bts_data(year=2023, month=1, cache_dir="../data")
print(f"Loaded: {raw.shape[0]:,} flights, {raw.shape[1]} columns")
raw.head(3)

df = engineer_features(raw)
print(f"Engineered dataset: {df.shape[0]:,} flights")
print(f"Delay rate (>15 min): {df[TARGET_COL].mean():.1%}")
df[FEATURE_COLS + [TARGET_COL]].describe().round(2)


corr = df["Prev_ArrDelay"].corr(df["ArrDelay"])
delayed_chain = df[df["Prev_ArrDelay"] > 15][TARGET_COL].mean()
on_time_chain = df[df["Prev_ArrDelay"] <= 15][TARGET_COL].mean()
lift = delayed_chain / on_time_chain

print(f"Pearson correlation (Prev vs Current delay):  {corr:.3f}")
print(f"P(delayed | prev flight on time):             {on_time_chain:.1%}")
print(f"P(delayed | prev flight delayed >15 min):     {delayed_chain:.1%}")
print(f"Propagation lift:                             {lift:.2f}×")

plot_delay_propagation_lift(df, OUTPUT_DIR)


X_train, X_test, y_train, y_test = time_split(df)
log_reg, xgb, scaler = train_models(X_train, y_train)
lr_auc, xgb_auc = evaluate(log_reg, xgb, scaler, X_test, y_test)


plot_roc_curves(log_reg, xgb, scaler, X_test, y_test, OUTPUT_DIR)


plot_feature_importance(xgb, OUTPUT_DIR)
