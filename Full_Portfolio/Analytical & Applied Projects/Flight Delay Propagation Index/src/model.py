"""
model.py
--------
Champion / Challenger training and evaluation.

Champion  : Logistic Regression  (interpretable baseline)
Challenger: XGBoost Classifier   (performance ceiling)

Design choice: time-ordered 80/20 split — no shuffling, no leakage.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, classification_report, roc_curve
from xgboost import XGBClassifier

from features import FEATURE_COLS, TARGET_COL


# ---------------------------------------------------------------------------
# Split
# ---------------------------------------------------------------------------

def time_split(df: pd.DataFrame, train_frac: float = 0.80):
    """
    Chronological train/test split — preserves temporal order to prevent leakage.
    Returns (X_train, X_test, y_train, y_test).
    """
    X = df[FEATURE_COLS]
    y = df[TARGET_COL]
    idx = int(len(X) * train_frac)
    return X.iloc[:idx], X.iloc[idx:], y.iloc[:idx], y.iloc[idx:]


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_models(X_train, y_train):
    """
    Fit LogReg (scaled) and XGBoost.
    Returns (log_reg, xgb, scaler).
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)

    log_reg = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    log_reg.fit(X_scaled, y_train)

    # scale_pos_weight ~ ratio of negatives to positives; 3 is a reasonable prior for ~25% delay rate
    pos_weight = int((y_train == 0).sum() / max((y_train == 1).sum(), 1))
    xgb = XGBClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=5,
        scale_pos_weight=pos_weight,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=42,
    )
    xgb.fit(X_train, y_train)

    return log_reg, xgb, scaler


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate(log_reg, xgb, scaler, X_test, y_test):
    """Print AUC scores and classification reports for both models."""
    X_scaled = scaler.transform(X_test)

    lr_auc = roc_auc_score(y_test, log_reg.predict_proba(X_scaled)[:, 1])
    xgb_auc = roc_auc_score(y_test, xgb.predict_proba(X_test)[:, 1])

    print(f"{'='*50}")
    print(f"  Logistic Regression  ROC-AUC: {lr_auc:.4f}")
    print(f"  XGBoost              ROC-AUC: {xgb_auc:.4f}")
    print(f"{'='*50}\n")

    print("--- XGBoost Classification Report ---")
    print(classification_report(y_test, xgb.predict(X_test)))

    return lr_auc, xgb_auc


# ---------------------------------------------------------------------------
# Visualisations
# ---------------------------------------------------------------------------

STYLE = {
    "bg": "#0d0f14",
    "panel": "#13161e",
    "accent": "#e84545",
    "accent2": "#4fc3f7",
    "text": "#e8e8e8",
    "muted": "#5a5f72",
    "grid": "#1e2230",
}


def _apply_base_style(fig, axes):
    fig.patch.set_facecolor(STYLE["bg"])
    for ax in (axes if hasattr(axes, "__iter__") else [axes]):
        ax.set_facecolor(STYLE["panel"])
        ax.tick_params(colors=STYLE["text"], labelsize=9)
        ax.xaxis.label.set_color(STYLE["text"])
        ax.yaxis.label.set_color(STYLE["text"])
        ax.title.set_color(STYLE["text"])
        for spine in ax.spines.values():
            spine.set_edgecolor(STYLE["grid"])
        ax.grid(color=STYLE["grid"], linewidth=0.6, alpha=0.8)


def plot_roc_curves(log_reg, xgb, scaler, X_test, y_test, output_dir: Path):
    """Dual ROC curves: champion vs challenger."""
    fig, ax = plt.subplots(figsize=(7, 5.5))
    _apply_base_style(fig, ax)

    for model, label, color, X_in in [
        (log_reg, "Logistic Regression", STYLE["accent2"], scaler.transform(X_test)),
        (xgb,     "XGBoost",            STYLE["accent"],  X_test),
    ]:
        fpr, tpr, _ = roc_curve(y_test, model.predict_proba(X_in)[:, 1])
        auc = roc_auc_score(y_test, model.predict_proba(X_in)[:, 1])
        ax.plot(fpr, tpr, color=color, lw=2, label=f"{label}  (AUC = {auc:.3f})")

    ax.plot([0, 1], [0, 1], "--", color=STYLE["muted"], lw=1, label="Random baseline")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves — Champion vs. Challenger", fontsize=13, pad=12)
    ax.legend(frameon=False, labelcolor=STYLE["text"], fontsize=9)

    out = output_dir / "roc_curves.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[model] Saved → {out}")


def plot_feature_importance(xgb, output_dir: Path):
    """Horizontal bar chart of XGBoost feature importances."""
    importance = pd.Series(xgb.feature_importances_, index=FEATURE_COLS).sort_values()

    fig, ax = plt.subplots(figsize=(7, 4))
    _apply_base_style(fig, ax)

    bars = ax.barh(importance.index, importance.values, color=STYLE["accent"], height=0.55)
    # Subtle gradient: lighten bars by rank
    for i, bar in enumerate(bars):
        bar.set_alpha(0.55 + 0.45 * (i / max(len(bars) - 1, 1)))

    ax.set_xlabel("Feature Importance (gain)")
    ax.set_title("XGBoost Feature Importance", fontsize=13, pad=12)
    ax.xaxis.set_major_formatter(mtick.FormatStrFormatter("%.3f"))

    out = output_dir / "feature_importance.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[model] Saved → {out}")


def plot_delay_propagation_lift(df: pd.DataFrame, output_dir: Path):
    """
    Business-forward bar chart: probability of delay conditional on
    whether the previous flight was delayed or on-time.
    """
    delayed_chain = df[df["Prev_ArrDelay"] > 15]["Target_Delayed"].mean()
    on_time_chain = df[df["Prev_ArrDelay"] <= 15]["Target_Delayed"].mean()
    lift = delayed_chain / on_time_chain

    fig, ax = plt.subplots(figsize=(6, 4.5))
    _apply_base_style(fig, ax)

    labels = ["Prev. Flight\nOn Time", "Prev. Flight\nDelayed (>15 min)"]
    vals = [on_time_chain, delayed_chain]
    colors = [STYLE["accent2"], STYLE["accent"]]

    bars = ax.bar(labels, [v * 100 for v in vals], color=colors, width=0.45, zorder=3)
    for bar, val in zip(bars, vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.8,
            f"{val:.1%}",
            ha="center", va="bottom",
            color=STYLE["text"], fontsize=11, fontweight="bold",
        )

    ax.set_ylabel("Probability of Delay (>15 min)")
    ax.set_title(
        f"Delay Propagation Lift: {lift:.1f}×\n"
        "A delayed inbound flight raises delay risk substantially",
        fontsize=11, pad=10,
    )
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_ylim(0, max(vals) * 100 * 1.2)

    out = output_dir / "propagation_lift.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[model] Saved → {out}")
