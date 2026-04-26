import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"


def available_countries() -> List[str]:
    return sorted([p.stem for p in CONFIG_DIR.glob("*.json")])


def load_country_config(country: str) -> Tuple[str, Dict[str, Any]]:
    country = (country or "").strip().lower()
    cfg_path = CONFIG_DIR / f"{country}.json"
    if not cfg_path.exists():
        raise FileNotFoundError(f"Unknown country '{country}'. Available: {', '.join(available_countries())}")
    return country, json.loads(cfg_path.read_text(encoding="utf-8"))

