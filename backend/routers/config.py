from fastapi import APIRouter, HTTPException

from services.config_service import available_countries, load_country_config

router = APIRouter()


@router.get("/{country}")
def get_config(country: str):
    try:
        _, cfg = load_country_config(country)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"country": country, "available_countries": available_countries(), "config": cfg}

