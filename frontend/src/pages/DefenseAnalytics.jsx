import React, { useEffect, useState } from "react";
import { getAnalytics } from "../services/api.js";
import { Card, MetricCard, SectionTitle, LoadingState } from "../components/common.jsx";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";

export default function DefenseAnalytics() {
  const [data, setData] = useState(null);
  useEffect(() => { getAnalytics().then(setData); }, []);
  if (!data) return <LoadingState label="Running evaluation batch…" />;

  const cm = data.confusion_matrix;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Defense Analytics</h1>
        <p className="text-textSecondary text-sm mt-1">Measure how effectively the defense catches emerging attacks.</p>
      </div>

      <div className="grid grid-cols-5 gap-4">
        <MetricCard label="Precision" value={pct(data.overall.precision)} accent="purple" />
        <MetricCard label="Recall" value={pct(data.overall.recall)} accent="cyan" />
        <MetricCard label="F1" value={pct(data.overall.f1)} accent="success" />
        <MetricCard label="ROC-AUC" value={pct(data.overall.roc_auc)} accent="purple" />
        <MetricCard label="False Positive Rate" value={pct(data.overall.false_positive_rate)} accent="warning" />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Card>
          <SectionTitle>Recall by Attack Type</SectionTitle>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data.recall_by_attack_type}>
              <CartesianGrid strokeDasharray="3 3" stroke="#273244" />
              <XAxis dataKey="attack_type" tick={{ fill: "#9CA3AF", fontSize: 11 }} />
              <YAxis tick={{ fill: "#9CA3AF", fontSize: 11 }} domain={[0, 1]} />
              <Tooltip contentStyle={{ background: "#dfe9fe", border: "1px solid #dde6f5" }} />
              <Bar dataKey="recall" fill="#7C5CFF" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <SectionTitle>ROC Curve</SectionTitle>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={data.roc_curve}>
              <CartesianGrid strokeDasharray="3 3" stroke="#273244" />
              <XAxis dataKey="fpr" tick={{ fill: "#9CA3AF", fontSize: 11 }} />
              <YAxis dataKey="tpr" tick={{ fill: "#9CA3AF", fontSize: 11 }} />
              <Tooltip contentStyle={{ background: "#d2e1ff", border: "1px solid #b0ceff" }} />
              <Line type="monotone" dataKey="tpr" stroke="#0c7e8f" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <SectionTitle>Confusion Matrix</SectionTitle>
          <table className="w-full text-sm text-center">
            <thead><tr><th></th><th className="text-textMuted font-normal">Pred. Legit</th><th className="text-textMuted font-normal">Pred. Fraud</th></tr></thead>
            <tbody>
              <tr><td className="text-textMuted">Actual Legit</td><td className="py-2 bg-success/10">{cm.predicted_legit.actual_legit}</td><td className="py-2 bg-danger/10">{cm.predicted_fraud.actual_legit}</td></tr>
              <tr><td className="text-textMuted">Actual Fraud</td><td className="py-2 bg-warning/10">{cm.predicted_legit.actual_fraud}</td><td className="py-2 bg-success/10">{cm.predicted_fraud.actual_fraud}</td></tr>
            </tbody>
          </table>
        </Card>

        <Card>
          <SectionTitle>Model Comparison</SectionTitle>
          <table className="w-full text-sm">
            <thead><tr className="text-textMuted"><th className="text-left">Model</th><th>Precision</th><th>Recall</th><th>F1</th></tr></thead>
            <tbody>
              {Object.entries(data.model_comparison).map(([name, m]) => (
                <tr key={name} className="border-t border-border/50">
                  <td className="py-2 capitalize">{name.replace("_", " ")}</td>
                  <td className="text-center">{pct(m.precision)}</td>
                  <td className="text-center">{pct(m.recall)}</td>
                  <td className="text-center">{pct(m.f1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>
    </div>
  );
}

function pct(v) { return v != null ? `${(v * 100).toFixed(1)}%` : "—"; }