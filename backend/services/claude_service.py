import json
import os
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

from anthropic import Anthropic
from dotenv import load_dotenv
import httpx

load_dotenv()


_SYSTEM_INTAKE_PROMPT = """You are a warm, skilled labor market analyst helping young informal workers in low-income countries map their skills.

Conduct a friendly conversational intake. Ask ONE question at a time. Keep responses to 1-2 sentences while gathering info.

You need to gather: what work they do, how long they've done it, their education level, any languages they speak, any tools or technology they use, and any informal training.

After 3-4 turns when you have enough information, output ONLY this JSON and nothing else:

{
  "extraction_complete": true,
  "profile": {
    "name": "string or Anonymous",
    "age": number or null,
    "education_level_local": "string",
    "isced_level": number,
    "years_of_experience": number,
    "primary_occupation_description": "string in their own words",
    "isco_search_terms": ["2-3 short search terms for occupation lookup"],
    "demonstrated_skills": [
      {
        "skill_name": "plain language",
        "category": "technical|interpersonal|language|digital|business",
        "evidence": "what they said",
        "proficiency": "basic|intermediate|advanced"
      }
    ],
    "languages": ["list"],
    "digital_access": "smartphone_only|laptop|no_device",
    "prior_training": ["any training mentioned"]
  }
}

While still gathering info, do NOT output JSON. Just respond conversationally.
"""

_SYSTEM_PROFILE_CARD_PROMPT = """Given extracted skills data, generate a human-readable skills profile card.

Output ONLY this JSON:
{
  "summary_paragraph": "2-3 sentence plain English summary the user can read to an employer",
  "key_skills": [
    {
      "skill": "plain skill name",
      "what_it_means": "one practical sentence",
      "category": "technical|interpersonal|digital|language"
    }
  ],
  "occupation_cluster": "plain language description of work type",
  "isco_search_terms": ["search terms for occupation label"],
  "honest_gaps": ["1-2 honest gaps or limitations to acknowledge"]
}

Be warm but honest. Do not inflate skills. Do not invent credentials.
"""


def _client() -> Anthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Missing ANTHROPIC_API_KEY. Set it in backend/.env.")
    return Anthropic(api_key=api_key)


DEFAULT_ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
_MODEL_CACHE: Optional[str] = None

# If your key doesn't have access to "latest"/newer model IDs, we automatically try older,
# widely-available IDs (no mocks; live retries only).
FALLBACK_MODELS = [
    # Claude 4.x (current Anthropic model IDs as of 2026)
    "claude-sonnet-4-6",
    "claude-opus-4-7",
    "claude-opus-4-6",
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-20250514",
    "claude-opus-4-20250514",
    # Legacy Claude 2 / Instant (many org keys still only have these enabled)
    "claude-2.1",
    "claude-2.0",
    "claude-instant-1.2",
    "claude-3-5-haiku-latest",
    "claude-3-5-haiku-20241022",
    "claude-3-haiku-20240307",
    "claude-3-sonnet-20240229",
    "claude-3-opus-20240229",
]


def _is_model_not_found_error(err_text: str) -> bool:
    t = (err_text or "").lower()
    return "not_found_error" in t and "model:" in t


async def _list_available_models(api_key: str) -> List[str]:
    base = os.getenv("ANTHROPIC_API_BASE", "https://api.anthropic.com").rstrip("/")
    version = os.getenv("ANTHROPIC_VERSION", "2023-06-01")
    headers = {"x-api-key": api_key, "anthropic-version": version}

    async with httpx.AsyncClient(timeout=25) as client:
        r = await client.get(f"{base}/v1/models", headers=headers)
        r.raise_for_status()
        data = r.json()

    models = []
    for m in (data.get("data") or []):
        mid = m.get("id")
        if isinstance(mid, str) and mid.strip():
            models.append(mid.strip())
    return models


async def _resolve_model() -> str:
    global _MODEL_CACHE
    if _MODEL_CACHE:
        return _MODEL_CACHE

    preferred = os.getenv("ANTHROPIC_MODEL")
    if preferred:
        _MODEL_CACHE = preferred
        return preferred

    api_key = os.getenv("ANTHROPIC_API_KEY") or ""
    if not api_key:
        _MODEL_CACHE = DEFAULT_ANTHROPIC_MODEL
        return _MODEL_CACHE

    try:
        models = await _list_available_models(api_key)
    except Exception:
        _MODEL_CACHE = DEFAULT_ANTHROPIC_MODEL
        return _MODEL_CACHE

    def score(mid: str) -> Tuple[int, str]:
        s = mid.lower()
        if "sonnet" in s:
            return (0, mid)
        if "haiku" in s:
            return (1, mid)
        if "opus" in s:
            return (2, mid)
        if "claude-2" in s:
            return (3, mid)
        if "instant" in s:
            return (4, mid)
        return (5, mid)

    if models:
        _MODEL_CACHE = sorted(models, key=score)[0]
        return _MODEL_CACHE

    _MODEL_CACHE = DEFAULT_ANTHROPIC_MODEL
    return _MODEL_CACHE


def _candidate_models(primary: str) -> List[str]:
    seen = set()
    ordered = [primary] + FALLBACK_MODELS
    out = []
    for m in ordered:
        if not m or m in seen:
            continue
        seen.add(m)
        out.append(m)
    return out


def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except Exception:
        return None


async def stream_intake(
    conversation_history: List[Dict[str, str]],
    country_config: Dict[str, Any],
) -> AsyncGenerator[bytes, None]:
    """
    Streams assistant tokens as bytes.
    When extraction completes, emits `[EXTRACTION_COMPLETE]` + JSON payload.
    """
    system = _SYSTEM_INTAKE_PROMPT + "\n\nCountry context:\n" + json.dumps(country_config, ensure_ascii=False)
    messages = [{"role": m["role"], "content": m["content"]} for m in conversation_history]

    collected = ""
    suppress_from_json = False

    # Try primary model; if Anthropic returns model 404, probe fallbacks until one works.
    primary_model = await _resolve_model()
    last_err: Optional[Exception] = None

    for model_id in _candidate_models(primary_model):
        try:
            with _client().messages.stream(
                model=model_id,
                system=system,
                messages=messages,
                max_tokens=600,
                temperature=0.4,
            ) as stream:
                for event in stream:
                    if event.type == "content_block_delta" and event.delta.type == "text_delta":
                        token = event.delta.text
                        collected += token

                        # If Claude starts emitting the final JSON extraction, don't stream it to the UI.
                        # We'll send it only via the special marker once parsed.
                        if not suppress_from_json:
                            first_non_ws = None
                            for ch in token:
                                if not ch.isspace():
                                    first_non_ws = ch
                                    break
                            if first_non_ws == "{":
                                suppress_from_json = True

                        if not suppress_from_json:
                            yield token.encode("utf-8")
            # success -> cache model for subsequent requests
            global _MODEL_CACHE
            _MODEL_CACHE = model_id
            break
        except Exception as e:
            last_err = e
            if _is_model_not_found_error(str(e)):
                continue
            err = {"error": str(e), "service": "claude_stream", "model": model_id}
            yield ("\n[STREAM_ERROR]\n" + json.dumps(err, ensure_ascii=False)).encode("utf-8")
            return

    # If we never streamed any text and last error was model-not-found, surface clear error.
    if collected == "" and last_err is not None and _is_model_not_found_error(str(last_err)):
        err = {
            "error": f"No accessible Claude model found. Tried: {', '.join(_candidate_models(primary_model))}. Last error: {last_err}",
            "service": "claude_stream",
        }
        yield ("\n[STREAM_ERROR]\n" + json.dumps(err, ensure_ascii=False)).encode("utf-8")
        return

    parsed = _extract_json_object(collected)
    if isinstance(parsed, dict) and parsed.get("extraction_complete") is True:
        payload = json.dumps(parsed, ensure_ascii=False)
        yield ("\n[EXTRACTION_COMPLETE]\n" + payload).encode("utf-8")


async def generate_profile_card(extracted_profile: Dict[str, Any], country_config: Dict[str, Any]) -> Dict[str, Any]:
    system = _SYSTEM_PROFILE_CARD_PROMPT + "\n\nCountry context:\n" + json.dumps(country_config, ensure_ascii=False)
    msg = json.dumps(extracted_profile, ensure_ascii=False)

    primary_model = await _resolve_model()
    last_err: Optional[Exception] = None
    resp = None

    for model_id in _candidate_models(primary_model):
        try:
            resp = _client().messages.create(
                model=model_id,
                system=system,
                messages=[{"role": "user", "content": msg}],
                max_tokens=700,
                temperature=0.3,
            )
            global _MODEL_CACHE
            _MODEL_CACHE = model_id
            break
        except Exception as e:
            last_err = e
            if _is_model_not_found_error(str(e)):
                continue
            raise

    if resp is None:
        raise RuntimeError(
            f"No accessible Claude model found. Tried: {', '.join(_candidate_models(primary_model))}. Last error: {last_err}"
        )

    text = ""
    for block in resp.content:
        if getattr(block, "type", None) == "text":
            text += block.text

    parsed = _extract_json_object(text)
    if not isinstance(parsed, dict):
        raise RuntimeError("Claude did not return valid JSON for profile card.")
    return parsed

