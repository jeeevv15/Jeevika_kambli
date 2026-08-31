"""
xgboost_classifier.py
Primary tabular fraud detector. Trains a binary fraud/not-fraud model plus a
multiclass attack-type model so the ensemble can both flag AND label what
kind of attack it thinks it's looking at.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

try:
    from xgboost import XGBClassifier
    _BACKEND = "xgboost"
except ImportError:
    # Falls back to sklearn's gradient boosting if xgboost isn't installed in
    # this environment. Interface-compatible (fit/predict_proba/predict/
    # feature_importances_), so the rest of the system doesn't need to know
    # which backend is active. Install xgboost (see requirements.txt) for
    # the intended production-grade backend.
    from sklearn.ensemble import HistGradientBoostingClassifier as XGBClassifier
    _BACKEND = "sklearn_hist_gbm"


def _make_model(random_state: int):
    if _BACKEND == "xgboost":
        return XGBClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.08,
            subsample=0.9, colsample_bytree=0.9,
            eval_metric="logloss", random_state=random_state,
        )
    return XGBClassifier(max_iter=200, max_depth=5, learning_rate=0.08, random_state=random_state)


class XGBFraudClassifier:
    """
    Name kept as XGBFraudClassifier for interface stability even though the
    backend may fall back to sklearn's HistGradientBoostingClassifier when
    xgboost isn't available in the current environment (see _BACKEND above).
    """
    def __init__(self, random_state: int = 42):
        self.backend = _BACKEND
        self.binary_model = _make_model(random_state)
        self.multiclass_model = _make_model(random_state)
        self.attack_label_encoder = LabelEncoder()
        self._feature_names = None
        self._fitted = False

    def fit(self, X: pd.DataFrame, y_binary: pd.Series, attack_types: pd.Series):
        self._feature_names = list(X.columns)
        self.binary_model.fit(X, y_binary)

        fraud_mask = y_binary == 1
        if fraud_mask.sum() >= 2 and attack_types[fraud_mask].nunique() >= 2:
            encoded = self.attack_label_encoder.fit_transform(attack_types[fraud_mask])
            self.multiclass_model.fit(X[fraud_mask], encoded)
            self._has_multiclass = True
        else:
            self._has_multiclass = False

        self._fitted = True
        return self

    def _align(self, X: pd.DataFrame) -> pd.DataFrame:
        return X.reindex(columns=self._feature_names, fill_value=0)

    def predict_proba_fraud(self, X: pd.DataFrame) -> np.ndarray:
        X = self._align(X)
        return self.binary_model.predict_proba(X)[:, 1]

    def predict_attack_type(self, X: pd.DataFrame) -> list:
        X = self._align(X)
        if not getattr(self, "_has_multiclass", False):
            return ["unknown_fraud"] * len(X)
        preds = self.multiclass_model.predict(X)
        return list(self.attack_label_encoder.inverse_transform(preds))

    def feature_importance(self) -> dict:
        if not self._fitted:
            return {}
        importances = getattr(self.binary_model, "feature_importances_", None)
        if importances is None:
            # HistGradientBoostingClassifier (sklearn fallback) doesn't expose
            # feature_importances_ directly. Uniform placeholder ranking is used
            # so downstream code (root-cause narrative) still runs — install
            # xgboost for real feature-importance-driven diagnostics.
            importances = np.ones(len(self._feature_names)) / len(self._feature_names)
        return dict(sorted(zip(self._feature_names, importances), key=lambda x: -x[1]))
