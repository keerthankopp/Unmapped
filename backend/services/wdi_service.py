import httpx
import asyncio
import os

WB_BASE = "https://api.worldbank.org/v2"

INDICATORS = {
    "youth_unemployment": "SL.UEM.1524.ZS",
    "gdp_per_capita": "NY.GDP.PCAP.CD",
    "employment_agriculture": "SL.AGR.EMPL.ZS",
    "employment_industry": "SL.IND.EMPL.ZS",
    "employment_services": "SL.SRV.EMPL.ZS",
    "school_enrollment_secondary": "SE.SEC.ENRR",
    "youth_population": "SP.POP.1524.TO",
    "youth_lfp_female": "SL.TLF.ACTI.1524.FE.ZS",
    "youth_lfp_male": "SL.TLF.ACTI.1524.MA.ZS",
    "wage_salaried_workers": "SL.EMP.WORK.ZS",
    "self_employed": "SL.EMP.SELF.ZS",
    "vulnerable_employment": "SL.EMP.VULN.ZS",
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",
    "poverty_215": "SI.POV.DDAY",
    "mobile_subscriptions": "IT.CEL.SETS.P2",
    "internet_users": "IT.NET.USER.ZS",
    "primary_completion_rate": "SE.PRM.CMPT.ZS",
    "literacy_rate": "SE.ADT.LITR.ZS",
}

INDICATOR_META = {
    "youth_unemployment": {
        "label": "Youth Unemployment Rate",
        "unit": "%",
        "source": "World Bank WDI · ILO modeled estimate",
    },
    "gdp_per_capita": {"label": "GDP per Capita", "unit": "USD", "source": "World Bank WDI"},
    "employment_agriculture": {"label": "Employment in Agriculture", "unit": "% of total", "source": "World Bank WDI · ILO"},
    "employment_industry": {"label": "Employment in Industry", "unit": "% of total", "source": "World Bank WDI · ILO"},
    "employment_services": {"label": "Employment in Services", "unit": "% of total", "source": "World Bank WDI · ILO"},
    "school_enrollment_secondary": {"label": "Secondary School Enrollment", "unit": "% gross", "source": "World Bank WDI · UNESCO"},
    "youth_population": {"label": "Youth Population (15-24)", "unit": "people", "source": "World Bank WDI · UN Population"},
    "youth_lfp_female": {"label": "Youth Labor Force Participation (Female)", "unit": "%", "source": "World Bank WDI · ILO"},
    "youth_lfp_male": {"label": "Youth Labor Force Participation (Male)", "unit": "%", "source": "World Bank WDI · ILO"},
    "wage_salaried_workers": {"label": "Wage & Salaried Workers", "unit": "% of employed", "source": "World Bank WDI · ILO"},
    "self_employed": {"label": "Self-Employed Workers", "unit": "% of employed", "source": "World Bank WDI · ILO"},
    "vulnerable_employment": {"label": "Vulnerable Employment", "unit": "% of total", "source": "World Bank WDI · ILO"},
    "gdp_growth": {"label": "GDP Growth", "unit": "% annual", "source": "World Bank WDI"},
    "poverty_215": {"label": "Poverty Rate ($2.15/day)", "unit": "% of population", "source": "World Bank WDI"},
    "mobile_subscriptions": {"label": "Mobile Subscriptions", "unit": "per 100 people", "source": "World Bank WDI · ITU"},
    "internet_users": {"label": "Internet Users", "unit": "% of population", "source": "World Bank WDI · ITU"},
    "primary_completion_rate": {"label": "Primary School Completion", "unit": "%", "source": "World Bank WDI · UNESCO"},
    "literacy_rate": {"label": "Adult Literacy Rate", "unit": "%", "source": "World Bank WDI · UNESCO"},
}


def parse_wdi(response_json: list, key: str) -> dict:
    meta = INDICATOR_META.get(key, {"label": key, "unit": "", "source": "World Bank WDI"})
    try:
        data_array = response_json[1]
        if not data_array:
            return {**meta, "value": None, "year": None, "key": key}
        for entry in data_array:
            if entry.get("value") is not None:
                return {
                    **meta,
                    "key": key,
                    "value": round(entry["value"], 2),
                    "year": entry["date"],
                    "country": entry["country"]["value"],
                }
    except (IndexError, KeyError, TypeError):
        pass
    return {**meta, "value": None, "year": None, "key": key}


async def fetch_indicator(iso3: str, key: str) -> dict:
    code = INDICATORS[key]
    url = f"{WB_BASE}/country/{iso3}/indicator/{code}?format=json&mrv=5&per_page=5"
    async with httpx.AsyncClient(timeout=8.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return parse_wdi(response.json(), key)


async def fetch_indicator_timeseries(iso3: str, key: str, years: int = 10) -> list:
    """Returns list of {year, value} for trend charts"""
    code = INDICATORS[key]
    url = f"{WB_BASE}/country/{iso3}/indicator/{code}?format=json&mrv={years}&per_page={years}"
    async with httpx.AsyncClient(timeout=8.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        entries = data[1] or []
        series = []
        for entry in entries:
            if entry.get("value") is not None:
                series.append({"year": int(entry["date"]), "value": round(entry["value"], 2)})
        return sorted(series, key=lambda x: x["year"])


async def fetch_all(iso3: str) -> dict:
    """Fetch all indicators concurrently"""
    keys = list(INDICATORS.keys())
    tasks = [fetch_indicator(iso3, key) for key in keys]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    output = {}
    for key, result in zip(keys, results):
        if isinstance(result, Exception):
            output[key] = {**INDICATOR_META.get(key, {}), "value": None, "year": None, "error": str(result)}
        else:
            output[key] = result
    return output


async def fetch_sector_timeseries(iso3: str) -> dict:
    """Fetch 10-year trend for all three sector employment shares"""
    tasks = [
        fetch_indicator_timeseries(iso3, "employment_agriculture", 10),
        fetch_indicator_timeseries(iso3, "employment_industry", 10),
        fetch_indicator_timeseries(iso3, "employment_services", 10),
    ]
    agr, ind, srv = await asyncio.gather(*tasks)
    return {
        "agriculture": agr,
        "industry": ind,
        "services": srv,
        "source": "World Bank WDI · ILO modeled estimates",
    }

