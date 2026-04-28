# Software Rationalization Workbench — User Guide

A consultant's manual for running a customer engagement end-to-end through the 11-phase Software Inventory, License Review, and Technical Debt Reduction Playbook.

---

## Contents

1. [Quick start](#quick-start)
2. [One-time setup](#one-time-setup-anthropic-api-key)
3. [The dashboard at a glance](#the-dashboard-at-a-glance)
4. [Running an engagement](#running-an-engagement)
   - [Create the engagement](#create-the-engagement)
   - [Phase 1 — Define the Scope](#phase-1--define-the-scope)
   - [Phase 2 — Request Customer Data](#phase-2--request-customer-data)
   - [Phase 3 — Build the Software Inventory](#phase-3--build-the-software-inventory)
   - [Phase 4 — Normalize the Data](#phase-4--normalize-the-data)
   - [Phase 5 — Identify Product Overlap](#phase-5--identify-product-overlap)
   - [Phase 6 — AI Assisted Comparison](#phase-6--ai-assisted-comparison)
   - [Phase 7 — Identify Technical Debt](#phase-7--identify-technical-debt)
   - [Phase 8 — Estimate Cost Savings](#phase-8--estimate-cost-savings)
   - [Phase 9 — Validate with Stakeholders](#phase-9--validate-with-stakeholders)
   - [Phase 10 — Create Recommendations](#phase-10--create-recommendations)
   - [Phase 11 — Executive Summary](#phase-11--executive-summary)
5. [Cross-cutting tips](#cross-cutting-tips)
6. [Deliverables reference](#deliverables-reference)
7. [Privacy and data handling](#privacy-and-data-handling)
8. [Backup, sharing, and migration](#backup-sharing-and-migration)
9. [Troubleshooting](#troubleshooting)

---

## Quick start

1. **Install Python 3.10+** if you don't have it already.
2. **Install the dependencies once**:
   ```
   pip install -r requirements.txt
   ```
3. **Start the workbench**:
   ```
   python app.py
   ```
4. **Open your browser** to **http://localhost:5055**.

That's it — you'll see the dashboard. Stop the server with `Ctrl+C` in the terminal when you're done for the day; restart with `python app.py` when you're ready to keep working. Your data persists between restarts.

---

## One-time setup: Anthropic API key

Phase 6 (AI Assisted Comparison) calls the Anthropic Claude API. The other 10 phases work without an API key.

1. **Get a key** at https://console.anthropic.com → Settings → API Keys → Create Key.
2. **Create a file named `.env`** in the `software_rationalization/` folder with this single line:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-yourkeyhere
   ```
3. **Restart the server** (`Ctrl+C`, then `python app.py` again).

Verify it worked: open any engagement that has products in its inventory, click into Phase 6 in the sidebar, and you should see findings appear within 30 seconds. If you see "AI review unavailable — ANTHROPIC_API_KEY is not set" instead, the file isn't being read — see [Troubleshooting](#troubleshooting).

The `.env` file is gitignored. The key never reaches version control. See [Privacy and data handling](#privacy-and-data-handling) for the full data flow.

---

## The dashboard at a glance

The home page (http://localhost:5055/) shows three things:

**Portfolio overview** — five tiles rolling up across all your engagements: total engagements (with active / complete breakdown), products reviewed, annual spend reviewed, savings identified, and accepted recommendations. Useful when you have multiple engagements running and want a quick health check.

**Engagement cards** — one card per customer engagement. Each shows:

- An **11-segment progress bar** colored per phase. Green = phase finalized, blue = in progress, gray = not started. Glance at the bar to see where the engagement is.
- A **status pill** telling you which phase is the current focus (e.g. "Phase 6 of 11").
- **Three quick stats**: number of products in inventory, total annual spend, savings identified.
- A **Continue:** button that jumps you straight back to the phase you were last working on.

**Three-stage playbook map** at the bottom — Discover (1-3), Analyze (4-7), Decide (8-11) — a reminder of the workflow shape.

---

## Running an engagement

### Create the engagement

Click **+ New engagement** anywhere on the dashboard. You'll see three fields:

| Field | What to enter |
|---|---|
| **Engagement name** | A short label, e.g. *"Acme Corp Q2 2026 Software Review"* |
| **Client / organization** | The customer name |
| **Lead consultant** | You. Optional, but useful when multiple consultants share a workbench. |

Click **Create engagement**. You'll land on the engagement overview page. From here you can either:

- Click **Edit scope** in the Phase 1 panel to start the workflow, or
- Use the **Phases** sidebar on the left to jump to any phase you want.

> **Tip:** the sidebar's status dots (green / blue / gray) update live as you progress. You can revisit any phase at any time, even after finalizing it — finalize is a soft lock you can reopen.

---

### Phase 1 — Define the Scope

**What it produces:** the **Software Review Scope Statement** — a one-page document that establishes what's in scope before any data gathering starts.

**What to fill in:**

- **Objectives** — what is the customer trying to accomplish? Reduce overlap? Cut spend before renewal? Identify shadow IT?
- **Business units in scope** — one per line. *Finance · HR · Engineering · Operations*
- **Tool categories in scope** — checkboxes covering cloud, SaaS, desktop, server, security, infrastructure, network, data and analytics, dev tools, AI tools.
- **Purchase sources in scope** — corporate card, enterprise agreements, department-level purchases, shadow IT.
- **Renewal window** — *e.g. "Renewals due in the next 12 months"* or *"FY26 renewals only"*.
- **Owners** — three groups (contract, technical, business). Use the format `Name | Role | email@example.com`, one per line. Role and email are optional.
- **Out of scope** — anything the customer explicitly does not want reviewed.
- **Constraints & assumptions** — timing windows, sensitivity restrictions, missing data sources.
- **Additional notes** — free-form.

**Workflow:**

- **Save draft** keeps your work without locking it.
- **Finalize scope** marks Phase 1 complete. The dashboard now shows Phase 1's progress dot as green and unlocks Phase 2 in the workflow.
- **Reopen scope** at any time if the customer changes the engagement scope mid-flight.

**Output:** click **View scope statement** for a printable HTML view, or **Download .txt** for a plain text copy you can paste into an email.

> **Tip:** finalize the scope before going to the customer for data. Without a finalized baseline, Phase 5 onwards starts producing numbers that may shift if the scope changes — finalizing pins it.

---

### Phase 2 — Request Customer Data

**What it produces:** the **Customer Data Request Checklist** — a list of 18 document types you may need from the customer, with status tracking per item plus uploaded files.

**What it auto-creates:** on first visit, the page seeds all 18 document types from the playbook (current software inventory, license agreements, purchase orders, invoices, renewal notices, SaaS exports, cloud marketplace purchases, vendor contracts, EAs, asset management exports, endpoint software reports, IdP application lists, finance/procurement reports, help desk catalog, cybersecurity tool list, architecture diagrams, network/endpoint exports, business-critical applications list).

**How to work it:**

1. Add a customer message at the top — this becomes the introductory note in the customer-facing checklist.
2. For each item, set its status:
   - **Requested** — outstanding, you've asked but haven't received yet
   - **Received** — got it
   - **N/A** — customer doesn't have this kind of document
   - **Waived** — agreed not to gather it (out of scope)
3. **Upload files** when documents come in. Drag/drop or click the file picker. Up to 50 MB per upload.
4. Add a note per item if useful — *"requested via email Jun 14, awaiting response"*.

**Auto-behaviors:**

- Uploading a file flips the item from Requested → Received automatically.
- Deleting the last file on a Received item flips it back to Requested.

**Sharing with the customer:** click **View customer-facing checklist** for a printable version, or **Download .txt** to send by email. The customer-facing version shows the customer message at the top and the document list below — clean, no editing controls.

**Finalize Phase 2** when you've gathered everything you're going to gather. This advances the engagement to Phase 3.

> **Tip:** don't wait for *every* document to be Received before moving on. The customer often won't have all 18 types, and that's fine. Mark the ones they don't have as N/A or Waived, and proceed.

---

### Phase 3 — Build the Software Inventory

**What it produces:** the **Master Software Inventory** — a 22-field spreadsheet that's the foundation for every subsequent phase.

**Two ways to add products:**

**A. Import from CSV or XLSX.** This is what you'll do most of the time — the customer almost always has *some* spreadsheet to start from.

1. Click **Import CSV / XLSX**.
2. Upload the file. The first row must be column headers.
3. The importer fuzzy-matches column names to the canonical 22 fields. Any of *"Product"*, *"Product name"*, *"Software"*, *"Application"*, or *"Tool"* maps to `product_name`. *"Annual cost"*, *"yearly cost"*, *"annual spend"* all map to `total_annual_cost`. The full alias list is shown on the import page.
4. Rows missing a product name are skipped and counted in the result.

**B. Add manually.** Click **+ Add product** for one-off entries. The form groups the 22 fields into five sections (Identity, Ownership, Licensing & cost, Contract, Deployment & use, Risk & compliance).

**Auto-calculations:**

- If you fill in **cost per license** and **licenses purchased** but leave **total annual cost** blank, the total auto-fills to the product on save.
- The summary tiles at the top of the list update live as you add or edit products.

**Filtering and sorting:**

- The search box at the top searches across every field.
- The category filter narrows the list.
- Click any column header to sort by that column (ascending / descending toggle).

**Exports:**

- **Export XLSX** — the formatted master inventory. This is what you'd typically share back to the customer.
- **Export CSV** — same data in CSV format.
- **Blank CSV template** — an empty CSV with the canonical headers, useful to send the customer if they want to prepare a fresh inventory in the right shape.

**Finalize Phase 3** when the inventory is comprehensive enough to act on.

> **Tip:** don't over-engineer the inventory. You don't need every field filled in for every product. Get product name + vendor + category + licenses + cost + renewal in for everything, then revisit risk / compliance / notes for the products you suspect are problems.

---

### Phase 4 — Normalize the Data

**What it produces:** a **cleaned and categorized inventory** — the underlying products are still the inventory from Phase 3, but Phase 4 surfaces and helps fix data-quality issues that would distort downstream analysis.

**What you'll see** — eight detector panels, one per issue category:

1. **Vendor name variants** — *"Microsoft"* vs *"Microsoft Corp"* vs *"Microsoft Corporation"*. One-click standardize merges them all to a single canonical vendor.
2. **Duplicate products** — same vendor + similar product name. One-click merge combines license counts and active users; the merge target keeps the most-recently-updated record.
3. **Unknown categories** — products with a category not in the standard list. One-click apply changes them to the suggested standard category.
4. **Missing owners** — products without a business / technical / contract owner. Click through to the product editor.
5. **Missing cost** — products with neither cost-per-license nor total-annual-cost. Click through to fix.
6. **Missing primary use case** — products without a documented purpose.
7. **Uncategorized products** — products with no category at all.
8. **License anomalies** — products where assigned > purchased (over-allocated) or where active > purchased (impossible without trials).

**Working a finding:**

- **Apply** — runs the suggested fix and removes the finding.
- **Ignore with reason** — leaves the data alone but acknowledges the finding (useful when a "duplicate" is actually two separately-licensed instances).
- **Open product** — jumps to the inventory editor so you can fix manually.

**Finalize Phase 4** once all findings are either applied or ignored.

> **Tip:** Phase 4 finds most data-quality issues without thinking. Run it before Phase 5 — clean inventory → cleaner overlap analysis.

---

### Phase 5 — Identify Product Overlap

**What it produces:** the **Product Overlap Analysis** — for every category that has 2+ products, a side-by-side comparison plus a per-product disposition decision.

**Workflow:**

1. The page lists every category with 2+ products as an "overlap cluster" (categories with only one product aren't shown — they're not overlap candidates).
2. For each product in a cluster, set:
   - **Disposition** — Keep, Consolidate, Retire, Replace, Renegotiate, or Further review required.
   - **Risk of removal** — Low, Medium, High, or Unknown.
   - **Notes** — rationale, dependencies, owner ask.
3. Click **Save category decisions** to persist all decisions in that cluster at once.

**Live savings calculator** — the summary tile updates as you save. It sums annual cost across products marked Retire / Replace / Consolidate. Renegotiate doesn't count here because the savings are partial — those flow through to Phase 8.

**Visual cues** — Keep rows tint green; Retire/Replace/Consolidate rows tint yellow.

**Output:**

- **View overlap analysis** — printable HTML for sharing internally.
- **Download .csv** — same data in spreadsheet format.

**Finalize Phase 5** to advance to Phase 6.

> **Tip:** don't agonize over Renegotiate vs Replace at this stage. The dispositions become Phase 8 cost savings opportunities, where you can revisit and refine the math. Phase 5 is about marking each product with an intent, not committing to a final action.

---

### Phase 6 — AI Assisted Comparison

**What it produces:** Claude-generated findings grouped by category, covering overlapping functionality, redundant features, underused licenses, outdated products, and consolidation opportunities.

**How it runs:**

- **Auto-runs in the background** the first time you visit Phase 6 (and re-runs whenever the inventory changes since the last run). The page shows a spinner with a 3-second meta-refresh until results land — typically 20-40 seconds.
- **Manual re-run** button is available once findings exist.

**What the AI sees** — only a sanitized subset of the inventory. The full list of fields sent vs stripped is shown in a green privacy banner at the top of the page. Quick summary:

- **Sent**: product name, vendor, version, category, license counts, costs, renewal date, contract term, deployment model, primary use case, data sensitivity. Each product is referenced by an anonymized `PROD_001`-style ID.
- **Stripped**: business / technical / contract owners, purchase source, systems supported, security/compliance freetext, known risks, notes. Engagement name, client name, and lead consultant never leave the box either.

**What you see** — the AI's response is mapped back to your real product names locally before display. You see "Slack vs Microsoft Teams overlap" rather than "PROD_001 vs PROD_002".

**Each finding includes:**

- **Summary** — one-line headline
- **Products** — clickable tags that jump to the product editor
- **Concern** — what the issue is
- **Potential risk** — what could go wrong
- **Cost impact** — rough $ estimate
- **Next step** — concrete first action

**Finalize Phase 6** to advance to Phase 7.

> **Tip:** treat AI findings as a second opinion, not gospel. The model is good at spotting overlap and unused licenses — patterns that show up in the structured data — and weaker at things that depend on customer-specific context (which it never sees). Use it to surface candidates, then verify with stakeholders in Phase 9.

---

### Phase 7 — Identify Technical Debt

**What it produces:** the **Technical Debt Findings Register** — per-product flags covering 14 debt categories from the playbook, with severity and notes.

**The 14 debt categories:**

1. Unsupported software
2. Outdated version
3. Unused product
4. Duplicative tool
5. No clear owner
6. Unclear mission need
7. Purchased outside governance
8. Does not integrate
9. Weak security controls
10. Excessive manual work
11. Creates a data silo
12. Poor adoption
13. High cost, low value
14. Nearing renewal without justification

**Auto-suggestions** — yellow chips above each product show flags the system thinks might apply, derived from existing inventory data:

- **No clear owner** when any owner field is blank
- **Unclear mission** when primary use case is blank
- **Duplicative tool** when the category has 2+ products
- **Unused** when assigned > 0 and active = 0
- **Poor adoption** when active < 20% of assigned
- **Outside governance** when purchase source mentions "card", "personal", "shadow", or "expense"
- **High cost, low value** when annual cost is in the top quartile and active < 50% of purchased
- **Renewal without justification** when renewal is within 90 days and primary use case is blank

Click a chip to tick the corresponding checkbox. You decide which actually apply — the suggestions are starting points, not assertions.

**Per product:**

- Tick all 14 flag checkboxes that apply.
- Set severity (Low / Medium / High).
- Add notes — why it's debt, what it would take to address, who owns the decision.

**Filters** — by flag, by severity, or "only flagged" to hide healthy products.

**Output:**

- **View debt register** — printable HTML.
- **Download .csv** — spreadsheet export.

**Finalize Phase 7** to advance to Phase 8.

> **Tip:** the auto-suggestions are deliberately conservative — they need multiple signals before firing — so when one appears, take it seriously. The detectors will miss soft issues (org politics, hidden integrations, customer asks) so don't rely on them alone.

---

### Phase 8 — Estimate Cost Savings

**What it produces:** the **Cost Savings Estimate** — a structured worksheet of consolidation opportunities, each with current cost, transition cost, recurring savings, and net first-year savings, rolling up to a portfolio total.

**Auto-seeding** — click **Seed from Phase 5 + 7** to bootstrap opportunities:

- One opportunity per Phase 5 disposition that's Retire, Replace, Consolidate, or Renegotiate. Recurring savings default to the product's full annual cost (or 20% for Renegotiate, since that's a discount, not a full retirement).
- One opportunity per product flagged "Unused" in Phase 7 that wasn't already covered by Phase 5. Recurring savings default to `cost-per-license × unused-license-count`.
- Re-clicking is idempotent — it won't create duplicates.

**Per opportunity** — the card has:

- **Title** (editable)
- **Disposition** — Retire, Replace, Consolidate, Renegotiate, Reduce licenses, or Other.
- **Status** — Proposed (default), Approved (signed off), or Rejected.
- **Five money fields**: current annual cost, recurring annual savings, one-time savings (e.g. break renewal, renegotiation discount), migration cost, training cost.
- **Computed totals** showing live: recurring/yr, net first-year, transition cost.
- **Notes** — rationale, dependencies, owner ask.
- **Quick actions** — approve, reset to proposed, reject, delete.

**Status semantics for the portfolio rollup:**

- **Non-rejected total** — the upside if every proposed opportunity lands. Use this internally.
- **Approved-only total** — the conservative number you'd commit to in front of leadership. Approved opportunities have been validated.

**Custom opportunity** — at the bottom, add an opportunity not tied to a specific Phase 5 or Phase 7 finding (e.g. bundle a multi-product renewal negotiation).

**Output:**

- **View savings estimate** — printable HTML.
- **Download .csv** — spreadsheet export.

**Finalize Phase 8** to advance to Phase 9.

> **Tip:** don't approve opportunities until they've been validated in Phase 9. The split between proposed and approved is what makes the leadership rollup credible — if everything starts as approved, the conservative number isn't conservative.

---

### Phase 9 — Validate with Stakeholders

**What it produces:** the **Stakeholder Validation Notes** — for each Phase 8 opportunity, a record of who you talked to and how they answered the playbook's seven validation questions.

**Per opportunity** — the card has:

**Stakeholder roster** — pipe-separated text, one stakeholder per line:

```
Jane Doe | IT leadership | 2026-04-30 | Agreed | wants migration plan
Bob Smith | Cybersecurity | 2026-05-02 | Pushback | concerns about replacement SSO posture
```

Recognized roles (case-insensitive): IT leadership, Cybersecurity team, Finance, Procurement, Business unit owner, System administrator, Power user, Compliance / legal. Recognized statuses: Consulted, Agreed, Pushback, Blocked. Unrecognized values are kept as free text.

**Seven validation questions** — answer the ones that apply:

1. Who uses this tool?
2. What business process depends on it?
3. What would break if it was removed?
4. Is there a better enterprise tool already available?
5. Is the tool required by contract, compliance, or customer need?
6. Is the cost justified by the value?
7. Can the function be absorbed by another product?

**Overall validation status** — Not started, In progress, Validated, or Blocked. Drives sort order on the page so blocked / pending opportunities surface first.

**Output:**

- **View validation notes** — printable HTML.
- **Download .csv** — spreadsheet export with per-stakeholder status counts.

**Finalize Phase 9** to advance to Phase 10.

> **Tip:** answer at least Q3 (what would break if removed?) and Q5 (required by contract / compliance?) for every opportunity. Those two prevent the most common rationalization mistakes — removing a tool that quietly underpins something important.

---

### Phase 10 — Create Recommendations

**What it produces:** the **Software Rationalization Recommendation Report** — leadership-ready recommendations, one per finding, covering all 11 fields the playbook calls for.

**Auto-seeding** — click **Seed from Phase 8** to create one recommendation per opportunity. The system fills in:

- **Finding** — opportunity title
- **Category** — derived from disposition (retire → Retirement, consolidate → Consolidation, renegotiate → Renewal Negotiation, etc.)
- **Business impact** — pulled from Phase 9 validation answers (`business_process` + `what_breaks`); falls back to product primary use case
- **Tech-debt impact** — distinct Phase 7 flag labels across affected products
- **Security impact** — Phase 7 weak_security flag presence + product data sensitivity levels
- **Cost impact** — formatted from Phase 8 totals
- **Recommended action** — templated by disposition + Phase 9 freeform notes
- **Status** — Accepted if Phase 8 opportunity is Approved, otherwise Draft

**You fill in:**

- **Level of effort** — Low / Medium / High
- **Risk level** — Low / Medium / High
- **Proposed timeline** — *e.g. "Q3 2026, before next renewal"*
- **Decision owner** — who signs off

**Eight categories** — recommendations group by category in this order: Immediate savings → Renewal negotiation → License reduction → Product consolidation → Product retirement → Security risk reduction → Governance improvement → Further analysis required.

**Custom recommendation** — for things that don't tie to a Phase 8 opportunity (e.g. *"Establish SaaS purchase governance"*). Multi-product picker lets you tag affected products optionally.

**Quick actions** per card — Accept / Return to draft / Defer / Delete.

**Output:**

- **View report** — printable HTML grouped by category, with a category-definitions reference at the bottom.
- **Download .csv** — spreadsheet export.

**Finalize Phase 10** to advance to Phase 11.

> **Tip:** before finalizing, sweep the page once and accept or defer every recommendation. Drafts left over after finalize show up as "decisions needed" on the executive briefing — leadership reads that as "the consultant didn't make a call here."

---

### Phase 11 — Executive Summary

**What it produces:** the **Executive Briefing** — the single-page document you walk leadership through. This is the engagement's headline deliverable.

**The seven leadership questions** auto-answer from prior phases:

1. **Products reviewed** — count from inventory
2. **Total annual software spend** — sum of `total_annual_cost`
3. **Products that overlap** — Phase 5 cluster sums
4. **Products with unused licenses** — Phase 7 unused-flag count + secondary under-utilized count
5. **Technical debt identified** — Phase 7 summary
6. **Estimated cost savings** — Phase 8 totals (both non-rejected and approved-only)
7. **Decisions needed from leadership** — Phase 10 recommendations still in draft or deferred

**Five narrative fields** — you fill in:

- **Headline** — the TL;DR sentence shown as a callout above everything on the briefing
- **Key strategic finding** — the pattern that connects multiple findings
- **Top recommendation** — the highest-impact action
- **Leadership ask** — 1-3 specific decisions you need
- **Next steps** — proposed timeline

**Prioritized action plan** — auto-built from accepted Phase 10 recommendations, sorted by risk (high first) → cost magnitude (high first) → level of effort (low first, favoring quick wins).

**Final deliverables manifest** — links to all 10 prior outputs with ready/not-ready state. Include this when handing off the engagement.

**Output:**

- **View executive briefing** — the printable, leadership-facing document. Use Print → Save as PDF if you want to email it.

**Finalize Phase 11** to mark the engagement `complete`. The dashboard now shows the engagement card with a green "Complete" pill.

> **Tip:** spend real time on the headline field. Leadership reads the briefing top-down and the headline is the only thing some of them will read carefully. State the dollar amount, the action, and the urgency in one sentence.

---

## Cross-cutting tips

**Finalize is a soft lock, not a hard lock.** Every phase has a Reopen button. Use finalize to mark "I'm done with this for now"; reopen if a stakeholder pushes back or the data changes.

**Use the sidebar's progress dots** as your at-a-glance status check. Green = finalized, blue = in progress, gray = not started. The dashboard's Continue button on each engagement card jumps you to the latest in-progress phase automatically.

**Edit a product anywhere.** Every product reference in Phases 5, 7, 8, 9, 10 is a clickable tag that opens the product editor. Make a correction, save, return — your edit propagates to every downstream phase.

**Auto-seeding is idempotent.** Phase 8's "Seed from Phase 5 + 7" and Phase 10's "Seed from Phase 8" both use stable seed keys — re-clicking them after adding new data only creates the new entries, never duplicates the old ones.

**Finalizing a phase pre-marks the next phase as in-progress.** Visual continuity in the sidebar — the next phase shows up active rather than gray, signaling where to go next.

---

## Deliverables reference

Every phase produces something you can share. Here's the master list with the exact URLs (replace `<id>` with your engagement ID):

| Phase | Deliverable | Format | URL |
|---|---|---|---|
| 1 | Software Review Scope Statement | HTML / TXT | `/engagements/<id>/scope/statement[.txt]` |
| 2 | Customer Data Request Checklist | HTML / TXT | `/engagements/<id>/data-request/checklist[.txt]` |
| 3 | Master Software Inventory | XLSX / CSV | `/engagements/<id>/inventory/export.xlsx` (or `.csv`) |
| 4 | Cleaned & Categorized Inventory | inline | `/engagements/<id>/normalize` |
| 5 | Product Overlap Analysis | HTML / CSV | `/engagements/<id>/overlap/analysis[.csv]` |
| 6 | AI Assisted Comparison Findings | inline | `/engagements/<id>/ai-review` |
| 7 | Technical Debt Findings Register | HTML / CSV | `/engagements/<id>/tech-debt/register[.csv]` |
| 8 | Cost Savings Estimate | HTML / CSV | `/engagements/<id>/savings/estimate[.csv]` |
| 9 | Stakeholder Validation Notes | HTML / CSV | `/engagements/<id>/validation/notes[.csv]` |
| 10 | Recommendation Report | HTML / CSV | `/engagements/<id>/recommendations/report[.csv]` |
| 11 | Executive Briefing | HTML | `/engagements/<id>/exec-summary/briefing` |

For HTML deliverables, use your browser's **Print → Save as PDF** to produce a portable file. The print stylesheet hides navigation and prints the document content only.

---

## Privacy and data handling

**Where engagement data lives.** Every engagement is one JSON file in `software_rationalization/data/<engagement_id>.json`. Files uploaded in Phase 2 live under `software_rationalization/data/uploads/<engagement_id>/`. Both `data/*.json` and `data/uploads/` are gitignored — they never reach version control.

**The Anthropic API key.** Stored in `software_rationalization/.env`, gitignored. Loaded into the process at startup via `python-dotenv`. Never logged to disk by the workbench.

**What goes to the Claude API in Phase 6.** A whitelist of fields per product, with anonymized `PROD_NNN` IDs. The full list is shown in the green privacy banner at the top of the Phase 6 page. Specifically:

- **Sent**: product_name, vendor, version, category, licenses_purchased, licenses_assigned, active_users, cost_per_license, total_annual_cost, renewal_date, contract_term, deployment_model, primary_use_case, data_sensitivity.
- **Stripped before send**: business_owner, technical_owner, contract_owner, purchase_source, systems_supported, security_compliance, known_risks, notes. Engagement name, client name, lead consultant never leave either.

**Why product and vendor names are sent.** They're public identifiers — Slack is Slack everywhere. Without them, the model can't reason about overlap meaningfully ("Tool A vs Tool B" tells the AI nothing). The customer-private signal is *who owns what at this customer*, not *what software exists in the world*. We protect the former, not the latter.

**De-anonymization is local.** The AI's response references products by `PROD_NNN`. After the response returns, the workbench maps those tokens back to your real product IDs in memory and renders the findings with real product names. The mapping never round-trips through the API.

**Verifying privacy on a real run.** After Phase 6 completes, you can open `data/<engagement_id>.json` and search the `ai_review.raw_response` field for any client-specific strings (customer name, employee names, internal system names). They should appear nowhere.

---

## Backup, sharing, and migration

**Daily working data lives in `data/`.** To back up an engagement, copy the JSON file plus the `data/uploads/<engagement_id>/` folder.

**To move an engagement to another machine** — copy the JSON + uploads folder into the target machine's `data/` directory. The dashboard picks it up on next page load.

**To share an engagement read-only with a colleague** — the simplest path is sharing the *deliverables* (the printable HTML / PDF / CSV exports), not the engagement JSON. The deliverables are the customer-facing artifacts and don't require the colleague to run the workbench.

**To delete an engagement** — delete its `.json` file from `data/` plus its `uploads/<engagement_id>/` folder if any. There's no undo.

**Don't commit `data/` to git.** The `.gitignore` already excludes it; just don't override that.

**Don't commit `.env`.** Same — already gitignored.

---

## Troubleshooting

**The server won't start.** Check Python is 3.10+ (`python --version`). Make sure dependencies are installed (`pip install -r requirements.txt`). Make sure port 5055 isn't already in use by another process.

**The page says "AI review unavailable — ANTHROPIC_API_KEY is not set" but I created a `.env`.** Two common causes:

1. The `.env` file is in the wrong folder. It must be in `software_rationalization/`, next to `app.py`.
2. The variable is already set as an empty string in your OS environment, shadowing the `.env` value. The workbench handles this — it calls `load_dotenv(override=True)` to win against blank shell vars — but if you've added the key as an OS env var via System Properties, that takes precedence over `.env`. Either remove the OS env var, or update its value.

**AI review starts but never finishes.** Check the terminal where you launched the server for an error. Common causes: invalid API key (you'll see a 401), no network, or the model you're using is unavailable. The page will eventually show an error and a Retry button if the API call fails.

**I uploaded a file in Phase 2 but it doesn't appear.** Refresh the page. If still missing, check the file size — anything over 50 MB is rejected silently. Check the file extension — only common formats are allowed (PDF, CSV, XLSX, DOCX, TXT, PNG, JPG, JSON, XML, ZIP, PPTX, VSDX).

**My CSV import skipped most rows.** Rows are skipped when they have no product name. Verify your CSV has a column header that matches one of the recognized aliases for `product_name` (Product, Product name, Software, Application, Tool, App, Name).

**I finalized a phase by accident.** Click into the phase from the sidebar and click **Reopen Phase X**. Reopen unlocks all editing controls.

**The "Continue" button on the dashboard sends me to the wrong phase.** It points to the latest *in-progress* phase. If you finalized a later phase but want to go back to an earlier one, use the **Phases** sidebar inside the engagement instead.

**A phase shows phantom data after I deleted products.** The phase has cached state derived from the inventory. For Phase 6 (AI review), use **Re-run review** to refresh. For Phase 8 / 10, the seed is idempotent — your manually-created opportunities remain, but stale seeded ones can be deleted with the per-card Delete button.

---

## Where to go from here

- **Run a real engagement** — start with a customer you know well so you can sanity-check the playbook's outputs against your own intuition.
- **Inspect `techdebtcontext.md`** — the running developer log of decisions and architecture if you ever want to extend the workbench.
- **Source on GitHub** — https://github.com/gene-png/tech-debt
