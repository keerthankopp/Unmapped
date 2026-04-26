import React from "react";
import ErrorCard from "../shared/ErrorCard";

function StatCard({ icon, title, value, meta }) {
  return (
    <div className="bg-white shadow-sm rounded-2xl p-4">
      <div className="text-xs text-slate-500 flex items-center gap-2">
        <span aria-hidden="true">{icon}</span>
        <span>{title}</span>
      </div>
      <div className="text-2xl font-semibold mt-2">{value}</div>
      <div className="text-xs text-slate-400 italic mt-2">{meta}</div>
    </div>
  );
}

const POLICYMAKER_CARDS = [
  { key: "youth_unemployment", icon: "📉", highlight: true },
  { key: "vulnerable_employment", icon: "⚠️", highlight: true },
  { key: "self_employed", icon: "🧑‍🔧", highlight: false },
  { key: "employment_services", icon: "🏪", highlight: false },
  { key: "employment_agriculture", icon: "🌾", highlight: false },
  { key: "gdp_growth", icon: "📈", highlight: false },
  { key: "internet_users", icon: "📱", highlight: false },
  { key: "literacy_rate", icon: "📚", highlight: false },
  { key: "school_enrollment_secondary", icon: "🎓", highlight: false }
];

export default function PolicymakerDashboard({ wdiHook }) {
  const { data: wdi, loading, error } = wdiHook || {};

  if (error) {
    return <ErrorCard message="Could not reach World Bank WDI" endpoint="api.worldbank.org" action="Check network or try again" />;
  }
  if (loading || !wdi) {
    return <div className="text-sm text-slate-500">Loading live WDI indicators…</div>;
  }

  const formatValue = (item) => {
    if (!item || item.value === null || item.value === undefined) return "—";
    const v = item.value;
    if (item.unit === "USD") return `${Number(v).toFixed(0)} USD`;
    if ((item.unit || "").includes("%")) return `${Number(v).toFixed(1)}%`;
    if ((item.unit || "").includes("people")) return `${Number(v).toFixed(0)}`;
    return `${Number(v).toFixed(2)}${item.unit ? ` ${item.unit}` : ""}`;
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {POLICYMAKER_CARDS.map((c) => {
        const item = wdi[c.key];
        const meta = `${item?.source || "World Bank WDI"} ${item?.year || ""}`.trim();
        return <StatCard key={c.key} icon={c.icon} title={item?.label || c.key} value={formatValue(item)} meta={meta} />;
      })}
    </div>
  );
}

