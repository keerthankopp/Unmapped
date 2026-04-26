import { useEffect, useState } from "react";
import { API_BASE_URL } from "../config/api";

export function useConfig(country) {
  const [config, setConfig] = useState(null);
  const [availableCountries, setAvailableCountries] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setIsLoading(true);
      setError(null);
      setConfig(null);
      setAvailableCountries([]);
      try {
        const res = await fetch(`${API_BASE_URL}/config/${country}`);
        if (!res.ok) throw new Error(await res.text());
        const json = await res.json();
        if (!cancelled) {
          setConfig(json.config);
          setAvailableCountries(json.available_countries || []);
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

  return { config, availableCountries, isLoading, error };
}

