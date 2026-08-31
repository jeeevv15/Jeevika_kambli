import React, { useState } from "react";
import { getClosedLoop, postRunLoop } from "../services/api.js";
import { useApiData } from "../hooks/useApiData.js";
import {
  Card,
  SectionTitle,
  Badge,
  ErrorState,
  ModelSourceBadge,
} from "../components/common.jsx";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { ArrowDown, AlertTriangle } from "lucide-react";

export default function ClosedLoop() {
  const { status, data, error, reload } = useApiData(getClosedLoop, []);
  const [running, setRunning] = useState(false);

  if (status === "loading")
    return (
      <p className="text-textMuted text-sm">
        Loading closed-loop history…
      </p>
    );

  if (status === "error")
    return <ErrorState message={error} onRetry={reload} />;

  async function runLoop() {
    const ok = window.confirm(
      "This re-runs the full closed loop from Round 1 and REPLACES the saved metrics/alerts history " +
        "(existing atomic-commit behavior in loop_runner.py — it does not append a round). Continue?"
    );

    if (!ok) return;

    setRunning(true);

    await postRunLoop({ n_rounds: 3 });
    await reload();

    setRunning(false);
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold">Closed-Loop Results</h1>

          <p className="text-textSecondary text-sm mt-1">
            Every missed attack becomes training data for the next defense
            iteration.
          </p>
        </div>

        <button onClick={runLoop} disabled={running} className="btn-fx">
          {running
            ? "Re-running full loop…"
            : "🔄 Re-run Closed Loop (3 rounds)"}
        </button>
      </div>

      <div className="flex justify-end">
        <ModelSourceBadge source={data.model_source} />
      </div>

      {data.plateau_detected && (
        <Card className="border-warning/40">
          <div className="flex items-center gap-2 text-warning font-semibold mb-1">
            <AlertTriangle size={16} />
            PERFORMANCE PLATEAU DETECTED
          </div>

          <div className="text-sm text-textSecondary">
            {data.next_action}
          </div>
        </Card>
      )}

      <div className="grid grid-cols-2 gap-4">
        <Card>
          <div className="text-xs text-textMuted uppercase">
            Defense Improvement
          </div>

          <div className="text-3xl font-bold text-success mt-1">
            +{data.improvement_pp ?? 0} pp
          </div>
        </Card>

        <Card>
          <div className="text-xs text-textMuted uppercase">
            Current Limitation
          </div>

          <div className="text-sm mt-1">
            {data.current_limitation ||
              "No remaining bypasses in the latest round."}
          </div>
        </Card>
      </div>

      <Card>
        <SectionTitle>Recall Improvement by Round</SectionTitle>

        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={data.overall_recall_trend}>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#ccddf8"
            />

            <XAxis
              dataKey="round"
              tick={{
                fill: "#9CA3AF",
                fontSize: 11,
              }}
              label={{
                value: "Round",
                position: "insideBottom",
                offset: -2,
                fill: "#6B7280",
              }}
            />

            <YAxis
              domain={[0, 1]}
              tick={{
                fill: "#9CA3AF",
                fontSize: 11,
              }}
            />

            <Tooltip
              contentStyle={{
                background: "#e4edff",
                border: "1px solid #b9d4ff",
              }}
              formatter={(v) => `${(v * 100).toFixed(1)}%`}
            />

            <Line
              type="monotone"
              dataKey="recall"
              stroke="#7a5eea"
              strokeWidth={2}
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      <Card>
        <SectionTitle>Round-by-Round Timeline</SectionTitle>

        <div className="space-y-4">
          {data.rounds.map((r) => (
            <div key={r.round}>
              <div className="flex items-center gap-3">
                <Badge color="purple">
                  Round {r.round}
                </Badge>

                <span className="text-sm">
                  {(r.overall.recall * 100).toFixed(1)}% recall
                </span>

                {r.alert && (
                  <span className="text-xs text-textMuted">
                    {r.alert_missed_count === 0
                      ? "No bypass — monitoring only"
                      : r.alert.what_happened}
                  </span>
                )}
              </div>

              {r.alert && r.alert_missed_count > 0 && (
                <div className="ml-4 mt-2 pl-4 border-l border-border text-xs text-textSecondary space-y-1">
                  <div className="flex items-center gap-1">
                    <ArrowDown size={12} />
                    OBSERVABILITY — {r.alert.failed_layer}
                  </div>

                  <div className="flex items-center gap-1">
                    <ArrowDown size={12} />
                    REMEDIATION — {r.alert.remediation}
                  </div>

                  <div className="flex items-center gap-1">
                    <ArrowDown size={12} />
                    RETRAIN — model updated
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

