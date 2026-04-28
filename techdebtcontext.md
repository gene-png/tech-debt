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
- `f4cbb98` (2026-04-28) — Backfill fd36790 commit hash in change log.
- `e9a919b` (2026-04-28) — Phase 5: Identify Product Overlap (8 files changed, +605 lines).
- `f280ab5` (2026-04-28) — Backfill e9a919b commit hash in change log.
- `54827a5` (2026-04-28) — Phase 6: AI Assisted Comparison (9 files changed, +785 lines).
- `5bf593e` (2026-04-28) — Backfill 54827a5 commit hash in change log.
- `8a56e8b` (2026-04-28) — Phase 7: Identify Technical Debt (8 files changed, +764 lines).
- `df10622` (2026-04-28) — Backfill 8a56e8b commit hash in change log.
- `6e29025` (2026-04-28) — Phase 8: Estimate Cost Savings (8 files changed, +930 lines).
- `2553709` (2026-04-28) — Backfill 6e29025 commit hash in change log.
- `feddd7d` (2026-04-28) — Phase 9: Validate with Stakeholders (8 files changed, +710 lines).
- `493930c` (2026-04-28) — Backfill feddd7d commit hash in change log.
- `632e47b` (2026-04-28) — Phase 10: Create Recommendations (8 files changed, +968 lines).
- `5a8eeb0` (2026-04-28) — Backfill 632e47b commit hash in change log.
- `9df6df6` (2026-04-28) — Phase 11: Executive Summary — all 11 phases complete (8 files changed, +744 lines).

The `data/` JSON files and `data/uploads/` directory are excluded by `.gitignore` — no customer data is ever pushed.

## Phase status

| # | Phase                          | Status   |
|---|--------------------------------|----------|
| 1 | Define the Scope               | **Live** |
| 2 | Request Customer Data          | **Live** |
| 3 | Build the Software Inventory   | **Live** |
| 4 | Normalize the Data             | **Live** |
| 5 | Identify Product Overlap       | **Live** |
| 6 | AI Assisted Comparison         | **Live** |
| 7 | Identify Technical Debt        | **Live** |
| 8 | Estimate Cost Savings          | **Live** |
| 9 | Validate with Stakeholders     | **Live** |
| 10 | Create Recommendations        | **Live** |
| 11 | Create the Executive Summary  | **Live** |

**All 11 playbook phases are now live.**

## Architecture

- **`app.py`** — All Flask routes for live phases (Phase 1 scope, Phase 2 data request + uploads, Phase 3 inventory CRUD / CSV+XLSX import-export, Phase 4 normalize, Phase 5 overlap, Phase 6 AI review), plus form coercion helpers, statement / checklist / inventory-export / overlap-analysis generators, and Jinja filters (`format_bytes`, `money`, `phase_label`, `phase_status_class`). The `PHASES` constant drives the sidebar; adding a new phase means adding a route + template + entry in `phase_progress`.
- **`ai_service.py`** — Phase 6 only. Anonymization (whitelist of safe fields, anonymized PROD_NNN IDs), Anthropic SDK call (system prompt + JSON-shaped output schema), tolerant JSON parsing (handles direct JSON / fenced / prose-with-fence), de-anonymization (maps PROD_NNN back to real product IDs and enriches findings with product details), background-thread worker with a per-engagement run lock. Hash-based cache invalidation by sanitized-inventory SHA-256.
- **`storage.py`** — JSON file I/O for engagements (`load_engagement`, `save_engagement`, `list_engagements`), plus the `new_engagement()` factory that pre-seeds `phase_progress` and `scope`. Other phases (`data_request`, `inventory`, `normalize`, `overlap`, `ai_review`) are lazily initialized inside `app.py` / `ai_service.py` on first visit so an engagement created before a phase shipped still works.
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

overlap: {                              ← Phase 5
  dispositions: {
    "<product_id>": {
      disposition,         ← keep | consolidate | retire | replace | renegotiate | further_review
      risk_of_removal,     ← low | medium | high | unknown
      notes,
      updated_at,
    }
  },
  finalized, finalized_at,
}

ai_review: {                            ← Phase 6
  running, started_at, completed_at,
  model,                            ← e.g. claude-opus-4-7
  last_inventory_hash,              ← cache-invalidation key (sanitized inventory hash)
  findings: [
    {
      category, summary,
      products: [{ id, product_name, vendor, category, annual_cost }],   ← re-hydrated from anonymized IDs
      concern, potential_risk, estimated_cost_impact, recommended_next_step,
    }
  ],
  raw_response,                     ← raw text from Claude (debug)
  error,                            ← string if last run failed
  anonymization_summary: { total_products, redacted_fields, safe_fields },
  finalized, finalized_at,
}

tech_debt: {                            ← Phase 7
  flags: {
    "<product_id>": {
      flags: [...]   ← any of: unsupported, outdated_version, unused, duplicative,
                       no_owner, unclear_mission, outside_governance, no_integration,
                       weak_security, manual_burden, data_silo, poor_adoption,
                       high_cost_low_value, renewal_no_justification
      severity: "low" | "medium" | "high",
      notes,
      updated_at,
    }
  },
  finalized, finalized_at,
}

savings: {                              ← Phase 8
  opportunities: {
    "<opp_id>": {
      id, title, source, seed_key,    ← source = phase5 | phase7-unused | manual
      product_ids: [...],
      disposition,                    ← retire | replace | consolidate | renegotiate | reduce_licenses | other
      current_annual_cost,            ← editable; auto-summed from product_ids on creation
      recurring_annual_savings,       ← editable; default depends on disposition
      one_time_savings,               ← e.g. break renewal, renegotiation discount
      migration_cost, training_cost,
      notes,
      status,                         ← proposed | approved | rejected
      created_at, updated_at,
    }
  },
  finalized, finalized_at,
}

validation: {                           ← Phase 9 (anchored to Phase 8 opportunities)
  validations: {
    "<opp_id>": {
      stakeholders: [
        {name, role_code, role_label, consulted_date, status_code, status_label, notes}
      ],
      answers: {
        who_uses, business_process, what_breaks, better_tool,
        required_by, cost_justified, absorbed_by,
      },
      overall_status,                 ← not_started | pending | validated | blocked
      notes,
      updated_at,
    }
  },
  finalized, finalized_at,
}

recommendations: {                      ← Phase 10
  recs: {
    "<rec_id>": {
      id, source_opp_id, seed_key,    ← seed_key=phase8:<opp_id> for auto-seeded; empty for manual
      finding,
      product_ids: [...],
      business_impact, tech_debt_impact, security_impact, cost_impact,
      recommended_action,
      category,                       ← one of 8 (immediate_savings, renewal_negotiation, license_reduction, consolidation, retirement, security_risk_reduction, governance_improvement, further_analysis)
      level_of_effort,                ← low | medium | high | ""
      risk_level,                     ← low | medium | high | ""
      timeline, decision_owner,
      notes,
      status,                         ← draft | accepted | deferred
      created_at, updated_at,
    }
  },
  finalized, finalized_at,
}

exec_summary: {                         ← Phase 11
  narrative: {
    headline,                       ← TL;DR for leadership
    key_finding,                    ← strategic pattern across the engagement
    top_recommendation,             ← highest-impact ask
    leadership_ask,                 ← 1–3 specific decisions needed
    next_steps,                     ← proposed timeline
  },
  finalized, finalized_at,
}
```

When Phase 11 finalizes, the engagement-level `status` flips to `complete` (instead of pre-marking a next phase, since this is the last one).

**Stakeholder roles** (8 from the playbook): IT leadership, Cybersecurity team, Finance, Procurement, Business unit owner, System administrator, Power user, Compliance / legal.

**Stakeholder per-line statuses**: Consulted, Agreed, Pushback, Blocked.

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

## Phase 5 deliverable

The **Product Overlap Analysis** — captures every category that has 2+ products, side-by-side comparison, and a per-product disposition decision. Available as:
- Workspace: `/engagements/<id>/overlap`
- Printable analysis: `/engagements/<id>/overlap/analysis`
- CSV export: `/engagements/<id>/overlap/analysis.csv`

**Disposition options** (per playbook):
- `keep` — current state
- `consolidate` — merge into another product in the same category
- `retire` — remove without replacement
- `replace` — swap for a different product
- `renegotiate` — keep but renegotiate terms
- `further_review` — undecided

**Risk of removal:** `low` / `medium` / `high` / `unknown`.

**Potential savings calculation:** sum of `total_annual_cost` across products marked `retire`, `replace`, or `consolidate` (controlled by `SAVINGS_DISPOSITIONS` in `app.py`). The summary tile updates as you save dispositions; the printable analysis bakes in the value at render time.

**Form behaviour:** one form per category with all dispositions submitted together (a single "Save category decisions" button per panel). Submitting blank values for a product clears its entry from `overlap.dispositions`. Categories with only one product are not shown — they're not overlap candidates.

Finalize advances `status` to `ai_review` and pre-marks Phase 6 as `in_progress`.

## Phase 6 deliverable

The **AI Assisted Comparison** is a Claude-generated review of the inventory grouped by category. Findings are presented as `summary` / `concern` / `potential_risk` / `estimated_cost_impact` / `recommended_next_step` with the affected products linked back to the inventory editor.

### Privacy model

This is the most security-sensitive part of the workspace. Inventory data is *anonymized* before leaving the box:

**Whitelist sent to Claude** (only these fields): `product_name`, `vendor`, `version`, `category`, `licenses_purchased`, `licenses_assigned`, `active_users`, `cost_per_license`, `total_annual_cost`, `renewal_date`, `contract_term`, `deployment_model`, `primary_use_case`, `data_sensitivity`. Each product is referenced by an anonymized ID (`PROD_001`, `PROD_002`…).

**Stripped before send** (always): `business_owner`, `technical_owner`, `contract_owner`, `purchase_source`, `systems_supported`, `security_compliance`, `known_risks`, `notes`. Engagement metadata (name, client, lead consultant) and product UUIDs never leave the box either.

Why these specific fields: vendor and product names *are* sent because the AI needs them to reason about overlap (Slack vs Microsoft Teams is meaningful; "Tool A" vs "Tool B" is useless). Those are public-knowledge identifiers, not customer-private. Owner names, internal system names, free-text notes (which often quote employees), and customer purchase details are exactly the things that would identify the customer if a prompt log leaked.

### De-anonymization

The AI's response references products only by `PROD_NNN`. After the call returns, those tokens are mapped back to real product IDs via an in-memory `deanon_map` (built fresh each run from the inventory order — never persisted), and each finding is enriched with `{id, product_name, vendor, category, annual_cost}` of the real products. The user sees their real product names and links; the API never did.

### Auto-run + manual re-run

When the user navigates to `/ai-review` and findings are stale (no findings yet, or the inventory hash differs from the last run), a background thread is kicked off automatically. The page renders a spinner with a 3-second meta-refresh until the worker writes results back. A manual "Re-run review" button is also visible at all times once findings exist. Cache invalidation is by SHA-256 of the sanitized inventory: change anything sent to the AI and the cache misses.

### Failure modes handled

- **No `ANTHROPIC_API_KEY`** — page renders setup instructions; Run button hidden.
- **Empty inventory** — page asks the user to build the inventory in Phase 3 first.
- **API call fails** (timeout, key rejected, network) — error stored on `ai_review.error` and surfaced with a Retry button.
- **Malformed JSON from Claude** — `_parse_findings_json` tries direct parse, then a fenced code block, then a regex over the response text. Falls back to an empty findings list rather than crashing.

### Routes

- GET `/engagements/<id>/ai-review` — main page (auto-runs if stale).
- POST `/engagements/<id>/ai-review/run` — force re-run.
- POST `/engagements/<id>/ai-review/finalize` — finalize / reopen. Finalize advances `status` to `tech_debt` and pre-marks Phase 7 as `in_progress`.

## Phase 7 deliverable

The **Technical Debt Findings Register** — captures, per product, which of the 14 debt categories from the playbook apply, plus severity (low/medium/high) and free-text notes. Available as:
- Workspace: `/engagements/<id>/tech-debt`
- Printable register: `/engagements/<id>/tech-debt/register`
- CSV export: `/engagements/<id>/tech-debt/register.csv`

### Auto-suggestions

Each product gets a list of *suggested* flags derived from the inventory it already has. Suggestions are NOT applied automatically — they appear as clickable yellow chips above the flag checkboxes; clicking a chip ticks the corresponding checkbox in the form (vanilla JS, no framework). Logic in `_suggest_debt_flags`:

| Suggested flag | Trigger |
|----------------|---------|
| `no_owner` | Any of business / technical / contract owner is blank |
| `unclear_mission` | `primary_use_case` is blank |
| `duplicative` | Product's category has 2+ products in the inventory |
| `unused` | `licenses_assigned > 0` AND `active_users == 0` |
| `poor_adoption` | `licenses_assigned > 0` AND `0 < active_users < licenses_assigned * 0.2` |
| `outside_governance` | `purchase_source` contains "card", "personal", "shadow", or "expense" |
| `high_cost_low_value` | Annual cost ≥ 75th percentile AND `active_users < licenses_purchased * 0.5` |
| `renewal_no_justification` | Renewal date within 90 days AND `primary_use_case` blank |

Detectors are deliberately conservative (mostly require multiple signals) to keep noise low.

### Filters

The workspace supports three filters via query string: `?flag=<key>` (only rows with that flag), `?severity=<level>`, and `?only_with_debt=1` (hide healthy products). Filter UI sits below the summary tiles.

### Routes

- GET `/engagements/<id>/tech-debt` — workspace (auto-init on first visit, supports filters)
- POST `/engagements/<id>/tech-debt/<product_id>` — save flags / severity / notes for one product (clears entry if all three are blank)
- POST `/engagements/<id>/tech-debt/finalize` — finalize / reopen (finalize advances `status` to `savings` and pre-marks Phase 8 as `in_progress`)
- GET `/engagements/<id>/tech-debt/register` — printable register, sorted by severity (high first) then product name
- GET `/engagements/<id>/tech-debt/register.csv` — CSV export

## Phase 8 deliverable

The **Cost Savings Estimate** is a structured worksheet of consolidation opportunities, each with current cost / transition cost / one-time / recurring / first-year-net broken out and rolled up to a portfolio total. Available as:
- Workspace: `/engagements/<id>/savings`
- Printable estimate: `/engagements/<id>/savings/estimate`
- CSV export: `/engagements/<id>/savings/estimate.csv`

### Auto-seeding from earlier phases

Click **Seed from Phase 5 + 7** to bootstrap opportunities. Idempotent — re-clicking won't duplicate (uses a stable `seed_key`):
- **Phase 5 dispositions** (`retire`, `replace`, `consolidate`, `renegotiate`) → one opportunity per product. `recurring_annual_savings` defaults to the product's full `total_annual_cost`, except `renegotiate` defaults to 20% (representing a discount, not full savings).
- **Phase 7 `unused` flag** (only when not already covered by Phase 5) → "Reduce unused licenses" opportunity. `recurring_annual_savings = cost_per_license × (purchased − active_users)`. Falls back to a proportional split of annual cost if per-license cost is missing.

User can add **custom opportunities** alongside seeded ones (multi-product, free-form title, dropdown disposition).

### Per-opportunity worksheet

Each opportunity card has editable fields for `current_annual_cost`, `recurring_annual_savings`, `one_time_savings`, `migration_cost`, `training_cost`, plus title / disposition / status / notes. Three computed totals shown live below:
- **Recurring / yr** = `recurring_annual_savings`
- **Net first-year** = `recurring + one_time − migration − training`
- **Transition cost** = `migration + training`

### Status-aware rollups

The portfolio summary shows two views: an **all-non-rejected** total (proposed + approved) and an **approved-only** total. Rejected opportunities are excluded from both. Approved-only is the conservative number to share with leadership; non-rejected is the upside if every proposed opportunity lands.

### Routes

- GET `/engagements/<id>/savings` — workspace
- POST `/engagements/<id>/savings/seed` — auto-seed from Phase 5 + 7 (idempotent)
- POST `/engagements/<id>/savings/new` — add a custom opportunity
- POST `/engagements/<id>/savings/<opp_id>/edit` — update one opportunity (all fields)
- POST `/engagements/<id>/savings/<opp_id>/status` — quick-action approve / reject / reset
- POST `/engagements/<id>/savings/<opp_id>/delete` — delete one opportunity
- POST `/engagements/<id>/savings/finalize` — finalize / reopen (advances `status` to `validation`, pre-marks Phase 9 `in_progress`)
- GET `/engagements/<id>/savings/estimate` — printable HTML
- GET `/engagements/<id>/savings/estimate.csv` — CSV export

## Phase 9 deliverable

The **Stakeholder Validation Notes** — captures, per Phase 8 opportunity, the stakeholder roster consulted and answers to the playbook's seven validation questions. Validation is anchored to opportunities (no orphan validations) so every recommendation has clear lineage. Available as:
- Workspace: `/engagements/<id>/validation`
- Printable notes: `/engagements/<id>/validation/notes`
- CSV export: `/engagements/<id>/validation/notes.csv`

### Stakeholder format

One stakeholder per line, pipe-separated: `Name | Role | YYYY-MM-DD | Status | notes`. Recognized **roles** (case-insensitive, label-or-code accepted): IT leadership, Cybersecurity team, Finance, Procurement, Business unit owner, System administrator, Power user, Compliance / legal. Recognized **statuses**: Consulted, Agreed, Pushback, Blocked. Unrecognized values are kept as free text in `role_label` / `status_label` (with `role_code` / `status_code` blank). Dates are normalized through `_coerce_date` so `5/10/2026` → `2026-05-10`.

### The seven validation questions

1. Who uses this tool?
2. What business process depends on it?
3. What would break if it was removed?
4. Is there a better enterprise tool already available?
5. Is the tool required by contract, compliance, or customer need?
6. Is the cost justified by the value?
7. Can the function be absorbed by another product?

### Overall validation status

`not_started` (no information captured), `pending` (in progress), `validated` (consensus reached, ready for recommendation), `blocked` (stakeholder objection or external dependency holding it up).

### Form behaviour

One form per opportunity, single Save button. Submitting empty everything (no stakeholders, no answers, status `not_started`, no notes) clears the entry from `validation.validations`. The workspace sorts opportunities so blocked / pending appear first and validated appears last — pushes attention to what needs work.

### Routes

- GET `/engagements/<id>/validation` — workspace
- POST `/engagements/<id>/validation/<opp_id>` — save validation for one opportunity
- POST `/engagements/<id>/validation/finalize` — finalize / reopen (advances `status` to `recommendations`, pre-marks Phase 10 `in_progress`)
- GET `/engagements/<id>/validation/notes` — printable HTML
- GET `/engagements/<id>/validation/notes.csv` — CSV export

## Phase 10 deliverable

The **Software Rationalization Recommendation Report** — synthesizes Phases 5, 7, 8, and 9 into structured per-finding recommendations leadership can act on. Available as:
- Workspace: `/engagements/<id>/recommendations`
- Printable report: `/engagements/<id>/recommendations/report` (grouped by category)
- CSV export: `/engagements/<id>/recommendations/report.csv`

### Auto-seeding from Phase 8

One recommendation per Phase 8 opportunity, idempotent via `seed_key=phase8:<opp_id>`. Auto-fill logic:
- **Finding** ← opportunity title
- **Category** ← `DISPOSITION_TO_CATEGORY` mapping (retire→retirement, replace/consolidate→consolidation, renegotiate→renewal_negotiation, reduce_licenses→license_reduction, other→further_analysis)
- **Business impact** ← Phase 9 `business_process` answer + `what_breaks` answer; falls back to product `primary_use_case` if no validation
- **Technical-debt impact** ← distinct Phase 7 flag labels across affected products
- **Security impact** ← Phase 7 `weak_security` flag (if any) + `data_sensitivity` levels listed
- **Cost impact** ← formatted from opportunity totals (recurring · first-year · transition)
- **Recommended action** ← templated by disposition + Phase 9 `notes` if present
- **Notes** ← combined Phase 8 + Phase 9 freeform notes
- **Status** ← `accepted` if Phase 8 opportunity is `approved`, else `draft`

Manual fields stay blank at seed time and are filled in by the consultant: `level_of_effort`, `risk_level`, `timeline`, `decision_owner`. The user can override any auto-filled field.

### 11 fields from the playbook

The recommendation card captures all 11 fields the playbook calls for: finding, products involved, business impact, tech-debt impact, security impact, cost impact, recommended action, level of effort, risk level, proposed timeline, decision owner.

### 8 categories

`immediate_savings`, `renewal_negotiation`, `license_reduction`, `consolidation`, `retirement`, `security_risk_reduction`, `governance_improvement`, `further_analysis`. Workspace and report group recommendations by category in this order. The printable report includes a category-definitions reference at the bottom.

### Status quick-actions

`draft` (default for seeded), `accepted` (signed off), `deferred` (parked). Status drives sort order within each category — accepted first, then draft, then deferred.

### Routes

- GET `/engagements/<id>/recommendations` — workspace
- POST `/engagements/<id>/recommendations/seed` — auto-seed from Phase 8 opportunities (idempotent)
- POST `/engagements/<id>/recommendations/new` — add a custom recommendation
- POST `/engagements/<id>/recommendations/<rec_id>/edit` — full update
- POST `/engagements/<id>/recommendations/<rec_id>/status` — quick accept / draft / defer
- POST `/engagements/<id>/recommendations/<rec_id>/delete` — delete one
- POST `/engagements/<id>/recommendations/finalize` — finalize / reopen (advances `status` to `exec_summary`, pre-marks Phase 11 `in_progress`)
- GET `/engagements/<id>/recommendations/report` — printable HTML
- GET `/engagements/<id>/recommendations/report.csv` — CSV export

## Phase 11 deliverable

The **Executive Briefing** is the final deliverable — a single-page summary leadership reads top-down. Available as:
- Workspace: `/engagements/<id>/exec-summary`
- Printable briefing: `/engagements/<id>/exec-summary/briefing`

### Auto-computed metrics (the seven leadership questions)

`_compute_exec_metrics(eng)` produces every metric on the briefing without any user input:

1. **Products reviewed** ← `len(inventory.products)`
2. **Total annual software spend** ← sum of `total_annual_cost` across inventory
3. **Products in overlap** ← Phase 5 cluster sums (`products_in_overlap` + `overlap_categories`)
4. **Products with unused licenses** ← Phase 7 `unused`-flagged count, plus a secondary "under-utilized" count for products where active < 70% of purchased that weren't already flagged
5. **Technical debt identified** ← Phase 7 summary (products flagged, severity breakdown, annual cost in flagged products)
6. **Estimated cost savings** ← Phase 8 summary, both non-rejected and approved-only
7. **Decisions needed** ← Phase 10 recommendations with status `draft` or `deferred`

### Editable narrative fields

Five fields the consultant fills in to frame the story:
- **headline** — TL;DR shown in a highlighted callout above everything else on the printable briefing
- **key_finding** — strategic pattern that connects multiple findings
- **top_recommendation** — single highest-impact action
- **leadership_ask** — 1–3 specific decisions needed at the briefing
- **next_steps** — proposed timeline / first actions

### Prioritized action plan

`_build_action_plan(eng)` returns accepted Phase 10 recommendations sorted by:
1. **Risk level** (high first — risk reduction is urgent)
2. **Cost magnitude** (high first — pulls dollar values from `cost_impact` text via regex)
3. **Level of effort** (low first — favor quick wins)

Each item shows finding, category, risk pill, products, timeline, decision owner, cost impact.

### Final deliverables manifest

`_deliverables_manifest(eng)` builds 10 entries (Phases 1–10) with title, URL, and a `ready` boolean derived from each phase's data:
- **Phase 1** Software Review Scope Statement (`scope.finalized`)
- **Phase 2** Customer Data Request Checklist (`data_request.finalized`)
- **Phase 3** Master Software Inventory XLSX (`inventory.products` non-empty)
- **Phase 4** Cleaned & Categorized Inventory (`normalize.finalized`)
- **Phase 5** Product Overlap Analysis (`overlap.finalized`)
- **Phase 6** AI Assisted Comparison Findings (`ai_review.findings` non-empty)
- **Phase 7** Technical Debt Findings Register (`tech_debt.flags` non-empty)
- **Phase 8** Cost Savings Estimate (`savings.opportunities` non-empty)
- **Phase 9** Stakeholder Validation Notes (`validation.validations` non-empty)
- **Phase 10** Recommendation Report (`recommendations.recs` non-empty)

The briefing itself is the eleventh deliverable, rendered inline as the executive summary document.

### Routes

- GET `/engagements/<id>/exec-summary` — workspace (auto-init on first visit, read-only metrics + editable narrative form + action plan preview + deliverables manifest)
- POST `/engagements/<id>/exec-summary` — save narrative (5 fields)
- POST `/engagements/<id>/exec-summary/finalize` — finalize / reopen. **This is the last phase**: finalize sets engagement `status` to `complete` (no next-phase pre-mark).
- GET `/engagements/<id>/exec-summary/briefing` — printable HTML briefing

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
| `/engagements/<id>/overlap` | GET / POST | Phase 5 — overlap workspace + save category dispositions |
| `/engagements/<id>/overlap/finalize` | POST | Phase 5 — finalize / reopen |
| `/engagements/<id>/overlap/analysis` | GET | Phase 5 deliverable (printable HTML) |
| `/engagements/<id>/overlap/analysis.csv` | GET | Phase 5 deliverable (CSV) |
| `/engagements/<id>/ai-review` | GET | Phase 6 — AI review page (auto-runs if stale) |
| `/engagements/<id>/ai-review/run` | POST | Phase 6 — force re-run in background |
| `/engagements/<id>/ai-review/finalize` | POST | Phase 6 — finalize / reopen |
| `/engagements/<id>/tech-debt` | GET | Phase 7 — debt workspace (`?flag=&severity=&only_with_debt=`) |
| `/engagements/<id>/tech-debt/<pid>` | POST | Phase 7 — save flags / severity / notes per product |
| `/engagements/<id>/tech-debt/finalize` | POST | Phase 7 — finalize / reopen |
| `/engagements/<id>/tech-debt/register` | GET | Phase 7 — printable findings register |
| `/engagements/<id>/tech-debt/register.csv` | GET | Phase 7 — CSV export |
| `/engagements/<id>/savings` | GET | Phase 8 — savings workspace |
| `/engagements/<id>/savings/seed` | POST | Phase 8 — auto-seed from Phase 5 + 7 |
| `/engagements/<id>/savings/new` | POST | Phase 8 — add a custom opportunity |
| `/engagements/<id>/savings/<oid>/edit` | POST | Phase 8 — update opportunity fields |
| `/engagements/<id>/savings/<oid>/status` | POST | Phase 8 — quick approve / reject / reset |
| `/engagements/<id>/savings/<oid>/delete` | POST | Phase 8 — delete opportunity |
| `/engagements/<id>/savings/finalize` | POST | Phase 8 — finalize / reopen |
| `/engagements/<id>/savings/estimate` | GET | Phase 8 — printable estimate |
| `/engagements/<id>/savings/estimate.csv` | GET | Phase 8 — CSV export |
| `/engagements/<id>/validation` | GET | Phase 9 — validation workspace |
| `/engagements/<id>/validation/<oid>` | POST | Phase 9 — save validation for one opportunity |
| `/engagements/<id>/validation/finalize` | POST | Phase 9 — finalize / reopen |
| `/engagements/<id>/validation/notes` | GET | Phase 9 — printable validation notes |
| `/engagements/<id>/validation/notes.csv` | GET | Phase 9 — CSV export |
| `/engagements/<id>/recommendations` | GET | Phase 10 — recommendations workspace |
| `/engagements/<id>/recommendations/seed` | POST | Phase 10 — auto-seed from Phase 8 opportunities |
| `/engagements/<id>/recommendations/new` | POST | Phase 10 — add a custom recommendation |
| `/engagements/<id>/recommendations/<rid>/edit` | POST | Phase 10 — update all fields |
| `/engagements/<id>/recommendations/<rid>/status` | POST | Phase 10 — quick accept / draft / defer |
| `/engagements/<id>/recommendations/<rid>/delete` | POST | Phase 10 — delete one |
| `/engagements/<id>/recommendations/finalize` | POST | Phase 10 — finalize / reopen |
| `/engagements/<id>/recommendations/report` | GET | Phase 10 — printable report (grouped by category) |
| `/engagements/<id>/recommendations/report.csv` | GET | Phase 10 — CSV export |
| `/engagements/<id>/exec-summary` | GET / POST | Phase 11 — workspace (GET renders, POST saves narrative) |
| `/engagements/<id>/exec-summary/finalize` | POST | Phase 11 — finalize / reopen (engagement → `complete`) |
| `/engagements/<id>/exec-summary/briefing` | GET | Phase 11 — printable Executive Briefing (final deliverable) |

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
- **Phase 6 anonymization is whitelist-based, not blacklist-based** — only explicitly safe fields are sent. Adding a new product field defaults to *not* sent; the developer has to consciously add it to `AI_SAFE_FIELDS` if it's appropriate. Less risk of accidental leakage when fields evolve.
- **Phase 6 vendor / product names ARE sent** — they're public-knowledge identifiers (Slack is Slack everywhere), and stripping them would render the AI useless. The customer-private signal is in *who owns what at the customer*, not *what software exists in the world*. We protect the former, not the latter.
- **Phase 6 anonymization map never persists** — `deanon_map` is built fresh each run from inventory order, used in-memory to substitute the AI response, then discarded. Persisting it alongside the data would defeat the purpose.
- **Phase 6 cache invalidation by inventory SHA-256** — cheaper than re-running the AI on every page load, and automatically picks up any change the user makes (add product, edit field, normalize). User can also force a re-run via the manual button.

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
- ~~Phase 5 (Identify Overlap) — per-category comparison?~~ **Resolved: yes. Categories with 2+ products surface as overlap candidates; per-product disposition selector + risk + notes; potential savings computed from Retire/Replace/Consolidate dispositions; printable analysis + CSV export.**
- ~~Phase 6 (AI Assisted Comparison) — auto-run + privacy?~~ **Resolved: auto-run on first visit when stale (background thread), manual re-run button always available; whitelist anonymization with PROD_NNN tokens; vendor / product names retained because they're public; owners / notes / internal systems / engagement metadata stripped; de-anon map ephemeral (never persisted).**
- ~~Phase 7 (Identify Technical Debt) — per-product flag-checker?~~ **Resolved: yes. 14 debt flags from the playbook, severity selector, free-text notes; auto-suggested flags derived from inventory data (no_owner, unclear_mission, duplicative, unused, poor_adoption, outside_governance, high_cost_low_value, renewal_no_justification); clickable suggestion chips tick the corresponding checkbox; printable register + CSV export.**
- ~~Phase 8 (Estimate Cost Savings) — separate worksheet or implicit in Phases 5/7?~~ **Resolved: separate worksheet that auto-seeds from Phase 5 dispositions + Phase 7 unused flags. Per-opportunity card with current cost / recurring savings / one-time / migration / training, status (proposed/approved/rejected), and a portfolio rollup that splits "non-rejected" from "approved-only" — the conservative number leadership uses.**
- ~~Phase 9 (Validate with Stakeholders) — anchor to what?~~ **Resolved: anchor to Phase 8 opportunities. Stakeholder roster (8 role types) parsed from a pipe-separated text block, structured answers to the 7 validation questions, overall status (not_started / pending / validated / blocked), free notes. No orphan validations — every validation lineages back to a savings opportunity.**
- ~~Phase 10 (Recommendations) — synthesize from prior phases?~~ **Resolved: yes. One auto-seeded recommendation per Phase 8 opportunity. Auto-fill pulls finding/products/cost from Phase 8, business impact from Phase 9 validation answers (with primary_use_case fallback), tech-debt impact from Phase 7 flag labels, security impact from `weak_security` flag + `data_sensitivity` levels, recommended action from disposition mapping. Manual fields (LoE, risk, timeline, decision owner) stay blank at seed time. 8 categories from the playbook drive grouping in workspace and printable report.**
- ~~Phase 11 (Executive Summary) — auto-compute or manual?~~ **Resolved: hybrid. The 7 leadership questions are computed entirely from prior-phase data (no manual entry — single source of truth). 5 narrative fields are editable to frame the story. Action plan is auto-built from accepted Phase 10 recommendations sorted by risk → cost → effort. Deliverables manifest auto-renders ready/not-ready state for all 10 prior outputs plus the briefing itself. Finalizing flips engagement status to `complete`.**
- ~~**`ANTHROPIC_API_KEY` setup**~~ **Resolved** — set up in `software_rationalization/.env` (gitignored). Loaded via `python-dotenv` at the top of `ai_service.py` with `override=True` to win against any empty/stale OS env var. Live Phase 6 run verified end-to-end on a populated demo engagement: 5 findings returned from Claude in 26 s, zero sensitive strings leaked into the AI payload (14 deliberately-seeded sensitive strings all absent), de-anonymization correctly re-hydrated real product names in the user-facing view.
- Customer-facing self-upload portal — currently the consultant uploads on the customer's behalf. A token-protected upload link the customer can use directly is a future enhancement (would need expiring tokens, throttling, anti-virus scan).
- Phase 6 token budget — currently sending the entire sanitized inventory in one prompt with `MAX_PRODUCTS_PER_RUN = 200`. For larger customer estates we'd need to chunk the inventory by category and merge findings, or summarize first. Not urgent for v1.
- Phase 6 attaching customer-supplied documents (Phase 2 uploads) into the AI context — explicitly NOT in v1. Documents may contain unredacted customer data; we'd need a separate redaction pass before they can be attached. Worth thinking about for v2.
- All 11 phases of the playbook are now live. Future enhancements would focus on quality-of-life polish: customer-facing self-upload portal for Phase 2, AI re-runs over uploaded documents for Phase 6 (currently inventory-only), multi-user auth for shared deployments, automated backup of `data/`. None of those block running real engagements end-to-end.
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

### 2026-04-28 — Phase 5 build (Identify Product Overlap)

- Added Phase 5 constants to `app.py`: `DISPOSITIONS` (6 options matching the playbook), `REMOVAL_RISKS` (4 levels), `SAVINGS_DISPOSITIONS` (the three that imply cost reduction).
- Helpers: `_ensure_overlap`, `_safe_float` / `_safe_int` (defensive numeric coercion for inventory fields that may be strings), `_overlap_clusters` (groups by category, only returns clusters of 2+ with annual/users/licenses rollups), `_overlap_summary` (engagement-wide rollup including potential savings + decisions made / undecided).
- Routes: `engagement_overlap` (GET + POST that takes a multi-row category form via `getlist("product_id")` + per-product `disposition_<id>` / `risk_<id>` / `notes_<id>` fields; clears entry if all three are blank), `engagement_overlap_finalize`, `engagement_overlap_analysis` (printable HTML), `engagement_overlap_analysis_csv`.
- New templates: `overlap.html` (5 summary tiles, per-category form panel with side-by-side comparison table, row-shading for keep/savings rows, finalize panel) and `overlap_analysis.html` (printable: summary table + per-category details + disposition definitions reference).
- Updated `_sidebar.html` (Phase 5 link), `engagement_view.html` (Phase 5 panel with workspace + analysis links), `home.html` (Phase 5 marked Live).
- New CSS: `.overlap-cluster-header`, `.overlap-form` / `.overlap-scroll`, `.overlap-table` with `.row-keep` (green tint) and `.row-savings` (yellow tint) row shading, condensed select/input styling inside the table.
- Smoke test (Flask test client, file-based): seeded 6 products with 2 overlap categories (3 PM tools + 2 collab tools) and 1 solo product. Verified `_overlap_summary` initial counts ($9,150 annual in overlap across 5 products in 2 categories). Saved PM dispositions (Keep/Retire/Consolidate) → potential savings = $1,300 (Asana $1k + Trello $300). Saved collab dispositions → decided_count = 5/5. Cleared Trello (blank submission) → entry removed from `dispositions`, savings drop to $1,000. Printable analysis renders with all expected strings. CSV export has 6 rows (header + 5 overlap products). Finalize advances engagement to Phase 6 (`ai_review` pre-marked `in_progress`); reopen reverses. Caught and fixed: Werkzeug test client wants dict-with-list-values for repeated form fields, not list-of-tuples.

### 2026-04-28 — Phase 6 build (AI Assisted Comparison)

- Added `anthropic` to `requirements.txt`.
- New module `ai_service.py` with privacy-first design: `AI_SAFE_FIELDS` whitelist + `AI_REDACTED_FIELDS` for UI transparency, `anonymize_inventory()` returning `(sanitized_products, deanon_map)` with `PROD_NNN` IDs, `inventory_hash()` for cache invalidation (SHA-256 over the sanitized payload), `call_claude()` with system + user messages and JSON output schema, `_parse_findings_json()` (tolerant of direct JSON / fenced / prose-with-fence), `deanonymize_findings()` to map PROD_NNN back to real product details, `kick_off_review()` background thread launcher with a per-engagement run lock, `is_stale()` / `has_api_key()` helpers.
- Anonymization invariants verified by smoke test: zero sensitive strings (employee names, internal system names, free-text notes containing personnel info, client name "Acme Corp", purchase source "Acme Corporate AmEx") leak into the JSON sent to Claude. Vendor + product names ARE retained — verified Slack / Microsoft / Atlassian / Asana Inc all present in sanitized payload because the AI needs them to compare overlap meaningfully.
- New routes in `app.py`: `engagement_ai_review` (GET, auto-runs in background thread when stale + api key + has inventory + not already running), `engagement_ai_review_run` (POST forces re-run), `engagement_ai_review_finalize` (POST). Route logic graceful in absence of API key, in absence of inventory, while a run is in flight, after a failed run.
- New template `ai_review.html` handling all five states: no-key (setup instructions, no Run button), no-inventory (link to Phase 3), running (spinner + 3s meta-refresh), error (alert + Retry button), findings (grouped by category, each finding showing summary / linked product tags / concern / risk / cost impact / next step). Always-visible privacy banner shows the field whitelist + redacted list at the top.
- Updated `_sidebar.html` to enable Phase 6 link, `engagement_view.html` to surface a Phase 6 panel showing finding count or run status, `home.html` to mark Phase 6 as Live.
- New CSS: `.privacy-card` (green banner), `.spinner` + `@keyframes spin` for the running state, `.ai-finding` with accent left-border, `.ai-finding-row` two-column label/value layout, `.ai-finding-products` for clickable product tags.
- Smoke test exercised: anonymization (zero sensitive strings in payload, vendor/product names retained, anonymized PROD_NNN ID assignment, all 4 redacted fields confirmed absent), hash determinism, `_parse_findings_json` over three input forms (direct, fenced, prose-with-fence), de-anonymization (real product names + IDs come back through the map), page renders 200 in no-key state and in with-findings state, finalize/reopen transitions advance engagement to `tech_debt`. The actual Claude API call is verified by hand once `ANTHROPIC_API_KEY` is exported — the test fixture seeds the engagement with completed findings to exercise the rendering path without making a real network call.

### 2026-04-28 — Phase 7 build (Identify Technical Debt)

- Added Phase 7 constants to `app.py`: `TECH_DEBT_FLAGS` (14 flags from the playbook, each with a key + label + helper-text shown in tooltip / register definitions section) and `DEBT_SEVERITIES` (low/medium/high).
- Helpers: `_ensure_tech_debt`, `_suggest_debt_flags` (8 inventory-derived auto-suggestions: missing-owner, unclear mission, duplicative-by-category, unused, poor-adoption, outside-governance via `purchase_source` heuristic, top-quartile-cost-low-utilization, near-renewal-no-justification within 90 days), `_tech_debt_summary` (rollup including per-flag counts, severity breakdown, and total annual cost in flagged products).
- Routes: `engagement_tech_debt` (GET with `?flag=&severity=&only_with_debt=` filters), `engagement_tech_debt_save` (POST per product — clears the entry if all of flags/severity/notes are blank), `engagement_tech_debt_finalize`, `engagement_tech_debt_register` (printable HTML), `engagement_tech_debt_register_csv`.
- New templates: `tech_debt.html` (5 summary tiles, filter row, per-product card with the product header line + suggestion chips + 14-flag checkbox grid + severity dropdown + notes input + Save button per row, vanilla JS to make suggestion chips tick the matching checkbox in their row), `tech_debt_register.html` (printable: summary table + flagged-products list sorted by severity then name + reference table of all 14 debt categories with definitions).
- Updated `_sidebar.html` (Phase 7 link), `engagement_view.html` (Phase 7 panel), `home.html` (Phase 7 marked Live).
- New CSS: `.debt-row` with red left-border when flagged, `.debt-suggestions` + `.debt-sugg-chip` (yellow dashed-border chips), `.debt-flag-grid` (responsive 220px columns), `.debt-register-item` for the printable view.
- Smoke test (Flask test client, file-based): seeded 6 products covering each detector path. Verified suggestions: ShadowApp gets `no_owner` + `unclear_mission` + `duplicative` + `outside_governance`; GhostTool (100 assigned, 0 active) gets `unused`; DustyTool (5/100 active) gets `poor_adoption`; FancySaaS (top-quartile cost, 200/1000 users) gets `high_cost_low_value`; Okta gets nothing (healthy). Saved high-severity flags on ShadowApp + medium on GhostTool + low on DustyTool. Empty submission for Okta correctly omits it from the flags map. Filter-by-severity, filter-by-flag, only-with-debt all return correct subsets. Register HTML and CSV both render with 3 flagged products. Finalize advances engagement to Phase 8 (`savings` pre-marked `in_progress`); reopen reverses.

- Spawned a follow-up task chip: "Set up ANTHROPIC_API_KEY for Phase 6" — covers exporting the key, restarting the server, verifying a real Phase 6 run, and confirming the privacy claims (no sensitive strings in `ai_review.raw_response`).

### 2026-04-28 — Phase 8 build (Estimate Cost Savings)

- Added Phase 8 constants to `app.py`: `SAVINGS_DISPOSITION_CHOICES` (6 — retire/replace/consolidate/renegotiate/reduce_licenses/other) and `SAVINGS_STATUSES` (proposed/approved/rejected).
- Helpers: `_ensure_savings`, `_new_opportunity` factory, `_opportunity_totals` (computes recurring / first-year / transition_total), `_seed_savings_opportunities` (idempotent — uses stable `seed_key` like `phase5:<pid>` or `phase7-unused:<pid>`), `_savings_summary` (split rollup: non-rejected vs approved-only).
- Routes: `engagement_savings` (GET, sorts opps by status then descending recurring), `engagement_savings_seed` (POST, creates seeded opps from Phase 5 dispositions + Phase 7 `unused` flags), `engagement_savings_new` (POST, manual opp), `engagement_savings_edit` (POST, full update), `engagement_savings_status` (POST, quick approve/reject/reset), `engagement_savings_delete` (POST), `engagement_savings_finalize`, `engagement_savings_estimate` (printable HTML), `engagement_savings_estimate_csv`.
- Seed semantics: Phase 5 `retire` / `replace` / `consolidate` → recurring = full annual cost; `renegotiate` → recurring = 20% of annual cost (representing a discount, not full retirement). Phase 7 `unused` → recurring = `cost_per_license × (purchased − active_users)` when per-license cost is known, else proportional split of annual cost. Re-seeding skips opportunities already present (matching by `seed_key`).
- New templates: `savings.html` (6 summary tiles, seed/add buttons, per-opportunity card with editable title input, disposition + status selectors, 5 numeric inputs in a responsive grid, live computed totals panel showing recurring / net first-year / transition cost, quick-action footer for approve/reject/reset/delete; "Add custom opportunity" form with multi-select product picker; finalize panel) and `savings_estimate.html` (printable: portfolio summary table + opportunities table sorted by status then savings + method + status legend).
- Updated `_sidebar.html`, `engagement_view.html`, `home.html` to surface Phase 8 as Live.
- New CSS: `.opp-card` with status-colored left-border (green=approved, blue=proposed, red+dimmed=rejected), `.opp-title-input` (in-place editable title), `.opp-numbers` responsive grid, `.opp-totals` panel with `.opp-total-value` typography, `.opp-quick-actions` footer.
- Smoke test (Flask test client, file-based): seeded inventory with 3 PM tools + 1 unused product + 1 large CRM. Set Phase 5 dispositions (Asana retire, Trello consolidate, FancySaaS renegotiate) and Phase 7 `unused` on GhostTool. Seed call created exactly 4 opportunities with correct recurring values: Asana $1k (full retire), Trello $300 (consolidate), FancySaaS $4k (20% of $20k renegotiate), GhostTool $5k (cost_per_license × unused count). Re-seed was idempotent (still 4). Edited Asana with $200 migration + $150 training and approved status → totals computed correctly: recurring $1k, first-year $650, transition $350. Status shortcuts moved Trello → approved, FancySaaS → rejected. Summary verified: count=4, approved=2, proposed=1, rejected=1; non-rejected recurring = $6,300; non-rejected first-year = $5,950 (= 6300 − 350 transition); approved-only recurring = $1,300. Custom multi-product opportunity (Jira + Trello bundle) auto-summed to $1,900. Delete worked. Estimate HTML and CSV both render correctly. Finalize advanced engagement to Phase 9 (`validation` pre-marked `in_progress`); reopen reverses. (Caught one test typo — case mismatch in product-name search.)

### 2026-04-28 — Phase 9 build (Validate with Stakeholders)

- Added Phase 9 constants to `app.py`: `STAKEHOLDER_ROLES` (8 — IT leadership, Cybersecurity team, Finance, Procurement, Business unit owner, System administrator, Power user, Compliance / legal), `STAKEHOLDER_STATUSES` (4 — Consulted, Agreed, Pushback, Blocked), `VALIDATION_QUESTIONS` (7, exact text from the playbook with stable keys), `VALIDATION_OVERALL_STATUSES` (4).
- Helpers: `_ensure_validation`, `_new_validation_record`, `_parse_stakeholders` (parses pipe-separated lines tolerantly — recognizes role labels OR codes case-insensitively, normalizes dates through `_coerce_date`, falls back to free-text labels for unrecognized roles/statuses), `_stakeholders_to_text` (round-trip back to text), `_validation_summary` (counts by overall_status and totals stakeholders recorded).
- Routes: `engagement_validation` (GET, sorts opps so blocked/pending appear first), `engagement_validation_save` (POST per opp — empty submission removes the record), `engagement_validation_finalize`, `engagement_validation_notes` (printable HTML), `engagement_validation_notes_csv`.
- New templates: `validation.html` (6 summary tiles, format hint with role/status chip references, per-opp card with stakeholder textarea + 7-question grid + overall-status dropdown + notes input + Save button; status-colored left-border on the card; finalize panel with warning if any opps still in `not_started`) and `validation_notes.html` (printable: summary table + per-opp section showing stakeholder table only when present + question answers grouped via dl, only renders questions that have answers + reference list of all 7 questions).
- Updated `_sidebar.html`, `engagement_view.html`, `home.html` to surface Phase 9 as Live.
- New CSS: `.val-card` with status-tinted left-border (good/danger/accent), `.val-questions` two-column grid that collapses to single on narrow screens, `.val-question` typography.
- Smoke test (file-based): exercised `_parse_stakeholders` over three input shapes (mapped role + agreed status + ISO date; mapped role + lowercase status; unrecognized role + unrecognized status + non-ISO date). All assertions passed: role/status codes map correctly, unrecognized values land in label fields with blank codes, dates normalize through `_coerce_date`. Saved a full validation with 7 answers + 3 stakeholders + validated status — record persisted correctly. Empty submission removed the record from `validation.validations`. Re-saving with content re-created it. `_validation_summary` returns expected counts. Notes HTML and CSV render with the saved data. Finalize advanced engagement to Phase 10 (`recommendations` pre-marked `in_progress`); reopen reverses.

### 2026-04-28 — Phase 10 build (Recommendations)

- Added Phase 10 constants to `app.py`: `RECOMMENDATION_CATEGORIES` (8 from the playbook), `DISPOSITION_TO_CATEGORY` map (Phase 8 → Phase 10), `LOE_LEVELS`, `RISK_LEVELS`, `RECOMMENDATION_STATUSES` (draft / accepted / deferred).
- Helpers: `_ensure_recommendations`, `_new_recommendation` factory (all 11 playbook fields plus metadata), `_format_money_str` (small money formatter), `_seed_recommendations` (rich auto-fill from Phases 7/8/9 — see below), `_recommendations_summary` (rollup by status/category/risk/LoE).
- Auto-fill at seed time (per Phase 8 opportunity, idempotent via `seed_key=phase8:<opp_id>`):
  - `finding` ← opportunity title
  - `category` ← `DISPOSITION_TO_CATEGORY` map (retire→retirement, replace/consolidate→consolidation, renegotiate→renewal_negotiation, reduce_licenses→license_reduction, other→further_analysis)
  - `business_impact` ← Phase 9 `business_process` + `what_breaks` validation answers; falls back to product `primary_use_case` when no validation
  - `tech_debt_impact` ← distinct Phase 7 flag labels across affected products (or "None recorded in Phase 7")
  - `security_impact` ← Phase 7 `weak_security` flag presence + product `data_sensitivity` levels listed
  - `cost_impact` ← formatted from `_opportunity_totals` (recurring · first-year · transition)
  - `recommended_action` ← templated by disposition + Phase 9 free notes if present
  - `notes` ← combined Phase 8 + Phase 9 freeform notes
  - `status` ← `accepted` if Phase 8 opp is `approved`, else `draft`
  - manual fields (LoE, risk, timeline, decision_owner) stay blank
- Routes: `engagement_recommendations` (GET, sorts by category order then status then finding), `engagement_recommendations_seed`, `engagement_recommendations_new` (custom), `engagement_recommendations_edit`, `engagement_recommendations_status` (quick action), `engagement_recommendations_delete`, `engagement_recommendations_finalize`, `engagement_recommendations_report` (printable, grouped by category), `engagement_recommendations_report_csv`.
- New templates: `recommendations.html` (6 summary tiles, by-category chip rollup, seed/add/report/csv buttons, per-rec card with editable finding + 4 dropdown selectors in a row + 4 impact textareas in a 2-col responsive grid + recommended action full-width + timeline/decision-owner row + notes + per-rec quick-action footer; "Add custom recommendation" form with multi-product picker; finalize panel) and `recommendations_report.html` (printable: summary table + per-category sections with each rec's full 11-field detail in a definition list + category-definitions reference at bottom).
- Updated `_sidebar.html`, `engagement_view.html`, `home.html` for Phase 10 Live state.
- New CSS: `.rec-category-header` (uppercase divider), `.rec-card` with status-tinted left-border (good for accepted, default border for deferred, accent for draft), `.rec-grid` responsive 2-col layout, `.rec-report-item` for the printable view.
- Smoke test (file-based): seeded inventory + Phase 5 retire disposition + Phase 7 (`weak_security` + `duplicative` flags) + Phase 8 opportunity + Phase 9 validation answers. Phase 10 seed created exactly 1 recommendation with all auto-fill working: category=retirement (from disposition=retire); business_impact contained Phase 9's "Marketing campaign planning" answer plus the "If removed: …" suffix from `what_breaks`; tech_debt_impact listed both Phase 7 flag labels; security_impact mentioned "Weak security controls flagged" + "Data sensitivity: Internal"; cost_impact formatted "$1,000/yr recurring savings"; status=draft (Phase 8 opp was proposed not approved). Re-seed was idempotent. Edited rec with all manual fields (LoE/risk/timeline/decision_owner) and accepted it. Custom recommendation (governance_improvement) added. Quick-action defer worked. Summary returned correct rollups. Report HTML grouped by category and rendered all expected strings; report CSV had header + 2 rec rows. Delete worked. Finalize advanced engagement to Phase 11 (`exec_summary` pre-marked `in_progress`); reopen reverses. Caught and fixed one Jinja gotcha: a context dict key named `items` collided with `dict.items()` method; renamed to `recs`.

### 2026-04-28 — Phase 11 build (Executive Summary) — engagement complete

- Added Phase 11 helpers to `app.py`: `_ensure_exec_summary`, `_compute_exec_metrics` (auto-answers all 7 leadership questions from prior-phase data — no manual entry), `_build_action_plan` (sorts accepted Phase 10 recommendations by risk → cost → LoE; cost magnitude extracted from `cost_impact` text via regex), `_deliverables_manifest` (10 entries Phase 1–10 with title/URL/ready boolean derived from each phase's data — uses Flask `url_for` so links survive route renames).
- Routes: `engagement_exec_summary` (GET workspace, POST saves narrative — 5 fields), `engagement_exec_summary_finalize` (last-phase finalize flips engagement `status` to `complete` — no next-phase pre-mark since this is the end), `engagement_exec_summary_briefing` (printable HTML).
- New templates: `exec_summary.html` (workspace with the 7 questions answered automatically as a numbered list with answer values pulled live, narrative form, action-plan preview with auto-numbered list, deliverables manifest table, finalize panel) and `exec_briefing.html` (printable: cover with eyebrow + title + meta, optional headline callout, 7-question table, narrative sections, action plan with full detail per item, pending decisions list, next steps, deliverables manifest with links).
- Updated `_sidebar.html` to enable the Phase 11 link and updated the helper text to "All 11 playbook phases are live." Updated `engagement_view.html` to surface a Phase 11 panel with completion notice. Updated `home.html` to mark every phase Live.
- New CSS: `.exec-questions` (numbered list with circular accent badges), `.exec-q` / `.exec-a` two-column row layout, `.action-plan` (numbered list with circular badges), `.briefing-cover` (centered cover block with double bottom border), `.briefing-eyebrow` (uppercase label), `.briefing-headline` (left-bordered callout in accent blue), `.briefing-q-table` (zebra-free q&a table), `.briefing-plan`.
- Smoke test (file-based): seeded full pipeline — 3 products, Phase 5 dispositions, Phase 7 unused flag, Phase 8 seeded opportunities, Phase 10 seeded recommendations with one accepted (Asana retire). Verified `_compute_exec_metrics`: products_reviewed=3, total_annual_spend=$7,600 (10×100 + 8×200 + 50×100), products_in_overlap=2, overlap_categories=1, unused_count_flagged=1, tech_debt.products_with_debt=1, savings.total_recurring=$6,000 ($1k Asana + $5k GhostTool), decisions_needed_count=1. Action plan returned the 1 accepted rec with correct sort + product names. Manifest returned 10 items with 4 in `ready=true` state (3, 7, 8, 10). Saved narrative with all 5 fields. Briefing HTML rendered: client name, headline callout, 7-question table, action plan, pending decisions, deliverables list — all present. Finalize set engagement.status to "complete"; reopen reverses.

**The dashboard now implements the entire playbook end-to-end.**

### 2026-04-28 — ANTHROPIC_API_KEY setup + live Phase 6 verification

- Added `python-dotenv` to `requirements.txt` and to `ai_service.py` (top-of-module, wrapped in `try/except ImportError` for graceful fallback). Used `load_dotenv(override=True)` after discovering an empty `ANTHROPIC_API_KEY` was already present in the OS environment — without `override=True`, that empty value silently shadowed the value in `.env`. The fix is documented in a code comment.
- Added `.env` and `.env.local` to `.gitignore` before writing the file. Confirmed gitignored via `git check-ignore -v .env`.
- Wrote `software_rationalization/.env` with the user's `ANTHROPIC_API_KEY` value. **The key is never persisted in any tracked file, never echoed in chat output, never written to commits.**
- Restarted the Flask server. Verified `ai_service.has_api_key()` returns True after the override fix.
- Seeded a demo engagement (`15c7b526`, "Acme Corp Q2 2026 Software Review") with 8 products covering 4 deliberate overlap clusters (Slack/Teams collaboration, Jira/Asana PM, Dropbox/Box document management, GhostAnalytics zero-usage shelfware). The seed payload included intentionally sensitive fields — employee names ("Sarah Chen", "Bob Martinez"), internal systems ("Acme Internal CRM", "Acme Vault"), purchase source ("Acme Corporate AmEx"), free-text notes quoting personnel behaviour, internal project codenames — to verify the anonymization layer in production.
- Hit `/ai-review`, watched the auto-run kick off in a background thread. Polling showed `running=True` for the first 24 seconds, then `running=False` with 5 findings at 26 seconds. Total round-trip: ~26 s. Model: `claude-opus-4-7`.
- **Privacy verification (zero leaks):** scanned `ai_review.raw_response` for all 14 sensitive strings. All 14 absent. Claude's response references products only by `PROD_001`..`PROD_008` — even the public vendor and product names (Slack, Microsoft Teams, etc.) didn't appear in the raw response because Claude followed the system prompt strictly and used the anonymized IDs. The user-facing rendered findings, however, show the real product names because de-anonymization happens locally via the in-memory `deanon_map` after the API call returns.
- **Quality verification:** Claude correctly identified all 4 planted overlap clusters with sensible cost-impact estimates and recommended next steps. It also correctly flagged Okta (the IAM tool) as a coordination dependency rather than a savings target — exactly the kind of nuance that would have been lost to a less capable model.
- Committed the code changes (ai_service.py, requirements.txt, .gitignore) plus this note. Did NOT commit `.env` — it is gitignored. The key remains local-only on the user's workstation.
