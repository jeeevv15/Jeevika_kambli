"""
ato_sim.py
Simulates account takeover with AI behavioral mimicry: the attacker has
compromised a real, established account (via credential stuffing / SIM swap)
and uses AI to imitate the victim's typical session shape, but the payout
destination and device are new. Fidelity signature: LOOKS like a normal
established account on paper (age, avg ticket) but device/beneficiary/auth
context is freshly discontinuous from history.
"""

import random
import time
from generate.data_schema import Transaction

def generate_ato_attacks(n: int, seed: int = None) -> list:
    if seed is not None:
        random.seed(seed)

    txns = []
    now = time.time()

    for i in range(n):
        avg_ticket = round(random.lognormvariate(mu=6.0, sigma=0.8), 2)
        account_age = random.randint(180, 2000)  # genuine, established account
        mimicry_quality = random.uniform(0.3, 0.95)  # how good is the attacker's behavioral mimicry

        # Higher mimicry quality -> amount/session closer to normal, but device/beneficiary still betray it
        amount = round(avg_ticket * random.uniform(1.0, 1.0 + (1 - mimicry_quality) * 4), 2)
        session_duration = random.uniform(20, 90) * mimicry_quality + random.uniform(5, 20)

        t = Transaction(
            account_id=f"ato_acct_{i}",
            timestamp=now - random.uniform(0, 7 * 24 * 3600),
            amount=amount,
            channel=random.choices(["online", "app"], weights=[0.7, 0.3])[0],
            merchant_category=random.choice(["electronics", "travel", "general_retail"]),
            account_age_days=account_age,
            kyc_tier="full",
            avg_ticket_size=avg_ticket,
            account_balance=round(avg_ticket * random.uniform(5, 40), 2),
            txn_count_last_1h=random.randint(1, 3),
            txn_count_last_24h=random.randint(1, 5),
            txn_count_last_7d=random.randint(2, 10),
            time_since_last_txn_sec=random.uniform(600, 5000),
            session_duration_sec=session_duration,
            deviation_from_avg_amount=(amount - avg_ticket) / max(avg_ticket, 1),
            device_id=f"new_dev_{i}",          # KEY tell: never seen on this account before
            device_known=False,
            ip_address=f"91.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
            ip_risk_score=round(random.uniform(0.3, 0.7), 3),
            is_vpn_or_proxy=random.choices([True, False], weights=[0.4, 0.6])[0],
            geo_country=random.choice(["IN", "AE", "SG", "GB"]),
            geo_mismatch=random.choices([True, False], weights=[0.55, 0.45])[0],
            merchant_risk_score=round(random.uniform(0.05, 0.3), 3),
            merchant_age_days=random.randint(500, 4000),
            merchant_chargeback_rate=round(random.uniform(0, 0.03), 4),
            shared_device_account_count=random.randint(1, 3),
            shared_ip_account_count=random.randint(1, 4),
            beneficiary_is_new=True,           # KEY tell: payout destination just changed
            auth_method=random.choices(["otp", "password"], weights=[0.6, 0.4])[0],
            liveness_confidence=round(random.uniform(0.4, 0.85), 3),  # mimicked, not perfect
            is_fraud=1,
            attack_type="account_takeover",
        )
        txns.append(t)

    return txns
