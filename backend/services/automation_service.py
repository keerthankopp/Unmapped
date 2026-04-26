from typing import Any, Dict, List


ROUTINE_KEYWORDS = [
    "record",
    "file",
    "enter data",
    "sort",
    "pack",
    "assemble",
    "process",
    "calculate",
    "compile",
    "copy",
    "fill",
    "prepare forms",
    "count",
    "weigh",
    "measure",
    "label",
    "load",
    "unload",
]

NONROUTINE_KEYWORDS = [
    "diagnose",
    "negotiate",
    "repair",
    "counsel",
    "design",
    "coordinate",
    "adapt",
    "communicate",
    "judge",
    "evaluate",
    "develop",
    "train",
    "advise",
    "inspect",
    "resolve",
    "manage",
    "lead",
    "create",
    "assess",
]


def count_keyword_matches(skills: List[str], keywords: List[str]) -> int:
    c = 0
    for s in skills:
        s_low = (s or "").lower()
        if any(k in s_low for k in keywords):
            c += 1
    return c


def calculate_adjusted_risk(task_statements: List[str], country_config: Dict[str, Any]) -> Dict[str, Any]:
    if not task_statements:
        raise ValueError("No task statements provided for automation risk calculation.")

    routine_score = count_keyword_matches(task_statements, ROUTINE_KEYWORDS) / len(task_statements)
    nonroutine_score = count_keyword_matches(task_statements, NONROUTINE_KEYWORDS) / len(task_statements)

    base_risk = routine_score / (routine_score + nonroutine_score + 0.001)

    lmic_discount = (
        country_config["lmic_discount_base"]
        + country_config["infrastructure_weight"] * (1 - country_config["broadband_penetration"])
        + country_config["informality_weight"] * country_config["informal_economy_share"]
    )

    adjusted_risk = max(0.05, min(0.95, base_risk - lmic_discount))

    durable = [s for s in task_statements if any(k in (s or "").lower() for k in NONROUTINE_KEYWORDS)][:3]
    at_risk = [s for s in task_statements if any(k in (s or "").lower() for k in ROUTINE_KEYWORDS)][:3]

    return {
        "base_risk": round(base_risk, 3),
        "adjusted_risk": round(adjusted_risk, 3),
        "lmic_discount_applied": round(lmic_discount, 3),
        "risk_label": "Low" if adjusted_risk < 0.3 else "Medium" if adjusted_risk < 0.65 else "High",
        "risk_color": "green" if adjusted_risk < 0.3 else "yellow" if adjusted_risk < 0.65 else "red",
        "durable_skills": durable,
        "at_risk_tasks": at_risk,
        "calibration_note": (
            f"Risk adjusted for {country_config['country_name']}: "
            f"{round(country_config['informal_economy_share']*100)}% informal economy, "
            f"{round(country_config['broadband_penetration']*100)}% broadband penetration"
        ),
    }

