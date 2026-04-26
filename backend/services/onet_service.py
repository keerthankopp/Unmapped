import asyncio
from typing import Any, Dict, List

import httpx


ONET_BASE_URL = "https://services.onetcenter.org/ws"


SOC_TO_ISCO = {
    "45-": "6",  # Farming -> ISCO Major Group 6
    "49-": "7",  # Repair/maintenance -> ISCO Group 7
    "43-": "4",  # Clerical -> ISCO Group 4
    "41-": "5",  # Sales -> ISCO Group 5
    "11-": "1",  # Management -> ISCO Group 1
    "15-": "2",  # Computer/IT -> ISCO Group 2
    "17-": "2",  # Engineering -> ISCO Group 2
    "29-": "2",  # Healthcare professionals -> ISCO Group 2
    "47-": "7",  # Construction -> ISCO Group 7
    "51-": "8",  # Production -> ISCO Group 8
    "53-": "8",  # Transportation -> ISCO Group 8
    "35-": "9",  # Food prep -> ISCO Group 9
    "37-": "9",  # Cleaning -> ISCO Group 9
}


def soc_to_isco_major(soc_code: str) -> str:
    for prefix, isco in SOC_TO_ISCO.items():
        if soc_code.startswith(prefix):
            return isco
    return "5"  # default to service workers


async def search_occupations(query: str, end: int = 5) -> List[Dict[str, Any]]:
    """
    GET /mnm/search?keyword={query}&end=5
    Returns: [{"code": "15-1254.00", "title": "Web Developers"}, ...]
    """
    headers = {"Accept": "application/json"}
    params = {"keyword": query, "end": end}
    async with httpx.AsyncClient(timeout=25) as client:
        r = await client.get(f"{ONET_BASE_URL}/mnm/search", params=params, headers=headers)
        r.raise_for_status()
        data = r.json()

    occs = data.get("occupation") or data.get("occupations") or []
    results = []
    if isinstance(occs, dict):
        occs = [occs]
    for o in occs:
        code = o.get("code")
        title = o.get("title")
        if code and title:
            results.append({"code": code, "title": title})
    return results


async def get_occupation_summary(soc_code: str) -> Dict[str, Any]:
    headers = {"Accept": "application/json"}
    async with httpx.AsyncClient(timeout=25) as client:
        r = await client.get(f"{ONET_BASE_URL}/online/occupations/{soc_code}/summary", headers=headers)
        r.raise_for_status()
        return r.json()


async def get_occupation_skills(soc_code: str) -> List[Dict[str, Any]]:
    headers = {"Accept": "application/json"}
    async with httpx.AsyncClient(timeout=25) as client:
        r = await client.get(f"{ONET_BASE_URL}/online/occupations/{soc_code}/details/skills", headers=headers)
        r.raise_for_status()
        data = r.json()

    out = []
    for item in (data.get("element") or []):
        name = (item.get("name") or item.get("title") or "").strip()
        val = item.get("value")
        if name and val is not None:
            out.append({"name": name, "importance": float(val)})
    return out


async def get_occupation_tasks(soc_code: str) -> List[str]:
    headers = {"Accept": "application/json"}
    async with httpx.AsyncClient(timeout=25) as client:
        r = await client.get(f"{ONET_BASE_URL}/online/occupations/{soc_code}/details/tasks", headers=headers)
        r.raise_for_status()
        data = r.json()

    tasks = []
    for item in (data.get("task") or data.get("element") or []):
        if isinstance(item, str):
            tasks.append(item)
        elif isinstance(item, dict):
            t = item.get("statement") or item.get("description") or item.get("name")
            if isinstance(t, str) and t.strip():
                tasks.append(t.strip())
    return tasks


async def get_full_occupation_profile(soc_code: str) -> Dict[str, Any]:
    summary, skills, tasks = await asyncio.gather(
        get_occupation_summary(soc_code),
        get_occupation_skills(soc_code),
        get_occupation_tasks(soc_code),
    )

    title = None
    if isinstance(summary.get("title"), str):
        title = summary["title"]
    elif isinstance(summary.get("occupation", {}).get("title"), str):
        title = summary["occupation"]["title"]

    description = summary.get("description") or summary.get("what_they_do")
    if isinstance(description, dict):
        description = description.get("content")
    if not isinstance(description, str):
        description = ""

    return {
        "soc_code": soc_code,
        "title": title or soc_code,
        "description": description,
        "skills": skills,
        "tasks": tasks,
        "source": "O*NET Online (US DOL)",
        "onet_url": f"https://www.onetonline.org/link/summary/{soc_code}",
        "isco_major_group": soc_to_isco_major(soc_code),
    }

