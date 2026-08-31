"""
adversarial_ml_sim.py
Simulates an attacker who has learned (via probing, or via a leaked model)
roughly where the current detector's decision boundary sits, and crafts
"low-and-slow" transactions engineered to sit just under it. This is the
attack that makes the closed loop meaningful: it doesn't just generate random
fraud, it generates fraud SHAPED to evade whatever detector currently exists.

If a trained model + feature pipeline is supplied, this module performs a
simple local search: generate candidate fraud transactions, score them, and
keep nudging features in the direction that lowers the fraud score, subject
to bounds that keep the transaction still "useful" to the attacker (non-zero
amount, plausible velocity). If no model is supplied, falls back to a
generic low-and-slow profile (round-1 baseline before any model exists).
"""

import random
import time
import copy
from generate.data_schema import Transaction

def _base_candidate(now, i):
    amount = round(random.uniform(80, 400), 2)
    return Transaction(
        account_id=f"adv_acct_{i}",
        timestamp=now - random.uniform(0, 12 * 3600),
        amount=amount,
        channel="online",
        merchant_category=random.choice(["general_retail", "electronics", "travel"]),
        account_age_days=random.randint(60, 400),
        kyc_tier="partial",
        avg_ticket_size=amount * random.uniform(0.9, 1.1),
        account_balance=round(random.uniform(500, 3000), 2),
        txn_count_last_1h=random.choices([0, 1], weights=[0.7, 0.3])[0],
        txn_count_last_24h=random.randint(1, 3),
        txn_count_last_7d=random.randint(2, 8),
        time_since_last_txn_sec=random.uniform(3000, 20000),  # deliberately spaced out — "slow"
        session_duration_sec=random.uniform(60, 200),
        deviation_from_avg_amount=round(random.uniform(0.0, 0.2), 3),
        device_id=f"adv_dev_{i}",
        device_known=random.choices([True, False], weights=[0.5, 0.5])[0],
        ip_address=f"49.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        ip_risk_score=round(random.uniform(0.05, 0.25), 3),   # deliberately low — "under the radar"
        is_vpn_or_proxy=False,
        geo_country="IN",
        geo_mismatch=False,
        merchant_risk_score=round(random.uniform(0.05, 0.2), 3),
        merchant_age_days=random.randint(500, 3000),
        merchant_chargeback_rate=round(random.uniform(0, 0.02), 4),
        shared_device_account_count=random.randint(1, 2),
        shared_ip_account_count=random.randint(1, 2),
        beneficiary_is_new=random.choices([True, False], weights=[0.5, 0.5])[0],
        auth_method=random.choices(["password", "otp"], weights=[0.5, 0.5])[0],
        liveness_confidence=round(random.uniform(0.7, 0.95), 3),
        is_fraud=1,
        attack_type="adversarial_ml",
    )


def generate_adversarial_ml_attacks(n: int, ensemble=None, seed: int = None, search_steps: int = 6) -> list:
    """
    ensemble: an optional trained defend.ensemble.FraudEnsemble instance.
              When provided, candidates are locally optimized to minimize the
              ensemble's predicted fraud score (bounded perturbation search).

    PERFORMANCE NOTE: the local search is BATCHED — all n candidates are
    perturbed and scored together in one ensemble.score() call per search
    step, rather than one score_transaction() call per candidate per step.
    Each score() call has fixed overhead (feature encoding, running the
    Isolation Forest's internal parallel worker pool, etc.) that dominates
    when transactions are scored one at a time. Batching turns
    n * search_steps individual scoring calls into just search_steps + 1
    calls total, which is what actually made this simulator slow — the
    Isolation Forest's parallelism is worthwhile for scoring hundreds of
    rows at once but is pure overhead when repeated hundreds of times for
    single rows.
    """
    if seed is not None:
        random.seed(seed)

    now = time.time()
    candidates = [_base_candidate(now, i) for i in range(n)]

    if ensemble is None:
        return candidates

    best = candidates
    best_scores = list(ensemble.score(best)["final_score"])

    for _ in range(search_steps):
        perturbed = []
        for c in best:
            p = copy.deepcopy(c)
            # Nudge the features the model most likely leans on
            p.txn_count_last_1h = max(0, p.txn_count_last_1h + random.choice([-1, 0]))
            p.time_since_last_txn_sec *= random.uniform(1.0, 1.4)   # space it out further
            p.ip_risk_score = max(0.0, p.ip_risk_score * random.uniform(0.5, 0.95))
            p.deviation_from_avg_amount = max(0.0, p.deviation_from_avg_amount * random.uniform(0.5, 0.9))
            p.amount = max(10, p.amount * random.uniform(0.85, 1.0))
            perturbed.append(p)

        # ONE batched scoring call for all n candidates this step, instead of n calls.
        perturbed_scores = list(ensemble.score(perturbed)["final_score"])

        for i in range(n):
            if perturbed_scores[i] < best_scores[i]:
                best[i] = perturbed[i]
                best_scores[i] = perturbed_scores[i]

    return best
