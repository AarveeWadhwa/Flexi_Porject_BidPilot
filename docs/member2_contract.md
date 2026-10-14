
# Member 2 Integration Contract

## Company profile
Use `CompanyProfile.from_dict(profile_dict)` to validate and normalize profile data.

```python
from backend.models.company import CompanyProfile
company = CompanyProfile.from_dict({
    "company_name": "Demo IT Solutions",
    "location": "Pune, Maharashtra",
    "annual_turnover_inr": 14_000_000,
    "years_experience": 4,
    "certifications": ["ISO 9001"],
    "available_documents": ["PAN.pdf", "GST certificate.pdf"]
})
```

## From Member 1's requirement extractor
Member 1 emits strings such as `₹1 crore`, `3 years`, `Maharashtra`, and a list of documents. Convert the output with:

```python
from backend.models.tender import TenderRequirements
requirements = TenderRequirements.from_extraction(extraction_output)
```

Then use normalized values with `EligibilityAgent`:

```python
from backend.agents.eligibility_agent import EligibilityAgent
result = EligibilityAgent().evaluate(company, requirements)
```

And check documents:

```python
from backend.agents.compliance_agent import ComplianceAgent
result = ComplianceAgent().evaluate(extraction_output["documents_required"], company)
```

## Status semantics
- `PASS`: known company value meets a known requirement.
- `FAIL`: known company value does not meet a known requirement.
- `UNKNOWN`: source/profile data is missing or ambiguous; human review needed.
- Document `AVAILABLE` means a likely inventory/filename match only, not proof that the document is valid.

## Notes
- Money parsing supports numeric amounts and common INR units such as lakh/crore. Ambiguous or unrecognized formats return `None`.
- Location checks are conservative because a tender's delivery location is not necessarily a bidder-location restriction.
- Keep original tender clauses and source documents available for human review.

Part 2: Evidence-aware eligibility and compliance

## Purpose
This overlay extends Member 2's existing starter module. It is designed to accept either the original Member 1 extraction structure or the `normalized_requirements` structure produced by Member 1's later work.

## Changes
- Expanded `TenderRequirements` to include EMD, tender fee, deadline, technical requirements, evidence, and review flags.
- Added an extraction adapter that reads normalized fields while retaining backward compatibility with older keys.
- Eligibility results carry supporting evidence when available and keep missing/unreliable facts as `UNKNOWN`.
- Compliance results accept document inventory entries as filenames or records with `status`, `expiry_date`, and `source`.
- Conservative document matching reduces false positives from very short partial names.
- Added `BidReadinessAgent` to combine eligibility and document compliance into one report with action items.

## Run tests
From the shared repository root:
```bash
python3 -m unittest discover -s tests -v
```

## Integration
```python
from backend.agents.bid_readiness_agent import BidReadinessAgent