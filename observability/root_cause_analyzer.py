"""
root_cause_analyzer.py
Given a set of missed attack transactions and the model's own feature
importances, produces a plain-English explanation of WHY the miss happened:
compares the missed transactions' feature values against the legitimate
baseline distribution and flags which of the layer's primary features failed
to separate the attack from normal traffic.
"""

import pandas as pd
from generate.data_schema import Transaction
from defend.feature_engineering import transactions_to_dataframe, build_feature_matrix


def _feature_gap(missed_raw_df: pd.DataFrame, legit_raw_df: pd.DataFrame, feature: str) -> float:
    """Normalized gap between the missed attack's feature value and the legit baseline mean."""
    if feature not in missed_raw_df.columns or feature not in legit_raw_df.columns:
        return 0.0
    try:
        legit_mean = legit_raw_df[feature].astype(float).mean()
        legit_std = legit_raw_df[feature].astype(float).std() + 1e-6
        missed_mean = missed_raw_df[feature].astype(float).mean()
        return abs(missed_mean - legit_mean) / legit_std
    except (ValueError, TypeError):
        return 0.0


def analyze(missed_transactions: list, legit_transactions: list, localization: dict, ensemble=None) -> dict:
    """
    Returns a structured root-cause explanation:
      - which primary features had almost NO separation from legit traffic
        (i.e. the attack successfully hid within normal-looking ranges for
        exactly the features this layer relies on)
      - the model's actual learned importance for those same features
        (low importance + low separation = the real root cause)
    """
    missed_df = transactions_to_dataframe(missed_transactions)
    legit_df = transactions_to_dataframe(legit_transactions)

    weak_features = []
    for feat in localization["primary_features_for_layer"]:
        gap = _feature_gap(missed_df, legit_df, feat)
        weak_features.append((feat, round(gap, 3)))

    weak_features.sort(key=lambda x: x[1])  # smallest gap first = least separable = biggest problem
    least_separable = [f for f, g in weak_features if g < 0.5]

    model_importance_note = ""
    if ensemble is not None:
        fi = ensemble.feature_importance(top_n=25)
        low_importance_overlap = [f for f, _ in weak_features if fi.get(f, 0) < 0.02]
        if low_importance_overlap:
            model_importance_note = (
                f"The model also assigns low learned importance to {', '.join(low_importance_overlap)}, "
                f"confirming the classifier isn't weighting these signals meaningfully."
            )

    if least_separable:
        explanation = (
            f"The classifier relies heavily on {', '.join([f for f,_ in weak_features[:2]])} for this layer, "
            f"but in these missed cases those features sit within {min(g for _,g in weak_features):.2f} "
            f"standard deviations of normal legitimate traffic — the attack is engineered to look statistically "
            f"ordinary on exactly the dimensions this layer checks."
        )
    else:
        explanation = (
            "The relevant features do show separation from legitimate traffic, suggesting the miss is more "
            "likely a threshold/calibration issue than a missing signal — consider lowering the decision "
            "threshold or re-weighting this layer in the ensemble."
        )

    return {
        "attack_type": localization["attack_type"],
        "failed_layer": localization["failed_layer"],
        "weak_features": weak_features,
        "explanation": explanation + (" " + model_importance_note if model_importance_note else ""),
    }
