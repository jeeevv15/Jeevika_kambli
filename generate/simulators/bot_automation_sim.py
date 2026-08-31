"""
bot_automation_sim.py
Simulates AI-adaptive payment bots: a coordinated network of accounts running
low-value, distributed transactions that dynamically slow down / diversify
when they detect friction (declines, flags). `aggression` controls how "loud"
the bot is — at low aggression, the bot doesn't just slow down, it also
spreads across MORE distinct devices/IPs, reduces its shared-fingerprint
footprint, and shifts its spending amounts toward normal customer ranges,
which is what makes a genuinely adaptive bot harder to catch.
Fidelity signature: many accounts, shared infra, individually low velocity,
high behavioral similarity across accounts — with fan-out that shrinks the
"shared device/IP" tell as aggression drops.
"""

import random
import time
from generate.data_schema import Transaction

def generate_bot_automation_attacks(n: int, aggression: float = 1.0, seed: int = None) -> list:
    """
    aggression: 1.0 = loud/obvious bot behavior (round 1 baseline).
                Lower values (e.g. 0.2) = the bot has adapted: slower
                velocity, more device/IP diversity, and spending amounts
                closer to normal customer behavior.
    """
    if seed is not None:
        random.seed(seed)

    aggression = max(0.05, min(1.0, aggression))
    txns = []
    now = time.time()
    n_bots = max(1, n // 15)
    shared_ip_base = f"104.{random.randint(0,255)}.{random.randint(0,255)}"

    device_pool_size = max(5, int(5 + (1 - aggression) * 20))

    for b in range(n_bots):
        ip = f"{shared_ip_base}.{random.randint(1, 254)}"
        botnet_size = min(15, n - len(txns))

        effective_shared_count = max(1, int(botnet_size * (0.15 + 0.85 * (aggression ** 1.3))))

        for i in range(botnet_size):
            device_id = f"botfarm_dev_{random.randint(0, device_pool_size - 1)}"

            velocity_1h = max(0, int(random.gauss(6 * aggression, 1)))
            low_aggression_amount = random.uniform(150, 450)   # blends with legit norms
            high_aggression_amount = random.uniform(20, 40)    # obviously bot-typical
            amount = round(high_aggression_amount * aggression + low_aggression_amount * (1 - aggression), 2)
            time_gap = random.uniform(30, 300) / max(aggression, 0.1)

            device_known_prob = 0.15 + 0.75 * (1 - aggression)

            t = Transaction(
                account_id=f"bot_acct_{b}_{i}",
                timestamp=now - random.uniform(0, 6 * 3600),
                amount=amount,
                channel="online",
                merchant_category=random.choice(["subscription", "general_retail", "entertainment"]),
                account_age_days=random.randint(1, 45) if aggression > 0.5 else random.randint(10, 120),
                kyc_tier=random.choices(["none", "partial"], weights=[0.7, 0.3])[0],
                avg_ticket_size=amount * random.uniform(0.8, 1.0),
                account_balance=round(random.uniform(50, 300), 2),
                txn_count_last_1h=velocity_1h,
                txn_count_last_24h=max(velocity_1h, int(random.gauss(15 * aggression, 3))),
                txn_count_last_7d=int(random.gauss(40 * aggression, 8)),
                time_since_last_txn_sec=time_gap,
                session_duration_sec=random.uniform(2, 15),
                deviation_from_avg_amount=round(random.uniform(0.0, 0.3) * aggression, 3),
                device_id=device_id,
                device_known=random.choices([True, False], weights=[device_known_prob, 1 - device_known_prob])[0],
                ip_address=ip,
                ip_risk_score=round(0.1 + 0.7 * (aggression ** 1.2), 3),
                is_vpn_or_proxy=random.choices([True, False], weights=[0.5 + 0.3*aggression, 0.5 - 0.3*aggression])[0],
                geo_country="IN",
                geo_mismatch=False,
                merchant_risk_score=round(random.uniform(0.1, 0.35), 3),
                merchant_age_days=random.randint(100, 2000),
                merchant_chargeback_rate=round(random.uniform(0.01, 0.06), 4),
                shared_device_account_count=effective_shared_count,
                shared_ip_account_count=effective_shared_count,
                beneficiary_is_new=random.choices([True, False], weights=[0.4, 0.6])[0],
                auth_method=random.choices(["password", "none"], weights=[0.6, 0.4])[0],
                liveness_confidence=round(random.uniform(0.5, 0.9), 3),
                is_fraud=1,
                attack_type="bot_automation",
            )
            txns.append(t)
        if len(txns) >= n:
            break

    return txns[:n]