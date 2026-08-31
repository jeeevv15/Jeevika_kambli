"""
card_abuse_sim.py
Simulates automated LLM-assisted card testing ("carding"): an attacker with a
list of stolen/generated card numbers fires small-value transactions rapidly
across many merchants to find which cards are still live, before cashing out
on valid ones. Fidelity signature: high velocity, small amounts, new/unknown
device, high merchant diversity, new beneficiary, weak auth.
"""

import random
import time
from generate.data_schema import Transaction

def generate_card_abuse_attacks(n: int, seed: int = None) -> list:
    if seed is not None:
        random.seed(seed)

    txns = []
    now = time.time()
    c = 0  # each "campaign" = one attacker session hitting many cards

    while len(txns) < n:
        device_id = f"carder_dev_{c}"
        ip = f"185.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"  # datacenter-style range
        campaign_size = min(25, n - len(txns))
        for i in range(campaign_size):
            t = Transaction(
                account_id=f"stolen_acct_{c}_{i}",
                timestamp=now - random.uniform(0, 3600),  # tight burst window
                amount=round(random.uniform(1, 50), 2),   # small "is this card alive" probes
                channel="online",
                merchant_category=random.choice(["electronics", "general_retail", "subscription", "travel"]),
                account_age_days=random.randint(0, 10),   # freshly compromised / synthetic
                kyc_tier="none",
                avg_ticket_size=0.0,
                account_balance=round(random.uniform(0, 500), 2),
                txn_count_last_1h=random.randint(8, 40),
                txn_count_last_24h=random.randint(15, 80),
                txn_count_last_7d=random.randint(15, 100),
                time_since_last_txn_sec=random.uniform(1, 30),  # rapid-fire
                session_duration_sec=random.uniform(1, 8),
                deviation_from_avg_amount=random.uniform(2, 10),
                device_id=device_id,
                device_known=False,
                ip_address=ip,
                ip_risk_score=round(random.uniform(0.6, 0.95), 3),
                is_vpn_or_proxy=random.choices([True, False], weights=[0.75, 0.25])[0],
                geo_country=random.choice(["IN", "US", "NG", "RU", "VN"]),
                geo_mismatch=random.choices([True, False], weights=[0.6, 0.4])[0],
                merchant_risk_score=round(random.uniform(0.1, 0.5), 3),
                merchant_age_days=random.randint(50, 3000),
                merchant_chargeback_rate=round(random.uniform(0.02, 0.1), 4),
                shared_device_account_count=campaign_size,
                shared_ip_account_count=campaign_size,
                beneficiary_is_new=True,
                auth_method="none",
                liveness_confidence=0.0,
                is_fraud=1,
                attack_type="card_abuse",
            )
            txns.append(t)
        c += 1
        if len(txns) >= n:
            break

    return txns[:n]
