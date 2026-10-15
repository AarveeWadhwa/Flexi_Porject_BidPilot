
# Tanishka Integration Contract

## Inputs from Member 2

`EligibilityAgent.evaluate(...)` returns an object containing `company_name`, `tender_id`, `eligibility_score`, `checks`, `failed_checks`, and `unknown_checks`.

`ComplianceAgent.evaluate(...)` returns `company_name`, `document_readiness_score`, `missing_count`, and `checklist`.

## Example orchestration

```python
from backend.agents.bid_analysis_agent import BidAnalysisAgent
from backend.agents.deadline_agent import DeadlineCorrigendumAgent
from backend.agents.preparation_agent import BidPreparationAgent

analysis = BidAnalysisAgent().analyze(
    eligibility_result=eligibility_result,
    compliance_result=compliance_result,
    tender=tender_record,
)
change_result = DeadlineCorrigendumAgent().compare(previous_tender, latest_tender)
report = BidPreparationAgent().prepare(
    analysis,
    tender=tender_record,
    compliance_result=compliance_result,
)
```

Use `format_tender_alert(change_result)` to render a message if `has_changes` is true.

## Scoring and safety
- Default score weights: 65% eligibility and 35% document readiness; configurable.
- The score is a readiness indicator, not a probability of winning.
- Any failed eligibility check or missing required document leads to `ACTION_REQUIRED`.
- Missing/unclear eligibility data leads to `NEEDS_HUMAN_REVIEW`.
- Monitoring compares snapshots supplied by a source adapter; it does not itself poll a live portal.
- A person must verify official documents, changes, deadlines, and final bid content.

# Tanishka — Part 2: Evidence-aware bid analysis and change monitoring

## What changed
- Snapshot-based deadline/corrigendum comparison produces field-level change events with severity.
- Bid analysis consumes Member 2 eligibility/compliance report shapes, reports strengths, risks, evidence, and prioritized actions.
- Preparation agent produces a checklist with general controls plus specific analysis/compliance actions.
- Notification service creates payloads for high-priority tender changes and deadline reminders; it does not send email/SMS by itself.
- Reports explicitly distinguish analysis from verified facts and retain human-review requirements.

## Run tests
From the shared repository root:
```bash
python3 -m unittest discover -s tests -v
```

## Example
```python
from backend.agents.deadline_agent import DeadlineAgent
from backend.agents.bid_analysis_agent import BidAnalysisAgent
from backend.agents.preparation_agent import PreparationAgent

changes = DeadlineAgent().compare_snapshots(old_snapshot, new_snapshot)
analysis = BidAnalysisAgent().analyze(tender_id, eligibility_report, compliance_report, changes)
checklist = PreparationAgent().prepare(tender_id, analysis, compliance_report, deadline)
```

## Boundaries
This package compares snapshots supplied by a caller. It does not poll tender portals, guarantee that every corrigendum has been captured, or send notifications without a delivery adapter. All official tender conditions and deadlines must be verified against the source.

# Member 3 — Part 3: Integrated Bid Workspace Pipeline

## Purpose
This layer combines the existing Member 3 agents into one repeatable workflow. For each upstream tender assessment, it produces a bid analysis, optional snapshot-change report, preparation checklist, and notification payloads.

## Inputs
- `assessments`: a JSON list or an object containing `assessments`/`results`. Each assessment needs `tender_id`, `eligibility_result`, and `compliance_result`; an optional `tender` object can include title and deadline.
- `current_snapshots` and `previous_snapshots`: optional lists keyed by `tender_id` or `id`. They are compared only when both snapshots exist for the same tender.

## Run
From the repository root, after extracting the overlay:

```bash
python3 -m unittest discover -s tests -v
python3 -m backend.agents.bid_workspace_agent \
  --assessments examples/assessments.json \
  --current-snapshots examples/current_snapshots.json \
  --previous-snapshots examples/previous_snapshots.json \
  --output outputs/member3_bid_workspace.json
```

The command creates the output directory if needed and writes the combined report as JSON.

## Output
- `analysis`: score, recommendation, strengths, risks, action items, missing documents, and evidence
- `change_report`: changed fields, severities, and human-review flag, when prior/current snapshots are supplied
- `preparation_checklist`: pending tasks derived from the analysis plus general bid controls
- `notifications`: structured alert payloads for important changes

## Boundaries
This is an orchestration layer over supplied JSON. It does not fetch tender portals, run scheduled monitoring, send email/SMS, verify document authenticity, submit bids, or make legal eligibility decisions. Scores are indicative and must be reviewed by a person. Inputs should be sourced from the project's actual upstream agents when integrated; the included example is a test fixture only.

# Member 3 Part 4 — Bid Portfolio Report and Action Register

## Purpose

Part 4 completes the Member 3 workflow by turning the integrated bid workspace JSON into a portfolio-level action register and shareable reports.

## Inputs and outputs

Input: JSON produced by `backend.agents.bid_workspace_agent` (`results[]` with analysis, change report and preparation checklist).

Outputs:
- JSON portfolio report with recommendation/risk counts and action register
- CSV action register for spreadsheet review
- Markdown summary for a project report or review meeting

## Run

```bash
python3 -m backend.agents.bid_portfolio_report_agent \
  --input outputs/member3_bid_workspace.json \
  --output outputs/member3_portfolio_report.json \
  --csv outputs/member3_action_register.csv \
  --markdown outputs/member3_portfolio_summary.md
```

## Scope and limitations

This component summarizes supplied output only. It does not verify tender portal facts, calculate legal eligibility, predict winning probability, poll for updates, or send notifications. Action detection depends on recognizable checklist fields and statuses; users should review the original tender documents and all generated flags.

