# AI Defense Lab for Payment Security
### Mastercard Innovation Challenge 2026 — GFF 2026

A closed-loop, red-team/blue-team AI system for payment fraud:

**Identify → Generate → Defend → Observe → Remediate → Retrain**

Instead of building a fraud classifier in isolation, this system attacks itself.
It simulates GenAI-powered fraud at scale, detects it with an ensemble model,
diagnoses *why* any attack slipped through using a dedicated observability
layer, automatically generates harder variants of whatever beat it, and
retrains — closing the loop.

---

## Architecture

```
identify/               Full attack taxonomy (67 attacks, 15 categories) — research layer
generate/                Synthetic transaction + attack simulators
  ├── data_schema.py      Canonical transaction schema
  ├── legit_transaction_sim.py   Realistic baseline traffic
  └── simulators/          One simulator per attack family
        card_abuse_sim.py
        ato_sim.py
        bot_automation_sim.py
        adversarial_ml_sim.py
        poisoning_sim.py
defend/                  Detection engine
  ├── feature_engineering.py
  ├── models/
  │     xgboost_classifier.py
  │     isolation_forest.py
  └── ensemble.py          Combines both into a final fraud score + attack-type prediction
observability/           The system explaining its own failures
  ├── error_detector.py     Finds missed attacks (false negatives) per round
  ├── error_localizer.py    Identifies which detection layer failed
  ├── root_cause_analyzer.py  Explains WHY, using feature-importance deltas
  ├── remediation_engine.py   Decides what harder variant to generate next
  ├── alert_manager.py       Formats 🚨 DEFENSE FAILURE cards
  └── event_logger.py        Persists every round as structured JSON for the dashboard
loop_runner.py           Orchestrates the full closed loop across N rounds
evaluate.py              Confusion matrix, per-class P/R/F1, ROC-AUC, FPR
run_demo.py              One command: runs the full loop, saves artifacts, prints a summary
backend/                 FastAPI service exposing the closed loop + live scoring over HTTP
  └── main.py              All /api/* endpoints (overview, live feed, simulate, analytics, closed-loop, alerts, observability, system health, model insights)
frontend/                 React + Vite dashboard (the "AI Payment Security Command Center")
  └── src/pages/            Overview, Attack Lab, Live Feed, Defense Analytics, Closed-Loop Results,
                             Alerts, Attack Taxonomy, Model Insights, Observability Logs, System Health
artifacts/                Generated JSON (metrics_history.json, alerts.json) read by the dashboard
```

## Quickstart

**1. Run the closed loop from the command line** (identify is pre-written, generate+defend+observe run live):

```bash
pip install -r requirements.txt
python run_demo.py
```

This runs 3 rounds by default: it trains an initial detector, evaluates it
against every attack simulator, finds what it misses, explains why via the
observability layer, generates targeted harder variants for the weakest
attack type, retrains, and re-evaluates. All metrics land in
`artifacts/metrics_history.json` and all failure cards land in
`artifacts/alerts.json`.

**2. Launch the interactive dashboard** (two terminals):

```bash
# Terminal 1 — backend API
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```

The frontend reads its API base URL from `VITE_API_BASE` (see
`frontend/.env.example`) and defaults to `http://localhost:8000`. Open the
printed Vite URL and click **Enter Command Center** to walk through
Identify → Generate → Defend → Observe → Remediate → Retrain in the UI.
The command center starts with a bootstrap model so Attack Lab and Live Feed
work immediately; triggering a closed-loop run from the UI swaps in the
retrained model.

## Why this design wins on the rubric

| Judging criterion | How this repo addresses it |
|---|---|
| Diversity of attacks identified | `identify/attack_taxonomy.md` — 67 attacks across 15 categories, sourced from real payment-fraud research |
| Fidelity of attacks in simulation | Each simulator is built around real behavioral signatures (velocity curves, device/IP entropy, mule-network graph structure) rather than random noise |
| Detection algorithms & efficacy | XGBoost + Isolation Forest ensemble, evaluated with per-attack-type recall, confusion matrix, ROC-AUC, and false-positive rate on legitimate traffic |
| Novelty | Adversarial-ML attacks that specifically target the live classifier's decision boundary, feedback-loop poisoning, and a self-diagnosing observability layer that explains *why* a detector failed, not just *that* it failed |
| Real-world feasibility | Feature set and architecture map directly onto fields available in real payment-rail data (issuer/acquirer transaction logs, device fingerprinting, KYC metadata) |

## Solo build note

This was built and is run by a single person. The closed loop is intentionally
scoped to 5 attack families run deeply and well (Card Abuse, Account Takeover,
Bot/Automation, Adversarial-ML, Poisoning) rather than shallow coverage of 20+ —
fidelity and a working demo beat breadth that doesn't run.
