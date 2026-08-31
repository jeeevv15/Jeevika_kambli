import React from "react";
import { getAlerts } from "../services/api.js";
import { useApiData } from "../hooks/useApiData.js";
import { Card, Badge, ErrorState, EmptyState } from "../components/common.jsx";
import { AlertTriangle } from "lucide-react";

const SEV_COLOR = { HIGH: "danger", MEDIUM: "warning", LOW: "success" };

export default function Alerts() {
  const { status, data, error, reload } = useApiData(getAlerts, []);
  if (status === "loading") return <p className="text-textMuted text-sm">Loading alerts…</p>;
  if (status === "error") return <ErrorState message={error} onRetry={reload} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Defense Failure Alerts</h1>
        <p className="text-textSecondary text-sm mt-1">Failures detected by the observability and remediation pipeline.</p>
      </div>

      {data.alerts.length === 0 && <EmptyState label="No alerts logged yet — run the closed loop first." />}

      {data.alerts.map((a, i) => (
        <Card key={i} className={a.severity === "HIGH" ? "border-danger/40" : ""}>
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle size={16} className={a.severity === "LOW" ? "text-success" : "text-danger"} />
            <Badge color={SEV_COLOR[a.severity]}>{a.severity} SEVERITY</Badge>
            <Badge color="purple">{a.attack_type}</Badge>
            <Badge color="muted">Round {a.round_num}</Badge>
          </div>
          <div className="text-sm font-medium mb-3">{a.what_happened}</div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <Field label="WHERE" value={a.failed_layer} />
            <Field label="IMPACT" value={a.impact} />
          </div>
          <Field label="WHY — LAYER ASSUMPTION & OBSERVED SEPARATION GAP" value={a.why_layer_assumption} className="mt-3" />
          {a.why_global_importance_note && (
            <Field label="WHY — GLOBAL MODEL IMPORTANCE (this round's trained model)" value={a.why_global_importance_note} className="mt-3" />
          )}
          <Field label="RECOMMENDED REMEDIATION" value={a.remediation} className="mt-3" />
          <div className="mt-3 text-xs text-textMuted">STATUS — {a.display_status}</div>
        </Card>
      ))}
    </div>
  );
}

function Field({ label, value, className = "" }) {
  return (
    <div className={className}>
      <div className="text-xs text-textMuted uppercase">{label}</div>
      <div className="text-sm text-textSecondary mt-1">{value}</div>
    </div>
  );
}