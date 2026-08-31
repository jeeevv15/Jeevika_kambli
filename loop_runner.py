"""
loop_runner.py
Orchestrates the full closed loop:

  Generate -> Detect -> Evaluate -> Localize misses -> Root-cause ->
  Remediate (generate harder variants) -> Retrain -> repeat

Each round trains/re-trains the FraudEnsemble, evaluates it against a fresh
mixed batch (legit + all attack types), diagnoses the weakest attack type via
the observability pipeline, generates harder variants of exactly that attack,
folds them into the next round's training data, and logs everything for the
dashboard.
"""

import random
import pandas as pd

from generate.legit_transaction_sim import generate_legit_transactions
from generate.simulators.card_abuse_sim import generate_card_abuse_attacks
from generate.simulators.ato_sim import generate_ato_attacks
from generate.simulators.bot_automation_sim import generate_bot_automation_attacks
from generate.simulators.adversarial_ml_sim import generate_adversarial_ml_attacks
from generate.simulators.poisoning_sim import generate_poisoning_scenario

from defend.ensemble import FraudEnsemble

from observability import error_detector, error_localizer, root_cause_analyzer, remediation_engine, alert_manager, event_logger

import evaluate as eval_module


def build_mixed_batch(n_legit=400, n_per_attack=60, bot_aggression=1.0, ensemble=None, seed=None):
    legit = generate_legit_transactions(n_legit, seed=seed)
    card = generate_card_abuse_attacks(n_per_attack, seed=seed)
    ato = generate_ato_attacks(n_per_attack, seed=seed)
    bots = generate_bot_automation_attacks(n_per_attack, aggression=bot_aggression, seed=seed)
    adv = generate_adversarial_ml_attacks(n_per_attack, ensemble=ensemble, seed=seed)
    return legit + card + ato + bots + adv


def run_closed_loop(n_rounds: int = 3, n_legit: int = 400, n_per_attack: int = 60, seed: int = 42, verbose: bool = True):
    # NOTE: disk writes are deferred to the very end of this function (see
    # bottom) — nothing is written or reset here. This means an interrupted
    # run (e.g. a double-clicked "Run closed loop" button cancelling a run
    # mid-way in Streamlit) can NEVER wipe or corrupt previously saved good
    # results. Only a fully-completed run ever touches artifacts/.
    random.seed(seed)

    ensemble = None
    bot_aggression = 1.0
    extra_hard_variants = []  # harder examples folded in from the previous round's remediation
    history = []

    for round_num in range(1, n_rounds + 1):
        if verbose:
            print(f"\n{'='*60}\nROUND {round_num}\n{'='*60}")

        # 1. GENERATE — fresh mixed batch, optionally probing the previous round's model
        train_batch = build_mixed_batch(n_legit, n_per_attack, bot_aggression, ensemble=ensemble, seed=seed + round_num)
        train_batch += extra_hard_variants  # fold in remediation output from the prior round

        # Poisoning scenario is injected into training only, to test data-integrity robustness
        poisoned_copy, poisoned_ids = generate_poisoning_scenario(seed=seed + round_num)
        train_batch += poisoned_copy

        # 2. DEFEND — train the ensemble on this round's data
        ensemble = FraudEnsemble()
        ensemble.fit(train_batch)

        # 3. EVALUATE — fresh, unseen evaluation batch (no poisoning here — this is ground truth)
        eval_batch = build_mixed_batch(n_legit, n_per_attack, bot_aggression, ensemble=ensemble, seed=seed + round_num + 1000)
        scored = ensemble.score(eval_batch)

        overall = eval_module.overall_metrics(scored)
        recall_df = error_detector.recall_by_attack_type(scored)

        if verbose:
            print(f"Overall: precision={overall['precision']} recall={overall['recall']} "
                  f"f1={overall['f1']} roc_auc={overall['roc_auc']} fpr={overall['false_positive_rate']}")
            print(recall_df.to_string(index=False))

        

        # 4. LOCALIZE + ROOT-CAUSE the weakest attack type this round
        weakest = error_detector.weakest_attack_type(scored)
        round_alert = None

        missed = error_detector.find_missed_attacks(scored)
        missed_of_type = missed[missed["true_attack_type"] == weakest] if weakest else missed.iloc[0:0]

        # Only build a DEFENSE FAILURE alert if something was actually missed.
        # weakest_attack_type() always returns *an* attack type (whichever has
        # the lowest recall), even when every type is at 100% recall — without
        # this guard, a perfect round still generates a misleading "failure"
        # card claiming 0 of N transactions were missed, which is not a
        # failure at all.
        if weakest and weakest != "legit" and len(missed_of_type) > 0:
            total_of_type = scored[(scored["true_attack_type"] == weakest)]

            missed_txns = [t for t in eval_batch if t.txn_id in set(missed_of_type["txn_id"])]
            legit_txns = [t for t in eval_batch if t.attack_type == "legit"]

            localization = error_localizer.localize(weakest)
            root_cause = root_cause_analyzer.analyze(missed_txns, legit_txns, localization, ensemble=ensemble)
            remediation_text = remediation_engine.recommend(weakest)

            alert = alert_manager.build_alert(
                round_num=round_num,
                attack_type=weakest,
                missed_count=len(missed_of_type),
                total_count=len(total_of_type),
                root_cause=root_cause,
                remediation_text=remediation_text,
            )
            round_alert = alert
           

            if verbose:
                print("\n" + alert.to_card_text())

            # 5. REMEDIATE — generate harder variants of the weakest attack type for next round
            if weakest == "bot_automation":
                bot_aggression = max(0.15, bot_aggression - 0.25)

            extra_hard_variants = remediation_engine.generate_harder_variants(
                weakest, n=n_per_attack, ensemble=ensemble, round_num=round_num, seed=seed + round_num + 1
            )
        else:
            extra_hard_variants = []
            if verbose:
                print("\nNo defense failures this round — every attack type caught at 100% recall.")

        history.append({
            "round": round_num,
            "overall": overall,
            "recall_by_attack_type": recall_df,
            "weakest_attack_type": weakest,
            "alert": round_alert,
            "poisoned_labels_injected": len(poisoned_ids),
        })

    # --- ATOMIC COMMIT: only reached if every round above completed without
    # being interrupted. This replaces old saved results with the new run's
    # results in one step — an interrupted/cancelled run never reaches here,
    # so it can never wipe existing good data.
    event_logger.reset_logs()
    for h in history:
        event_logger.log_metrics(h["round"], h["recall_by_attack_type"], h["overall"])
        if h["alert"] is not None:
            event_logger.log_alert(h["alert"].to_dict())

    return ensemble, history


if __name__ == "__main__":
    run_closed_loop()
