import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def engagement_path(engagement_id):
    return os.path.join(DATA_DIR, f"{engagement_id}.json")


def load_engagement(engagement_id):
    path = engagement_path(engagement_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_engagement(engagement):
    _ensure_dir()
    engagement["updated_at"] = datetime.utcnow().isoformat() + "Z"
    with open(engagement_path(engagement["id"]), "w", encoding="utf-8") as f:
        json.dump(engagement, f, indent=2)


def list_engagements():
    _ensure_dir()
    out = []
    for fn in os.listdir(DATA_DIR):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(DATA_DIR, fn), "r", encoding="utf-8") as f:
                out.append(json.load(f))
        except (json.JSONDecodeError, OSError):
            continue
    out.sort(key=lambda e: e.get("updated_at", ""), reverse=True)
    return out


def new_engagement(name, client, lead):
    import uuid
    eid = uuid.uuid4().hex[:8]
    now = datetime.utcnow().isoformat() + "Z"
    eng = {
        "id": eid,
        "name": name,
        "client": client,
        "lead": lead,
        "created_at": now,
        "updated_at": now,
        "status": "scope",
        "phase_progress": {
            "scope": "in_progress",
            "data_request": "not_started",
            "inventory": "not_started",
            "normalize": "not_started",
            "overlap": "not_started",
            "ai_review": "not_started",
            "tech_debt": "not_started",
            "savings": "not_started",
            "validation": "not_started",
            "recommendations": "not_started",
            "exec_summary": "not_started",
        },
        "scope": {
            "business_units": [],
            "tool_categories": [],
            "include_corporate_card": False,
            "include_enterprise_agreements": False,
            "include_department_purchases": False,
            "include_shadow_it": False,
            "renewal_window": "",
            "contract_owners": [],
            "technical_owners": [],
            "business_owners": [],
            "objectives": "",
            "out_of_scope": "",
            "constraints": "",
            "scope_notes": "",
            "finalized": False,
            "finalized_at": None,
        },
    }
    save_engagement(eng)
    return eng
