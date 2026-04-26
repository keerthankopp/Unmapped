import React, { useEffect, useState } from "react";
import CountrySelector from "./components/shared/CountrySelector";
import ErrorCard from "./components/shared/ErrorCard";
import ConversationalIntake from "./components/intake/ConversationalIntake";
import SkillsProfileCard from "./components/intake/SkillsProfileCard";
import ReadinessCard from "./components/readiness/ReadinessCard";
import YouthDashboard from "./components/opportunity/YouthDashboard";
import PolicymakerDashboard from "./components/opportunity/PolicymakerDashboard";
import GrowDashboard from "./components/grow/GrowDashboard";
import { useConfig } from "./hooks/useConfig";
import { useOpportunities } from "./hooks/useOpportunities";
import { useSkillsProfile } from "./hooks/useSkillsProfile";
import { useWDIData } from "./hooks/useWDIData";

export default function App() {
  const [country, setCountry] = useState("ghana");
  const [mode, setMode] = useState("youth"); // youth | policymaker
  const [tab, setTab] = useState("skills"); // skills | readiness | opportunities
  const [toast, setToast] = useState(null);

  const { config, isLoading: configLoading, error: configError } = useConfig(country);

  const skillsHook = useSkillsProfile(country, config?.ui?.intake_greeting);

  const iso3 = config?.wb_iso3;
  const wdiHook = useWDIData(iso3);

  const oppHook = useOpportunities();

  useEffect(() => {
    if (!skillsHook.occupation || !wdiHook.data || wdiHook.loading || !config) return;
    oppHook.generateMatches(skillsHook.occupation, wdiHook.data, wdiHook.sectorTrends, config);
  }, [skillsHook.occupation, wdiHook.data, wdiHook.loading, wdiHook.sectorTrends, config]);

  return (
    <div className="min-h-screen flex flex-col">
      <div className="no-print bg-white border-b border-slate-200 px-4 py-3 flex items-center justify-between">
        <div className="font-semibold text-teal-700">UNMAPPED</div>
        <div className="flex items-center gap-3">
          <CountrySelector
            country={country}
            disabled={configLoading || Boolean(configError)}
            onChange={(c) => {
              setCountry(c);
              setToast(`Reconfiguring for ${c}…`);
              setTimeout(() => setToast(null), 1500);
            }}
          />
          <div className="flex items-center gap-1 bg-slate-100 rounded-xl p-1">
            <button
              className={`px-3 py-1 rounded-lg text-sm ${mode === "youth" ? "bg-white shadow-sm" : "text-slate-600"}`}
              onClick={() => setMode("youth")}
            >
              Youth
            </button>
            <button
              className={`px-3 py-1 rounded-lg text-sm ${
                mode === "policymaker" ? "bg-white shadow-sm" : "text-slate-600"
              }`}
              onClick={() => setMode("policymaker")}
            >
              Policymaker
            </button>
          </div>
        </div>
      </div>

      {toast ? (
        <div className="no-print px-4 py-2 text-sm bg-teal-50 text-teal-800 border-b border-teal-100">{toast}</div>
      ) : null}

      <div className="flex-1 px-4 py-4 max-w-3xl w-full mx-auto">
        {configLoading ? <div className="text-sm text-slate-500">Loading country config…</div> : null}
        {configError ? (
          <ErrorCard message="Could not load country config" endpoint="backend /config" action="Check backend or network" />
        ) : null}

        {tab === "skills" ? (
          <div className="flex flex-col gap-3">
            <ConversationalIntake hook={skillsHook} />
            {skillsHook.profileCard ? (
              <SkillsProfileCard
                profileCard={skillsHook.profileCard}
                title={config?.ui?.profile_title}
              />
            ) : null}
          </div>
        ) : null}

        {tab === "readiness" ? (
          <ReadinessCard countryName={config?.country_name || country} wdiHook={wdiHook} />
        ) : null}

        {tab === "opportunities" ? (
          mode === "policymaker" ? (
            <PolicymakerDashboard wdiHook={wdiHook} />
          ) : (
            <YouthDashboard hook={oppHook} currencyLabel={config?.currency_label} />
          )
        ) : null}

        {tab === "grow" ? (
          <GrowDashboard occupation={skillsHook.occupation} wdiHook={wdiHook} countryConfig={config} />
        ) : null}
      </div>

      <div className="no-print bg-white border-t border-slate-200 px-4 py-2 flex items-center justify-around">
        {[
          { id: "skills", label: "Skills" },
          { id: "readiness", label: "Readiness" },
          { id: "opportunities", label: "Opportunities" },
          { id: "grow", label: "Grow" }
        ].map((t) => (
          <button
            key={t.id}
            className={`text-sm px-3 py-2 rounded-xl ${tab === t.id ? "text-teal-700 font-semibold" : "text-slate-500"}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>
    </div>
  );
}

