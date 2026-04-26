const WB_BASE = "https://api.worldbank.org/v2";

const INDICATORS = {
  youth_unemployment: "SL.UEM.1524.ZS",
  gdp_per_capita: "NY.GDP.PCAP.CD",
  employment_agriculture: "SL.AGR.EMPL.ZS",
  employment_industry: "SL.IND.EMPL.ZS",
  employment_services: "SL.SRV.EMPL.ZS",
  school_enrollment_secondary: "SE.SEC.ENRR",
  youth_population: "SP.POP.1524.TO",
  youth_lfp_female: "SL.TLF.ACTI.1524.FE.ZS",
  youth_lfp_male: "SL.TLF.ACTI.1524.MA.ZS",
  wage_salaried_workers: "SL.EMP.WORK.ZS",
  self_employed: "SL.EMP.SELF.ZS",
  vulnerable_employment: "SL.EMP.VULN.ZS",
  gdp_growth: "NY.GDP.MKTP.KD.ZG",
  poverty_215: "SI.POV.DDAY",
  mobile_subscriptions: "IT.CEL.SETS.P2",
  internet_users: "IT.NET.USER.ZS",
  primary_completion_rate: "SE.PRM.CMPT.ZS",
  literacy_rate: "SE.ADT.LITR.ZS"
};

const INDICATOR_META = {
  youth_unemployment: { label: "Youth Unemployment Rate", unit: "%", source: "World Bank WDI · ILO modeled estimate" },
  gdp_per_capita: { label: "GDP per Capita", unit: "USD", source: "World Bank WDI" },
  employment_agriculture: { label: "Employment in Agriculture", unit: "% of total", source: "World Bank WDI · ILO" },
  employment_industry: { label: "Employment in Industry", unit: "% of total", source: "World Bank WDI · ILO" },
  employment_services: { label: "Employment in Services", unit: "% of total", source: "World Bank WDI · ILO" },
  school_enrollment_secondary: { label: "Secondary School Enrollment", unit: "% gross", source: "World Bank WDI · UNESCO" },
  youth_population: { label: "Youth Population (15–24)", unit: "people", source: "World Bank WDI · UN Population" },
  youth_lfp_female: { label: "Youth Labour Force Participation (F)", unit: "%", source: "World Bank WDI · ILO" },
  youth_lfp_male: { label: "Youth Labour Force Participation (M)", unit: "%", source: "World Bank WDI · ILO" },
  wage_salaried_workers: { label: "Wage & Salaried Workers", unit: "% of employed", source: "World Bank WDI · ILO" },
  self_employed: { label: "Self-Employed Workers", unit: "% of employed", source: "World Bank WDI · ILO" },
  vulnerable_employment: { label: "Vulnerable Employment", unit: "% of total", source: "World Bank WDI · ILO" },
  gdp_growth: { label: "GDP Growth", unit: "% annual", source: "World Bank WDI" },
  poverty_215: { label: "Poverty Rate ($2.15/day)", unit: "%", source: "World Bank WDI" },
  mobile_subscriptions: { label: "Mobile Subscriptions", unit: "per 100 people", source: "World Bank WDI · ITU" },
  internet_users: { label: "Internet Users", unit: "% of population", source: "World Bank WDI · ITU" },
  primary_completion_rate: { label: "Primary School Completion", unit: "%", source: "World Bank WDI · UNESCO" },
  literacy_rate: { label: "Adult Literacy Rate", unit: "%", source: "World Bank WDI · UNESCO" }
};

function parseWDI(json, key) {
  const meta = INDICATOR_META[key] || { label: key, unit: "", source: "World Bank WDI" };
  try {
    const dataArray = json[1];
    if (!dataArray) return { ...meta, key, value: null, year: null };
    for (const entry of dataArray) {
      if (entry.value !== null && entry.value !== undefined) {
        return {
          ...meta,
          key,
          value: Math.round(entry.value * 100) / 100,
          year: entry.date,
          country: entry.country.value
        };
      }
    }
  } catch (e) {}
  return { ...meta, key, value: null, year: null };
}

async function fetchIndicator(iso3, key) {
  const code = INDICATORS[key];
  const url = `${WB_BASE}/country/${iso3}/indicator/${code}?format=json&mrv=5&per_page=5`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`WDI ${key} failed: ${res.status}`);
  const json = await res.json();
  return parseWDI(json, key);
}

async function fetchTimeseries(iso3, key, years = 10) {
  const code = INDICATORS[key];
  const url = `${WB_BASE}/country/${iso3}/indicator/${code}?format=json&mrv=${years}&per_page=${years}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`WDI timeseries ${key} failed`);
  const json = await res.json();
  const entries = json[1] || [];
  return entries
    .filter((e) => e.value !== null)
    .map((e) => ({ year: parseInt(e.date), value: Math.round(e.value * 100) / 100 }))
    .sort((a, b) => a.year - b.year);
}

export async function fetchAllWDI(iso3) {
  const keys = Object.keys(INDICATORS);
  const results = await Promise.allSettled(keys.map((k) => fetchIndicator(iso3, k)));
  const output = {};
  keys.forEach((key, i) => {
    const r = results[i];
    output[key] =
      r.status === "fulfilled"
        ? r.value
        : { ...INDICATOR_META[key], key, value: null, year: null, error: r.reason?.message };
  });
  return output;
}

export async function fetchSectorTimeseries(iso3) {
  const [agr, ind, srv] = await Promise.allSettled([
    fetchTimeseries(iso3, "employment_agriculture"),
    fetchTimeseries(iso3, "employment_industry"),
    fetchTimeseries(iso3, "employment_services")
  ]);
  return {
    agriculture: agr.status === "fulfilled" ? agr.value : [],
    industry: ind.status === "fulfilled" ? ind.value : [],
    services: srv.status === "fulfilled" ? srv.value : [],
    source: "World Bank WDI · ILO modeled estimates"
  };
}

export async function fetchYouthUnemploymentTrend(iso3) {
  return fetchTimeseries(iso3, "youth_unemployment", 10);
}

import { useState, useEffect } from "react";

export function useWDIData(iso3) {
  const [data, setData] = useState(null);
  const [sectorTrends, setSectorTrends] = useState(null);
  const [unemploymentTrend, setUnemploymentTrend] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!iso3) return;
    setLoading(true);
    setError(null);

    Promise.all([fetchAllWDI(iso3), fetchSectorTimeseries(iso3), fetchYouthUnemploymentTrend(iso3)])
      .then(([allData, sectors, unemploymentT]) => {
        setData(allData);
        setSectorTrends(sectors);
        setUnemploymentTrend(unemploymentT);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [iso3]);

  return { data, sectorTrends, unemploymentTrend, loading, error };
}

