import os
import uuid

from flask import Flask, render_template, request, redirect, url_for, abort, Response, send_from_directory
from datetime import datetime
from werkzeug.utils import secure_filename

import storage

app = Flask(__name__)

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "uploads")
MAX_UPLOAD_BYTES = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {
    ".pdf", ".csv", ".tsv", ".xlsx", ".xls", ".xlsm", ".docx", ".doc",
    ".txt", ".md", ".png", ".jpg", ".jpeg", ".gif", ".json", ".xml",
    ".zip", ".pptx", ".ppt", ".vsdx", ".vsd",
}
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES

DATA_REQUEST_TYPES = [
    ("current_inventory", "Current software inventory"),
    ("license_agreements", "License agreements"),
    ("purchase_orders", "Purchase orders"),
    ("invoices", "Invoices"),
    ("renewal_notices", "Renewal notices"),
    ("saas_exports", "SaaS subscription exports"),
    ("cloud_marketplace", "Cloud marketplace purchases"),
    ("vendor_contracts", "Vendor contracts"),
    ("enterprise_license_agreements", "Enterprise license agreements"),
    ("asset_management", "Asset management exports"),
    ("endpoint_software", "Endpoint software reports"),
    ("idp_apps", "Identity provider application lists"),
    ("finance_procurement", "Finance or procurement reports"),
    ("helpdesk_catalog", "Help desk application catalog"),
    ("cyber_tool_list", "Cybersecurity tool list"),
    ("architecture", "Architecture diagrams"),
    ("network_endpoint_exports", "Network or endpoint management exports"),
    ("critical_apps", "Business critical applications list"),
]

DATA_REQUEST_STATUSES = [
    ("requested", "Requested"),
    ("received", "Received"),
    ("not_applicable", "N/A"),
    ("waived", "Waived"),
]

TOOL_CATEGORIES = [
    ("cloud", "Cloud services"),
    ("saas", "SaaS applications"),
    ("desktop", "Desktop software"),
    ("server", "Server software"),
    ("security", "Security tools"),
    ("infrastructure", "Infrastructure"),
    ("network", "Network tools"),
    ("data", "Data and analytics"),
    ("dev", "Development tools"),
    ("ai", "AI tools"),
]

PHASES = [
    ("scope", "1. Define the Scope"),
    ("data_request", "2. Request Customer Data"),
    ("inventory", "3. Build Inventory"),
    ("normalize", "4. Normalize Data"),
    ("overlap", "5. Identify Overlap"),
    ("ai_review", "6. AI Assisted Comparison"),
    ("tech_debt", "7. Identify Technical Debt"),
    ("savings", "8. Estimate Cost Savings"),
    ("validation", "9. Stakeholder Validation"),
    ("recommendations", "10. Recommendations"),
    ("exec_summary", "11. Executive Summary"),
]


def _parse_lines(text):
    if not text:
        return []
    return [line.strip() for line in text.splitlines() if line.strip()]


def _parse_owners(text):
    """Parse 'Name | Role | Email' lines into structured records."""
    out = []
    for line in _parse_lines(text):
        parts = [p.strip() for p in line.split("|")]
        record = {"name": parts[0] if len(parts) > 0 else ""}
        if len(parts) > 1:
            record["role"] = parts[1]
        if len(parts) > 2:
            record["email"] = parts[2]
        out.append(record)
    return out


def _owners_to_text(owners):
    lines = []
    for o in owners or []:
        parts = [o.get("name", "")]
        if o.get("role"):
            parts.append(o["role"])
        if o.get("email"):
            parts.append(o["email"])
        lines.append(" | ".join(parts))
    return "\n".join(lines)


@app.route("/")
def home():
    engagements = storage.list_engagements()
    return render_template("home.html", engagements=engagements, phases=PHASES)


@app.route("/engagements/new", methods=["GET", "POST"])
def engagement_new():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        client = request.form.get("client", "").strip()
        lead = request.form.get("lead", "").strip()
        if not name or not client:
            return render_template(
                "engagement_new.html",
                error="Engagement name and client are required.",
                form=request.form,
            )
        eng = storage.new_engagement(name=name, client=client, lead=lead)
        return redirect(url_for("engagement_view", engagement_id=eng["id"]))
    return render_template("engagement_new.html", error=None, form={})


@app.route("/engagements/<engagement_id>")
def engagement_view(engagement_id):
    eng = storage.load_engagement(engagement_id)
    if not eng:
        abort(404)
    return render_template(
        "engagement_view.html",
        eng=eng,
        phases=PHASES,
    )


@app.route("/engagements/<engagement_id>/scope", methods=["GET", "POST"])
def engagement_scope(engagement_id):
    eng = storage.load_engagement(engagement_id)
    if not eng:
        abort(404)

    if request.method == "POST":
        scope = eng.get("scope", {})
        scope["business_units"] = _parse_lines(request.form.get("business_units", ""))
        scope["tool_categories"] = request.form.getlist("tool_categories")
        scope["include_corporate_card"] = bool(request.form.get("include_corporate_card"))
        scope["include_enterprise_agreements"] = bool(request.form.get("include_enterprise_agreements"))
        scope["include_department_purchases"] = bool(request.form.get("include_department_purchases"))
        scope["include_shadow_it"] = bool(request.form.get("include_shadow_it"))
        scope["renewal_window"] = request.form.get("renewal_window", "").strip()
        scope["contract_owners"] = _parse_owners(request.form.get("contract_owners", ""))
        scope["technical_owners"] = _parse_owners(request.form.get("technical_owners", ""))
        scope["business_owners"] = _parse_owners(request.form.get("business_owners", ""))
        scope["objectives"] = request.form.get("objectives", "").strip()
        scope["out_of_scope"] = request.form.get("out_of_scope", "").strip()
        scope["constraints"] = request.form.get("constraints", "").strip()
        scope["scope_notes"] = request.form.get("scope_notes", "").strip()

        action = request.form.get("action", "save")
        if action == "finalize":
            scope["finalized"] = True
            scope["finalized_at"] = datetime.utcnow().isoformat() + "Z"
            eng["phase_progress"]["scope"] = "complete"
            eng["phase_progress"]["data_request"] = "in_progress"
            eng["status"] = "data_request"
        elif action == "reopen":
            scope["finalized"] = False
            scope["finalized_at"] = None
            eng["phase_progress"]["scope"] = "in_progress"
            eng["status"] = "scope"
        else:
            if not scope.get("finalized"):
                eng["phase_progress"]["scope"] = "in_progress"

        eng["scope"] = scope
        storage.save_engagement(eng)
        if action == "finalize":
            return redirect(url_for("scope_statement", engagement_id=engagement_id))
        return redirect(url_for("engagement_scope", engagement_id=engagement_id))

    return render_template(
        "engagement_scope.html",
        eng=eng,
        tool_categories=TOOL_CATEGORIES,
        owners_to_text=_owners_to_text,
        phases=PHASES,
    )


@app.route("/engagements/<engagement_id>/scope/statement")
def scope_statement(engagement_id):
    eng = storage.load_engagement(engagement_id)
    if not eng:
        abort(404)
    cat_lookup = dict(TOOL_CATEGORIES)
    return render_template(
        "scope_statement.html",
        eng=eng,
        cat_lookup=cat_lookup,
    )


@app.route("/engagements/<engagement_id>/scope/statement.txt")
def scope_statement_txt(engagement_id):
    eng = storage.load_engagement(engagement_id)
    if not eng:
        abort(404)
    s = eng.get("scope", {})
    cat_lookup = dict(TOOL_CATEGORIES)

    def yn(v):
        return "Yes" if v else "No"

    lines = []
    lines.append("SOFTWARE REVIEW SCOPE STATEMENT")
    lines.append("=" * 50)
    lines.append(f"Engagement: {eng.get('name', '')}")
    lines.append(f"Client: {eng.get('client', '')}")
    lines.append(f"Lead consultant: {eng.get('lead', '')}")
    lines.append(f"Created: {eng.get('created_at', '')}")
    if s.get("finalized_at"):
        lines.append(f"Scope finalized: {s.get('finalized_at')}")
    lines.append("")
    lines.append("OBJECTIVES")
    lines.append("-" * 50)
    lines.append(s.get("objectives") or "(not set)")
    lines.append("")
    lines.append("BUSINESS UNITS IN SCOPE")
    lines.append("-" * 50)
    for bu in s.get("business_units") or []:
        lines.append(f"- {bu}")
    if not s.get("business_units"):
        lines.append("(none listed)")
    lines.append("")
    lines.append("TOOL CATEGORIES IN SCOPE")
    lines.append("-" * 50)
    for k in s.get("tool_categories") or []:
        lines.append(f"- {cat_lookup.get(k, k)}")
    if not s.get("tool_categories"):
        lines.append("(none selected)")
    lines.append("")
    lines.append("PURCHASE SOURCES IN SCOPE")
    lines.append("-" * 50)
    lines.append(f"Corporate credit card purchases: {yn(s.get('include_corporate_card'))}")
    lines.append(f"Enterprise agreements: {yn(s.get('include_enterprise_agreements'))}")
    lines.append(f"Department-level purchases: {yn(s.get('include_department_purchases'))}")
    lines.append(f"Shadow IT / non-IT purchases: {yn(s.get('include_shadow_it'))}")
    lines.append("")
    lines.append("RENEWAL WINDOW")
    lines.append("-" * 50)
    lines.append(s.get("renewal_window") or "(not set)")
    lines.append("")

    for label, key in [
        ("CONTRACT OWNERS", "contract_owners"),
        ("TECHNICAL OWNERS", "technical_owners"),
        ("BUSINESS OWNERS", "business_owners"),
    ]:
        lines.append(label)
        lines.append("-" * 50)
        people = s.get(key) or []
        if not people:
            lines.append("(none listed)")
        for p in people:
            bits = [p.get("name", "")]
            if p.get("role"):
                bits.append(p["role"])
            if p.get("email"):
                bits.append(p["email"])
            lines.append("- " + " | ".join(bits))
        lines.append("")

    lines.append("OUT OF SCOPE")
    lines.append("-" * 50)
    lines.append(s.get("out_of_scope") or "(not set)")
    lines.append("")
    lines.append("CONSTRAINTS AND ASSUMPTIONS")
    lines.append("-" * 50)
    lines.append(s.get("constraints") or "(not set)")
    lines.append("")
    lines.append("ADDITIONAL NOTES")
    lines.append("-" * 50)
    lines.append(s.get("scope_notes") or "(none)")

    body = "\n".join(lines)
    fn = f"scope-statement-{eng.get('id')}.txt"
    return Response(
        body,
        mimetype="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


# ---------------------------------------------------------------------------
# Phase 2 — Request Customer Data
# ---------------------------------------------------------------------------

def _ensure_data_request(eng):
    """Initialize the Phase 2 data structure on the engagement if missing."""
    dr = eng.get("data_request")
    if dr and dr.get("documents"):
        return False
    documents = []
    for key, label in DATA_REQUEST_TYPES:
        documents.append({
            "id": uuid.uuid4().hex[:8],
            "doc_type_key": key,
            "doc_type_label": label,
            "status": "requested",
            "notes": "",
            "uploaded_files": [],
        })
    eng["data_request"] = {
        "documents": documents,
        "customer_message": "",
        "finalized": False,
        "finalized_at": None,
    }
    return True


def _engagement_upload_dir(engagement_id, item_id):
    p = os.path.join(UPLOADS_DIR, engagement_id, item_id)
    os.makedirs(p, exist_ok=True)
    return p


def _data_request_summary(dr):
    summary = {"requested": 0, "received": 0, "not_applicable": 0, "waived": 0}
    for d in dr["documents"]:
        summary[d["status"]] = summary.get(d["status"], 0) + 1
    summary["total"] = len(dr["documents"])
    summary["files_total"] = sum(len(d.get("uploaded_files", [])) for d in dr["documents"])
    return summary


@app.route("/engagements/<engagement_id>/data-request", methods=["GET", "POST"])
def engagement_data_request(engagement_id):
    eng = storage.load_engagement(engagement_id)
    if not eng:
        abort(404)

    initialized = _ensure_data_request(eng)
    if initialized:
        if (eng["phase_progress"].get("scope") == "complete"
                and eng["phase_progress"].get("data_request") == "not_started"):
            eng["phase_progress"]["data_request"] = "in_progress"
        storage.save_engagement(eng)

    if request.method == "POST":
        action = request.form.get("action")
        dr = eng["data_request"]
        if action == "save_message":
            dr["customer_message"] = request.form.get("customer_message", "").strip()
        elif action == "update_item":
            item_id = request.form.get("item_id")
            for d in dr["documents"]:
                if d["id"] == item_id:
                    new_status = request.form.get("status", d["status"])
                    if new_status in dict(DATA_REQUEST_STATUSES):
                        d["status"] = new_status
                    d["notes"] = request.form.get("notes", "").strip()
                    break
        elif action == "finalize":
            dr["finalized"] = True
            dr["finalized_at"] = datetime.utcnow().isoformat() + "Z"
            eng["phase_progress"]["data_request"] = "complete"
            eng["status"] = "inventory"
            if eng["phase_progress"].get("inventory") == "not_started":
                eng["phase_progress"]["inventory"] = "in_progress"
        elif action == "reopen":
            dr["finalized"] = False
            dr["finalized_at"] = None
            eng["phase_progress"]["data_request"] = "in_progress"
            eng["status"] = "data_request"
        else:
            return "Unknown action", 400

        if not dr["finalized"] and eng["phase_progress"]["data_request"] == "not_started":
            eng["phase_progress"]["data_request"] = "in_progress"
        storage.save_engagement(eng)
        return redirect(url_for("engagement_data_request", engagement_id=engagement_id))

    summary = _data_request_summary(eng["data_request"])
    return render_template(
        "data_request.html",
        eng=eng,
        statuses=DATA_REQUEST_STATUSES,
        summary=summary,
        phases=PHASES,
    )


@app.route("/engagements/<engagement_id>/data-request/items/<item_id>/upload", methods=["POST"])
def engagement_data_request_upload(engagement_id, item_id):
    eng = storage.load_engagement(engagement_id)
    if not eng:
        abort(404)
    _ensure_data_request(eng)
    item = next((d for d in eng["data_request"]["documents"] if d["id"] == item_id), None)
    if not item:
        abort(404)

    files = request.files.getlist("file")
    saved = 0
    for f in files:
        if not f or not f.filename:
            continue
        original = f.filename
        ext = os.path.splitext(original)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            continue
        safe = secure_filename(original) or "upload"
        file_id = uuid.uuid4().hex[:8]
        stored_filename = f"{file_id}_{safe}"
        upload_dir = _engagement_upload_dir(engagement_id, item_id)
        full_path = os.path.join(upload_dir, stored_filename)
        f.save(full_path)
        size = os.path.getsize(full_path)
        item["uploaded_files"].append({
            "id": file_id,
            "original_filename": original,
            "stored_filename": stored_filename,
            "size_bytes": size,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "content_type": f.mimetype,
        })
        if item["status"] == "requested":
            item["status"] = "received"
        saved += 1

    if eng["phase_progress"].get("data_request") == "not_started":
        eng["phase_progress"]["data_request"] = "in_progress"
    storage.save_engagement(eng)
    return redirect(url_for("engagement_data_request", engagement_id=engagement_id) + f"#item-{item_id}")


@app.route("/engagements/<engagement_id>/data-request/items/<item_id>/files/<file_id>")
def engagement_data_request_download(engagement_id, item_id, file_id):
    eng = storage.load_engagement(engagement_id)
    if not eng:
        abort(404)
    item = next((d for d in eng.get("data_request", {}).get("documents", []) if d["id"] == item_id), None)
    if not item:
        abort(404)
    fr = next((fl for fl in item["uploaded_files"] if fl["id"] == file_id), None)
    if not fr:
        abort(404)
    upload_dir = os.path.join(UPLOADS_DIR, engagement_id, item_id)
    return send_from_directory(
        upload_dir,
        fr["stored_filename"],
        as_attachment=True,
        download_name=fr["original_filename"],
    )


@app.route("/engagements/<engagement_id>/data-request/items/<item_id>/files/<file_id>/delete", methods=["POST"])
def engagement_data_request_delete_file(engagement_id, item_id, file_id):
    eng = storage.load_engagement(engagement_id)
    if not eng:
        abort(404)
    item = next((d for d in eng.get("data_request", {}).get("documents", []) if d["id"] == item_id), None)
    if not item:
        abort(404)
    fr = next((fl for fl in item["uploaded_files"] if fl["id"] == file_id), None)
    if not fr:
        abort(404)
    full_path = os.path.join(UPLOADS_DIR, engagement_id, item_id, fr["stored_filename"])
    try:
        if os.path.exists(full_path):
            os.remove(full_path)
    except OSError:
        pass
    item["uploaded_files"] = [fl for fl in item["uploaded_files"] if fl["id"] != file_id]
    if not item["uploaded_files"] and item["status"] == "received":
        item["status"] = "requested"
    storage.save_engagement(eng)
    return redirect(url_for("engagement_data_request", engagement_id=engagement_id) + f"#item-{item_id}")


@app.route("/engagements/<engagement_id>/data-request/checklist")
def engagement_data_request_checklist(engagement_id):
    eng = storage.load_engagement(engagement_id)
    if not eng:
        abort(404)
    if _ensure_data_request(eng):
        storage.save_engagement(eng)
    return render_template("data_request_checklist.html", eng=eng)


@app.route("/engagements/<engagement_id>/data-request/checklist.txt")
def engagement_data_request_checklist_txt(engagement_id):
    eng = storage.load_engagement(engagement_id)
    if not eng:
        abort(404)
    if _ensure_data_request(eng):
        storage.save_engagement(eng)
    dr = eng["data_request"]
    status_label = dict(DATA_REQUEST_STATUSES)
    lines = []
    lines.append("CUSTOMER DATA REQUEST CHECKLIST")
    lines.append("=" * 50)
    lines.append(f"Engagement: {eng.get('name')}")
    lines.append(f"Client: {eng.get('client')}")
    if eng.get("lead"):
        lines.append(f"Lead consultant: {eng['lead']}")
    lines.append("")
    if dr.get("customer_message"):
        lines.append("MESSAGE FROM CONSULTANT")
        lines.append("-" * 50)
        lines.append(dr["customer_message"])
        lines.append("")
    lines.append("REQUESTED DOCUMENTS")
    lines.append("-" * 50)
    for i, d in enumerate(dr["documents"], 1):
        sl = status_label.get(d["status"], d["status"])
        lines.append(f"{i:2d}. [ {sl:>9s} ]  {d['doc_type_label']}")
        if d.get("notes"):
            lines.append(f"      Notes: {d['notes']}")
    body = "\n".join(lines)
    fn = f"data-request-checklist-{eng.get('id')}.txt"
    return Response(
        body,
        mimetype="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


@app.template_filter("format_bytes")
def format_bytes(n):
    if n is None:
        return ""
    n = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{int(n)} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


@app.template_filter("phase_label")
def phase_label_filter(key):
    return dict(PHASES).get(key, key)


@app.template_filter("phase_status_class")
def phase_status_class(value):
    return {
        "complete": "status-complete",
        "in_progress": "status-progress",
        "not_started": "status-pending",
    }.get(value, "status-pending")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5055, debug=True)
