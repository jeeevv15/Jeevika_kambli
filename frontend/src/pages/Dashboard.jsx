import React from "react";
import { Routes, Route } from "react-router-dom";
import { AppShell } from "../components/layout.jsx";
import Overview from "./Overview.jsx";
import AttackLab from "./AttackLab.jsx";
import LiveFeed from "./LiveFeed.jsx";
import DefenseAnalytics from "./DefenseAnalytics.jsx";
import ClosedLoop from "./ClosedLoop.jsx";
import Alerts from "./Alerts.jsx";
import AttackTaxonomy from "./AttackTaxonomy.jsx";
import ModelInsights from "./ModelInsights.jsx";
import Observability from "./Observability.jsx";
import SystemHealth from "./SystemHealth.jsx";

export default function Dashboard() {
  return (
    <AppShell>
      <Routes>
        <Route index element={<Overview />} />
        <Route path="attack-lab" element={<AttackLab />} />
        <Route path="live-feed" element={<LiveFeed />} />
        <Route path="analytics" element={<DefenseAnalytics />} />
        <Route path="closed-loop" element={<ClosedLoop />} />
        <Route path="alerts" element={<Alerts />} />
        <Route path="taxonomy" element={<AttackTaxonomy />} />
        <Route path="model-insights" element={<ModelInsights />} />
        <Route path="observability" element={<Observability />} />
        <Route path="system-health" element={<SystemHealth />} />
      </Routes>
    </AppShell>
  );
}
