
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

