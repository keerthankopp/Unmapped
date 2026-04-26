import React, { useMemo } from "react";

const COUNTRIES = [
  { id: "ghana", label: "Ghana", emoji: "🇬🇭", region: "West Africa" },
  { id: "nigeria", label: "Nigeria", emoji: "🇳🇬", region: "West Africa" },
  { id: "kenya", label: "Kenya", emoji: "🇰🇪", region: "East Africa" },
  { id: "ethiopia", label: "Ethiopia", emoji: "🇪🇹", region: "East Africa" },
  { id: "india", label: "India", emoji: "🇮🇳", region: "South Asia" },
  { id: "bangladesh", label: "Bangladesh", emoji: "🇧🇩", region: "South Asia" },
  { id: "pakistan", label: "Pakistan", emoji: "🇵🇰", region: "South Asia" },
  { id: "philippines", label: "Philippines", emoji: "🇵🇭", region: "Southeast Asia" }
];

export default function CountrySelector({ country, onChange, disabled }) {
  const grouped = useMemo(() => {
    const map = new Map();
    for (const c of COUNTRIES) {
      if (!map.has(c.region)) map.set(c.region, []);
      map.get(c.region).push(c);
    }
    return Array.from(map.entries());
  }, []);

  return (
    <label className="flex items-center gap-2 text-sm text-slate-700">
      <span className="text-slate-500">Country:</span>
      <select
        className="bg-white border border-slate-200 rounded-xl px-2 py-1"
        value={country}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      >
        {grouped.map(([region, items]) => (
          <optgroup key={region} label={region}>
            {items.map((c) => (
              <option key={c.id} value={c.id}>
                {c.label} {c.emoji}
              </option>
            ))}
          </optgroup>
        ))}
      </select>
    </label>
  );
}

