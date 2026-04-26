import { useCallback, useMemo, useRef, useState } from "react";
import { API_BASE_URL } from "../config/api";

export function useSkillsProfile(country, intakeGreeting) {
  const [messages, setMessages] = useState(() =>
    intakeGreeting
      ? [{ role: "assistant", content: intakeGreeting }]
      : [{ role: "assistant", content: "Hello! Tell me what kind of work you've been doing." }]
  );
  const [isStreaming, setIsStreaming] = useState(false);
  const [profile, setProfile] = useState(null);
  const [profileCard, setProfileCard] = useState(null);
  const [occupation, setOccupation] = useState(null);
  const [profileErrors, setProfileErrors] = useState([]);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);

  const isProfileReady = useMemo(() => Boolean(profileCard), [profileCard]);

  async function generateProfileCardWithClaude(extracted, countryConfig) {
    const system = `Given extracted skills data, generate a human-readable skills profile card.

Output ONLY this JSON:
{
  "summary_paragraph": "2-3 sentence plain English summary the user can read to an employer",
  "key_skills": [
    {
      "skill": "plain skill name",
      "what_it_means": "one practical sentence",
      "category": "technical|interpersonal|digital|language"
    }
  ],
  "occupation_cluster": "plain language description of work type",
  "isco_search_terms": ["search terms for occupation label"],
  "honest_gaps": ["1-2 honest gaps or limitations to acknowledge"]
}

Be warm but honest. Do not inflate skills. Do not invent credentials.`;

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
        max_tokens: 900,
        temperature: 0.3,
        system: `${system}\n\nCountry context:\n${JSON.stringify(countryConfig || {})}`,
        messages: [{ role: "user", content: JSON.stringify(extracted) }]
      })
    });

    const data = await response.json();
    let text = data?.content?.[0]?.text?.trim?.() || "";
    const start = text.indexOf("{");
    const end = text.lastIndexOf("}");
    if (start === -1 || end === -1) throw new Error("Claude did not return JSON for profile card.");
    return JSON.parse(text.slice(start, end + 1));
  }

  const sendMessage = useCallback(
    async (text) => {
      setError(null);
      const userMsg = { role: "user", content: text };
      const nextHistory = [...messages, userMsg];
      setMessages(nextHistory);

      setIsStreaming(true);
      abortRef.current?.abort?.();
      const controller = new AbortController();
      abortRef.current = controller;

      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      try {
        const res = await fetch(`${API_BASE_URL}/intake/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ messages: nextHistory, country }),
          signal: controller.signal
        });
        if (!res.ok || !res.body) {
          throw new Error(await res.text());
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let assistantText = "";
        let buffer = "";
        let extractionJson = null;
        let streamErrorJson = null;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;

          const errIdx = buffer.indexOf("[STREAM_ERROR]");
          if (errIdx !== -1) {
            assistantText += buffer.slice(0, errIdx);
            const jsonPart = buffer.slice(errIdx + "[STREAM_ERROR]".length);
            buffer = "";
            streamErrorJson = jsonPart;
            break;
          }

          const markerIdx = buffer.indexOf("[EXTRACTION_COMPLETE]");
          if (markerIdx !== -1) {
            assistantText += buffer.slice(0, markerIdx);
            const jsonPart = buffer.slice(markerIdx + "[EXTRACTION_COMPLETE]".length);
            buffer = ""; // stop rendering after marker
            extractionJson = jsonPart;
            break;
          } else {
            assistantText += buffer;
            buffer = "";
          }

          setMessages((prev) => {
            const copy = [...prev];
            copy[copy.length - 1] = { role: "assistant", content: assistantText };
            return copy;
          });
        }

        // finalize assistant message
        setMessages((prev) => {
          const copy = [...prev];
          copy[copy.length - 1] = { role: "assistant", content: assistantText.trim() || assistantText };
          return copy;
        });

        if (streamErrorJson) {
          const start = streamErrorJson.indexOf("{");
          const end = streamErrorJson.lastIndexOf("}");
          const detail =
            start !== -1 && end !== -1 ? streamErrorJson.slice(start, end + 1) : JSON.stringify({ error: "Stream failed" });
          throw new Error(detail);
        }

        if (extractionJson) {
          const start = extractionJson.indexOf("{");
          const end = extractionJson.lastIndexOf("}");
          if (start === -1 || end === -1) throw new Error("Extraction JSON not found in stream.");
          const extracted = JSON.parse(extractionJson.slice(start, end + 1));
          setProfile(extracted);

          // WDI-only data layer: generate profile card directly via Claude from the browser.
          const card = await generateProfileCardWithClaude(extracted, null);
          setProfileCard(card);
          const extractedProfile = extracted?.profile || {};
          setOccupation({
            occupation_label: card.occupation_cluster || extractedProfile.primary_occupation_description || "Unknown",
            isco_code: null,
            isced_level: extractedProfile.isced_level,
            essential_skills: (card.key_skills || []).map((s) => ({ name: s.skill }))
          });
          setProfileErrors([]);
        }
      } catch (e) {
        setError(e);
      } finally {
        setIsStreaming(false);
      }
    },
    [country, messages]
  );

  return {
    messages,
    sendMessage,
    isStreaming,
    profile,
    profileCard,
    occupation,
    profileErrors,
    isProfileReady,
    error
  };
}

