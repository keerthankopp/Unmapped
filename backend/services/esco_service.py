from typing import Any, Dict, List, Optional

import httpx

from services.esco_mirror_service import essential_skills_local, search_occupations_local

ESCO_BASE_URL = "https://esco.ec.europa.eu/api/v1"


def _best_label(item: Dict[str, Any]) -> str:
    for k in ("title", "preferredLabel", "label"):
        v = item.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    title = item.get("title")
    if isinstance(title, dict):
        for v in title.values():
            if isinstance(v, str) and v.strip():
                return v.strip()
    return "Unknown"


async def search_occupations(query: str, lang: str) -> List[Dict[str, Any]]:
    params = {"text": query, "language": lang, "type": "occupation", "limit": 5}
    async with httpx.AsyncClient(timeout=25) as client:
        r = await client.get(f"{ESCO_BASE_URL}/search", params=params)
        if r.status_code == 403:
            # ESCO edge blocks many clients (robots.txt). Use local mirror if available.
            return search_occupations_local(query=query, limit=5)
        r.raise_for_status()
        data = r.json()

    results = []
    for hit in (data.get("_embedded", {}).get("results") or data.get("results") or []):
        uri = hit.get("uri") or hit.get("id")
        results.append(
            {
                "uri": uri,
                "title": _best_label(hit),
                "iscoGroup": hit.get("iscoGroup") or hit.get("iscoGroupCode"),
                "description": hit.get("description"),
            }
        )
    return results


async def fetch_occupation_essential_skills(esco_uri: str, lang: str) -> Dict[str, Any]:
    params = {"uri": esco_uri, "language": lang}
    async with httpx.AsyncClient(timeout=25) as client:
        r = await client.get(f"{ESCO_BASE_URL}/resource/occupation/essentialSkills", params=params)
        if r.status_code == 403:
            return {"uri": esco_uri, "essential_skills": essential_skills_local(esco_uri), "source": "ESCO mirror"}
        r.raise_for_status()
        data = r.json()

    skills = []
    embedded = data.get("_embedded") or {}
    for sk in embedded.get("essentialSkills") or embedded.get("skills") or []:
        skills.append(_best_label(sk))

    return {"uri": esco_uri, "essential_skills": skills, "source": "ESCO API"}


async def search_skills(skill_text: str, lang: str) -> List[Dict[str, Any]]:
    params = {"text": skill_text, "language": lang, "type": "skill", "limit": 8}
    async with httpx.AsyncClient(timeout=25) as client:
        r = await client.get(f"{ESCO_BASE_URL}/search", params=params)
        r.raise_for_status()
        data = r.json()

    results = []
    for hit in (data.get("_embedded", {}).get("results") or data.get("results") or []):
        results.append({"uri": hit.get("uri") or hit.get("id"), "title": _best_label(hit)})
    return results

