"""
run_demo.py
One command to run the full closed loop end-to-end and produce every artifact
the dashboard and Solution Walkthrough doc need.

Usage:
    python run_demo.py
"""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loop_runner import run_closed_loop


def print_banner(text):
    print("\n" + "#" * 70)
    print(f"# {text}")
    print("#" * 70)


def main():
    print_banner("AI DEFENSE LAB FOR PAYMENT SECURITY — CLOSED LOOP DEMO")
    print("Identify -> Generate -> Defend -> Observe -> Remediate -> Retrain\n")

    ensemble, history = run_closed_loop(n_rounds=3, n_legit=400, n_per_attack=60)

    print_banner("SUMMARY: RECALL BY ATTACK TYPE ACROSS ROUNDS")
    rows = []
    for h in history:
        for r in h["recall_by_attack_type"].to_dict(orient="records"):
            rows.append({"round": h["round"], **r})
    summary_df = pd.DataFrame(rows)
    pivot = summary_df.pivot_table(index="attack_type", columns="round", values="recall")
    print(pivot.round(3).to_string())

    # Counts are computed from `history` (what actually just ran), NOT from a
    # fresh disk read — this guarantees the printed summary can never disagree
    # with the rounds you just watched execute above.
    n_rounds_run = len(history)
    n_alerts_run = sum(1 for h in history if h.get("alert") is not None)

    print_banner("ARTIFACTS WRITTEN")
    print(f"Metrics history -> artifacts/metrics_history.json ({n_rounds_run} rounds)")
    print(f"Defense-failure alerts -> artifacts/alerts.json ({n_alerts_run} alerts)")

    print_banner("NEXT STEP")
    print("Launch the dashboard:")
    print("  1) Backend:  python -m uvicorn backend.main:app --reload")
    print("  2) Frontend: cd frontend && npm install && npm run dev")


if __name__ == "__main__":
    main()