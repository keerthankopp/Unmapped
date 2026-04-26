import React from "react";
import CourseCard from "./CourseCard";

const relevanceConfig = {
  protects: {
    bg: "bg-green-50",
    border: "border-green-200",
    badge: "bg-green-100 text-green-700",
    label: "Protects against automation"
  },
  complements: {
    bg: "bg-blue-50",
    border: "border-blue-200",
    badge: "bg-blue-100 text-blue-700",
    label: "Complements your current work"
  },
  pivots: {
    bg: "bg-purple-50",
    border: "border-purple-200",
    badge: "bg-purple-100 text-purple-700",
    label: "Opens a new career path"
  }
};

export default function SkillTrackCard({ track }) {
  if (!track) return null;
  const cfg = relevanceConfig[track.automation_relevance] || relevanceConfig.complements;

  return (
    <div className={`${cfg.bg} ${cfg.border} border rounded-2xl p-4`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-base font-semibold text-slate-800">{track.track_name}</div>
          <div className="text-xs text-slate-500 mt-1">{track.why_now}</div>
        </div>
        <div className="flex flex-col items-end gap-2">
          <div className={`text-xs px-2 py-1 rounded-full ${cfg.badge}`}>{cfg.label}</div>
          <div className="text-xs px-2 py-1 rounded-full bg-white/60 text-slate-700 border border-white/60">
            {track.difficulty}
          </div>
        </div>
      </div>

      {track.market_signal ? <div className="text-sm text-slate-700 mt-3">{track.market_signal}</div> : null}

      <div className="text-xs text-slate-600 mt-3">
        Basic: <span className="font-semibold">{track.time_to_basic}</span> · Job-ready:{" "}
        <span className="font-semibold">{track.time_to_job_ready}</span>
      </div>

      <div className="mt-3">
        <div className="text-sm font-semibold text-slate-800">Skills to learn</div>
        <div className="flex flex-wrap gap-2 mt-2">
          {(track.skills_to_learn || []).map((s, i) => (
            <span key={i} className="text-xs px-2 py-1 rounded-full bg-white/70 border border-white/70 text-slate-700">
              {s}
            </span>
          ))}
        </div>
      </div>

      <div className="mt-4">
        <div className="text-sm font-semibold text-slate-800">Courses</div>
        <div className="mt-2 divide-y divide-slate-200/60">
          {(track.courses || []).slice(0, 2).map((c, i) => (
            <CourseCard key={i} course={c} />
          ))}
        </div>
      </div>
    </div>
  );
}

