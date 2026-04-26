import React from "react";
import EconSignalBadge from "../shared/EconSignalBadge";
import ErrorCard from "../shared/ErrorCard";

export default function YouthDashboard({ hook, currencyLabel }) {
  const { matches, isLoading, error } = hook;

  if (error) {
    return (
      <ErrorCard message="Could not reach opportunities service" endpoint="api.worldbank.org" action="Check network or try again" />
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {isLoading ? <div className="text-sm text-slate-500">Loading live opportunities…</div> : null}
      {(matches || []).slice(0, 5).map((m, idx) => (
        <div key={idx} className="bg-white shadow-sm rounded-2xl p-4 border border-teal-100">
          <div className="text-base font-semibold">{m.title}</div>
          <div className="text-sm text-slate-600 mt-1">{m.why_it_matches}</div>

          <div className="mt-3 flex flex-wrap gap-2">
            <EconSignalBadge
              icon="🏪"
              label="Sector employment share"
              value={`${m.wage_signal?.value ?? "—"}${m.wage_signal?.unit ? ` ${m.wage_signal.unit}` : ""}`}
              source={m.wage_signal?.source || "World Bank WDI"}
            />
            <EconSignalBadge
              icon="📈"
              label="GDP growth"
              value={`${m.growth_signal?.value ?? "—"}${m.growth_signal?.unit ? ` ${m.growth_signal.unit}` : ""}`}
              source={m.growth_signal?.source || "World Bank WDI"}
            />
          </div>

          <div className="mt-3 text-sm text-slate-700">
            <span className="font-semibold">Barrier:</span> {m.honest_barrier}
          </div>
          <div className="mt-2 text-sm text-slate-700">
            <span className="font-semibold">First step:</span> {m.first_step}
          </div>
        </div>
      ))}
      {!isLoading && (!matches || matches.length === 0) ? (
        <div className="bg-white shadow-sm rounded-2xl p-4 text-sm text-slate-500">No matches yet.</div>
      ) : null}
    </div>
  );
}

