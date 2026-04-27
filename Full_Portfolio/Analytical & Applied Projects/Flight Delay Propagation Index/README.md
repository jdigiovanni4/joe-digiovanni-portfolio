# Flight Delay Propagation Index

Quantifying how delays cascade through aircraft tail chains using BTS On-Time Performance data.

## The Problem

Airlines schedule aircraft in chains: the same plane flies BOS→ATL, then ATL→DFW, then DFW→PHX. A delay on leg one propagates forward. This project measures that propagation effect and builds a classifier to predict downstream delays **using only pre-departure information**.

## Key Findings

- **521,827 flights** analyzed (BTS On-Time Performance, January 2023)
- **21.3% baseline delay rate** (arrival > 15 minutes late)
- A flight whose inbound leg arrived late (>15 min) has a **49.4% chance of itself being delayed**, vs. 13.6% when the prior leg was on time (a **3.6× propagation lift**)
- Pearson correlation between consecutive delays on the same aircraft: **0.285**
- `Airport_Congestion` ranked as the **strongest XGBoost feature** showing systemic airport pressure outweighs individual aircraft history
- XGBoost ROC-AUC: **0.870** · Logistic Regression ROC-AUC: **0.847**. The narrow gap suggests the relationship is largely linear once features are well-specified

## Project Structure

```
flight-delay-propagation/
├── data/               # Cached raw CSVs (not tracked in git)
├── notebooks/
│   └── delay_propagation_index.py   # Main analysis (run as Jupyter/Colab)
├── outputs/            # Generated figures
├── src/
│   ├── ingest.py       # BTS data download + caching
│   ├── features.py     # Tail-chain lag + airport congestion engineering
│   └── model.py        # Training, evaluation, and visualisation
└── requirements.txt
```

## Quickstart

```bash
pip install -r requirements.txt
jupyter notebook notebooks/delay_propagation_index.py
```

Or open in Google Colab directly. The ingest module downloads and caches January 2023 BTS data (~60MB) on first run; subsequent runs load from disk.

## Data Source

[BTS On-Time Reporting Carrier On-Time Performance](https://www.transtats.bts.gov/Tables.asp?QO_VQ=EFD): public domain, Federal Aviation Administration / Bureau of Transportation Statistics.

## Methodology Notes

**Time-ordered split**: Train/test uses an 80/20 chronological split rather than random shuffling to prevent leakage and mirror real deployment conditions.

**Class imbalance**: Handled via `class_weight='balanced'` in LogReg and `scale_pos_weight` set to the actual negative/positive ratio in XGBoost (~3.7 for this dataset).

**Airport congestion window**: 60-minute rolling mean of arrival delays at the origin airport. Acts as a proxy for real-time systemic pressure independent of any single aircraft.

**Feature importance note**: XGBoost ranked `Airport_Congestion` above `Prev_ArrDelay`, suggesting that where a plane is departing from matters more than what happened to that specific plane , which a useful operational distinction for gate and crew planning.
