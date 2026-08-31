
import React, { useEffect, useState } from "react";
import { getObservabilityLogs } from "../services/api.js";
import { Card, Badge, LoadingState } from "../components/common.jsx";

const SEV_COLOR = {
  HIGH: "danger",
  INFO: "cyan",
};

export default function Observability() {
  const [data, setData] = useState(null);
  const [filter, setFilter] = useState("All");

  useEffect(() => {
    getObservabilityLogs().then(setData);
  }, []);

  if (!data) {
    return <LoadingState label="Loading observability logs…" />;
  }

  const filtered =
    filter === "All"
      ? data.events
      : data.events.filter(
          (e) => e.severity === filter.toUpperCase()
        );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">
          Observability Logs
        </h1>

        <p className="text-textSecondary text-sm mt-1">
          How was the failure diagnosed?
        </p>
      </div>

      <div className="flex gap-2">
        {["All", "High", "Info"].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`btn-fx ${filter === f ? "" : "!bg-gray-100 !text-textSecondary"}`}
          >
            {f}
          </button>
        ))}
      </div>

      <Card>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-textMuted border-b border-border">
              <th className="py-2">Round</th>
              <th>Event</th>
              <th>Component</th>
              <th>Severity</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            {filtered.map((e, i) => (
              <tr
                key={i}
                className="border-b border-border/50"
              >
                <td className="py-2">
                  {e.round}
                </td>

                <td className="font-mono text-xs">
                  {e.event}
                </td>

                <td>
                  {e.component}
                </td>

                <td>
                  <Badge
                    color={SEV_COLOR[e.severity] || "muted"}
                  >
                    {e.severity}
                  </Badge>
                </td>

                <td className="text-success text-xs">
                  {e.status}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
