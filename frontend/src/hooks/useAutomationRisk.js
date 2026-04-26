import { useEffect, useState } from "react";
import { API_BASE_URL } from "../config/api";

export function useAutomationRisk(country) {
  const [wdiSnapshot, setWdiSnapshot] = useState(null);
  const [readinessProxy, setReadinessProxy] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setIsLoading(true);
      setError(null);
      setWdiSnapshot(null);
      setReadinessProxy(null);
      try {
        const res = await fetch(`${API_BASE_URL}/readiness/assess`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ country })
        });
        if (!res.ok) throw new Error(await res.text());
        const json = await res.json();
        if (!cancelled) {
          setWdiSnapshot(json.wdi_snapshot);
          setReadinessProxy(json.readiness_proxy);
        }
      } catch (e) {
        if (!cancelled) setError(e);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [country]);

  return { wdiSnapshot, readinessProxy, isLoading, error };
}

