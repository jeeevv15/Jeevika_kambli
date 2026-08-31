"""
legit_transaction_sim.py
Generates realistic, non-fraudulent baseline traffic. Fraud detection is
meaningless without a believable "normal" distribution to contrast against —
this module exists to give every attack simulator something real to hide inside.
"""

import random
import time
import uuid
from generate.data_schema import Transaction

MERCHANT_CATEGORIES = [
    "grocery", "general_retail", "electronics", "travel", "dining",
    "utilities", "subscription", "fuel", "pharmacy", "entertainment",
]

def _new_account(account_pool_size: int) -> dict:
    """Represents a stable, established user profile."""
    avg_ticket = round(random.lognormvariate(mu=6.0, sigma=0.8), 2)  # ~ INR 400-3000 typical
    return {
        "account_id": f"acct_{random.randint(1, account_pool_size)}",
        "device_id": f"dev_{random.randint(1, account_pool_size)}",
        "account_age_days": random.randint(90, 2500),
        "avg_ticket_size": avg_ticket,
        "account_balance": round(avg_ticket * random.uniform(5, 50), 2),
        "kyc_tier": random.choices(["full", "partial"], weights=[0.9, 0.1])[0],
    }


def generate_legit_transactions(n: int, account_pool_size: int = 500, seed: int = None) -> list:
    if seed is not None:
        random.seed(seed)

    accounts = [_new_account(account_pool_size) for _ in range(min(account_pool_size, n))]
    txns = []
    now = time.time()

    for i in range(n):
        acct = random.choice(accounts)
        amount = max(10, round(random.gauss(acct["avg_ticket_size"], acct["avg_ticket_size"] * 0.35), 2))

        t = Transaction(
            account_id=acct["account_id"],
            timestamp=now - random.uniform(0, 30 * 24 * 3600),
            amount=amount,
            channel=random.choices(["online", "card_present", "app", "wallet"], weights=[0.4, 0.3, 0.2, 0.1])[0],
            merchant_category=random.choice(MERCHANT_CATEGORIES),
            account_age_days=acct["account_age_days"],
            kyc_tier=acct["kyc_tier"],
            avg_ticket_size=acct["avg_ticket_size"],
            account_balance=acct["account_balance"],
            txn_count_last_1h=random.choices([0, 1, 2], weights=[0.85, 0.12, 0.03])[0],
            txn_count_last_24h=random.randint(0, 4),
            txn_count_last_7d=random.randint(1, 15),
            time_since_last_txn_sec=random.uniform(1800, 172800),
            session_duration_sec=random.uniform(30, 600),
            deviation_from_avg_amount=(amount - acct["avg_ticket_size"]) / max(acct["avg_ticket_size"], 1),
            device_id=acct["device_id"],
            device_known=random.choices([True, False], weights=[0.95, 0.05])[0],
            ip_address=f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
            ip_risk_score=round(random.uniform(0, 0.15), 3),
            is_vpn_or_proxy=random.choices([True, False], weights=[0.03, 0.97])[0],
            geo_country="IN",
            geo_mismatch=False,
            merchant_risk_score=round(random.uniform(0, 0.2), 3),
            merchant_age_days=random.randint(200, 4000),
            merchant_chargeback_rate=round(random.uniform(0, 0.02), 4),
            shared_device_account_count=1,
            shared_ip_account_count=random.choices([1, 2], weights=[0.9, 0.1])[0],
            beneficiary_is_new=random.choices([True, False], weights=[0.1, 0.9])[0],
            auth_method=random.choices(["password", "otp", "biometric_face"], weights=[0.4, 0.4, 0.2])[0],
            liveness_confidence=round(random.uniform(0.9, 1.0), 3),
            is_fraud=0,
            attack_type="legit",
        )
        txns.append(t)

    return txns
