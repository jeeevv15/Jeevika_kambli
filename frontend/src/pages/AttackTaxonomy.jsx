import React, { useEffect, useState } from "react";
import { getTaxonomy } from "../services/api.js";
import { Card, Badge, LoadingState } from "../components/common.jsx";
import { ChevronDown, ChevronRight } from "lucide-react";

export default function AttackTaxonomy() {
  const [data, setData] = useState(null);
  const [open, setOpen] = useState({});
  useEffect(() => { getTaxonomy().then(setData); }, []);
  if (!data) return <LoadingState label="Loading taxonomy…" />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{data.total_attacks} Attacks · {data.total_categories} Categories</h1>
        <p className="text-textSecondary text-sm mt-1">Full GenAI payment-fraud threat landscape.</p>
      </div>

      <div className="space-y-2">
        {data.categories.map((c) => (
          <Card key={c.id}>
            <button className="w-full flex justify-between items-center text-left" onClick={() => setOpen((o) => ({ ...o, [c.id]: !o[c.id] }))}>
              <div className="flex items-center gap-2">
                {open[c.id] ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                <span className="font-semibold">{c.id}. {c.title}</span>
                {c.simulated_category && <Badge color="cyan">SIMULATED</Badge>}
              </div>
              <span className="text-xs text-textMuted">{c.attacks.length} attacks</span>
            </button>
            {open[c.id] && (
              <div className="mt-3 space-y-2 pl-6">
                {c.attacks.map((a) => (
                  <div key={a.num} className="flex items-center justify-between text-sm border-t border-border/50 pt-2">
                    <span className="text-textSecondary">{a.num}. {a.text}</span>
                    <div className="flex gap-1 shrink-0 ml-3">
                      <Badge color="purple">GENAI</Badge>
                      {a.active_simulation ? <Badge color="success">ACTIVE SIMULATION</Badge> : <Badge color="muted">RESEARCHED</Badge>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}