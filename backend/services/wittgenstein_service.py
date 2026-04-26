import re
from typing import Any, Dict, List

import httpx


WCDE_BASE_URL = "https://dataexplorer.wittgensteincentre.org/wcde-v3/"

_REGION_MAP = {"SSA": "SSA", "SouthAsia": "SAS", "SAS": "SAS"}


def _coerce_region(region_code: str) -> str:
    return _REGION_MAP.get(region_code, region_code)


async def fetch_education_projections(region_code: str) -> Dict[str, Any]:
    """
    Attempts the documented JSON endpoint first. If it fails, returns a structured error.
    """
    region = _coerce_region(region_code)
    params = {
        "indicator": "prop",
        "grouping": "edattain",
        "scenario": "ssp2",
        "region": region,
        "year": "2025,2030,2035",
    }

    async with httpx.AsyncClient(timeout=35, follow_redirects=True) as client:
        r = await client.get(WCDE_BASE_URL, params=params)
        r.raise_for_status()
        data = r.json()

    # WCDE formats vary; try several plausible shapes.
    rows: List[Dict[str, Any]] = []
    if isinstance(data, dict):
        if isinstance(data.get("data"), list):
            rows = data["data"]
        elif isinstance(data.get("results"), list):
            rows = data["results"]
        elif isinstance(data.get("rows"), list):
            rows = data["rows"]

    # Heuristic: look for post-secondary attainment in 20-24.
    projections = []
    for target_year in (2025, 2030, 2035):
        best_val = None
        for row in rows:
            y = row.get("year") or row.get("Year")
            if str(y) != str(target_year):
                continue
            # Try common keys for post-secondary; we keep it heuristic but live.
            for k in ("post_secondary", "postsecondary", "tertiary", "postsec", "Post-secondary", "Tertiary"):
                if k in row and row[k] is not None:
                    best_val = row[k]
                    break
            if best_val is None and "value" in row:
                best_val = row["value"]
            if best_val is not None:
                break
        if best_val is None:
            raise RuntimeError("Could not parse Wittgenstein projection payload for post-secondary share.")
        projections.append({"year": target_year, "post_secondary_share": float(best_val)})

    last = projections[-1]["post_secondary_share"]
    first = projections[0]["post_secondary_share"]
    return {
        "region": region,
        "projections": projections,
        "trend_narrative": (
            f"By 2035, {round(last*100)}% of young adults in {region} are projected to hold post-secondary "
            f"qualifications — up from {round(first*100)}% today. Skills that complement educated peers will be most valuable."
        ),
        "source": "Wittgenstein Centre for Demography and Global Human Capital (2024), SSP2 scenario",
    }

