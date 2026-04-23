import logging
from typing import Optional
from bot.utils.groq_client import GroqClient
from bot.utils.api_client import get_categories

logger = logging.getLogger(__name__)

groq = GroqClient()


async def parse_user_message(telegram_id: int, text: str) -> dict:
    """Fetch categories then run LLM intent parsing."""
    try:
        categories = await get_categories(telegram_id)
    except Exception as exc:
        logger.warning("Could not fetch categories: %s", exc)
        categories = []

    try:
        result = groq.parse_intent(text, categories)
    except Exception as exc:
        logger.error("Groq parse_intent failed: %s", exc)
        result = {
            "intent": "unknown",
            "missing_fields": [],
            "confidence": 0.0,
            "original_language": "en",
        }

    # Resolve category name → id
    if result.get("category") and categories:
        cat_name_lower = result["category"].lower()
        cat_type = result.get("type")
        match = None
        for c in categories:
            if c["name"].lower() == cat_name_lower:
                if cat_type is None or c["type"] == cat_type:
                    match = c
                    break
        if match is None:
            # Fuzzy match
            for c in categories:
                if cat_name_lower in c["name"].lower() or c["name"].lower() in cat_name_lower:
                    if cat_type is None or c["type"] == cat_type:
                        match = c
                        break
        if match:
            result["category_id"] = match["id"]
            result["category_name"] = match["name"]
            if "category" not in result.get("missing_fields", []):
                result.setdefault("missing_fields", [])
                if "category" in result["missing_fields"]:
                    result["missing_fields"].remove("category")
        else:
            if "category" not in result.get("missing_fields", []):
                result.setdefault("missing_fields", []).append("category")

    return result
