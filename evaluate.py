"""
evaluate.py
Standard evaluation utilities: confusion matrix, per-attack-type precision/
recall/F1, overall ROC-AUC, and false-positive rate on legitimate traffic —
the numbers that go straight into the Solution Walkthrough doc.
"""

import pandas as pd
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score, confusion_matrix


def overall_metrics(scored_df: pd.DataFrame) -> dict:
    y_true = scored_df["true_is_fraud"]
    y_pred = scored_df["predicted_fraud"]
    y_score = scored_df["final_score"]

    metrics = {
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "f1": round(f1_score(y_true, y_pred, zero_division=0), 4),
    }

    try:
        metrics["roc_auc"] = round(roc_auc_score(y_true, y_score), 4)
    except ValueError:
        metrics["roc_auc"] = None

    legit = scored_df[scored_df["true_is_fraud"] == 0]
    if len(legit) > 0:
        metrics["false_positive_rate"] = round((legit["predicted_fraud"] == 1).mean(), 4)
    else:
        metrics["false_positive_rate"] = None

    metrics["total_transactions"] = len(scored_df)
    metrics["total_fraud"] = int(y_true.sum())
    metrics["total_caught"] = int(((y_true == 1) & (y_pred == 1)).sum())

    return metrics


def confusion(scored_df: pd.DataFrame) -> pd.DataFrame:
    cm = confusion_matrix(scored_df["true_is_fraud"], scored_df["predicted_fraud"], labels=[0, 1])
    return pd.DataFrame(cm, index=["actual_legit", "actual_fraud"], columns=["predicted_legit", "predicted_fraud"])


def per_attack_type_report(scored_df: pd.DataFrame) -> pd.DataFrame:
    """Precision/recall/F1 per attack type, treating each type as a one-vs-rest detection problem."""
    rows = []
    for attack_type in scored_df.loc[scored_df["true_is_fraud"] == 1, "true_attack_type"].unique():
        subset_mask = (scored_df["true_attack_type"] == attack_type) | (scored_df["true_is_fraud"] == 0)
        subset = scored_df[subset_mask]
        y_true = (subset["true_attack_type"] == attack_type).astype(int)
        y_pred = subset["predicted_fraud"]
        rows.append({
            "attack_type": attack_type,
            "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
            "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
            "f1": round(f1_score(y_true, y_pred, zero_division=0), 4),
            "n": int((subset["true_attack_type"] == attack_type).sum()),
        })
    return pd.DataFrame(rows).sort_values("recall")
