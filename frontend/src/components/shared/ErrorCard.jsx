import React from "react";

export default function ErrorCard({ message, endpoint, action }) {
  return (
    <div className="bg-white shadow-sm rounded-2xl p-4 border border-red-200">
      <div className="text-sm font-semibold text-red-700">{message}</div>
      {endpoint ? <div className="text-xs text-slate-500 mt-1">Endpoint: {endpoint}</div> : null}
      {action ? <div className="text-xs text-slate-500 mt-1">{action}</div> : null}
    </div>
  );
}

