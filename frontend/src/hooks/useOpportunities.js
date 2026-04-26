import { useState } from "react";

export function useOpportunities() {
  const [matches, setMatches] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function generateMatches(occupation, wdiData, sectorTrends, countryConfig) {
    setLoading(true);
    setError(null);

    const wdiSummary = Object.entries(wdiData || {})
      .filter(([, v]) => v?.value !== null && v?.value !== undefined)
      .map(([, v]) => `${v.label}: ${v.value} ${v.unit} (${v.year}) · ${v.source}`)
      .join("\n");

    const prompt = `You are a labor market analyst for low-income countries.

Country: ${countryConfig.country_name}
Occupation: ${occupation.occupation_label} (ISCO ${occupation.isco_code})
Skills: ${(occupation.essential_skills || []).map((s) => s.name).join(", ")}
Education: ISCED ${occupation.isced_level || 2}

Real World Bank WDI Data:
${wdiSummary}

Sector employment trends (recent years):
Agriculture: ${JSON.stringify(sectorTrends?.agriculture?.slice(-3))}
Services: ${JSON.stringify(sectorTrends?.services?.slice(-3))}
Industry: ${JSON.stringify(sectorTrends?.industry?.slice(-3))}

Generate exactly 4 honest, reachable opportunity matches grounded in the real WDI numbers above.

Return ONLY this JSON:
{
  "matches": [
    {
      "title": "opportunity title",
      "type": "formal_employment|self_employment|gig|training",
      "why_it_matches": "one sentence referencing their specific skills",
      "sector": "Agriculture|Services|Industry|Trade|ICT",
      "wage_signal": {
        "description": "specific insight from WDI data",
        "value": number,
        "unit": "unit label",
        "source": "World Bank WDI [year]"
      },
      "growth_signal": {
        "description": "specific trend insight from WDI data",
        "value": number,
        "unit": "unit label",
        "source": "World Bank WDI [year]"
      },
      "honest_barrier": "one real obstacle",
      "first_step": "single most actionable next step"
    }
  ]
}`;

    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": import.meta.env.VITE_ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "anthropic-dangerous-direct-browser-access": "true"
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 2000,
        messages: [{ role: "user", content: prompt }]
      })
    });

    const data = await response.json();
    let text = data?.content?.[0]?.text?.trim?.() || "";
    if (text.startsWith("```")) {
      text = text.split("```")[1];
      if (text.startsWith("json")) text = text.slice(4);
    }
    const result = JSON.parse(text.trim());
    setMatches(result.matches);
    setLoading(false);
  }

  return { matches, loading, error, generateMatches };
}

