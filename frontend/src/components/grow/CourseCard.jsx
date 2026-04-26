import React from "react";

const formatIcons = {
  video: "🎬",
  text: "📄",
  audio: "🎙️",
  SMS: "💬",
  offline: "📦"
};

const costColors = {
  Free: "bg-green-100 text-green-700",
  Freemium: "bg-amber-100 text-amber-700",
  Paid: "bg-slate-100 text-slate-600"
};

export default function CourseCard({ course }) {
  if (!course) return null;
  const icon = formatIcons[course.format] || "📘";
  const costClass = costColors[course.cost] || "bg-slate-100 text-slate-600";

  return (
    <div className="flex items-start justify-between gap-3 py-2">
      <div className="flex items-start gap-2">
        <div className="text-lg" aria-hidden="true">
          {icon}
        </div>
        <div>
          <div className="text-sm font-semibold text-slate-800">
            {course.name} <span className="text-slate-500 font-normal">— {course.provider}</span>
          </div>
          <div className="text-xs text-slate-500 mt-1">
            {course.duration} · {course.mobile_friendly ? "📱" : "💻"} · {course.language}
          </div>
          {course.why_this_one ? <div className="text-xs text-slate-500 mt-1">{course.why_this_one}</div> : null}
          {course.url ? (
            <a href={course.url} target="_blank" rel="noopener noreferrer" className="text-xs text-teal-700 underline mt-1 inline-block">
              Visit resource →
            </a>
          ) : null}
        </div>
      </div>
      <div className={`text-xs px-2 py-1 rounded-full ${costClass}`}>{course.cost || "Free"}</div>
    </div>
  );
}

