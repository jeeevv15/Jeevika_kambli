"""
isolation_forest.py
Unsupervised anomaly layer. Complements the supervised XGBoost model by
catching attack patterns that don't resemble any previously-labeled fraud
(the "zero-day" case) — trained only on legitimate-looking distribution,
flags anything that sits far outside it regardless of whether it matches a
known attack signature.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class AnomalyDetector:
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        self.model = IsolationForest(
            n_estimators=200, contamination=contamination,
            random_state=random_state, n_jobs=-1,
        )
        self.scaler = StandardScaler()
        self._feature_names = None
        self._fitted = False

    def fit(self, X: pd.DataFrame, y_binary: pd.Series = None):
        """
        Trains primarily on transactions believed legitimate so the model
        learns a tight boundary of 'normal'. If labels are available, fits
        on the legit subset; falls back to fitting on everything if no
        labels are usable (e.g. very small/skewed batch).
        """
        self._feature_names = list(X.columns)
        if y_binary is not None and (y_binary == 0).sum() >= 20:
            fit_X = X[y_binary == 0]
        else:
            fit_X = X

        Xs = self.scaler.fit_transform(fit_X)
        self.model.fit(Xs)
        self._fitted = True
        return self

    def _align(self, X: pd.DataFrame) -> pd.DataFrame:
        return X.reindex(columns=self._feature_names, fill_value=0)

    def anomaly_score(self, X: pd.DataFrame) -> np.ndarray:
        """Returns a 0-1 score where higher = more anomalous."""
        X = self._align(X)
        Xs = self.scaler.transform(X)
        raw = self.model.decision_function(Xs)  # higher = more normal
        # normalize/flip to 0-1, higher = more anomalous
        score = -raw
        score = (score - score.min()) / (score.max() - score.min() + 1e-9)
        return score
