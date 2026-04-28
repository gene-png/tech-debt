# Tech Debt Workbench — Context File

This file is the running log of decisions, work completed, and open questions for the **Software Rationalization Workbench** (the standalone Flask app under `software_rationalization/`). Updated after each series of commands.

---

## Project at a glance

- **Goal:** web-accessible dashboard implementing the 11-phase *Software Inventory, License Review, and Technical Debt Reduction Playbook*.
- **Local location:** `software_rationalization/` — a standalone app, separate from the parent TSMA assessment app.
- **GitHub:** https://github.com/gene-png/tech-debt — mirror of `software_rationalization/` flattened to repo root (so a fresh clone runs `python app.py` directly).
- **Stack:** Flask + Jinja2 + plain CSS. JSON file storage (one file per engagement under `data/`).
- **Port:** 5055 — http://localhost:5055
- **Run:** `cd software_rationalization && pip install -r requirements.txt && python app.py`

## GitHub sync workflow

The local working copy lives in this worktree under `software_rationalization/`. The GitHub repo at https://github.com/gene-png/tech-debt expects the **same files at the repo root** (no `software_rationalization/` prefix). To push updates, mirror the contents to a working clone and push. A scratch working copy used for the initial push lives at `C:/Users/pow_w/AppData/Local/Temp/tech-debt-push`. For long-term use, clone `tech-debt.git` somewhere permanent and treat that as the canonical pull/push target — the worktree copy here is convenient for iteration but the temp directory is ephemeral.

### Recent pushes

- `f90df8b` (2026-04-27) — Initial commit: Phases 1 & 2 build (16 files).
- `0eef907` (2026-04-27) — Documented GitHub sync workflow in this context file.
- `98d0bed` (2026-04-27) — Phase 3: Build the Software Inventory (10 files changed, +1097 lines).
- `0adbac0` (2026-04-27) — Refresh techdebtcontext.md to post-Phase-3 state.
- `fd36790` (2026-04-28) — Phase 4: Normalize the Data (7 files changed, +816 lines).

The `data/` JSON files and `data/uploads/` directory are excluded by `.gitignore` — no customer data is ever pushed.

## Phase status

| # | Phase                          | Status   |
|---|--------------------------------|----------|
| 1 | Define the Scope               | **Live** |
| 2 | Request Customer Data          | **Live** |
| 3 | Build the Software Inventory   | **Live** |
| 4 | Normalize the Data             | **Live** |
| 5 | Identify Product Overlap       | Planned  |
| 6 | AI Assisted Comparison         | Planned  |
| 7 | Identify Technical Debt        | Planned  |
| 8 | Estimate Cost Savings          | Planned  |
| 9 | Validate with Stakeholders     | Planned  |
| 10 | Create Recommendations        | Planned  |
| 11 | Create the Executive Summary  | Planned  |

## Architecture

- **`app.py`** — All Flask routes for live phases (Phase 1 scope, Phase 2 data request + uploads, Phase 3 inventory CRUD / CSV+XLSX import-export), plus form coercion helpers, status-statement / checklist / inventory-export generators, and Jinja filters (`format_bytes`, `money`, `phase_label`, `phase_status_class`). The `PHASES` constant drives the sidebar; adding a new phase means adding a route + template + entry in `phase_progress`.
- **`storage.py`** — JSON file I/O for engagements (`load_engagement`, `save_engagement`, `list_engagements`), plus the `new_engagement()` factory that pre-seeds `phase_progress` and `scope`. Other phases (`data_request`, `inventory`) are lazily initialized inside `app.py` on first visit so an engagement created before a phase shipped still works.
- **`templates/`** — `base.html` is the shared shell, `_sidebar.html` renders the phase nav with status dots, and each phase has dedicated templates: `engagement_scope.html` + `scope_statement.html` (Phase 1), `data_request.html` + `data_request_checklist.html` (Phase 2), `inventory_list.html` + `inventory_form.html` + `inventory_import.html` (Phase 3). The two "statement" / "checklist" templates are print-styled and use a separate `.statement` CSS class.
- **`static/style.css`** — single CSS file, no JS framework, no build step. Sections: base/typography, layout, sidebar, panels, forms, tags, statement (print), Phase 2 data-request, Phase 3 inventory table.
- **`data/`** — runtime, gitignored. One JSON file per engagement plus `uploads/<engagement_id>/<item_id>/` for Phase 2 file storage.

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

inventory: {                           ← Phase 3
  products: [
    {
      id, created_at, updated_at,
      product_name, vendor, version, category,
      business_owner, technical_owner, contract_owner,
      licenses_purchased, licenses_assigned, active_users,
      cost_per_license, total_annual_cost,
      renewal_date, contract_term, purchase_source,
      deployment_model, primary_use_case, systems_supported,
      data_sensitivity, security_compliance,
      known_risks, notes,
    }
  ],
  finalized, finalized_at,
}

normalize: {                            ← Phase 4 (auto-init when inventory finalizes)
  ignored_issues: {
    "<issue_id>": { ignored_at, reason }
  },
  finalized, finalized_at,
}
```

**Issue ID schemes** (deterministic, so ignores stick across reloads):
- `dup:<sorted product ids joined>` — duplicate product cluster
- `vv:<sorted normalized vendor names joined with |>` — vendor name variants
- `cv:<unmapped category text>` — category outside the standard list
- `uc:<product_id>` — uncategorized
- `mo:<product_id>:<missing-roles-csv>` — missing ownership
- `mc:<product_id>` — missing cost
- `mu:<product_id>` — missing primary use case
- `la:<product_id>:<type>` — license math anomaly

Future phases will add new top-level keys (e.g. `overlap`, `tech_debt`, `recommendations`) without touching existing fields.

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

## Phase 3 deliverable

The **Master Software Inventory** is the deliverable for Phase 3. Available as:
- Web view: `/engagements/<id>/inventory` (sortable / filterable table, summary tiles for product count, annual spend, licenses purchased / assigned, by-category rollup)
- CSV export: `/engagements/<id>/inventory/export.csv`
- XLSX export (formatted, frozen header): `/engagements/<id>/inventory/export.xlsx`
- Blank CSV template for customers preparing data: `/engagements/<id>/inventory/template.csv`

CRUD operations:
- Add: `/engagements/<id>/inventory/new`
- Edit: `/engagements/<id>/inventory/<product_id>/edit`
- Delete: POST `/engagements/<id>/inventory/<product_id>/delete`
- Import (CSV or XLSX, fuzzy column-header matching): `/engagements/<id>/inventory/import`

The 22 master inventory fields and their CSV header aliases live in `PRODUCT_FIELDS` and `PRODUCT_FIELD_ALIASES` in `app.py`. Column-header matching is case- and whitespace-insensitive — a column called "Annual Cost", "annual_cost", or "Yearly Cost" all map to `total_annual_cost`. Rows missing a product name are skipped and counted in the import result.

Auto-calc behaviour: if `total_annual_cost` is blank but `cost_per_license` and `licenses_purchased` are both present, the total is computed on save / import.

Finalize advances `status` to `normalize` and pre-marks Phase 4 as `in_progress`. Reopen reverts.

## Phase 4 deliverable

The **Cleaned and Categorized Software Inventory** — Phase 4 doesn't produce a new artifact, it *transforms* the Phase 3 inventory in place. The normalize page surfaces eight kinds of findings, all of which can be fixed inline:

| Detector | What it flags | Fix offered |
|----------|---------------|-------------|
| Duplicates | Same normalized (product, vendor) on 2+ rows | Pick keeper, merge (delete others) |
| Vendor variants | Different spellings/suffixes of the same vendor (suffix-strip pass + difflib pass at 0.85) | Pick canonical name, apply to all rows in cluster |
| Unmapped categories | Categories outside `PRODUCT_CATEGORIES` | Map to a standard category (suggested via difflib at 0.6) |
| Uncategorized | Blank category | Edit product |
| Missing owners | Blank business / technical / contract owner | Edit product |
| Missing cost | Blank cost-per-license AND blank total-annual-cost | Edit product |
| Unclear use | Blank primary use case | Edit product |
| License anomalies | `assigned > purchased` or `users > assigned` | Edit product |

**Ignore mechanism** — every finding has a stable `issue_id`. Marking a finding "ignore" stores `{ignored_at, reason}` in `normalize.ignored_issues`; subsequent loads skip it. Un-ignore is a single click.

**Routes:**
- GET `/engagements/<id>/normalize` — main workspace
- POST `/normalize/apply-vendor` — standardize vendor cluster (`cluster_norms` + `canonical`)
- POST `/normalize/apply-category` — remap a category (`old_category` + `new_category`)
- POST `/normalize/merge-duplicates` — keep one row, delete others (`keep_id` + `delete_ids` CSV)
- POST `/normalize/ignore` — ignore or un-ignore (`issue_id`, optional `reason`, optional `action=unignore`)
- POST `/normalize/finalize` — finalize / reopen

Finalize advances `status` to `overlap` and pre-marks Phase 5 as `in_progress`.

## Routes quick reference

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Engagement list + playbook overview |
| `/engagements/new` | GET / POST | Create engagement |
| `/engagements/<id>` | GET | Engagement overview (all phase panels) |
| `/engagements/<id>/scope` | GET / POST | Phase 1 — scope form (save / finalize / reopen) |
| `/engagements/<id>/scope/statement` | GET | Phase 1 deliverable (printable HTML) |
| `/engagements/<id>/scope/statement.txt` | GET | Phase 1 deliverable (.txt download) |
| `/engagements/<id>/data-request` | GET / POST | Phase 2 — checklist + per-item status / message / finalize |
| `/engagements/<id>/data-request/items/<iid>/upload` | POST | Phase 2 — file upload (multipart) |
| `/engagements/<id>/data-request/items/<iid>/files/<fid>` | GET | Phase 2 — file download |
| `/engagements/<id>/data-request/items/<iid>/files/<fid>/delete` | POST | Phase 2 — file delete |
| `/engagements/<id>/data-request/checklist` | GET | Phase 2 deliverable (printable HTML) |
| `/engagements/<id>/data-request/checklist.txt` | GET | Phase 2 deliverable (.txt download) |
| `/engagements/<id>/inventory` | GET | Phase 3 — list (`?q=&category=&sort=&dir=`) |
| `/engagements/<id>/inventory/new` | GET / POST | Phase 3 — add product |
| `/engagements/<id>/inventory/<pid>/edit` | GET / POST | Phase 3 — edit product |
| `/engagements/<id>/inventory/<pid>/delete` | POST | Phase 3 — delete product |
| `/engagements/<id>/inventory/import` | GET / POST | Phase 3 — CSV / XLSX import |
| `/engagements/<id>/inventory/finalize` | POST | Phase 3 — finalize / reopen |
| `/engagements/<id>/inventory/export.csv` | GET | Phase 3 deliverable (CSV) |
| `/engagements/<id>/inventory/export.xlsx` | GET | Phase 3 deliverable (formatted XLSX) |
| `/engagements/<id>/inventory/template.csv` | GET | Empty CSV template (canonical headers) |
| `/engagements/<id>/normalize` | GET | Phase 4 — guided cleanup workspace |
| `/engagements/<id>/normalize/apply-vendor` | POST | Phase 4 — standardize vendor cluster |
| `/engagements/<id>/normalize/apply-category` | POST | Phase 4 — remap unmapped category |
| `/engagements/<id>/normalize/merge-duplicates` | POST | Phase 4 — merge duplicate cluster |
| `/engagements/<id>/normalize/ignore` | POST | Phase 4 — ignore / un-ignore finding |
| `/engagements/<id>/normalize/finalize` | POST | Phase 4 — finalize / reopen |

## Decisions made

- **Standalone app** under `software_rationalization/`, separate from the parent TSMA Flask app — keeps concerns clean and avoids touching existing TSMA storage/templates.
- **Port 5055** chosen to avoid clashing with the parent app on the default 5000.
- **Owner records** entered as `Name | Role | email` per line — keeps the form simple while still producing structured records.
- **Phase progress** stored as a per-key dict rather than a single status field — lets phases be reopened independently.
- **No auth yet** — single-user local workbench. Add auth before deploying anywhere shared.
- **GitHub repo flattened** — the dashboard sits at the root of `tech-debt.git`, not under `software_rationalization/`. Rationale: a fresh clone should be runnable with `pip install && python app.py`; nesting it would force every user to `cd` first.
- **Phase 2 uploads stored on disk, metadata in JSON** — keeps the JSON file small and lets the user open the original files directly. Filenames are stored as `<file_id>_<safe_filename>` to avoid collisions while preserving the human name on download.
- **Auto status transitions in Phase 2** — first upload → "Received", deleting last file → "Requested". Cuts manual clicks for the common case while still letting the consultant override.
- **Fuzzy CSV header matching for Phase 3 import** — customers ship spreadsheets in inconsistent formats. `PRODUCT_FIELD_ALIASES` lets headers like "Annual Cost", "yearly cost", or "annual_cost" all map to the same field. Strict matching would force re-formatting before every import.
- **Auto-calc `total_annual_cost`** — if blank but `cost_per_license × licenses_purchased` are present, the total is filled. Manual entries always take precedence.
- **openpyxl for XLSX I/O** — already a dependency of the parent TSMA app; reusing it keeps deps minimal. CSV is preferred for round-tripping (no XLSX read on import would block customers; we support both).
- **Finalize-then-pre-mark-next** — finalizing a phase advances the engagement `status` AND pre-marks the next phase as `in_progress`. Gives the next phase visible momentum in the sidebar instead of looking idle.

## Verified working

Each live phase has a complete end-to-end smoke test (Flask test client) plus live-server confirmation. Specifics live in the per-phase change-log entries below; high-level current state:

- App boots on port 5055 (Flask dev server, debug + autoreloader on). All static assets served.
- **Phase 1** — engagement create, scope edit, save draft, finalize, reopen, scope statement HTML + `.txt` download.
- **Phase 2** — auto-init checklist on first visit, status updates, customer-message save, multi-file upload (verified bytes round-trip via download), checklist HTML + `.txt`, file delete with auto status revert, finalize / reopen with status transitions.
- **Phase 3** — inventory CRUD (auto-calc total verified), CSV import with fuzzy header matching (rows missing product name skipped and counted), XLSX import, list page with search + category filter + per-column sort, CSV export with all 22 columns, formatted XLSX export (verified valid ZIP container), blank CSV template, finalize / reopen advancing engagement to Phase 4.
- Live server traffic confirmed for `/`, `/engagements/<id>`, `/engagements/<id>/scope`, `/engagements/<id>/data-request`, `/engagements/<id>/inventory` and their sub-routes (200 / 302 in access log after Flask reloader picks up edits).

## Open questions / next decisions

- ~~Phase 2 — static checklist or real uploads?~~ **Resolved: real uploads with on-disk storage.**
- ~~Inventory build (Phase 3) — manual entry first, or CSV/XLSX import first?~~ **Resolved: both. Manual add form + CSV/XLSX import with fuzzy column matching.**
- ~~Phase 4 (Normalize) — separate review pass or inline?~~ **Resolved: separate review pass. Eight detectors run live each load, producing findings with stable issue IDs. One-click apply for vendor / category / merge; "ignore with reason" for false positives; remaining findings link to the product editor.**
- Customer-facing self-upload portal — currently the consultant uploads on the customer's behalf. A token-protected upload link the customer can use directly is a future enhancement (would need expiring tokens, throttling, anti-virus scan).
- Phase 5 (Identify Overlap) — overlap is a category-level question ("two project management tools, one wins"). Likely a per-category breakdown showing all products in that category side-by-side with cost / users / contract status, plus per-product disposition (Keep / Consolidate / Retire / Replace / Renegotiate / Further review).
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

### 2026-04-27 — Initial GitHub publish

- The worktree's `origin` was pointed at `gene-png/csf2-tool.git` (a different project), so adding `tech-debt` as a remote inside the worktree would have been confusing. Instead, the project was staged into a clean temp directory (`C:/Users/pow_w/AppData/Local/Temp/tech-debt-push`) with the `software_rationalization/` contents flattened to the root.
- Verified the GitHub repo `gene-png/tech-debt` was empty, then ran `git init -b main`, added origin, committed everything (16 files), and pushed.
- `git push -u origin main` succeeded; `git ls-remote` confirms `refs/heads/main` at commit `f90df8b9...`.
- `data/` JSON files and `data/uploads/` were excluded by `.gitignore` so no customer data ever lands on GitHub.

### 2026-04-27 — Phase 3 build (Build the Software Inventory)

- Added `openpyxl` to `requirements.txt` for XLSX import / export.
- Added Phase 3 constants to `app.py`: `PRODUCT_CATEGORIES` (16 + Other), `DEPLOYMENT_MODELS` (6), `DATA_SENSITIVITY_LEVELS` (4), `PRODUCT_FIELDS` (22 fields with type metadata), `PRODUCT_FIELD_ALIASES` (CSV header fuzzy-match dictionary).
- Helpers: `_ensure_inventory`, `_new_product`, `_coerce_int / _money / _date`, `_apply_form` (with auto-calc of total_annual_cost), `_csv_header_to_field`, `_import_csv_text`, `_inventory_summary`.
- New routes: list (`/inventory` with `?q=...&category=...&sort=...&dir=...`), `/inventory/new`, `/inventory/<pid>/edit`, `/inventory/<pid>/delete`, `/inventory/import` (CSV + XLSX), `/inventory/finalize`, `/inventory/export.csv`, `/inventory/export.xlsx`, `/inventory/template.csv` (blank).
- New templates: `inventory_list.html` (table with per-column sort, search box, category filter, summary tiles, by-category rollup, finalize button), `inventory_form.html` (grouped 22-field form with auto-calc placeholder hint and inline delete), `inventory_import.html` (upload + recognized-headers reference table).
- Updated `_sidebar.html` to make Phase 3 clickable; updated `engagement_view.html` to surface a Phase 3 panel and offer the XLSX export from there; updated `home.html` to mark Phase 3 as Live.
- New CSS: `.inventory-table` (sticky header, numeric column alignment), `.sort-link`, `.inventory-scroll`, `.category-rollup`. New `money` Jinja filter.
- Smoke test (Flask test client): create engagement → add product (auto-calc 12.50×500=6250 verified) → edit (override total) → CSV import (4 rows added, 1 missing-name row skipped) → list, search, category filter, sort all return 200 → CSV export (header row matches PRODUCT_FIELDS) → XLSX export (verified ZIP container is valid) → blank template → delete → finalize (advances to Phase 4 `in_progress`) → reopen → engagement view renders Phase 3 panel. All checks pass. Live server confirmed Phase 3 routes return 200 after the Flask reloader picked up changes. (Caught and fixed one Jinja syntax error: nested-escape backslashes in a JS confirm dialog were rejected by the parser; simplified the confirm message.)

### 2026-04-27 — Context file refresh

- Refreshed `techdebtcontext.md` to reflect the post-Phase-3 state. Architecture section now describes all live-phase code paths (was Phase-1 only). "Verified working" section replaced the stale Phase-1-only list with a per-phase summary plus pointer to the change-log entries below. Added a "Recent pushes" subsection under GitHub sync workflow. Added a "Routes quick reference" table covering all live endpoints. Captured the design decisions made during Phase 2 and Phase 3 (file storage on disk, auto status transitions, fuzzy CSV matching, auto-calc total, openpyxl reuse, finalize-then-pre-mark-next).
- Removed a slightly inaccurate sentence: data model said "future phases will add new top-level keys (e.g. `inventory`, …)" — `inventory` is no longer hypothetical.

### 2026-04-28 — Phase 4 build (Normalize the Data)

- Added `import difflib` to top-level imports.
- Phase 4 helpers: `_ensure_normalize`, `_norm_text`, `_norm_vendor` (strips a curated list of corporate suffixes — Inc, Corp, Corporation, Technologies, LLC, GmbH, AG, etc.), eight detector functions (`detect_duplicates`, `detect_vendor_variants`, `detect_unmapped_categories`, `detect_uncategorized`, `detect_missing_owners`, `detect_missing_cost`, `detect_unclear_use`, `detect_license_anomalies`), `_build_vendor_cluster`, and `collect_normalize_findings` (filters out ignored issues + adds `total_open` count).
- Vendor variant detection runs in two passes: first a suffix-strip group (catches "Microsoft" vs "Microsoft Corporation" exactly), then difflib at 0.85 over the remaining single-spelling normalized vendors (catches typos like "Atlasian" vs "Atlassian"). Initial threshold was 0.85 only — caught typos but missed the suffix case (12-char suffix delta drops ratio below threshold). Added the suffix-strip pass to fix.
- New routes: `engagement_normalize` (GET), `apply-vendor` / `apply-category` / `merge-duplicates` / `ignore` / `finalize` (all POST).
- New template `normalize.html`: summary tiles for each finding category, separate sections for duplicates (with merge form), vendor variants (with canonical-name input), unmapped categories (with mapping select), license anomalies, missing data (sub-grouped: ownership / cost / uncategorized / unclear use), an "Ignored findings" panel, and a finalize button.
- New CSS: `.finding`, `.finding-header`, `.finding-table`. `_sidebar.html` enables Phase 4 link, `engagement_view.html` surfaces a Phase 4 panel, `home.html` marks Phase 4 as Live.
- Smoke test (Flask test client, file-based to dodge bash-quoting headaches): seeded 8 specimen products covering all eight detector cases. Verified counts (1 dup, ≥1 vendor variant, 1 unmapped cat, 1 each missing-owner / cost / use case / uncategorized, 2 license anomalies). Applied vendor standardization → both Microsoft variants merged. Applied category standardization → Wiki/KB → Document management. Merged duplicate Slack pair → 1 Slack row left. Ignored a license anomaly → count drops by 1, ignored_count rises; un-ignore reverses both. Finalize advanced engagement to Phase 5 and pre-marked overlap as `in_progress`. Reopen reverses. Live server confirmed `/normalize` returns 200 after reloader picked up changes.
