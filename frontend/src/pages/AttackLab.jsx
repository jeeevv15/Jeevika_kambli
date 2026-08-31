import React, { useEffect, useState } from "react";
import { getSimulateOptions, postSimulate } from "../services/api.js";
import { useApiData } from "../hooks/useApiData.js";
import { Card, SectionTitle, ProgressBar, Badge, ErrorState, ModelSourceBadge } from "../components/common.jsx";
import { Zap, AlertTriangle } from "lucide-react";

export default function AttackLab() {
  const { status, data: options, error, reload } = useApiData(getSimulateOptions, []);
  const [attackType, setAttackType] = useState("adversarial_ml");
  const [n, setN] = useState(60);
  const [difficulty, setDifficulty] = useState("normal");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);

  if (status === "loading") return <p className="text-textMuted text-sm">Loading attack lab…</p>;
  if (status === "error") return <ErrorState message={error} onRetry={reload} />;

  const supportsDifficulty = options.attack_types.find((a) => a.id === attackType)?.difficulty_supported;

  async function launch() {
    setRunning(true);
    setResult(null);
    try {
      const data = await postSimulate({ attack_type: attackType, n, difficulty });
      setResult(data);
    } catch (e) {
      setResult({ error: e?.message || "Simulation failed" });
    }
    setRunning(false);
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Attack Lab</h1>
        <p className="text-textSecondary text-sm mt-1">Launch a simulated attack and watch the defense respond.</p>
      </div>

      <Card>
        <div className="grid grid-cols-4 gap-4 items-end">
          <div>
            <label className="text-xs text-textMuted">Attack Category</label>
            <select className="w-full mt-1 bg-elevated border border-border rounded-lg px-3 py-2 text-sm" value={attackType} onChange={(e) => setAttackType(e.target.value)}>
              {options.attack_types.map((a) => <option key={a.id} value={a.id}>{a.label}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-textMuted">Transactions: {n}</label>
            <input type="range" min={20} max={200} step={10} value={n} onChange={(e) => setN(Number(e.target.value))} className="w-full mt-2" />
          </div>
          <div>
            <label className="text-xs text-textMuted">Difficulty</label>
            <select
              className="w-full mt-1 bg-elevated border border-border rounded-lg px-3 py-2 text-sm disabled:opacity-40"
              value={difficulty}
              disabled={!supportsDifficulty}
              onChange={(e) => setDifficulty(e.target.value)}
            >
              <option value="normal">Normal</option>
              <option value="advanced">Advanced</option>
              <option value="extreme">Extreme</option>
            </select>
            {!supportsDifficulty && (
              <div className="text-[11px] text-textMuted mt-1">Not supported for this simulator — generation profile is fixed.</div>
            )}
          </div>
          <button onClick={launch} disabled={running} className="btn-fx flex items-center justify-center gap-2">
            <Zap size={16} /> {running ? "Running…" : "Launch Simulation"}
          </button>
        </div>
      </Card>

      {result?.error && <ErrorState message={result.error} onRetry={launch} />}

      {result && !result.error && (
        <>
          <Card>
            <div className="flex justify-between items-center mb-2">
              <SectionTitle>Simulation Status — {result.attack_label}</SectionTitle>
              <ModelSourceBadge source={result.model_source} />
            </div>
            {result.difficulty_applied === null && (
              <div className="text-[11px] text-warning mb-2">Difficulty was requested but ignored by this simulator (unsupported).</div>
            )}
            <div className="grid grid-cols-4 gap-4 text-sm mb-3">
              <Stat label="Generated" value={result.generated} />
              <Stat label="Processed" value={result.processed} />
              <Stat label="Detected" value={result.detected} color="success" />
              <Stat label="Missed" value={result.missed} color={result.missed > 0 ? "danger" : "success"} />
            </div>
            <ProgressBar value={result.detected} max={result.generated} color="success" />
          </Card>

          <Card>
            <SectionTitle>Live Model Response</SectionTitle>
            <div className="max-h-96 overflow-y-auto space-y-1.5">
              {result.transactions.map((t) => (
                <div key={t.txn_id} className="flex items-center justify-between bg-elevated border border-border rounded-lg px-3 py-2 text-sm">
                  <span className="text-textMuted font-mono text-xs">{t.txn_id.slice(0, 8)}</span>
                  <span>₹{t.amount.toFixed(0)}</span>
                  <Badge color="purple">{t.attack_type}</Badge>
                  <span className="text-xs">Risk {t.final_score.toFixed(2)}</span>
                  {t.detected ? <Badge color="danger">DETECTED</Badge> : <Badge color="warning">MISSED</Badge>}
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <SectionTitle>Attack Result</SectionTitle>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <Stat label="Detection Recall" value={`${(result.detection_recall * 100).toFixed(1)}%`} />
              <Stat label="Precision" value={`${(result.precision * 100).toFixed(1)}%`} />
              <Stat label="Missed Attacks" value={`${result.missed} / ${result.generated}`} color={result.missed > 0 ? "danger" : "success"} />
            </div>
            {result.defense_failure && (
              <div className="mt-4 flex items-center gap-2 text-danger font-semibold text-sm">
                <AlertTriangle size={16} /> DEFENSE FAILURE DETECTED — see Defense Failure Alerts after running a remediation round
              </div>
            )}
          </Card>
        </>
      )}
    </div>
  );
}

function Stat({ label, value, color = "purple" }) {
  const map = { purple: "text-purple", success: "text-success", danger: "text-danger" };
  return (
    <div>
      <div className="text-xs text-textMuted uppercase">{label}</div>
      <div className={`text-2xl font-bold ${map[color]}`}>{value}</div>
    </div>
  );
}

