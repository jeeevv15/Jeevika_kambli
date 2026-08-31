import React, { useState } from "react";
import { Link } from "react-router-dom";
import {
  Shield,
  ArrowRight,
  Search,
  FlaskConical,
  ShieldCheck,
  Eye,
  Wrench,
  RefreshCw,
  Crosshair,
} from "lucide-react";
import PrismaticBurst from "../components/PrismaticBurst.jsx";

const STAGES = [
  {
    key: "identify",
    label: "IDENTIFY",
    icon: Search,
    color: "#7C4DFF",
    desc: "67 attack vectors mapped",
  },
  {
    key: "generate",
    label: "GENERATE",
    icon: FlaskConical,
    color: "#F5A623",
    desc: "5 simulated attack families",
  },
  {
    key: "defend",
    label: "DEFEND",
    icon: ShieldCheck,
    color: "#2F8FFF",
    desc: "XGBoost + Isolation Forest",
  },
  {
    key: "observe",
    label: "OBSERVE",
    icon: Eye,
    color: "#FF6FA5",
    desc: "Root-cause diagnosis",
  },
  {
    key: "remediate",
    label: "REMEDIATE",
    icon: Wrench,
    color: "#16A34A",
    desc: "Harder variants generated",
  },
  {
    key: "retrain",
    label: "RETRAIN",
    icon: RefreshCw,
    color: "#7C4DFF",
    desc: "Model updated each round",
  },
];

const METRICS = [
  { value: "67", label: "ATTACK VECTORS" },
  { value: "15", label: "ATTACK CATEGORIES" },
  { value: "5", label: "SIMULATED FAMILIES" },
  { value: "3", label: "CLOSED-LOOP ROUNDS" },
];

const FAMILIES = [
  "Card Abuse",
  "Account Takeover",
  "Bot / Automation",
  "Adversarial-ML",
  "Poisoning",
];

const CAPABILITIES = [
  {
    icon: Crosshair,
    title: "IDENTIFY",
    color: "#ccb9ff",
    bg: "bg-statPink",
    desc: "67 attack vectors mapped across 15 categories of emerging payment-fraud threats.",
  },
  {
    icon: FlaskConical,
    title: "GENERATE",
    color: "#B8860B",
    bg: "bg-statYellow",
    desc: "High-fidelity simulation of five attack families using behavioral attack signatures.",
  },
  {
    icon: Shield,
    title: "DEFEND",
    color: "#2F8FFF",
    bg: "bg-statBlue",
    desc: "An ensemble combining XGBoost classification with Isolation Forest anomaly detection.",
  },
];

const ROUNDS = [
  { round: 1, recall: 93.3 },
  { round: 2, recall: 97.8 },
  { round: 3, recall: 100 },
];

export default function Landing() {
  const [activeStage, setActiveStage] = useState(null);

  return (
    <div className="min-h-screen bg-[#F7F8FC] relative overflow-x-hidden">

      {/* =========================================================
          FIXED BACKGROUND
          Stays inside the browser viewport while page content scrolls.
          ========================================================= */}

      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
  <div className="absolute inset-0">
    <PrismaticBurst
      colors={["#5227FF", "#7C4DFF", "#2F8FFF"]}
      backgroundColor="#F7F8FC"
      speed={0.3}
      streakCount={4}
      streakWidth={1.5}
      streakLength={1}
      density={0.5}
      twinkle={0.15}
      glow={1.2}
      backgroundGlow={0.02}
      zoom={3.2}
      opacity={1}
      mouseInteraction={true}
      lightMode={true}
    />
  </div>

  {/* Flat even veil across the WHOLE canvas — kills the left/right imbalance */}
  <div
    className="absolute inset-0"
    style={{ background: "rgba(247,248,252,0.55)" }}
  />

  {/* Translucent blob behind the hero text only */}
  <div
    className="absolute inset-0"
    style={{
      background:
        "radial-gradient(ellipse 55% 45% at 50% 22%, rgba(255,255,255,0.7) 0%, rgba(255,255,255,0.35) 50%, rgba(255,255,255,0) 78%)",
    }}
  />
</div>

      {/* =========================================================
          CONTENT
          ========================================================= */}

      <div className="relative z-10">

        {/* HEADER */}
        <header className="flex items-center gap-2 px-8 py-6">
          <Shield className="text-purple" size={24} />

          <div>
            <div className="font-heading font-extrabold text-base tracking-wide">
              AI DEFENSE LAB
            </div>

            <div className="text-[10px] text-textMuted font-medium tracking-wide">
              PAYMENT SECURITY
            </div>
          </div>
        </header>


<div className="max-w-5xl mx-auto px-6">
  {/* Added mb-12 here to push lower components away */}
  <div className="bg-white/60 backdrop-blur-md rounded-[32px] px-6 md:px-12 py-10 md:py-14 border border-white/40 shadow-[0_8px_40px_rgba(80,50,200,0.08)] mb-12">


        {/* =======================================================
            HERO
            ======================================================= */}

        <section className="flex flex-col items-center text-center pb-8">
      <span className="text-xs font-bold tracking-[0.2em] text-purple uppercase mb-4">
        AI Defense Lab · Payment Security
      </span>

      <h1 className="font-heading font-extrabold text-4xl md:text-6xl max-w-4xl leading-[1.04] text-textPrimary tracking-tight">
        BUILD THE ATTACK.
        <br />
        MAKE THE DEFENSE STRONGER.
      </h1>

      <p className="text-textSecondary font-normal mt-5 max-w-2xl text-base leading-relaxed">
        An end-to-end AI security system that identifies emerging
        GenAI-powered payment fraud, simulates adversarial attacks,
        detects them, and learns from missed attacks.
      </p>

      <Link
        to="/app"
        className="btn-fx mt-8 inline-flex items-center gap-2 !px-8 !py-3 !text-base font-bold"
      >
            ENTER COMMAND CENTER
            <ArrowRight size={18} />
      </Link>
    </section>

    {/* CLOSED LOOP PIPELINE */}
    <section>
      <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
        {STAGES.map((stage, index) => {
          const Icon = stage.icon;
          return (
            <div
              key={stage.key}
              onMouseEnter={() => setActiveStage(stage.key)}
              onMouseLeave={() => setActiveStage(null)}
              className="relative bg-white border border-border rounded-2xl p-3 text-center cursor-default transition-all duration-200"
              style={{
                borderColor: activeStage === stage.key ? stage.color : undefined,
                transform: activeStage === stage.key ? "translateY(-3px)" : undefined,
                boxShadow: activeStage === stage.key ? `0 8px 24px ${stage.color}30` : undefined,
              }}
            >
              <Icon size={18} className="mx-auto mb-1.5" style={{ color: stage.color }} />
              <div className="text-[11px] font-heading font-extrabold tracking-wide">{stage.label}</div>
              {activeStage === stage.key && (
                <div className="text-[10px] text-textSecondary font-normal mt-1">{stage.desc}</div>
              )}
              {index < STAGES.length - 1 && (
                <ArrowRight size={12} className="hidden md:block absolute -right-3 top-1/2 -translate-y-1/2 text-textMuted" />
              )}
            </div>
          );
        })}
      </div>
    </section>

    {/* KEY METRICS */}
    <section className="mt-10">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-5">
        {METRICS.map((metric) => (
          <div key={metric.label} className="text-center">
            <div className="font-heading font-extrabold text-4xl text-textPrimary">{metric.value}</div>
            <div className="text-[10px] font-bold text-textMuted tracking-wide mt-1">{metric.label}</div>
          </div>
        ))}
      </div>
      <div className="flex flex-wrap justify-center gap-2">
        {FAMILIES.map((family) => (
          <span key={family} className="text-xs font-semibold px-3 py-1.5 rounded-full border border-border bg-white text-textSecondary">
            {family}
          </span>
        ))}
      </div>
    </section>

  </div>
</div>
            

        {/* =======================================================
            THREE CORE CAPABILITIES
            ======================================================= */}

        <section className="px-6 max-w-5xl mx-auto mb-14">

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">

            {CAPABILITIES.map((capability) => {
              const Icon = capability.icon;

              return (
                <div
                  key={capability.title}
                  className={`metric-blob-card p-6 text-left ${capability.bg}`}
                >
                  <Icon
                    size={22}
                    className="relative z-10 mb-3"
                    style={{ color: capability.color }}
                  />

                  <div className="font-heading font-extrabold relative z-10">
                    {capability.title}
                  </div>

                  <div className="text-sm text-textSecondary font-normal mt-1 leading-relaxed relative z-10">
                    {capability.desc}
                  </div>
                </div>
              );
            })}

          </div>
        </section>

        {/* =======================================================
            CLOSED LOOP EVALUATION
            ======================================================= */}

        <section className="px-6 max-w-4xl mx-auto mb-14">

          <div className="text-center mb-6">

            <span className="text-[11px] font-bold tracking-[0.15em] text-textMuted uppercase">
              3-Round Simulated Evaluation
            </span>

            <h2 className="font-heading font-extrabold text-2xl mt-1">
              Closed-Loop Evaluation
            </h2>

          </div>

          <div className="bg-white/90 backdrop-blur-sm border border-border rounded-2xl p-6">

            <div className="flex items-end justify-center gap-10 mb-6">

              {ROUNDS.map((round) => (
                <div key={round.round} className="text-center">

                  <div
                    className="w-14 rounded-t-lg mx-auto"
                    style={{
                      height: `${round.recall}px`,
                      background:
                        round.recall === 100
                          ? "#16A34A"
                          : "#7C4DFF",
                    }}
                  />

                  <div className="font-heading font-extrabold text-lg mt-2">
                    {round.recall}%
                  </div>

                  <div className="text-[11px] font-bold text-textMuted">
                    ROUND {round.round}
                  </div>

                </div>
              ))}

            </div>

            <div className="grid grid-cols-5 gap-3 border-t border-border pt-4">

              {[
                ["Precision", "100%"],
                ["Recall", "100%"],
                ["F1", "100%"],
                ["ROC-AUC", "100%"],
                ["FPR", "0%"],
              ].map(([label, value]) => (
                <div key={label} className="text-center">

                  <div className="font-heading font-extrabold text-success text-lg">
                    {value}
                  </div>

                  <div className="text-[10px] font-bold text-textMuted">
                    {label}
                  </div>

                </div>
              ))}

            </div>

          </div>
        </section>

        {/* =======================================================
            DIFFERENTIATOR
            ======================================================= */}

        <section className="px-6 max-w-3xl mx-auto pb-20 text-center">

          <h3 className="font-heading font-extrabold text-xl md:text-2xl">
            EVERY MISSED ATTACK BECOMES A{" "}
            <span className="text-danger">
              NEW DEFENSE SIGNAL.
            </span>
          </h3>

          <div className="flex flex-wrap items-center justify-center gap-2 mt-5 text-xs font-bold">

            {[
              "MISS",
              "OBSERVE",
              "REMEDIATE",
              "RETRAIN",
              "STRONGER DEFENSE",
            ].map((step, index, array) => (
              <React.Fragment key={step}>

                <span
                  className={`px-3 py-1.5 rounded-full border ${
                    index === array.length - 1
                      ? "bg-green-50 border-green-300 text-success"
                      : "bg-white/90 border-border text-textSecondary"
                  }`}
                >
                  {step}
                </span>

                {index < array.length - 1 && (
                  <ArrowRight
                    size={12}
                    className="text-textMuted"
                  />
                )}

              </React.Fragment>
            ))}

          </div>

        </section>

      </div>
    </div>
  );
}