"""
poisoning_sim.py
Simulates feedback-loop / training-data poisoning: an attacker doesn't attack
a transaction, they attack the DEFENSE by injecting mislabeled examples into
what becomes the model's training set (e.g. via a compromised chargeback/
dispute-resolution feedback pipeline that mislabels fraud as legitimate, or
legitimate as fraud to raise false positives and erode trust in the system).

This module doesn't produce a transaction "attack type" you detect at score
time — it produces a *label-corrupted training set* used by loop_runner to
demonstrate degraded model performance and its detection via observability.
"""

import random
from generate.legit_transaction_sim import generate_legit_transactions


def poison_labels(transactions: list, poison_rate: float = 0.05, mode: str = "flip_fraud_to_legit", seed: int = None) -> list:
    """
    mode:
      'flip_fraud_to_legit' -> mislabels a fraction of real fraud as legit
                                 (teaches the model to ignore real fraud signatures)
      'flip_legit_to_fraud' -> mislabels a fraction of real legit txns as fraud
                                 (raises false positives, erodes trust / usability)
    """
    if seed is not None:
        random.seed(seed)

    poisoned = list(transactions)
    if mode == "flip_fraud_to_legit":
        candidates = [t for t in poisoned if t.is_fraud == 1]
    else:
        candidates = [t for t in poisoned if t.is_fraud == 0]

    n_to_poison = int(len(candidates) * poison_rate)
    targets = random.sample(candidates, min(n_to_poison, len(candidates)))

    poisoned_ids = set()
    for t in targets:
        if mode == "flip_fraud_to_legit":
            t.is_fraud = 0
            t.attack_type = "legit"  # ground truth in eval set stays separate; this corrupts TRAINING copy only
        else:
            t.is_fraud = 1
            t.attack_type = "poisoned_false_positive"
        poisoned_ids.add(t.txn_id)

    return poisoned, poisoned_ids


def generate_poisoning_scenario(n_legit: int = 200, n_fraud_to_mix: int = 20, poison_rate: float = 0.15, seed: int = None):
    """
    Convenience wrapper: builds a small mixed batch and poisons a slice of it,
    returning (poisoned_training_copy, poisoned_txn_ids) for loop_runner to
    inject into a training set and observability to later detect.
    """
    legit = generate_legit_transactions(n_legit, seed=seed)
    return poison_labels(legit, poison_rate=poison_rate, mode="flip_legit_to_fraud", seed=seed)
