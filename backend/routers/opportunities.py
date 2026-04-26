import asyncio
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.claude_service import generate_opportunity_matches
from services.config_service import load_country_config
from services.wdi_service import fetch_all, fetch_indicator_timeseries, fetch_sector_timeseries

router = APIRouter()


@router.post("/match")
async def match_opportunities(body: Dict[str, Any]):
    if "country" not in body or "occupation" not in body:
        raise HTTPException(status_code=400, detail="Body must include { country, occupation }")
    try:
        _, cfg = load_country_config(body["country"])
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        iso3 = cfg["wb_iso3"]
        wdi_data, sector_trends = await asyncio.gather(fetch_all(iso3), fetch_sector_timeseries(iso3))
        matches = await generate_opportunity_matches(
            occupation=body["occupation"],
            wdi_data=wdi_data,
            sector_trends=sector_trends,
            country_config=cfg,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {
        "matches": matches,
        "econometric_signals": {
            "youth_unemployment": wdi_data.get("youth_unemployment"),
            "self_employed": wdi_data.get("self_employed"),
            "vulnerable_employment": wdi_data.get("vulnerable_employment"),
            "employment_agriculture": wdi_data.get("employment_agriculture"),
            "employment_services": wdi_data.get("employment_services"),
            "gdp_growth": wdi_data.get("gdp_growth"),
        },
        "sector_trends": sector_trends,
        "source": "World Bank World Development Indicators",
    }


@router.get("/policymaker/{country}")
async def policymaker(country: str):
    try:
        _, cfg = load_country_config(country)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        iso3 = cfg["wb_iso3"]
        wdi_data, sector_trends, youth_unemployment_trend = await asyncio.gather(
            fetch_all(iso3),
            fetch_sector_timeseries(iso3),
            fetch_indicator_timeseries(iso3, "youth_unemployment", 10),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not reach World Bank WDI: {e}")

    return {
        "country": cfg["country_name"],
        "snapshot": wdi_data,
        "sector_trends": sector_trends,
        "youth_unemployment_trend": youth_unemployment_trend,
        "source": "World Bank World Development Indicators",
    }

