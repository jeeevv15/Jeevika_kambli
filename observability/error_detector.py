"""
error_detector.py
Finds defense failures: attacks the ensemble scored as legitimate (false
negatives), broken down per attack type. This is step 1 of the observability
pipeline — it doesn't explain anything yet, it just finds what broke.
"""

import pandas as pd


def find_missed_attacks(scored_df: pd.DataFrame) -> pd.DataFrame:
    """
    scored_df: output of FraudEnsemble.score() — must contain true_is_fraud,
    true_attack_type, predicted_fraud.
    Returns the subset of rows that are real attacks the model missed.
    """
    missed = scored_df[(scored_df["true_is_fraud"] == 1) & (scored_df["predicted_fraud"] == 0)]
    return missed


def recall_by_attack_type(scored_df: pd.DataFrame) -> pd.DataFrame:
    """Per-attack-type recall — the core metric for 'diversity of detection'."""
    fraud_rows = scored_df[scored_df["true_is_fraud"] == 1]
    if fraud_rows.empty:
        return pd.DataFrame(columns=["attack_type", "total", "caught", "recall"])

    summary = (
        fraud_rows.groupby("true_attack_type")
        .apply(lambda g: pd.Series({
            "total": len(g),
            "caught": int(g["predicted_fraud"].sum()),
        }))
        .reset_index()
        .rename(columns={"true_attack_type": "attack_type"})
    )
    summary["recall"] = summary["caught"] / summary["total"]
    return summary.sort_values("recall")


def weakest_attack_type(scored_df: pd.DataFrame) -> str:
    """Identifies the attack type with the lowest recall — what the loop should target next."""
    summary = recall_by_attack_type(scored_df)
    if summary.empty:
        return None
    return summary.iloc[0]["attack_type"]
