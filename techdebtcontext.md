# Tech Debt Workbench — Context File

This file is the running log of decisions, work completed, and open questions for the **Software Rationalization Workbench** (the standalone Flask app under `software_rationalization/`). Updated after each series of commands.

---

## Project at a glance

- **Goal:** web-accessible dashboard implementing the 11-phase *Software Inventory, License Review, and Technical Debt Reduction Playbook*.
- **Location:** `software_rationalization/` — a standalone app, separate from the parent TSMA assessment app.
- **Stack:** Flask + Jinja2 + plain CSS. JSON file storage (one file per engagement under `data/`).
- **Port:** 5055 — http://localhost:5055
- **Run:** `cd software_rationalization && pip install -r requirements.txt && python app.py`

## Phase status

| # | Phase                          | Status   |
|---|--------------------------------|----------|
| 1 | Define the Scope               | **Live** |
| 2 | Request Customer Data          | **Live** |
| 3 | Build the Software Inventory   | Planned  |
| 4 | Normalize the Data             | Planned  |
| 5 | Identify Product Overlap       | Planned  |
| 6 | AI Assisted Comparison         | Planned  |
| 7 | Identify Technical Debt        | Planned  |
| 8 | Estimate Cost Savings          | Planned  |
| 9 | Validate with Stakeholders     | Planned  |
| 10 | Create Recommendations        | Planned  |
| 11 | Create the Executive Summary  | Planned  |

## Architecture

- **`app.py`** — Flask routes, form parsing, scope statement generator. `PHASES` constant drives the sidebar; adding a new phase means adding a route + template + an entry in `phase_progress`.
- **`storage.py`** — JSON file I/O for engagements, plus `new_engagement()` factory that pre-seeds the `phase_progress` and `scope` keys.
- **`templates/`** — `base.html` is the shared shell, `_sidebar.html` renders the phase nav, individual templates per phase. `scope_statement.html` is print-styled.
- **`static/style.css`** — single CSS file; no JS framework, no build step.
- **`data/`** — runtime, gitignored. One JSON file per engagement.

## Data model (engagement JSON)

```
id, name, client, lead, created_at, updated_at, status
phase_progress: { scope, data_request, inventory, ... }   ← one of: not_started | in_progress | complete

scope: {                              ← Phase 1
  business_units[], tool_categories[],
  include_corporate_card, include_enterprise_agreements,
  include_department_purchases, include_shadow_it,
  renewal_window,
  contract_owners[], technical_owners[], business_owners[],   ← {name, role, email}
  objectives, out_of_scope, constraints, scope_notes,
  finalized, finalized_at,
}

data_request: {                        ← Phase 2 (auto-initialized on first visit)
  documents: [
    {
      id, doc_type_key, doc_type_label,
      status,         ← requested | received | not_applicable | waived
      notes,
      uploaded_files: [
        { id, original_filename, stored_filename, size_bytes, uploaded_at, content_type }
      ]
    }
  ],
  customer_message,
  finalized, finalized_at,
}
```

Future phases will add new top-level keys (e.g. `inventory`, `overlap`, `tech_debt`, `recommendations`) without touching existing fields.

### File upload storage

Uploaded files live under `data/uploads/<engagement_id>/<item_id>/<file_id>_<safe_filename>`. The JSON record holds metadata only — the actual bytes are on disk. Allowed extensions: PDF, CSV, TSV, XLSX, XLS, XLSM, DOCX, DOC, TXT, MD, PNG, JPG, JPEG, GIF, JSON, XML, ZIP, PPTX, PPT, VSDX, VSD. Max 50 MB per request (Flask `MAX_CONTENT_LENGTH`).

## Phase 1 deliverable

Once scope is finalized, the **Software Review Scope Statement** is available as:
- HTML (printable): `/engagements/<id>/scope/statement`
- Plain text download: `/engagements/<id>/scope/statement.txt`

## Phase 2 deliverable

The **Customer Data Request Checklist** is available at any time (auto-initializes 18 default document types):
- Consultant working view: `/engagements/<id>/data-request`
- Customer-facing checklist (printable): `/engagements/<id>/data-request/checklist`
- Plain text download: `/engagements/<id>/data-request/checklist.txt`

Per-item operations:
- Update status/notes: POST to `/engagements/<id>/data-request` with `action=update_item`
- Upload file(s): POST multipart to `/engagements/<id>/data-request/items/<item_id>/upload`
- Download a file: GET `/engagements/<id>/data-request/items/<item_id>/files/<file_id>`
- Delete a file: POST `/engagements/<id>/data-request/items/<item_id>/files/<file_id>/delete`

Behaviours worth noting:
- Uploading a file auto-flips status from "Requested" to "Received".
- Deleting the last uploaded file reverts status from "Received" back to "Requested".
- Finalizing Phase 2 transitions the engagement to Phase 3 (Inventory) status and pre-marks Phase 3 as `in_progress` so the next phase is visibly ready when it ships.

The 18 document types are defined in `DATA_REQUEST_TYPES` in `app.py`, matching the playbook list verbatim.

## Decisions made

- **Standalone app** under `software_rationalization/`, separate from the parent TSMA Flask app — keeps concerns clean and avoids touching existing TSMA storage/templates.
- **Port 5055** chosen to avoid clashing with the parent app on the default 5000.
- **Owner records** entered as `Name | Role | email` per line — keeps the form simple while still producing structured records.
- **Phase progress** stored as a per-key dict rather than a single status field — lets phases be reopened independently.
- **No auth yet** — single-user local workbench. Add auth before deploying anywhere shared.

## Verified working (this session)

- App boots on port 5055 (Flask dev server, debug mode on).
- Routes returning 200/302 in real browser session (server log confirms):
  - `GET /` (home)
  - `GET /engagements/new`
  - `POST /engagements/new` → 302 redirect
  - `GET /engagements/<id>` (overview)
  - `GET /engagements/<id>/scope` (Phase 1 form)
- Flask test-client smoke test exercised the full Phase 1 flow including finalize, HTML statement, and `.txt` download.

## Open questions / next decisions

- ~~Phase 2 — static checklist or real uploads?~~ **Resolved: real uploads with on-disk storage.**
- Customer-facing self-upload portal — currently the consultant uploads on the customer's behalf. A token-protected upload link the customer can use directly is a future enhancement (would need expiring tokens, throttling, anti-virus scan).
- Inventory build (Phase 3) — manual entry first, or CSV/XLSX import first? Probably CSV import since the customer typically has spreadsheets, plus a manual add row for one-offs.
- Multi-user / auth — not needed for v1 but will be once this is hosted somewhere shared.
- Backup strategy for `data/` JSON + `data/uploads/` — currently nothing. Once real customer documents are stored, we'll want at least a periodic zip of the engagement folder.
- Phase 2 file size limit — currently 50 MB per request. Some asset management exports could exceed this; revisit if it becomes an issue.

---

## Change log

### 2026-04-27 — Phase 1 build + first run

- Scaffolded `software_rationalization/` (folders, `requirements.txt`, `.gitignore`).
- Implemented `storage.py` with engagement JSON I/O and the `new_engagement` factory.
- Implemented `app.py` with routes for home, new-engagement, engagement-view, Phase 1 scope edit, scope-statement HTML, and scope-statement `.txt`.
- Built CSS shell (`static/style.css`) and templates: `base.html`, `_sidebar.html`, `home.html`, `engagement_new.html`, `engagement_view.html`, `engagement_scope.html`, `scope_statement.html`.
- Smoke-tested the full Phase 1 flow via Flask's test client — all routes returned 200/302.
- Started the actual server (`python app.py`) — initial run reported "didn't open" because the smoke test had only used the test client, not started a real server. Started in background; verified `HTTP 200` via curl. User-driven traffic in the access log confirms the dashboard is reachable in the browser.
- Created this `techdebtcontext.md` to track ongoing decisions and changes.

### 2026-04-27 — Phase 2 build (Request Customer Data)

- Added Phase 2 constants (`DATA_REQUEST_TYPES`, `DATA_REQUEST_STATUSES`, upload allowed extensions, 50 MB max content length) to `app.py`.
- Added `_ensure_data_request()` to lazily initialize the 18-item checklist on first visit.
- New routes: `engagement_data_request` (GET/POST), `engagement_data_request_upload`, `engagement_data_request_download`, `engagement_data_request_delete_file`, `engagement_data_request_checklist`, `engagement_data_request_checklist_txt`.
- Auto-status behaviour: first upload flips an item to "Received"; deleting the last file reverts to "Requested".
- Finalize/reopen workflow on Phase 2 mirrors Phase 1; finalize advances `status` to `inventory` and pre-marks Phase 3 as `in_progress`.
- New templates: `data_request.html` (consultant view) and `data_request_checklist.html` (customer-facing printable). Updated `_sidebar.html` to make Phase 2 clickable, `engagement_view.html` to surface a Phase 2 status panel, and `home.html` to mark both Phase 1 and 2 as Live.
- New CSS: `.dr-summary` summary tiles, `.status-pill` status pills, `.file-list`, `.checklist-table`, `.btn-link`. `data/uploads/` added to `.gitignore`.
- New `format_bytes` Jinja filter for file sizes.
- Smoke test (Flask test client) exercised: auto-init, status update, customer message save, file upload (verified bytes round-trip via download), checklist HTML, checklist .txt, file delete (with auto status revert), finalize (verified phase_progress + status transitions), reopen, engagement view rendering. All 14 steps passed. Live server confirmed Phase 2 routes return 200 after Flask reloader picked up the changes.
