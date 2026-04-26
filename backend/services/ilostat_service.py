import re
from typing import Any, Dict, List, Tuple

import httpx


ILOSTAT_BASE_URL = "https://ilostat.ilo.org/api/sdmx-json/data"


def _parse_sdmx_observations(data: Dict[str, Any]) -> Tuple[Dict[str, List[Any]], List[Dict[str, Any]]]:
    obs = data["data"]["dataSets"][0]["observations"]
    dims = data["data"]["structure"]["dimensions"]["observation"]
    return obs, dims


def _dim_values(dims: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    return [d.get("values") or [] for d in dims]


def _obs_key_to_indexes(key: str) -> List[int]:
    return [int(x) for x in key.split(":")]


def _find_dim_index_by_id(dims: List[Dict[str, Any]], dim_id: str) -> int:
    for i, d in enumerate(dims):
        if d.get("id") == dim_id:
            return i
    return -1


def _label_for_dim_value(dims: List[Dict[str, Any]], dim_idx: int, value_idx: int) -> str:
    values = (dims[dim_idx].get("values") or [])
    if value_idx < 0 or value_idx >= len(values):
        return "Unknown"
    return values[value_idx].get("name") or values[value_idx].get("id") or "Unknown"


async def fetch_wages(country_code: str) -> Dict[str, Any]:
    """
    Monthly earnings by skill level.
    Returns: {"values": {"Low skill": 450, ...}, "source": "ILO ILOSTAT"}
    """
    path = (
        f"DF_EAR_INEE_SEX_OCU_NB/{country_code}..SEX_T."
        "OCU_SKILL_1+OCU_SKILL_2+OCU_SKILL_3+OCU_SKILL_4/all"
    )
    params = {"format": "jsondata", "startPeriod": "2019", "endPeriod": "2024"}

    async with httpx.AsyncClient(timeout=35) as client:
        r = await client.get(f"{ILOSTAT_BASE_URL}/{path}", params=params)
        r.raise_for_status()
        data = r.json()

    obs, dims = _parse_sdmx_observations(data)
    dim_ocu = _find_dim_index_by_id(dims, "OCU")  # often the skill-level dimension
    dim_time = _find_dim_index_by_id(dims, "TIME_PERIOD")
    if dim_ocu == -1:
        dim_ocu = _find_dim_index_by_id(dims, "OCU_SKILL")

    best_by_label: Dict[str, Tuple[int, float]] = {}
    for k, v in obs.items():
        if not v or v[0] is None:
            continue
        idxs = _obs_key_to_indexes(k)
        ocu_label = _label_for_dim_value(dims, dim_ocu, idxs[dim_ocu]) if dim_ocu != -1 else "Unknown"
        time_label = _label_for_dim_value(dims, dim_time, idxs[dim_time]) if dim_time != -1 else "Unknown"
        year = int(time_label) if re.fullmatch(r"\d{4}", str(time_label or "")) else 0
        val = float(v[0])
        prev = best_by_label.get(ocu_label)
        if prev is None or year > prev[0]:
            best_by_label[ocu_label] = (year, val)

    values = {k: round(v[1], 2) for k, v in best_by_label.items()}
    years = {k: v[0] for k, v in best_by_label.items()}
    return {"values": values, "years": years, "source": "ILO ILOSTAT"}


async def fetch_employment_by_sector(country_code: str) -> Dict[str, Any]:
    path = (
        f"DF_EMP_TEMP_SEX_ECO_NB/{country_code}..SEX_T."
        "ECO_ISIC4_A+ECO_ISIC4_G+ECO_ISIC4_C+ECO_ISIC4_F+ECO_ISIC4_J/all"
    )
    params = {"format": "jsondata", "startPeriod": "2020", "endPeriod": "2024"}

    async with httpx.AsyncClient(timeout=35) as client:
        r = await client.get(f"{ILOSTAT_BASE_URL}/{path}", params=params)
        r.raise_for_status()
        data = r.json()

    obs, dims = _parse_sdmx_observations(data)
    dim_eco = _find_dim_index_by_id(dims, "ECO")
    dim_time = _find_dim_index_by_id(dims, "TIME_PERIOD")

    best: Dict[str, Tuple[int, float]] = {}
    for k, v in obs.items():
        if not v or v[0] is None:
            continue
        idxs = _obs_key_to_indexes(k)
        eco_label = _label_for_dim_value(dims, dim_eco, idxs[dim_eco]) if dim_eco != -1 else "Unknown"
        time_label = _label_for_dim_value(dims, dim_time, idxs[dim_time]) if dim_time != -1 else "Unknown"
        year = int(time_label) if re.fullmatch(r"\d{4}", str(time_label or "")) else 0
        val = float(v[0])
        prev = best.get(eco_label)
        if prev is None or year > prev[0]:
            best[eco_label] = (year, val)

    return {"values": {k: round(v[1], 2) for k, v in best.items()}, "years": {k: v[0] for k, v in best.items()}, "source": "ILO ILOSTAT"}


async def fetch_youth_neet(country_code: str) -> Dict[str, Any]:
    path = f"DF_EIP_NEET_SEX_AGE_RT/{country_code}..SEX_T.AGE_YTHADULT_Y15-24/all"
    params = {"format": "jsondata", "startPeriod": "2015", "endPeriod": "2024"}

    async with httpx.AsyncClient(timeout=35) as client:
        r = await client.get(f"{ILOSTAT_BASE_URL}/{path}", params=params)
        r.raise_for_status()
        data = r.json()

    obs, dims = _parse_sdmx_observations(data)
    dim_time = _find_dim_index_by_id(dims, "TIME_PERIOD")

    by_year: Dict[int, float] = {}
    for k, v in obs.items():
        if not v or v[0] is None:
            continue
        idxs = _obs_key_to_indexes(k)
        time_label = _label_for_dim_value(dims, dim_time, idxs[dim_time]) if dim_time != -1 else None
        if not time_label or not re.fullmatch(r"\d{4}", str(time_label)):
            continue
        by_year[int(time_label)] = float(v[0])

    trend = [{"year": y, "value": round(by_year[y], 3)} for y in sorted(by_year.keys())][-5:]
    return {"trend": trend, "source": "ILO ILOSTAT"}


async def fetch_informal_employment_share(country_code: str) -> Dict[str, Any]:
    path = f"DF_EMP_NIFL_SEX_ECO_NB/{country_code}..SEX_T._T/all"
    params = {"format": "jsondata", "startPeriod": "2019", "endPeriod": "2024"}

    async with httpx.AsyncClient(timeout=35) as client:
        r = await client.get(f"{ILOSTAT_BASE_URL}/{path}", params=params)
        r.raise_for_status()
        data = r.json()

    obs, dims = _parse_sdmx_observations(data)
    dim_time = _find_dim_index_by_id(dims, "TIME_PERIOD")

    best = None
    for k, v in obs.items():
        if not v or v[0] is None:
            continue
        idxs = _obs_key_to_indexes(k)
        time_label = _label_for_dim_value(dims, dim_time, idxs[dim_time]) if dim_time != -1 else None
        year = int(time_label) if time_label and re.fullmatch(r"\d{4}", str(time_label)) else 0
        if best is None or year > best[0]:
            best = (year, float(v[0]))

    if not best:
        raise RuntimeError("No informal employment observation found.")
    return {"year": best[0], "value": round(best[1], 3), "source": "ILO ILOSTAT"}

