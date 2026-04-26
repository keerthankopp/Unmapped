import React from "react";

export default function EconSignalBadge({ icon, label, value, source }) {
  return (
    <div className="inline-flex flex-col px-3 py-2 rounded-full bg-white border border-slate-200 shadow-sm">
      <div className="flex items-center gap-2">
        <span aria-hidden="true">{icon}</span>
        <div className="text-xs text-slate-500">{label}</div>
        <div className="text-sm font-semibold text-slate-800">{value}</div>
      </div>
      <div className="text-[11px] text-slate-400 italic mt-1">{source}</div>
    </div>
  );
}

