"""
ensemble.py
Combines the supervised XGBoost classifier and the unsupervised Isolation
Forest anomaly detector into one final fraud score + attack-type prediction.
This is the single object the rest of the system (loop_runner, observability,
dashboard, and the adversarial simulator's local search) scores transactions
against.
"""

import pandas as pd
from generate.data_schema import Transaction
from defend.feature_engineering import transactions_to_dataframe, build_feature_matrix, get_labels
from defend.models.xgboost_classifier import XGBFraudClassifier
from defend.models.isolation_forest import AnomalyDetector


class FraudEnsemble:
    def __init__(self, xgb_weight: float = 0.7, anomaly_weight: float = 0.3, decision_threshold: float = 0.5):
        self.xgb = XGBFraudClassifier()
        self.anomaly = AnomalyDetector()
        self.xgb_weight = xgb_weight
        self.anomaly_weight = anomaly_weight
        self.decision_threshold = decision_threshold
        self.encoder_categories = None
        self._fitted = False

    def fit(self, transactions: list):
        df = transactions_to_dataframe(transactions)
        X, self.encoder_categories = build_feature_matrix(df)
        y, attack_types = get_labels(df)

        self.xgb.fit(X, y, attack_types)
        self.anomaly.fit(X, y)
        self._fitted = True
        return self

    def _featurize(self, transactions: list) -> pd.DataFrame:
        df = transactions_to_dataframe(transactions)
        X, _ = build_feature_matrix(df, encoder_categories=self.encoder_categories)
        return X

    def score(self, transactions: list) -> pd.DataFrame:
        """
        Returns a DataFrame with txn_id, fraud_probability, anomaly_score,
        final_score, predicted_fraud (bool), predicted_attack_type.
        """
        X = self._featurize(transactions)
        fraud_prob = self.xgb.predict_proba_fraud(X)
        anomaly_score = self.anomaly.anomaly_score(X)
        final_score = self.xgb_weight * fraud_prob + self.anomaly_weight * anomaly_score
        predicted_attack_type = self.xgb.predict_attack_type(X)

        return pd.DataFrame({
            "txn_id": [t.txn_id for t in transactions],
            "account_id": [t.account_id for t in transactions],
            "true_is_fraud": [t.is_fraud for t in transactions],
            "true_attack_type": [t.attack_type for t in transactions],
            "fraud_probability": fraud_prob,
            "anomaly_score": anomaly_score,
            "final_score": final_score,
            "predicted_fraud": (final_score >= self.decision_threshold).astype(int),
            "predicted_attack_type": predicted_attack_type,
        })

    def score_transaction(self, transaction: Transaction) -> float:
        """Single-transaction convenience used by the adversarial-ML simulator's local search."""
        return float(self.score([transaction])["final_score"].iloc[0])

    def feature_importance(self, top_n: int = 10) -> dict:
        fi = self.xgb.feature_importance()
        return dict(list(fi.items())[:top_n])
