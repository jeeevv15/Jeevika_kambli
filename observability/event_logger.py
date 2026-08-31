"""
event_logger.py
Persists structured JSON for every round of the closed loop — metrics history
(recall-by-attack-type over time) and alert cards — so the Streamlit dashboard
can read them without needing to re-run the loop live.

Metrics are keyed by round number and DEDUPED on write: if a round gets
logged twice (e.g. from an accidental double-trigger of the closed loop),
the later write replaces the earlier one instead of creating a duplicate
entry with conflicting numbers.
"""

import json
import os

ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "artifacts")
METRICS_PATH = os.path.join(ARTIFACTS_DIR, "metrics_history.json")
ALERTS_PATH = os.path.join(ARTIFACTS_DIR, "alerts.json")


def _ensure_dir():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)


def log_metrics(round_num: int, recall_df, overall_metrics: dict):
    _ensure_dir()
    history = load_metrics_history()

    # Dedupe by round: replace any existing entry for this round number
    # instead of appending a second one.
    history = [h for h in history if h.get("round") != round_num]
    history.append({
        "round": round_num,
        "recall_by_attack_type": recall_df.to_dict(orient="records"),
        "overall": overall_metrics,
    })
    history.sort(key=lambda h: h["round"])

    with open(METRICS_PATH, "w") as f:
        json.dump(history, f, indent=2, default=str)
    return history


def load_metrics_history() -> list:
    if not os.path.exists(METRICS_PATH):
        return []
    with open(METRICS_PATH, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def log_alert(alert_dict: dict):
    _ensure_dir()
    alerts = load_alerts()

    # Dedupe by (round, attack_type): replace rather than duplicate.
    key = (alert_dict.get("round_num"), alert_dict.get("attack_type"))
    alerts = [a for a in alerts if (a.get("round_num"), a.get("attack_type")) != key]
    alerts.append(alert_dict)
    alerts.sort(key=lambda a: (a.get("round_num", 0), a.get("attack_type", "")))

    with open(ALERTS_PATH, "w") as f:
        json.dump(alerts, f, indent=2, default=str)
    return alerts


def load_alerts() -> list:
    if not os.path.exists(ALERTS_PATH):
        return []
    with open(ALERTS_PATH, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def reset_logs():
    _ensure_dir()
    for path in (METRICS_PATH, ALERTS_PATH):
        if os.path.exists(path):
            os.remove(path)