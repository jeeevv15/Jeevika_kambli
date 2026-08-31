
import React, { useEffect, useState } from "react";
import { getLiveFeed, getTransaction } from "../services/api.js";
import {
  Card,
  MetricCard,
  SectionTitle,
  Badge,
  Drawer,
  LoadingState,
} from "../components/common.jsx";
import { RefreshCw } from "lucide-react";

const DECISION_COLOR = {
  LEGIT: "success",
  REVIEW: "warning",
  FRAUD: "danger",
};

export default function LiveFeed() {
  const [data, setData] = useState(null);
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);

  function load() {
    getLiveFeed(50).then(setData);
  }

  useEffect(load, []);

  async function openTxn(id) {
    setSelected(id);
    setDetail(await getTransaction(id));
  }

  if (!data) return <LoadingState label="Loading transaction feed…" />;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Live Transaction Feed</h1>
          <p className="text-textSecondary text-sm mt-1">
            Real-time transaction scoring and fraud decisions.
          </p>
        </div>

        <button onClick={load} className="btn-fx flex items-center gap-2">
          <RefreshCw size={14} />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <MetricCard
          label="Transactions"
          value={data.total}
          fill="#d1e2ff"
        />
        <MetricCard
          label="Fraud"
          value={data.fraud}
          fill="#f8d7da"
        />
        <MetricCard
          label="Suspicious"
          value={data.review}
          fill="#fff3cd"
        />
        <MetricCard
          label="Legitimate"
          value={data.legit}
          fill="#d4edda"
        />
      </div>

      <Card>
        <SectionTitle>Transactions</SectionTitle>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-textMuted border-b border-border">
                <th className="py-2 pr-3">Txn ID</th>
                <th className="py-2 pr-3">Amount</th>
                <th className="py-2 pr-3">Attack Type</th>
                <th className="py-2 pr-3">Device Risk</th>
                <th className="py-2 pr-3">IP Risk</th>
                <th className="py-2 pr-3">Behavior</th>
                <th className="py-2 pr-3">Fraud Prob.</th>
                <th className="py-2 pr-3">Decision</th>
              </tr>
            </thead>

            <tbody>
              {data.transactions.map((t) => (
                <tr
                  key={t.txn_id}
                  onClick={() => openTxn(t.txn_id)}
                  className="border-b border-border/50 hover:bg-white/5 cursor-pointer"
                >
                  <td className="py-2 pr-3 font-mono text-xs text-textMuted">
                    {t.txn_id.slice(0, 8)}
                  </td>

                  <td className="py-2 pr-3">
                    ₹{t.amount.toFixed(0)}
                  </td>

                  <td className="py-2 pr-3">
                    <Badge color="purple">
                      {t.attack_type}
                    </Badge>
                  </td>

                  <td className="py-2 pr-3">
                    {t.device_risk ? "High" : "Low"}
                  </td>

                  <td className="py-2 pr-3">
                    {t.ip_risk.toFixed(2)}
                  </td>

                  <td className="py-2 pr-3">
                    {t.behavior_deviation.toFixed(2)}
                  </td>

                  <td className="py-2 pr-3">
                    {(t.fraud_probability * 100).toFixed(1)}%
                  </td>

                  <td className="py-2 pr-3">
                    <Badge color={DECISION_COLOR[t.decision]}>
                      {t.decision}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <Drawer
        open={!!selected}
        onClose={() => setSelected(null)}
        title="Transaction Analysis"
      >
        {detail && (
          <div className="space-y-4 text-sm">
            <div className="text-xs text-textMuted font-mono">
              {detail.transaction.txn_id}
            </div>

            <div>
              <div className="text-xs text-textMuted">
                Fraud Probability
              </div>
              <div className="text-2xl font-bold text-danger">
                {(detail.fraud_probability * 100).toFixed(1)}%
              </div>
            </div>

            <div>
              <div className="text-xs text-textMuted">
                Predicted Attack
              </div>
              <div>{detail.predicted_attack_type}</div>
            </div>

            <div>
              <div className="text-xs text-textMuted mb-1">
                Risk Signals
              </div>

              <div className="flex flex-wrap gap-1">
                {detail.risk_signals.length ? (
                  detail.risk_signals.map((s) => (
                    <Badge key={s} color="warning">
                      {s}
                    </Badge>
                  ))
                ) : (
                  <span className="text-textMuted">
                    None flagged
                  </span>
                )}
              </div>
            </div>

            <div>
              <div className="text-xs text-textMuted mb-1">
                Model Output
              </div>

              <Row
                label="XGBoost"
                value={`${(detail.fraud_probability * 100).toFixed(0)}%`}
              />

              <Row
                label="Isolation Forest"
                value={`${(detail.anomaly_score * 100).toFixed(0)}%`}
              />

              <Row
                label="Ensemble"
                value={`${(detail.final_score * 100).toFixed(0)}%`}
              />
            </div>

            <div
              className={`font-semibold ${
                detail.predicted_fraud
                  ? "text-danger"
                  : "text-success"
              }`}
            >
              {detail.predicted_fraud
                ? "🚨 FRAUD DETECTED"
                : "✓ LEGITIMATE"}
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between py-1">
      <span className="text-textMuted">{label}</span>
      <span>{value}</span>
    </div>
  );
}
