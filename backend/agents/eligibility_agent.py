
"""Eligibility Agent: compare verified company facts with extracted tender rules."""
from __future__ import annotations
from typing import Any
from backend.models.company import CompanyProfile
from backend.models.tender import TenderRequirements


class EligibilityAgent:
    """Returns PASS, FAIL, or UNKNOWN for each comparable requirement.

    UNKNOWN is used when either side is missing or could not be normalized.
    The summary score only uses checks that have a definite PASS/FAIL result.
    """

    def evaluate(
        self,
        company: CompanyProfile | dict[str, Any],
        tender: TenderRequirements | dict[str, Any],
    ) -> dict[str, Any]:
        company = company if isinstance(company, CompanyProfile) else CompanyProfile.from_dict(company)
        tender = tender if isinstance(tender, TenderRequirements) else TenderRequirements(**tender)

        checks = []
        checks.append(self._numeric_check(
            "annual_turnover",
            "Annual turnover",
            company.annual_turnover_inr,
            tender.minimum_turnover_inr,
            "INR",
        ))
        checks.append(self._numeric_check(
            "experience",
            "Relevant experience",
            company.years_experience,
            tender.minimum_experience_years,
            "years",
        ))
        checks.append(self._location_check(company.location, tender.location_requirement))

        certifications = {self._norm(x) for x in company.certifications}
        for required in tender.certifications:
            required_norm = self._norm(required)
            if not required_norm:
                continue
            present = any(required_norm in cert or cert in required_norm for cert in certifications)
            checks.append({
                "key": f"certification:{required}",
                "requirement": f"Certification: {required}",
                "status": "PASS" if present else ("UNKNOWN" if not company.certifications else "FAIL"),
                "company_value": sorted(company.certifications),
                "required_value": required,
                "explanation": (
                    f"Company profile lists a matching certification for {required}."
                    if present else
                    (f"Certification data is incomplete; verify whether {required} is held."
                     if not company.certifications else
                     f"No matching certification for {required} is listed in the profile.")
                ),
            })

        definite = [c for c in checks if c["status"] in {"PASS", "FAIL"}]
        passed = sum(c["status"] == "PASS" for c in definite)
        score = round(passed / len(definite) * 100, 1) if definite else None
        failed = [c for c in checks if c["status"] == "FAIL"]
        unknown = [c for c in checks if c["status"] == "UNKNOWN"]
        if failed:
            outcome = "POTENTIAL_GAPS"
        elif unknown:
            outcome = "NEEDS_REVIEW"
        else:
            outcome = "MEETS_CHECKED_CRITERIA"

        return {
            "company_name": company.company_name,
            "tender_id": tender.tender_id,
            "outcome": outcome,
            "eligibility_score": score,
            "checks": checks,
            "failed_checks": failed,
            "unknown_checks": unknown,
            "disclaimer": "Preliminary screening only. Verify tender clauses and supporting evidence before making a bid decision.",
        }

    @staticmethod
    def _norm(value: str | None) -> str:
        return " ".join((value or "").lower().replace("-", " ").split())

    def _numeric_check(self, key: str, label: str, actual: float | None,
                       required: float | None, unit: str) -> dict[str, Any]:
        if required is None:
            status, explanation = "UNKNOWN", "The requirement could not be reliably extracted."
        elif actual is None:
            status, explanation = "UNKNOWN", "Company profile does not contain this value."
        elif actual >= required:
            status, explanation = "PASS", f"Company value meets or exceeds the required {unit} threshold."
        else:
            status, explanation = "FAIL", f"Company value is below the required {unit} threshold."
        return {
            "key": key, "requirement": label, "status": status,
            "company_value": actual, "required_value": required,
            "unit": unit, "explanation": explanation,
        }

    def _location_check(self, actual: str, required: str | None) -> dict[str, Any]:
        if not required:
            status, explanation = "UNKNOWN", "No clear location restriction was extracted."
        elif not actual:
            status, explanation = "UNKNOWN", "Company location is not provided."
        elif self._norm(required) in self._norm(actual) or self._norm(actual) in self._norm(required):
            status, explanation = "PASS", "Company location appears consistent with the tender location."
        else:
            status, explanation = "UNKNOWN", "Location wording differs; confirm whether the tender restricts bidder registration or only delivery."
        return {
            "key": "location", "requirement": "Location",
            "status": status, "company_value": actual,
            "required_value": required, "explanation": explanation,
        }


if __name__ == "__main__":
    sample_company = {
        "company_name": "Demo IT Solutions",
        "industry": "IT",
        "location": "Pune, Maharashtra",
        "annual_turnover_inr": 14_000_000,
        "years_experience": 4,
        "certifications": ["ISO 9001"],
    }
    sample_tender = {
        "tender_id": "BP-2026-001",
        "minimum_turnover_inr": 10_000_000,
        "minimum_experience_years": 3,
        "location_requirement": "Maharashtra",
        "certifications": ["ISO 9001"],
    }
    import json
    print(json.dumps(EligibilityAgent().evaluate(sample_company, sample_tender), indent=2))
