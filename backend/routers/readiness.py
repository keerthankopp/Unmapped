from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.config_service import load_country_config
from services.wdi_service import fetch_all

router = APIRouter()


class ReadinessAssessRequest(BaseModel):
    country: str


@router.post("/assess")
async def assess(req: ReadinessAssessRequest):
    """
    WDI-only readiness proxy.
    Returns live WDI snapshot + a simple "automation exposure" proxy score driven by:
    - internet_users (higher -> higher automation feasibility)
    - vulnerable_employment (higher -> lower standardization -> lower near-term automation)
    - self_employed (higher -> lower standardization -> lower near-term automation)
    """
    try:
        _, cfg = load_country_config(req.country)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        wdi = await fetch_all(cfg["wb_iso3"])
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not reach World Bank WDI: {e}")

    internet = (wdi.get("internet_users") or {}).get("value")
    vuln = (wdi.get("vulnerable_employment") or {}).get("value")
    self_emp = (wdi.get("self_employed") or {}).get("value")

    # Normalize to 0-1 where possible.
    def pct_to_01(x):
        try:
            return max(0.0, min(1.0, float(x) / 100.0))
        except Exception:
            return None

    internet_01 = pct_to_01(internet)
    vuln_01 = pct_to_01(vuln)
    self_01 = pct_to_01(self_emp)

    # Proxy score (not a scientific automation model; clearly labeled in UI as WDI-based proxy).
    # Higher internet increases feasibility; higher vulnerability/self-employment decreases standardization.
    parts = []
    if internet_01 is not None:
        parts.append(0.6 * internet_01)
    if vuln_01 is not None:
        parts.append(0.2 * (1 - vuln_01))
    if self_01 is not None:
        parts.append(0.2 * (1 - self_01))
    score = sum(parts) / (0.6 + 0.2 + 0.2) if parts else None

    label = None
    if score is not None:
        label = "Low" if score < 0.35 else "Medium" if score < 0.65 else "High"

    return {
        "wdi_snapshot": wdi,
        "readiness_proxy": {
            "value": round(score, 3) if score is not None else None,
            "label": label,
            "note": "Proxy based on WDI internet use, vulnerable employment, and self-employment. (WDI-only mode)",
            "source": "World Bank WDI",
        },
    }

