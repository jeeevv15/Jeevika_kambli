"""
feature_engineering.py
Converts a list of Transaction objects into a model-ready pandas DataFrame:
encodes categoricals, adds a couple of derived ratio features, and keeps
label columns separate from feature columns so nothing leaks into training.
"""

import pandas as pd
from generate.data_schema import FEATURE_COLUMNS, LABEL_COLUMN, ATTACK_TYPE_COLUMN

CATEGORICAL_COLUMNS = ["channel", "merchant_category", "kyc_tier", "auth_method"]
BOOLEAN_COLUMNS = ["device_known", "is_vpn_or_proxy", "geo_mismatch", "beneficiary_is_new"]


def transactions_to_dataframe(transactions: list) -> pd.DataFrame:
    rows = [t.__dict__ for t in transactions]
    return pd.DataFrame(rows)


def build_feature_matrix(df: pd.DataFrame, encoder_categories: dict = None):
    """
    Returns (X, encoder_categories) where X is a numeric-only DataFrame.
    encoder_categories: pass in the categories learned at train time so
    eval/live-scoring data gets consistently one-hot encoded even if some
    categories don't appear in the new batch.
    """
    df = df.copy()

    for col in BOOLEAN_COLUMNS:
        df[col] = df[col].astype(int)

    # a couple of cheap derived features that meaningfully help fraud models
    df["velocity_ratio_1h_24h"] = df["txn_count_last_1h"] / (df["txn_count_last_24h"] + 1)
    df["amount_to_balance_ratio"] = df["amount"] / (df["account_balance"] + 1)
    df["shared_device_risk"] = (df["shared_device_account_count"] > 1).astype(int)
    df["shared_ip_risk"] = (df["shared_ip_account_count"] > 1).astype(int)

    engineered_extra = ["velocity_ratio_1h_24h", "amount_to_balance_ratio", "shared_device_risk", "shared_ip_risk"]
    base_cols = [c for c in FEATURE_COLUMNS if c not in CATEGORICAL_COLUMNS]
    numeric_df = df[base_cols + engineered_extra].copy()

    cat_df = pd.get_dummies(df[CATEGORICAL_COLUMNS], prefix=CATEGORICAL_COLUMNS)

    if encoder_categories is not None:
        # align columns to training-time schema
        cat_df = cat_df.reindex(columns=encoder_categories, fill_value=0)
    else:
        encoder_categories = list(cat_df.columns)

    X = pd.concat([numeric_df.reset_index(drop=True), cat_df.reset_index(drop=True)], axis=1)
    X = X.fillna(0)
    return X, encoder_categories


def get_labels(df: pd.DataFrame):
    y = df[LABEL_COLUMN].astype(int)
    attack_types = df[ATTACK_TYPE_COLUMN]
    return y, attack_types
