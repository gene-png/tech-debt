"""
Phase 6 — AI Assisted Comparison.

This module handles the *anonymization* of customer data before it is sent to
the Claude API and the *de-anonymization* of the response so the user sees
their own identifiers.

Why anonymize: a software-rationalization workspace contains organizational
detail (client name, employee names, internal system names, free-text notes
that may quote people). If the AI traffic is ever logged or leaked, none of
that should be recoverable from the prompt or response. Vendor and product
names ARE sent because the AI needs them to reason about overlap (Slack vs
Microsoft Teams is meaningful; "Tool A" vs "Tool B" tells the AI nothing) —
those are public-knowledge identifiers, not customer-private.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import threading
from datetime import datetime
from typing import Tuple

import storage


# Whitelist — only these fields leave the box. Everything else is dropped.
AI_SAFE_FIELDS = (
    "product_name",
    "vendor",
    "version",
    "category",
    "licenses_purchased",
    "licenses_assigned",
    "active_users",
    "cost_per_license",
    "total_annual_cost",
    "renewal_date",
    "contract_term",
    "deployment_model",
    "primary_use_case",
    "data_sensitivity",
)

# Fields that COULD contain PII or org-internal identifiers and are explicitly
# stripped. Listed here so the UI can show the user what we're protecting.
AI_REDACTED_FIELDS = (
    "business_owner",
    "technical_owner",
    "contract_owner",
    "purchase_source",
    "systems_supported",
    "security_compliance",
    "known_risks",
    "notes",
)

DEFAULT_MODEL = "claude-opus-4-7"
HARD_TIMEOUT_SECONDS = 60
MAX_PRODUCTS_PER_RUN = 200


# ---------------------------------------------------------------------------
# Anonymization
# ---------------------------------------------------------------------------

def anonymize_inventory(eng: dict) -> Tuple[list, dict]:
    """
    Return (sanitized_products, deanon_map).

    sanitized_products: list of dicts with anonymized IDs (PROD_001, ...)
                        containing ONLY whitelisted fields.
    deanon_map:         {anon_id -> real_product_id} so AI output can be
                        mapped back to real products.
    """
    products = eng.get("inventory", {}).get("products", [])
    if len(products) > MAX_PRODUCTS_PER_RUN:
        products = products[:MAX_PRODUCTS_PER_RUN]
    sanitized = []
    deanon_map = {}
    for i, p in enumerate(products, 1):
        anon_id = f"PROD_{i:03d}"
        deanon_map[anon_id] = p["id"]
        s = {"id": anon_id}
        for f in AI_SAFE_FIELDS:
            v = p.get(f)
            if v not in (None, ""):
                s[f] = v
        sanitized.append(s)
    return sanitized, deanon_map


def inventory_hash(sanitized_products: list) -> str:
    """Stable 16-char hash for cache invalidation."""
    text = json.dumps(sanitized_products, sort_keys=True, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Claude call
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an enterprise software rationalization consultant.

You will receive a sanitized software inventory in JSON. All products are
referenced by anonymized IDs in the format PROD_NNN. Reference products
ONLY by these IDs in your output. Do not invent products or IDs.

Identify products with overlapping functionality, duplicate business use
cases, underused licenses, outdated products, and potential consolidation
opportunities. Group findings by software category.

Return strict JSON in this exact schema (no commentary, no markdown
fences). Keep each finding self-contained:

{
  "findings": [
    {
      "category": "string — software category",
      "summary": "string — one-line headline",
      "products_involved": ["PROD_NNN", "..."],
      "concern": "string — what is the issue / overlap",
      "potential_risk": "string — risk if left unaddressed or risk of changing",
      "estimated_cost_impact": "string — rough $ or % impact",
      "recommended_next_step": "string — concrete first action"
    }
  ]
}
"""


def call_claude(sanitized_products: list, model: str = DEFAULT_MODEL) -> Tuple[dict, str]:
    """
    Call the Anthropic API. Returns (parsed_findings_dict, raw_text).
    Raises RuntimeError on configuration / API failure.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Export it in your environment "
            "before running the AI review."
        )
    try:
        from anthropic import Anthropic
    except ImportError as exc:
        raise RuntimeError(
            "anthropic SDK not installed. Run: pip install anthropic"
        ) from exc

    client = Anthropic(api_key=api_key, timeout=HARD_TIMEOUT_SECONDS)
    user_message = (
        f"Inventory ({len(sanitized_products)} products):\n"
        f"{json.dumps(sanitized_products, indent=2, default=str)}"
    )
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    text = ""
    for block in response.content or []:
        if getattr(block, "type", None) == "text":
            text += block.text
    return _parse_findings_json(text), text


def _parse_findings_json(text: str) -> dict:
    """Tolerant JSON extraction. Returns {'findings': []} on failure."""
    if not text:
        return {"findings": []}
    # Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Markdown code fence
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # First top-level {...findings...} block
    m = re.search(r"\{[\s\S]*\"findings\"[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return {"findings": []}


# ---------------------------------------------------------------------------
# De-anonymization
# ---------------------------------------------------------------------------

def deanonymize_findings(findings_dict: dict, deanon_map: dict, products_by_id: dict) -> list:
    """
    Replace anonymized PROD_xxx references with real product details.
    Returns a list of finding dicts with a `products` array of full product
    info (name, vendor, category, annual cost) instead of anonymized IDs.
    """
    out = []
    for f in findings_dict.get("findings", []) or []:
        details = []
        for anon_id in f.get("products_involved", []) or []:
            real_id = deanon_map.get(anon_id)
            if not real_id:
                continue
            p = products_by_id.get(real_id)
            if not p:
                continue
            details.append({
                "id": real_id,
                "product_name": p.get("product_name", ""),
                "vendor": p.get("vendor", ""),
                "category": p.get("category", ""),
                "annual_cost": p.get("total_annual_cost", ""),
            })
        out.append({
            "category": (f.get("category") or "").strip(),
            "summary": (f.get("summary") or "").strip(),
            "products": details,
            "concern": (f.get("concern") or "").strip(),
            "potential_risk": (f.get("potential_risk") or "").strip(),
            "estimated_cost_impact": (f.get("estimated_cost_impact") or "").strip(),
            "recommended_next_step": (f.get("recommended_next_step") or "").strip(),
        })
    return out


# ---------------------------------------------------------------------------
# Background worker
# ---------------------------------------------------------------------------

_running_engagements: set = set()
_running_lock = threading.Lock()


def is_running(engagement_id: str) -> bool:
    with _running_lock:
        return engagement_id in _running_engagements


def kick_off_review(engagement_id: str) -> bool:
    """Start a background review run if one isn't already in flight."""
    with _running_lock:
        if engagement_id in _running_engagements:
            return False
        _running_engagements.add(engagement_id)
    t = threading.Thread(
        target=_run_review_worker,
        args=(engagement_id,),
        daemon=True,
        name=f"ai-review-{engagement_id}",
    )
    t.start()
    return True


def _run_review_worker(engagement_id: str) -> None:
    try:
        eng = storage.load_engagement(engagement_id)
        if not eng:
            return
        eng.setdefault("ai_review", _new_ai_review_block())
        eng["ai_review"]["running"] = True
        eng["ai_review"]["started_at"] = datetime.utcnow().isoformat() + "Z"
        eng["ai_review"]["error"] = None
        storage.save_engagement(eng)

        sanitized, deanon_map = anonymize_inventory(eng)
        h = inventory_hash(sanitized)
        products_by_id = {p["id"]: p for p in eng.get("inventory", {}).get("products", [])}

        try:
            findings_raw, raw_text = call_claude(sanitized)
        except Exception as exc:  # noqa: BLE001
            eng = storage.load_engagement(engagement_id)
            eng.setdefault("ai_review", _new_ai_review_block())
            eng["ai_review"]["running"] = False
            eng["ai_review"]["error"] = str(exc)
            eng["ai_review"]["completed_at"] = datetime.utcnow().isoformat() + "Z"
            storage.save_engagement(eng)
            return

        findings_real = deanonymize_findings(findings_raw, deanon_map, products_by_id)

        eng = storage.load_engagement(engagement_id)
        eng.setdefault("ai_review", _new_ai_review_block())
        eng["ai_review"].update({
            "running": False,
            "completed_at": datetime.utcnow().isoformat() + "Z",
            "model": DEFAULT_MODEL,
            "last_inventory_hash": h,
            "findings": findings_real,
            "raw_response": raw_text,
            "error": None,
            "anonymization_summary": {
                "total_products": len(sanitized),
                "redacted_fields": list(AI_REDACTED_FIELDS),
                "safe_fields": list(AI_SAFE_FIELDS),
            },
        })
        storage.save_engagement(eng)
    finally:
        with _running_lock:
            _running_engagements.discard(engagement_id)


def _new_ai_review_block() -> dict:
    return {
        "running": False,
        "started_at": None,
        "completed_at": None,
        "model": "",
        "last_inventory_hash": "",
        "findings": [],
        "raw_response": "",
        "error": None,
        "anonymization_summary": {},
        "finalized": False,
        "finalized_at": None,
    }


def ensure_ai_review(eng: dict) -> bool:
    if "ai_review" in eng and "findings" in eng["ai_review"]:
        return False
    eng["ai_review"] = _new_ai_review_block()
    return True


def is_stale(eng: dict) -> bool:
    """True if there are no cached findings, or the inventory hash changed."""
    ar = eng.get("ai_review") or {}
    if ar.get("running"):
        return False
    if not ar.get("findings"):
        return True
    sanitized, _ = anonymize_inventory(eng)
    return inventory_hash(sanitized) != ar.get("last_inventory_hash", "")


def has_api_key() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))
