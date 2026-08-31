import React, { useEffect, useState } from "react";
import { getSystemHealth } from "../services/api.js";
import { Card, SectionTitle, StatusDot, LoadingState } from "../components/common.jsx";

export default function SystemHealth() {
  const [data, setData] = useState(null);
  useEffect(() => { getSystemHealth().then(setData); }, []);
  if (!data) return <LoadingState label="Checking system status…" />;

  const rows = [
    ["Backend", data.backend],
    ["ML Engine", data.ml_engine],
    ["Attack Simulator", data.attack_simulator],
    ["Observability", data.observability],
    ["Artifacts", data.artifacts_available ? "Available" : "Not found"],
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">System Health</h1>
        <p className="text-textSecondary text-sm mt-1">Is the system operational?</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Card>
          <SectionTitle>Component Status</SectionTitle>
          {rows.map(([label, status]) => (
            <div key={label} className="flex justify-between py-1.5 border-b border-border/50 text-sm">
              <span className="text-textSecondary">{label}</span>
              <span className="flex items-center"><StatusDot ok={String(status).toLowerCase().includes("online") || status === "Available"} />{status}</span>
            </div>
          ))}
        </Card>
        <Card>
          <SectionTitle>Run Info</SectionTitle>
          <Row label="Current round" value={data.current_round ?? "—"} />
          <Row label="Total rounds logged" value={data.total_rounds_logged} />
          <Row label="Last evaluation" value={data.last_evaluation ?? "—"} />
        </Card>
      </div>
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between py-1.5 border-b border-border/50 text-sm">
      <span className="text-textSecondary">{label}</span>
      <span>{value}</span>
    </div>
  );
}