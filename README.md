# Software Rationalization Workbench

Web-accessible dashboard that walks an engagement through the **Software Inventory, License Review, and Technical Debt Reduction Playbook**.

This is a standalone Flask app, separate from the TSMA assessment app in the parent directory.

## Status

| Phase | Description                       | Status   |
|-------|-----------------------------------|----------|
| 1     | Define the Scope                  | **Live** |
| 2     | Request Customer Data             | Planned  |
| 3     | Build the Software Inventory      | Planned  |
| 4     | Normalize the Data                | Planned  |
| 5     | Identify Product Overlap          | Planned  |
| 6     | AI Assisted Comparison            | Planned  |
| 7     | Identify Technical Debt           | Planned  |
| 8     | Estimate Cost Savings             | Planned  |
| 9     | Validate with Stakeholders        | Planned  |
| 10    | Create Recommendations            | Planned  |
| 11    | Create the Executive Summary      | Planned  |

## Run

```bash
cd software_rationalization
pip install -r requirements.txt
python app.py
```

The app listens on **http://localhost:5055**.

## Storage

Engagements are persisted as JSON files under `data/`. Delete the file to delete an engagement. The `data/` folder is gitignored.

## Data model

Each engagement file contains:

- `id`, `name`, `client`, `lead`, `created_at`, `updated_at`, `status`
- `phase_progress` — one of `not_started` / `in_progress` / `complete` for each of the 11 phases
- `scope` — Phase 1 fields (business units, tool categories, purchase sources, renewal window, contract/technical/business owners, objectives, constraints, finalize state)

Phases 2–11 will add their own top-level keys (e.g. `inventory`, `overlap`, `tech_debt`, `recommendations`) without changing existing fields.

## Phase 1 output

Once the scope is finalized, the **Software Review Scope Statement** is available at:

- HTML: `/engagements/<id>/scope/statement` (printable)
- Plain text download: `/engagements/<id>/scope/statement.txt`
