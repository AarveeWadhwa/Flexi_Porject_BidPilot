
# BidPilot AI — Member 2(Saara): Eligibility & Compliance

This module owns company-profile validation, tender eligibility checks, and required-document matching.

## Files
- `backend/models/company.py` — normalized company profile model and validation
- `backend/models/tender.py` — requirement schema used by the eligibility/compliance modules
- `backend/agents/eligibility_agent.py` — compares company facts with tender requirements
- `backend/agents/compliance_agent.py` — compares available company documents with requested tender documents
- `tests/test_eligibility.py` and `tests/test_compliance.py` — unit tests
- `docs/member2_contract.md` — integration notes for the team

## Setup
Copy these files into the shared BidPilot repository, preserving existing files from Members 1 and 3. The code uses only the Python standard library.

Run tests from the shared repository root:
```bash
python -m unittest discover -s tests -v
```

## Important
This module produces preliminary decision support. It must not represent an unclear or missing value as a definite failure, and it does not replace human review of the tender documents. A missing document is marked missing; it does not automatically mean the company is legally ineligible.

Part 3

Overlay extending Member 2 Parts 1 and 2. Extract at the shared repository root and preserve other members' work.

New integration: `TenderAssessmentPipeline` adapts Member 1's tender-intelligence JSON envelope to Member 2 eligibility/compliance checks and produces a combined report.

Run tests with `python3 -m unittest discover -s tests -v`. See `docs/member2_part3.md`.

Part 4 Overlay

This overlay contains the explainable tender-assessment insights implementation.

## Files
- `backend/services/assessment_insights.py` — assessment insight/summary service.
- `backend/agents/assessment_insights_agent.py` — agent wrapper for assessment insights.
- `tests/test_assessment_insights.py` — focused tests.

## Apply
Copy the files into the matching paths in your existing BidPilot project. Review any differences before overwriting files. From the project root, run:

```bash
python -m unittest tests.test_assessment_insights -v
```

This overlay is intended for the existing project; it is not a standalone application. It does not include secrets, database files, or deployment configuration.
