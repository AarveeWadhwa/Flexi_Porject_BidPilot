
# BidPilot AI — Member 1: Tender Intelligence

This module covers:
1. **Tender Discovery Agent** — ranks tenders from a local/sample tender catalogue against a company profile.
2. **Tender Requirement Extraction Agent** — extracts structured requirements from tender text or PDF files.
3. **Source and document utilities** — loads sample tenders and extracts text from TXT/PDF documents.

The module is intentionally runnable without paid APIs or credentials. The discovery source uses a local JSON catalogue for the mini-project demo; `scraper.py` contains a clear adapter point for connecting approved public tender sources later.

## Setup

Python 3.10+ recommended.

```bash
cd BidPilot_Member1
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

## Run the discovery demo

```bash
python -m backend.agents.discovery_agent
```

## Extract requirements from a text file

```bash
python -m backend.agents.requirement_agent data/sample_tenders/tender_001.txt
```

For a PDF:
```bash
python -m backend.agents.requirement_agent path/to/tender.pdf
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Integration contract for the other team members

Discovery returns dictionaries with `tender_id`, `title`, `organization`, `location`, `deadline`, `estimated_value`, `categories`, `description`, `source_url`, `relevance_score`, and `matched_terms`.

Requirement extraction returns:
- `tender_id` (when supplied)
- `eligibility`: turnover, experience, location and other eligibility conditions
- `technical_requirements`
- `financial_requirements`: EMD and tender fee where detected
- `certifications`
- `documents_required`
- `deadlines`
- `evaluation_criteria`
- `evidence`: snippets supporting extracted fields
- `warnings`: fields that need human verification

The downstream eligibility/compliance agents should treat extracted values as **candidate facts**, not authoritative legal conclusions. Always retain the source text and ask a human to verify tender requirements before bidding.
