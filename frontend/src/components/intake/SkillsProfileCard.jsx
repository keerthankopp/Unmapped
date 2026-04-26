import React from "react";

function chipColor(category) {
  if (category === "technical") return "bg-slate-100 text-slate-800";
  if (category === "interpersonal") return "bg-teal-50 text-teal-800";
  if (category === "digital") return "bg-blue-50 text-blue-800";
  if (category === "language") return "bg-purple-50 text-purple-800";
  return "bg-slate-100 text-slate-800";
}

export default function SkillsProfileCard({ profileCard, title }) {
  if (!profileCard) return null;

  return (
    <div className="bg-white shadow-sm rounded-2xl p-4 print-card">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-xs text-slate-500">{title || "Your Skills Profile"}</div>
          <div className="text-xl font-semibold mt-1">{profileCard.occupation_cluster}</div>
        </div>
        <button
          className="no-print px-3 py-2 rounded-xl bg-slate-100 text-slate-700 text-sm"
          onClick={() => window.print()}
        >
          Download as PDF
        </button>
      </div>

      <div className="mt-3 bg-teal-50 border border-teal-100 rounded-2xl p-3">
        <div className="text-sm text-slate-700">{profileCard.summary_paragraph}</div>
      </div>

      <div className="mt-4">
        <div className="text-sm font-semibold">Key skills</div>
        <div className="flex flex-wrap gap-2 mt-2">
          {(profileCard.key_skills || []).map((s, idx) => (
            <div key={idx} className={"px-3 py-2 rounded-full text-xs " + chipColor(s.category)}>
              <div className="font-semibold">{s.skill}</div>
              <div className="text-[11px] opacity-80">{s.what_it_means}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-4 bg-amber-50 border border-amber-100 rounded-2xl p-3">
        <div className="text-sm font-semibold text-amber-900">Honest gaps</div>
        <ul className="mt-1 text-sm text-amber-900 list-disc pl-5">
          {(profileCard.honest_gaps || []).map((g, idx) => (
            <li key={idx}>{g}</li>
          ))}
        </ul>
      </div>

      {/* WDI-only mode: no external occupation taxonomy API */}
    </div>
  );
}

