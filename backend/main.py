# fraud-defense-lab/backend/main.py
import os
import re
import time
import random

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.metrics import roc_curve, precision_score, recall_score, f1_score

from generate.legit_transaction_sim import generate_legit_transactions
from generate.simulators.card_abuse_sim import generate_card_abuse_attacks
from generate.simulators.ato_sim import generate_ato_attacks
from generate.simulators.bot_automation_sim import generate_bot_automation_attacks
from generate.simulators.adversarial_ml_sim import generate_adversarial_ml_attacks

from defend.ensemble import FraudEnsemble

from observability import error_detector, event_logger
import evaluate as eval_module
from loop_runner import run_closed_loop, build_mixed_batch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAXONOMY_PATH = os.path.join(BASE_DIR, "identify", "attack_taxonomy.md")

app = FastAPI(title="AI Defense Lab API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ---------------------------------------------------------------------------
# STATE — one FraudEnsemble instance shared by every endpoint. It starts as a
# generic bootstrap model (so Attack Lab/Live Feed work before you ever click
# "run closed loop"), and gets REPLACED by the actual closed-loop-trained
# model the moment /api/run-loop completes. model_meta always tells you which
# one you're looking at — nothing here is hidden or implied to be unified
# when it isn't.
# ---------------------------------------------------------------------------
STATE = {
    "ensemble": None,
    "txn_cache": {},
    "model_meta": {"origin": "none", "trained_through_round": None, "in_sync_with_artifacts": False},
}

DIFFICULTY_PARAMS = {
    "normal": {"aggression": 1.0, "search_steps": 6},
    "advanced": {"aggression": 0.5, "search_steps": 10},
    "extreme": {"aggression": 0.2, "search_steps": 16},
}

# Only these two simulators actually accept a tunable "harder" parameter.
DIFFICULTY_SUPPORTED = {"bot_automation", "adversarial_ml"}

ATTACK_SIMULATORS = {
    "card_abuse": "Card Abuse",
    "account_takeover": "Account Takeover",
    "bot_automation": "Bot / Automation",
    "adversarial_ml": "Adversarial ML",
}


def ensure_ensemble() -> FraudEnsemble:
    """Only trains a bootstrap model if NOTHING exists yet (fresh process, or
    before /api/run-loop has ever been called). If a closed-loop model is
    already installed in STATE, it is reused as-is."""
    if STATE["ensemble"] is None:
        batch = build_mixed_batch(n_legit=300, n_per_attack=50, ensemble=None, seed=7)
        ens = FraudEnsemble()
        ens.fit(batch)
        STATE["ensemble"] = ens
        STATE["model_meta"] = {
            "origin": "live_demo_bootstrap",
            "trained_through_round": None,
            "in_sync_with_artifacts": False,
        }
    return STATE["ensemble"]


def generate_attack_batch(attack_type: str, n: int, difficulty: str, ensemble, seed: int):
    params = DIFFICULTY_PARAMS.get(difficulty, DIFFICULTY_PARAMS["normal"])
    if attack_type == "card_abuse":
        return generate_card_abuse_attacks(n, seed=seed)
    if attack_type == "account_takeover":
        return generate_ato_attacks(n, seed=seed)
    if attack_type == "bot_automation":
        return generate_bot_automation_attacks(n, aggression=params["aggression"], seed=seed)
    if attack_type == "adversarial_ml":
        return generate_adversarial_ml_attacks(n, ensemble=ensemble, seed=seed, search_steps=params["search_steps"])
    raise HTTPException(400, f"Unknown attack_type '{attack_type}'")


def cache_transactions(txns, scored_df: pd.DataFrame):
    rows = scored_df.to_dict(orient="records")
    row_by_id = {r["txn_id"]: r for r in rows}
    for t in txns:
        STATE["txn_cache"][t.txn_id] = {"txn": t, "row": row_by_id.get(t.txn_id, {})}


def txn_to_public_dict(t) -> dict:
    return {
        "txn_id": t.txn_id, "account_id": t.account_id, "timestamp": t.timestamp,
        "amount": t.amount, "channel": t.channel, "merchant_category": t.merchant_category,
        "device_known": t.device_known, "ip_risk_score": t.ip_risk_score,
        "is_vpn_or_proxy": t.is_vpn_or_proxy, "geo_mismatch": t.geo_mismatch,
        "deviation_from_avg_amount": t.deviation_from_avg_amount,
        "beneficiary_is_new": t.beneficiary_is_new, "attack_type": t.attack_type,
    }


def parse_taxonomy():
    with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    lines = text.splitlines()
    categories, current = [], None
    cat_re = re.compile(r"^## ([A-Z])\.\s+(.+?)\s*$")
    item_re = re.compile(r"^(\d+)\.\s+(.+?)\s*$")

    for line in lines:
        if line.startswith("## Why"):
            break
        m_cat = cat_re.match(line)
        if m_cat:
            letter, title = m_cat.groups()
            simulated = "[SIMULATED]" in title
            title = re.sub(r"\*\*\[SIMULATED\]\*\*", "", title).strip()
            current = {"id": letter, "title": title, "simulated_category": simulated, "attacks": []}
            categories.append(current)
            continue
        m_item = item_re.match(line)
        if m_item and current is not None:
            num, body = m_item.groups()
            sim_file_match = re.search(r"`([a-zA-Z0-9_]+\.py)`", body)
            clean_body = re.sub(r"\s*—\s*`[a-zA-Z0-9_]+\.py`", "", body)
            current["attacks"].append({
                "num": int(num), "text": clean_body,
                "active_simulation": bool(sim_file_match),
                "sim_file": sim_file_match.group(1) if sim_file_match else None,
            })

    total_attacks = sum(len(c["attacks"]) for c in categories)
    return {"categories": categories, "total_attacks": total_attacks, "total_categories": len(categories)}


def parse_missed(what_happened: str):
    m = re.match(r"^(\d+) of (\d+)", what_happened or "")
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


def severity_from_alert(alert: dict) -> str:
    missed, total = parse_missed(alert.get("what_happened", ""))
    if missed is None:
        return "MEDIUM"
    if missed == 0:
        return "LOW"
    frac = missed / max(total, 1)
    return "HIGH" if (missed >= 10 or frac >= 0.15) else "MEDIUM"


def split_why_text(why: str):
    """
    root_cause_analyzer.py's explanation string is built from up to two parts:
      1) the layer's DESIGN-ASSUMPTION features (error_localizer.py's static
         mapping) plus the REAL statistical separation gap for this round's
         missed transactions.
      2) an optional note about this round's trained model's REAL global
         feature importance for those same features.
    This just labels/splits that existing text for display — it does not
    recompute or invent anything.
    """
    marker = "The model also assigns low learned importance to"
    if not why:
        return None, None
    if marker in why:
        idx = why.index(marker)
        return why[:idx].strip(), why[idx:].strip()
    return why.strip(), None


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/overview")
def overview():
    tax = parse_taxonomy()
    history = event_logger.load_metrics_history()
    alerts = event_logger.load_alerts()
    latest = history[-1] if history else None
    latest_alert = alerts[-1] if alerts else None

    return {
        "attacks_identified": tax["total_attacks"],
        "categories": tax["total_categories"],
        "simulated_categories": sum(1 for c in tax["categories"] if c["simulated_category"]),
        "latest_round": latest["round"] if latest else None,
        "total_rounds": len(history),
        "detection_recall": latest["overall"]["recall"] if latest else None,
        "f1_score": latest["overall"]["f1"] if latest else None,
        "precision": latest["overall"]["precision"] if latest else None,
        "roc_auc": latest["overall"]["roc_auc"] if latest else None,
        "false_positive_rate": latest["overall"]["false_positive_rate"] if latest else None,
        "defense_failures": len(alerts),
        "latest_failure": latest_alert,
        "stages": {
            "identify": {"complete": tax["total_attacks"] > 0, "detail": f"{tax['total_attacks']} attacks, {tax['total_categories']} categories"},
            "generate": {"complete": True, "detail": "5 simulators active"},
            "defend": {"complete": latest is not None, "detail": f"F1 {latest['overall']['f1']*100:.2f}%" if latest else "Not yet run"},
            "observe": {"complete": len(alerts) > 0, "detail": f"{len(alerts)} alerts logged"},
            "remediate": {"complete": len(alerts) > 0, "detail": "Harder variants generated" if alerts else "—"},
            "retrain": {"complete": len(history) > 1, "detail": f"Round {latest['round']}" if latest else "—"},
        },
    }


@app.get("/api/taxonomy")
def taxonomy():
    return parse_taxonomy()


@app.get("/api/simulate/options")
def simulate_options():
    return {
        "attack_types": [
            {"id": k, "label": v, "difficulty_supported": k in DIFFICULTY_SUPPORTED}
            for k, v in ATTACK_SIMULATORS.items()
        ],
        "difficulties": ["normal", "advanced", "extreme"],
    }


class SimulateRequest(BaseModel):
    attack_type: str
    n: int = 60
    difficulty: str = "normal"


@app.post("/api/simulate")
def simulate(req: SimulateRequest):
    if req.attack_type not in ATTACK_SIMULATORS:
        raise HTTPException(400, f"attack_type must be one of {list(ATTACK_SIMULATORS)}")

    ensemble = ensure_ensemble()
    seed = random.randint(0, 1_000_000)
    difficulty_applied = req.difficulty if req.attack_type in DIFFICULTY_SUPPORTED else None

    attacks = generate_attack_batch(req.attack_type, req.n, req.difficulty, ensemble, seed)
    legit_sample = generate_legit_transactions(min(req.n, 150), seed=seed + 1)

    scored_attacks = ensemble.score(attacks)
    scored_legit = ensemble.score(legit_sample)
    combined = pd.concat([scored_attacks, scored_legit], ignore_index=True)
    cache_transactions(attacks + legit_sample, combined)

    rows = []
    for t in attacks:
        r = scored_attacks[scored_attacks["txn_id"] == t.txn_id].iloc[0]
        rows.append({
            "txn_id": t.txn_id, "amount": t.amount, "attack_type": t.attack_type,
            "final_score": round(float(r["final_score"]), 4), "detected": bool(r["predicted_fraud"]),
        })

    overall = eval_module.overall_metrics(combined)
    detected = sum(1 for r in rows if r["detected"])

    return {
        "attack_label": ATTACK_SIMULATORS[req.attack_type],
        "difficulty_requested": req.difficulty,
        "difficulty_applied": difficulty_applied,  # None means the simulator ignored it — surfaced, not hidden
        "generated": len(attacks), "processed": len(attacks),
        "detected": detected, "missed": len(attacks) - detected,
        "detection_recall": round(detected / max(len(attacks), 1), 4),
        "precision": overall["precision"],
        "false_positive_rate": overall["false_positive_rate"],
        "transactions": rows,
        "defense_failure": detected < len(attacks),
        "model_source": STATE["model_meta"],
    }


@app.get("/api/live-feed")
def live_feed(n: int = 40):
    ensemble = ensure_ensemble()
    seed = random.randint(0, 1_000_000)
    per_attack = max(1, n // 5)
    batch = build_mixed_batch(n_legit=n, n_per_attack=per_attack, ensemble=ensemble, seed=seed)
    scored = ensemble.score(batch)
    cache_transactions(batch, scored)

    by_id = {t.txn_id: t for t in batch}
    rows = []
    for r in scored.to_dict(orient="records"):
        t = by_id[r["txn_id"]]
        if r["predicted_fraud"] == 1:
            decision = "FRAUD"
        elif r["final_score"] >= 0.3:
            decision = "REVIEW"
        else:
            decision = "LEGIT"
        rows.append({
            "txn_id": t.txn_id, "timestamp": t.timestamp, "amount": t.amount, "attack_type": t.attack_type,
            "device_risk": 0 if t.device_known else 1, "ip_risk": round(t.ip_risk_score, 3),
            "behavior_deviation": round(t.deviation_from_avg_amount, 3),
            "fraud_probability": round(float(r["fraud_probability"]), 4),
            "final_score": round(float(r["final_score"]), 4), "decision": decision,
        })
    rows.sort(key=lambda r: r["timestamp"], reverse=True)

    return {
        "total": len(rows),
        "fraud": sum(1 for r in rows if r["decision"] == "FRAUD"),
        "review": sum(1 for r in rows if r["decision"] == "REVIEW"),
        "legit": sum(1 for r in rows if r["decision"] == "LEGIT"),
        "transactions": rows,
        "model_source": STATE["model_meta"],
    }


@app.get("/api/transaction/{txn_id}")
def transaction_detail(txn_id: str):
    cached = STATE["txn_cache"].get(txn_id)
    if not cached:
        raise HTTPException(404, "Transaction not found in current session cache (cache is in-memory only)")
    t, row = cached["txn"], cached["row"]
    ensemble = ensure_ensemble()
    fi = ensemble.feature_importance(top_n=6)

    signals = []
    if not t.device_known: signals.append("Device anomaly")
    if t.ip_risk_score >= 0.3: signals.append("IP risk")
    if abs(t.deviation_from_avg_amount) >= 0.5: signals.append("Behavioral deviation")
    if t.beneficiary_is_new: signals.append("New beneficiary")
    if t.geo_mismatch: signals.append("Geo mismatch")

    return {
        "transaction": txn_to_public_dict(t),
        "fraud_probability": round(float(row.get("fraud_probability", 0)), 4),
        "anomaly_score": round(float(row.get("anomaly_score", 0)), 4),
        "final_score": round(float(row.get("final_score", 0)), 4),
        "predicted_fraud": bool(row.get("predicted_fraud", 0)),
        "predicted_attack_type": row.get("predicted_attack_type"),
        "risk_signals": signals,
        "top_features": [{"feature": k, "importance": round(float(v), 4)} for k, v in fi.items()],
        "note": "top_features is this session's live model's GLOBAL feature importance, shown alongside this transaction's own field values above — not a per-transaction SHAP value.",
    }


@app.get("/api/analytics")
def analytics():
    ensemble = ensure_ensemble()
    seed = random.randint(0, 1_000_000)
    batch = build_mixed_batch(n_legit=300, n_per_attack=50, ensemble=ensemble, seed=seed)
    scored = ensemble.score(batch)

    overall = eval_module.overall_metrics(scored)
    confusion = eval_module.confusion(scored)
    per_attack = eval_module.per_attack_type_report(scored)
    recall_by_type = error_detector.recall_by_attack_type(scored)

    fpr, tpr, _ = roc_curve(scored["true_is_fraud"], scored["final_score"])
    idx = np.linspace(0, len(fpr) - 1, min(30, len(fpr))).astype(int)
    roc_points = [{"fpr": round(float(fpr[i]), 4), "tpr": round(float(tpr[i]), 4)} for i in idx]

    def sub_metrics(pred_col):
        y_true = scored["true_is_fraud"]
        y_pred = (scored[pred_col] >= 0.5).astype(int)
        return {
            "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
            "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
            "f1": round(f1_score(y_true, y_pred, zero_division=0), 4),
        }

    return {
        "overall": overall,
        "confusion_matrix": confusion.to_dict(),
        "per_attack_type": per_attack.to_dict(orient="records"),
        "recall_by_attack_type": recall_by_type.to_dict(orient="records"),
        "roc_curve": roc_points,
        "model_comparison": {
            "xgboost": sub_metrics("fraud_probability"),
            "isolation_forest": sub_metrics("anomaly_score"),
            "ensemble": {"precision": overall["precision"], "recall": overall["recall"], "f1": overall["f1"]},
        },
        "model_source": STATE["model_meta"],
        "note": "Computed live against a fresh evaluation batch using the model_source below. If in_sync_with_artifacts is false, these numbers will not exactly match the Overview page (which reads the saved closed-loop artifacts) — run the closed loop to sync them.",
    }


@app.get("/api/closed-loop")
def closed_loop():
    history = event_logger.load_metrics_history()
    alerts = event_logger.load_alerts()
    if not history:
        return {"rounds": [], "overall_recall_trend": [], "improvement_pp": None,
                 "current_limitation": None, "plateau_detected": False, "next_action": None,
                 "model_source": STATE["model_meta"]}

    rounds = []
    for h in history:
        round_alert = next((a for a in alerts if a.get("round_num") == h["round"]), None)
        missed, total = parse_missed(round_alert["what_happened"]) if round_alert else (None, None)
        rounds.append({
            "round": h["round"], "overall": h["overall"], "recall_by_attack_type": h["recall_by_attack_type"],
            "alert": round_alert, "alert_missed_count": missed, "alert_total_count": total,
        })

    trend = [{"round": h["round"], "recall": h["overall"]["recall"]} for h in history]
    improvement_pp = round((trend[-1]["recall"] - trend[0]["recall"]) * 100, 1) if len(trend) > 1 else 0.0

    last_alert = alerts[-1] if alerts else None
    current_limitation = None
    if last_alert:
        missed, _ = parse_missed(last_alert.get("what_happened", ""))
        if missed:
            current_limitation = last_alert["what_happened"]

    plateau_detected, next_action = False, None
    if len(history) >= 2 and last_alert:
        missed, _ = parse_missed(last_alert.get("what_happened", ""))
        recall_delta = abs(trend[-1]["recall"] - trend[-2]["recall"])
        if missed == 0 and recall_delta < 0.01:
            plateau_detected = True
            next_action = (
                "Performance plateau detected — the most recent round bypassed nothing and overall "
                "recall is stable round-over-round. Further automatic retraining on this same data "
                "distribution is unlikely to help; recommended next step is expanding the feature set "
                "or routing the flagged category to human review rather than looping again."
            )

    return {
        "rounds": rounds, "overall_recall_trend": trend, "improvement_pp": improvement_pp,
        "current_limitation": current_limitation, "plateau_detected": plateau_detected,
        "next_action": next_action, "model_source": STATE["model_meta"],
    }


@app.get("/api/alerts")
def alerts():
    alerts_list = event_logger.load_alerts()
    out = []
    for a in alerts_list:
        missed, total = parse_missed(a.get("what_happened", ""))
        layer_assumption, global_note = split_why_text(a.get("why", ""))
        display_status = a["status"]
        if missed == 0:
            display_status = "🟢 Monitoring — no bypass this round (still the relatively weakest category)"
        out.append({
            **a,
            "severity": severity_from_alert(a),
            "missed_count": missed,
            "total_count": total,
            "why_layer_assumption": layer_assumption,   # design-assumption + real local statistical gap
            "why_global_importance_note": global_note,   # real global feature importance from that round, if flagged
            "display_status": display_status,
        })
    return {"alerts": list(reversed(out))}


class RunLoopRequest(BaseModel):
    n_rounds: int = 3      # matches run_demo.py's default; avoids silently shrinking existing history
    n_legit: int = 250
    n_per_attack: int = 40


@app.post("/api/run-loop")
def run_loop(req: RunLoopRequest):
    rounds_before = len(event_logger.load_metrics_history())
    ensemble, history = run_closed_loop(
        n_rounds=req.n_rounds, n_legit=req.n_legit, n_per_attack=req.n_per_attack, verbose=False
    )
    # Install the ACTUAL trained model from this run — this is the fix for the
    # "two unrelated defense systems" problem: Attack Lab / Live Feed / Model
    # Insights / Analytics now all read this same instance until the process
    # restarts or /api/run-loop is called again.
    STATE["ensemble"] = ensemble
    STATE["model_meta"] = {
        "origin": "closed_loop",
        "trained_through_round": history[-1]["round"] if history else None,
        "in_sync_with_artifacts": True,
    }
    STATE["txn_cache"] = {}  # old cached rows were scored by the previous model instance

    return {
        "rounds_run": len(history),
        "rounds_before_this_call": rounds_before,
        "history_replaced": True,  # loop_runner.run_closed_loop() always rewrites both JSON files from round 1 — pre-existing behavior, surfaced here rather than hidden
        "final_recall": history[-1]["overall"]["recall"] if history else None,
        "final_f1": history[-1]["overall"]["f1"] if history else None,
        "model_source": STATE["model_meta"],
    }


@app.get("/api/observability/logs")
def observability_logs():
    history = event_logger.load_metrics_history()
    alerts_list = event_logger.load_alerts()
    events = []
    pipeline = ["ERROR_DETECTOR", "ERROR_LOCALIZER", "ROOT_CAUSE_ANALYZER", "REMEDIATION_ENGINE", "ALERT_MANAGER", "EVENT_LOGGER"]

    for h in history:
        events.append({"round": h["round"], "event": "METRICS_LOGGED", "component": "Event Logger",
                        "severity": "INFO", "status": "Complete"})
        round_alert = next((a for a in alerts_list if a.get("round_num") == h["round"]), None)
        if round_alert:
            sev = severity_from_alert(round_alert)
            for step in pipeline:
                events.append({
                    "round": h["round"], "event": step, "component": step.replace("_", " ").title(),
                    "severity": "HIGH" if sev == "HIGH" and step in ("ERROR_DETECTOR", "ALERT_MANAGER") else "INFO",
                    "status": "Complete",
                })
    return {"events": events, "note": "Ordered by round number only — event_logger.py does not persist per-event clock timestamps, so none are shown."}


@app.get("/api/system-health")
def system_health():
    history = event_logger.load_metrics_history()
    metrics_path = event_logger.METRICS_PATH
    last_eval = None
    if os.path.exists(metrics_path):
        last_eval = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(metrics_path)))

    return {
        "backend": "online",
        "ml_engine": "online" if STATE["ensemble"] is not None else "idle (trains on first request)",
        "attack_simulator": "online",
        "observability": "online",
        "artifacts_available": os.path.exists(metrics_path),
        "current_round": history[-1]["round"] if history else None,
        "total_rounds_logged": len(history),
        "last_evaluation": last_eval,
        "model_source": STATE["model_meta"],
        "model_persistence": "in-memory only — a backend restart clears STATE and the next request retrains a fresh bootstrap model (no model file is saved to disk in the current codebase).",
    }


@app.get("/api/model-insights")
def model_insights():
    ensemble = ensure_ensemble()
    fi = ensemble.feature_importance(top_n=15)
    return {
        "feature_importance": [{"feature": k, "importance": round(float(v), 4)} for k, v in fi.items()],
        "model_source": STATE["model_meta"],
    }