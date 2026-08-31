import React from "react";
import { NavLink, Link } from "react-router-dom";
import {
  LayoutDashboard, Crosshair, Activity, BarChart3, GitBranch, AlertTriangle,
  Layers, Brain, Terminal, ServerCog, Shield,
} from "lucide-react";
import { StatusDot } from "./common.jsx";

const MAIN_NAV = [
  { to: "/app", label: "Overview", icon: LayoutDashboard },
  { to: "/app/attack-lab", label: "Attack Lab", icon: Crosshair },
  { to: "/app/live-feed", label: "Live Transaction Feed", icon: Activity },
  { to: "/app/analytics", label: "Defense Analytics", icon: BarChart3 },
  { to: "/app/closed-loop", label: "Closed-Loop Results", icon: GitBranch },
  { to: "/app/alerts", label: "Defense Failure Alerts", icon: AlertTriangle },
];

const INTEL_NAV = [
  { to: "/app/taxonomy", label: "Attack Taxonomy", icon: Layers },
  { to: "/app/model-insights", label: "Model Insights", icon: Brain },
  { to: "/app/observability", label: "Observability Logs", icon: Terminal },
];

const SYS_NAV = [
  { to: "/app/system-health", label: "System Health", icon: ServerCog },
];

function NavGroup({ title, items }) {
  return (
    <div className="mb-6">
      <div className="text-[11px] uppercase tracking-wider text-textSecondary font-bold px-3 mb-2">{title}</div>
      <div className="flex flex-col gap-1">
        {items.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} end={to === "/app"}
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}>
            <Icon size={16} /> {label}
          </NavLink>
        ))}
      </div>
    </div>
  );
}

export function Sidebar() {
  return (
    <aside className="w-64 bg-sidebar border-r border-border h-screen sticky top-0 flex flex-col p-4">
      <Link to="/" className="flex items-center gap-2 px-2 mb-8 mt-1">
        <Shield className="text-purple" size={22} />
        <div>
          <div className="text-sm font-heading font-bold tracking-wide text-textPrimary">AI DEFENSE LAB</div>
          <div className="text-[11px] font-semibold text-textSecondary">Payment Security</div>
        </div>
      </Link>
      <NavGroup title="Main" items={MAIN_NAV} />
      <NavGroup title="Intelligence" items={INTEL_NAV} />
      <NavGroup title="System" items={SYS_NAV} />
    </aside>
  );
}

export function Topbar({ round }) {
  return (
    <header className="h-14 border-b border-border flex items-center justify-between px-6 sticky top-0 bg-white z-30">
      <div className="text-sm font-heading font-semibold text-textPrimary">AI Payment Security Command Center</div>
      <div className="flex items-center gap-3 text-xs font-bold text-textSecondary">
        <span className="px-2 py-1 rounded-md bg-gray-100 border border-border">SIMULATION</span>
        <span className="flex items-center"><StatusDot ok={true} /> SYSTEM ACTIVE</span>
        {round != null && <span className="px-2 py-1 rounded-md bg-statPurple text-purple border border-purple/20">ROUND {round}</span>}
      </div>
    </header>
  );
}

export function AppShell({ children, round }) {
  return (
    <div className="flex min-h-screen bg-bg">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Topbar round={round} />
        <main className="p-6 flex-1">{children}</main>
      </div>
    </div>
  );
}