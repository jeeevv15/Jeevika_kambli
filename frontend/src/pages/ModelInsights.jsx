import React, { useEffect, useState } from "react";
import { getModelInsights } from "../services/api.js";
import { Card, SectionTitle, LoadingState } from "../components/common.jsx";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export default function ModelInsights() {
  const [data, setData] = useState(null);
  useEffect(() => { getModelInsights().then(setData); }, []);
  if (!data) return <LoadingState label="Loading model insights…" />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Model Insights</h1>
        <p className="text-textSecondary text-sm mt-1">Why did the model make this decision?</p>
      </div>

      <Card>
        <SectionTitle subtitle="XGBoost feature importance — learned directly from the trained ensemble">Feature Importance</SectionTitle>
        <ResponsiveContainer width="100%" height={360}>
          <BarChart data={data.feature_importance} layout="vertical" margin={{ left: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0ecff" />
            <XAxis type="number" tick={{ fill: "#9CA3AF", fontSize: 11 }} />
            <YAxis type="category" dataKey="feature" width={160} tick={{ fill: "#9CA3AF", fontSize: 11 }} />
            <Tooltip contentStyle={{ background: "#dde8ff", border: "1px solid #b7d2ff" }} />
            <Bar dataKey="importance" fill="#7C5CFF" radius={[0, 6, 6, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Card>
      <p className="text-xs text-textMuted">
        Open a transaction from the Live Transaction Feed to see its "why was this flagged" breakdown against these same importances.
      </p>
    </div>
  );
}