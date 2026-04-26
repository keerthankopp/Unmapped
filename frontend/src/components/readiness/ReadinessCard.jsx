import React from "react";
import ErrorCard from "../shared/ErrorCard";

function Gauge({ pct, color }) {
  const r = 42;
  const c = 2 * Math.PI * r;
  const dash = c * pct;
  const rest = c - dash;
  const stroke = color === "red" ? "#ef4444" : color === "yellow" ? "#f59e0b" : "#22c55e";

  return (
    <svg width="120" height="120" viewBox="0 0 120 120" className="mx-auto">
      <circle cx="60" cy="60" r={r} fill="none" stroke="#e2e8f0" strokeWidth="10" />
      <circle
        cx="60"
        cy="60"
        r={r}
        fill="none"
        stroke={stroke}
        strokeWidth="10"
        strokeDasharray={`${dash} ${rest}`}
        strokeLinecap="round"
        transform="rotate(-90 60 60)"
      />
      <text x="60" y="66" textAnchor="middle" fontSize="18" fontWeight="700" fill="#0f172a">
        {Math.round(pct * 100)}%
      </text>
    </svg>
  );
}

export default function ReadinessCard({ countryName, wdiHook }) {
  const { data, loading, error } = wdiHook || {};

  if (error) {
    return (
      <ErrorCard
        message="Could not reach World Bank WDI"
        endpoint="api.worldbank.org"
        action="Check network or try again"
      />
    );
  }

  const internet = data?.internet_users;
  const vuln = data?.vulnerable_employment;
  const youthUnemp = data?.youth_unemployment;

  const pct = internet?.value !== null && internet?.value !== undefined ? Math.max(0, Math.min(1, internet.value / 100)) : null;
  const color = pct === null ? "yellow" : pct < 0.35 ? "green" : pct < 0.65 ? "yellow" : "red";

  return (
    <div className="bg-white shadow-sm rounded-2xl p-4">
      <div className="text-sm font-semibold">Readiness context (WDI-only)</div>
      {loading ? <div className="text-sm text-slate-500 mt-2">Loading live World Bank WDI…</div> : null}

      {pct !== null ? (
        <>
          <div className="mt-3">
            <Gauge pct={pct} color={color} />
            <div className="text-xs text-slate-500 text-center mt-2">Calibrated for {countryName}</div>
          </div>

          <div className="mt-4 text-sm text-slate-700">
            Internet access (proxy for automation feasibility): <span className="font-semibold">{internet?.value ?? "—"}%</span>
          </div>
          <div className="text-xs text-slate-400 italic mt-1">
            {internet?.source || "World Bank WDI"} {internet?.year || ""}
          </div>

          <div className="mt-4 text-sm text-slate-700">
            Vulnerable employment (proxy for informality/standardization):{" "}
            <span className="font-semibold">{vuln?.value ?? "—"}%</span>
          </div>
          <div className="text-xs text-slate-400 italic mt-1">
            {vuln?.source || "World Bank WDI"} {vuln?.year || ""}
          </div>

          <div className="mt-4 text-sm text-slate-700">
            Youth unemployment: <span className="font-semibold">{youthUnemp?.value ?? "—"}%</span>
          </div>
          <div className="text-xs text-slate-400 italic mt-1">
            {youthUnemp?.source || "World Bank WDI"} {youthUnemp?.year || ""}
          </div>
        </>
      ) : (
        <div className="text-sm text-slate-500 mt-2">No proxy score available yet.</div>
      )}
    </div>
  );
}

