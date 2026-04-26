import { useState } from "react";

const GROW_PROMPT = `
You are a career development advisor for young workers in low-income countries.

Given a worker's occupation and real economic context data, generate personalized learning and market readiness recommendations.

Rules:
- Every recommendation must be accessible on a smartphone with limited data
- Prioritize FREE resources first, paid second
- Be realistic about what is achievable without formal credentials
- Reference the actual country context — what skills are growing in THAT labor market
- Include one "quick win" (learnable in days/weeks) and one "long game" (months)
- If internet penetration is low, prioritize offline-compatible or SMS-based options

Reference resources (examples of real platforms; prefer these):
- Coursera: coursera.org (audit for free)
- edX: edx.org (audit for free)
- Khan Academy: khanacademy.org (free)
- Google Digital Garage: learndigital.withgoogle.com (free)
- Alison: alison.com (free with ads)
- LinkedIn Learning: linkedin.com/learning (trial)
- atingi: atingi.org (free, offline-capable)
- SWAYAM: swayam.gov.in (India)
- DigiSkills Pakistan: digiskills.pk (Pakistan)
- freeCodeCamp (YouTube)
- Kolibri by Learning Equality (offline capable)

Return ONLY this JSON:
{
  "headline": "One sentence summarizing this person's growth direction",
  "skill_tracks": [
    {
      "track_name": "short track name e.g. Digital Payments",
      "why_now": "one sentence why this matters in their specific country context right now",
      "automation_relevance": "protects|complements|pivots",
      "time_to_basic": "e.g. 2 weeks",
      "time_to_job_ready": "e.g. 3 months",
      "difficulty": "beginner|intermediate",
      "skills_to_learn": ["specific skill 1", "specific skill 2", "specific skill 3"],
      "courses": [
        {
          "name": "course or resource name",
          "provider": "provider name",
          "url": "real URL — only include if you are confident it exists",
          "cost": "Free|Freemium|Paid",
          "format": "video|text|audio|SMS|offline",
          "duration": "e.g. 6 hours total",
          "mobile_friendly": true,
          "language": "English or local language if available",
          "why_this_one": "one sentence specific reason"
        }
      ],
      "market_signal": "one concrete sentence about demand for this skill in their country using the WDI data provided"
    }
  ],
  "quick_win": {
    "action": "single most impactful thing they can do this week",
    "resource": "specific free resource name",
    "resource_url": "real URL",
    "outcome": "what they will be able to do after"
  },
  "long_game": {
    "goal": "where they could realistically be in 12 months",
    "path": "3-step plain language progression",
    "market_opportunity": "what economic opportunity this unlocks in their country"
  },
  "avoid": ["one type of training to avoid wasting time on given their context"]
}

Generate exactly 3 skill tracks.
`;

export function useGrowRecommendations() {
  const [recommendations, setRecommendations] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecommendations = async ({ occupation, wdiData, countryConfig }) => {
    setIsLoading(true);
    setError(null);
    try {
      const wdiSummary = Object.entries(wdiData || {})
        .filter(([, v]) => v?.value !== null && v?.value !== undefined)
        .map(([, v]) => `${v.label}: ${v.value} ${v.unit} (${v.year}) · ${v.source}`)
        .join("\n");

      const prompt = `${GROW_PROMPT}

Country: ${countryConfig.country_name}
Currency: ${countryConfig.currency_label}
Internet users: ${wdiData?.internet_users?.value ?? "unavailable"}%
Mobile subscriptions per 100: ${wdiData?.mobile_subscriptions?.value ?? "unavailable"}
Informal economy share (config): ${Math.round((countryConfig.informal_economy_share || 0) * 100)}%
Primary sectors (config): ${(countryConfig.primary_sectors || []).join(", ")}

Worker occupation: ${occupation?.occupation_label}
Current skills: ${(occupation?.essential_skills || []).map((s) => s.name).join(", ")}

WDI economic signals:
${wdiSummary}
`;

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
          max_tokens: 3000,
          temperature: 0.3,
          messages: [{ role: "user", content: prompt }]
        })
      });

      const data = await response.json();
      let text = data?.content?.[0]?.text?.trim?.() || "";
      const start = text.indexOf("{");
      const end = text.lastIndexOf("}");
      if (start === -1 || end === -1) throw new Error("Claude did not return JSON.");
      const parsed = JSON.parse(text.slice(start, end + 1));
      setRecommendations(parsed);
    } catch (e) {
      setError(e.message || String(e));
    } finally {
      setIsLoading(false);
    }
  };

  return { recommendations, isLoading, error, fetchRecommendations };
}

