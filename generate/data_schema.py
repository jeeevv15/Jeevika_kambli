"""
data_schema.py
Canonical transaction schema used by every simulator and the detection engine.
Every simulator returns dicts matching this shape so the feature engineering
and models don't need to special-case attack families.
"""

from dataclasses import dataclass, field, fields
from typing import Optional
import uuid
import time


@dataclass
class Transaction:
    # --- identifiers ---
    txn_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    account_id: str = ""
    timestamp: float = field(default_factory=time.time)

    # --- core transaction ---
    amount: float = 0.0
    currency: str = "INR"
    channel: str = "online"          # online | card_present | app | wallet
    merchant_category: str = "general_retail"

    # --- entity / account context ---
    account_age_days: int = 365
    kyc_tier: str = "full"           # none | partial | full
    avg_ticket_size: float = 0.0     # user's historical average
    account_balance: float = 0.0

    # --- behavioral ---
    txn_count_last_1h: int = 0
    txn_count_last_24h: int = 0
    txn_count_last_7d: int = 0
    time_since_last_txn_sec: float = 3600.0
    session_duration_sec: float = 120.0
    deviation_from_avg_amount: float = 0.0   # (amount - avg_ticket_size) / avg_ticket_size

    # --- device / network ---
    device_id: str = ""
    device_known: bool = True                # has this device been seen on this account before
    ip_address: str = "0.0.0.0"
    ip_risk_score: float = 0.0               # 0-1, higher = riskier (VPN/proxy/datacenter/known-bad)
    is_vpn_or_proxy: bool = False
    geo_country: str = "IN"
    geo_mismatch: bool = False               # billing country vs IP country mismatch

    # --- merchant ---
    merchant_risk_score: float = 0.0         # 0-1
    merchant_age_days: int = 1000
    merchant_chargeback_rate: float = 0.01

    # --- relational / graph ---
    shared_device_account_count: int = 1     # how many accounts share this device fingerprint
    shared_ip_account_count: int = 1         # how many accounts share this IP recently
    beneficiary_is_new: bool = False

    # --- auth ---
    auth_method: str = "password"            # password | otp | biometric_face | biometric_voice | none
    liveness_confidence: float = 1.0         # 0-1, for biometric auth events

    # --- labels (ground truth, used for training/eval only) ---
    is_fraud: int = 0
    attack_type: str = "legit"


SCHEMA_FIELDS = [f.name for f in fields(Transaction)]

# Fields the model is allowed to see (excludes IDs / raw timestamp / ground truth)
FEATURE_COLUMNS = [
    "amount", "channel", "merchant_category", "account_age_days", "kyc_tier",
    "avg_ticket_size", "account_balance", "txn_count_last_1h", "txn_count_last_24h",
    "txn_count_last_7d", "time_since_last_txn_sec", "session_duration_sec",
    "deviation_from_avg_amount", "device_known", "ip_risk_score", "is_vpn_or_proxy",
    "geo_mismatch", "merchant_risk_score", "merchant_age_days", "merchant_chargeback_rate",
    "shared_device_account_count", "shared_ip_account_count", "beneficiary_is_new",
    "auth_method", "liveness_confidence",
]

LABEL_COLUMN = "is_fraud"
ATTACK_TYPE_COLUMN = "attack_type"
