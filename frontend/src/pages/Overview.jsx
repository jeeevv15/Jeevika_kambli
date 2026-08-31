import React, { useEffect, useState } from "react";
import { getOverview } from "../services/api.js";
import { Card, MetricCard, SectionTitle, Badge, LoadingState } from "../components/common.jsx";
import { CheckCircle2, AlertTriangle, ArrowRight } from "lucide-react";

const STAGE_ORDER = ["identify", "generate", "defend", "observe", "remediate", "retrain"];
const STAGE_LABELS = { identify: "IDENTIFY", generate: "GENERATE", defend: "DEFEND", observe: "OBSERVE", remediate: "REMEDIATE", retrain: "RETRAIN" };

export default function Overview() {
  const [data, setData] = useState(null);

  useEffect(() => { getOverview().then(setData); }, []);

  if (!data) return <LoadingState label="Loading command center…" />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">AI Defense Lab</h1>
        <p className="text-textSecondary mt-1">Payment Security Command Center</p>
        <p className="text-sm text-textMuted italic mt-1">
          "Closed-loop adversarial defense for emerging GenAI payment fraud."
        </p>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <MetricCard label="Attacks Identified" value={data.attacks_identified} sub={`${data.categories} categories`} accent="yellow" />
        <MetricCard label="Detection Recall" value={data.detection_recall != null ? `${(data.detection_recall * 100).toFixed(1)}%` : "—"} sub={`Round ${data.latest_round ?? "—"}`} accent="lavender" />
        <MetricCard label="F1 Score" value={data.f1_score != null ? `${(data.f1_score * 100).toFixed(2)}%` : "—"} sub="Ensemble" accent="blue" />
        <MetricCard label="Defense Failures" value={data.defense_failures} sub={data.defense_failures > 0 ? "Requires attention" : "None logged"  } accent="pink" />
      </div>

      <Card>
        <SectionTitle>Closed-Loop Defense</SectionTitle>
        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          {STAGE_ORDER.map((key, i) => {
            const s = data.stages[key];
            return (
              <React.Fragment key={key}>
                <div className="min-w-[150px] bg-elevated border border-border rounded-card p-3">
                  <div className="text-xs font-semibold text-textSecondary tracking-wide">{STAGE_LABELS[key]}</div>
                  <div className="text-xs text-textMuted mt-1">{s.detail}</div>
                  <div className={`text-xs mt-2 flex items-center gap-1 ${s.complete ? "text-success" : "text-warning"}`}>
                    {s.complete ? <CheckCircle2 size={13} /> : <AlertTriangle size={13} />}
                    {s.complete ? "Complete" : "Attention"}
                  </div>
                </div>
                {i < STAGE_ORDER.length - 1 && <ArrowRight size={16} className="text-textMuted shrink-0" />}
              </React.Fragment>
            );
          })}
        </div>
      </Card>

      <div className="grid grid-cols-2 gap-4">
        <Card>
          <SectionTitle>Defense Status</SectionTitle>
          <div className="space-y-2 text-sm">
            <Row label="Precision" value={pct(data.precision)} />
            <Row label="Recall" value={pct(data.detection_recall)} />
            <Row label="F1" value={pct(data.f1_score)} />
            <Row label="ROC-AUC" value={pct(data.roc_auc)} />
            <Row label="False Positive Rate" value={pct(data.false_positive_rate)} />
          </div>
        </Card>
        <Card>
          <SectionTitle>System Summary</SectionTitle>
          <div className="space-y-2 text-sm text-textSecondary">
            <Row label="Simulated categories" value={data.simulated_categories} />
            <Row label="Total rounds run" value={data.total_rounds} />
            <Row label="Latest round" value={data.latest_round ?? "—"} />
          </div>
        </Card>
      </div>

      {data.latest_failure && (
        <Card className="border-danger/40">
          <div className="flex items-center gap-2 text-danger font-semibold mb-2">
            <AlertTriangle size={18} /> DEFENSE FAILURE
          </div>
          <div className="text-sm text-textSecondary space-y-1">
            <div><Badge color="purple">{data.latest_failure.attack_type}</Badge> <Badge color="muted">Round {data.latest_failure.round_num}</Badge></div>
            <div className="mt-2">{data.latest_failure.what_happened}</div>
            <div className="text-xs text-textMuted mt-2">ROOT CAUSE</div>
            <div>{data.latest_failure.failed_layer}</div>
          </div>
        </Card>
      )}
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between">
      <span className="text-textMuted">{label}</span>
      <span className="text-textPrimary font-medium">{value}</span>
    </div>
  );
}
function pct(v) { return v != null ? `${(v * 100).toFixed(1)}%` : "—"; }