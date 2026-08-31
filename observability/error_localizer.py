"""
error_localizer.py
Given a missed attack type, identifies WHICH detection layer was responsible
for catching that family of attack and therefore where the failure lives.
This is a curated mapping grounded in how each simulator's fidelity signature
was designed (see generate/simulators/*.py docstrings) — e.g. bot/automation
attacks are meant to be caught primarily by velocity/behavioral features, so
a miss there localizes to the "Behavioral Detection Layer".
"""

ATTACK_TYPE_TO_LAYER = {
    "card_abuse": "Transaction Velocity & Merchant-Risk Layer",
    "account_takeover": "Device & Beneficiary Continuity Layer",
    "bot_automation": "Behavioral Detection Layer",
    "adversarial_ml": "Ensemble Decision-Boundary Layer",
    "poisoned_false_positive": "Training Data Integrity Layer",
    "unknown_fraud": "Anomaly (Isolation Forest) Layer",
}

PRIMARY_FEATURES_BY_LAYER = {
    "Transaction Velocity & Merchant-Risk Layer": [
        "txn_count_last_1h", "txn_count_last_24h", "merchant_risk_score", "shared_device_risk",
    ],
    "Device & Beneficiary Continuity Layer": [
        "device_known", "beneficiary_is_new", "geo_mismatch", "liveness_confidence",
    ],
    "Behavioral Detection Layer": [
        "velocity_ratio_1h_24h", "time_since_last_txn_sec", "deviation_from_avg_amount",
    ],
    "Ensemble Decision-Boundary Layer": [
        "ip_risk_score", "deviation_from_avg_amount", "amount",
    ],
    "Training Data Integrity Layer": [
        "is_fraud (label)", "attack_type (label)",
    ],
    "Anomaly (Isolation Forest) Layer": [
        "all numeric features (unsupervised distance-based)",
    ],
}


def localize(attack_type: str) -> dict:
    layer = ATTACK_TYPE_TO_LAYER.get(attack_type, "Anomaly (Isolation Forest) Layer")
    return {
        "attack_type": attack_type,
        "failed_layer": layer,
        "primary_features_for_layer": PRIMARY_FEATURES_BY_LAYER.get(layer, []),
    }
