import React, { useEffect } from "react";
import ErrorCard from "../shared/ErrorCard";
import SkillTrackCard from "./SkillTrackCard";
import { useGrowRecommendations } from "../../hooks/useGrowRecommendations";

export default function GrowDashboard({ occupation, wdiHook, countryConfig }) {
  const { recommendations, isLoading, error, fetchRecommendations } = useGrowRecommendations();
  const { data: wdiData, loading: wdiLoading } = wdiHook || {};

  useEffect(() => {
    if (!occupation || !wdiData || wdiLoading || !countryConfig) return;
    if (recommendations || isLoading) return;
    fetchRecommendations({ occupation, wdiData, countryConfig });
  }, [occupation, wdiData, wdiLoading, countryConfig, recommendations, isLoading]);

  if (!occupation) {
    return (
      <div className="bg-white shadow-sm rounded-2xl p-4 text-sm text-slate-600">
        Complete your Skills intake first to unlock personalized growth tracks.
      </div>
    );
  }

  if (error) {
    return <ErrorCard message="Could not generate Grow recommendations" endpoint="api.anthropic.com" action={error} />;
  }

  if (isLoading || wdiLoading || !recommendations) {
    return <div className="text-sm text-slate-500">Building your Grow plan from live WDI signals…</div>;
  }

  const data = recommendations;

  return (
    <div className="flex flex-col gap-3">
      <div className="bg-teal-700 text-white rounded-2xl p-4">
        <p className="text-xs uppercase tracking-wide opacity-70 mb-1">Your Growth Direction</p>
        <p className="font-bold text-lg leading-snug">{data.headline}</p>
      </div>

      {data.quick_win ? (
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xl" aria-hidden="true">
              ⚡
            </span>
            <p className="font-bold text-amber-800">This Week&apos;s Quick Win</p>
          </div>
          <p className="text-slate-700 font-medium">{data.quick_win.action}</p>
          <p className="text-sm text-slate-500 mt-1">{data.quick_win.outcome}</p>
          {data.quick_win.resource_url ? (
            <a href={data.quick_win.resource_url} target="_blank" rel="noopener noreferrer" className="text-xs text-teal-700 underline mt-2 block">
              {data.quick_win.resource} →
            </a>
          ) : null}
        </div>
      ) : null}

      {(data.skill_tracks || []).map((track) => (
        <SkillTrackCard key={track.track_name} track={track} />
      ))}

      {data.long_game ? (
        <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4">
          <p className="font-bold text-slate-700 mb-1">🎯 12-Month Goal</p>
          <p className="text-slate-600">{data.long_game.goal}</p>
          <p className="text-sm text-teal-700 font-medium mt-2">{data.long_game.market_opportunity}</p>
          <p className="text-sm text-slate-600 mt-2">{data.long_game.path}</p>
        </div>
      ) : null}

      {data.avoid?.length ? (
        <div className="bg-red-50 border border-red-100 rounded-2xl p-3">
          <p className="text-xs font-semibold text-red-600 uppercase tracking-wide mb-1">⚠️ Avoid</p>
          <p className="text-sm text-slate-600">{data.avoid[0]}</p>
        </div>
      ) : null}
    </div>
  );
}

