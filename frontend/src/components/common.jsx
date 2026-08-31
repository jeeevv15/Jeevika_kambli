import React from "react";

export function Card({ children, className = "" }) {
  return (
    <div className={`rounded-2xl border border-border bg-card shadow-sm p-5 ${className}`}>
      {children}
    </div>
  );
}

export function SectionTitle({ children, subtitle }) {
  return (
    <div className="mb-4">
      <h2 className="text-lg font-semibold text-textPrimary font-heading">{children}</h2>
      {subtitle && <p className="text-sm text-textSecondary mt-1">{subtitle}</p>}
    </div>
  );
}

const STAT_BG = { yellow: "bg-statYellow", lavender: "bg-statPurple", blue: "bg-statBlue", pink: "bg-statPink" };
const STAT_TEXT = { yellow: "text-yellow-800", lavender: "text-purple", blue: "text-blue-700", pink: "text-pink-700" };

export function MetricCard({ label, value, sub, accent = "lavender" }) {
  return (
    <div className={`metric-blob-card p-5 shadow-sm ${STAT_BG[accent]}`}>
      <div className="text-xs uppercase tracking-wide font-bold text-textSecondary relative z-10">{label}</div>
      <div className={`text-3xl font-heading font-bold mt-2 relative z-10 ${STAT_TEXT[accent]}`}>{value}</div>
      {sub && <div className="text-xs font-semibold text-textMuted mt-1 relative z-10">{sub}</div>}
    </div>
  );
}

export function Badge({ children, color = "muted" }) {
  const map = {
    success: "bg-green-100 text-green-800 border-green-200",
    warning: "bg-yellow-100 text-yellow-800 border-yellow-200",
    danger: "bg-red-100 text-red-700 border-red-200",
    purple: "bg-purple-100 text-purple-800 border-purple-200",
    cyan: "bg-blue-100 text-blue-800 border-blue-200",
    muted: "bg-gray-100 text-textSecondary border-gray-200",
  };
  return <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold border ${map[color]}`}>{children}</span>;
}

export function ProgressBar({ value, max = 1, color = "purple" }) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  const colorMap = { purple: "bg-purple", success: "bg-success", warning: "bg-warning", danger: "bg-danger" };
  return (
    <div className="w-full h-2 rounded-full bg-gray-100 overflow-hidden">
      <div className={`h-full ${colorMap[color]} transition-all duration-500`} style={{ width: `${pct}%` }} />
    </div>
  );
}

export function StatusDot({ ok }) {
  return <span className={`inline-block w-2 h-2 rounded-full mr-2 ${ok ? "bg-success" : "bg-danger"}`} />;
}

export function LoadingState({ label = "Loading…" }) {
  return <div className="text-sm text-textSecondary font-semibold py-10 text-center">{label}</div>;
}

export function EmptyState({ label }) {
  return <div className="text-sm text-textSecondary font-semibold py-10 text-center border border-dashed border-border rounded-2xl">{label}</div>;
}

export function Drawer({ open, onClose, title, children }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/20" onClick={onClose} />
      <div className="relative w-full max-w-md bg-card border-l border-border h-full overflow-y-auto p-5">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-base font-heading font-semibold">{title}</h3>
          <button onClick={onClose} className="text-textSecondary hover:text-textPrimary font-bold">✕</button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="border border-danger/30 bg-danger/5 rounded-2xl p-6 text-center">
      <div className="text-danger font-bold mb-1">BACKEND CONNECTION ERROR</div>
      <div className="text-sm text-textSecondary font-semibold mb-4">
        Unable to reach the Payment Security Engine.{message ? ` (${message})` : ""}
      </div>
      {onRetry && <button onClick={onRetry} className="btn-fx">RETRY</button>}
    </div>
  );
}

export function ModelSourceBadge({ source }) {
  if (!source) return null;
  const synced = source.in_sync_with_artifacts;
  return (
    <span className={`text-[11px] font-bold px-2 py-1 rounded-md border ${synced ? "border-green-300 text-green-800 bg-green-50" : "border-yellow-300 text-yellow-800 bg-yellow-50"}`}>
      {synced ? `Closed-Loop Model — Round ${source.trained_through_round}` : "Live Demo Model (not synced with saved artifacts)"}
    </span>
  );
}
