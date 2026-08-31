"""
remediation_engine.py
Given a root-cause diagnosis, decides the concrete remediation action and
executes it: generates additional, harder variants of the specific attack
type that beat the model, so loop_runner can fold them into retraining.
This is what turns the loop from "detect and log" into "detect, diagnose,
and actually get better."
"""

from generate.simulators.card_abuse_sim import generate_card_abuse_attacks
from generate.simulators.ato_sim import generate_ato_attacks
from generate.simulators.bot_automation_sim import generate_bot_automation_attacks
from generate.simulators.adversarial_ml_sim import generate_adversarial_ml_attacks

REMEDIATION_TEXT = {
    "card_abuse": "Generate additional high-velocity / low-amount card-testing variants across a wider merchant spread → retrain classifier → re-evaluate.",
    "account_takeover": "Generate additional ATO variants with higher behavioral-mimicry quality (closer to victim's normal session shape) → retrain → re-evaluate.",
    "bot_automation": "Generate additional low-velocity variants → retrain classifier → re-evaluate.",
    "adversarial_ml": "Run adversarial local-search against the CURRENT model to generate harder boundary-evading variants → retrain → re-evaluate.",
    "poisoned_false_positive": "Flag and quarantine suspected poisoned labels → exclude from next training round → audit feedback pipeline.",
    "unknown_fraud": "Lower anomaly-detector contamination threshold → retrain Isolation Forest on refreshed legit baseline → re-evaluate.",
}


def recommend(attack_type: str) -> str:
    return REMEDIATION_TEXT.get(attack_type, "Generate additional variants of this attack type → retrain → re-evaluate.")


def generate_harder_variants(attack_type: str, n: int, ensemble=None, round_num: int = 1, seed: int = None):
    """
    Executes the remediation: produces n NEW, harder examples of the given
    attack type for the next training round. 'Harder' is operationalized
    per attack family:
      - bot_automation: lower aggression each round (quieter bot)
      - adversarial_ml: run local search directly against the current ensemble
      - card_abuse / account_takeover: simply more volume/diversity (these
        families are volume-driven rather than boundary-driven)
    """
    if attack_type == "bot_automation":
        aggression = max(0.15, 1.0 - 0.25 * round_num)
        return generate_bot_automation_attacks(n, aggression=aggression, seed=seed)

    if attack_type == "adversarial_ml":
        return generate_adversarial_ml_attacks(n, ensemble=ensemble, seed=seed, search_steps=6 + round_num * 2)

    if attack_type == "account_takeover":
        return generate_ato_attacks(n, seed=seed)

    if attack_type == "card_abuse":
        return generate_card_abuse_attacks(n, seed=seed)

    # fallback: generic adversarial-ml style hard negatives
    return generate_adversarial_ml_attacks(n, ensemble=ensemble, seed=seed)
