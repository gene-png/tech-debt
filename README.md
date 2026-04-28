# Software Rationalization Workbench

A consultant's workbench that walks a customer engagement end-to-end through the **Software Inventory, License Review, and Technical Debt Reduction Playbook** — from defining scope to delivering an executive briefing.

Standalone Flask app. JSON file storage. No build step. Single-user local workbench by default.

## Status

All 11 playbook phases are live:

| # | Phase | Deliverable |
|---|---|---|
| 1 | Define the Scope | Software Review Scope Statement |
| 2 | Request Customer Data | Customer Data Request Checklist |
| 3 | Build the Software Inventory | Master Software Inventory (XLSX/CSV) |
| 4 | Normalize the Data | Cleaned & categorized inventory |
| 5 | Identify Product Overlap | Product Overlap Analysis |
| 6 | AI Assisted Comparison | Claude-powered findings (anonymized) |
| 7 | Identify Technical Debt | Technical Debt Findings Register |
| 8 | Estimate Cost Savings | Cost Savings Estimate |
| 9 | Validate with Stakeholders | Stakeholder Validation Notes |
| 10 | Create Recommendations | Software Rationalization Recommendation Report |
| 11 | Executive Summary | Executive Briefing |

## Quick start

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:5055.

For Phase 6 (AI review), create a `.env` file in this folder with:

```
ANTHROPIC_API_KEY=sk-ant-api03-yourkeyhere
```

## Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)** — the consultant's manual: how to run an engagement end-to-end, phase by phase, with tips and a deliverables reference. **Start here.**
- **[techdebtcontext.md](techdebtcontext.md)** — running developer log of decisions, data model, architecture, and per-phase implementation notes. Useful if you're extending the workbench.

## Privacy at a glance

- Engagement data lives in `data/` (gitignored). Customer documents live in `data/uploads/` (gitignored).
- The Anthropic API key lives in `.env` (gitignored).
- Phase 6 anonymizes the inventory before sending to Claude — owner names, internal system names, free-text notes, engagement metadata are all stripped. Vendor / product names are retained because the AI needs them to reason about overlap. De-anonymization happens locally before display. Full details in [USER_GUIDE.md § Privacy and data handling](USER_GUIDE.md#privacy-and-data-handling).

## Stack

Flask + Jinja2 + plain CSS (no build step). `openpyxl` for XLSX I/O. `python-dotenv` for `.env` loading. `anthropic` for the Claude API. JSON file storage — one file per engagement.

Listens on port 5055.

## Repo layout

```
software_rationalization/
├── app.py                    # all Flask routes + helpers per phase
├── ai_service.py             # Phase 6 anonymization + Claude API + worker
├── storage.py                # engagement JSON I/O
├── templates/                # Jinja2 templates (one per phase + shared)
├── static/style.css          # single stylesheet, no framework
├── data/                     # runtime engagement files (gitignored)
├── requirements.txt
├── .env                      # ANTHROPIC_API_KEY (gitignored, you create this)
├── .gitignore
├── README.md                 # this file
├── USER_GUIDE.md             # consultant's manual
└── techdebtcontext.md        # developer log
```
