
"""Bid Analysis Agent: combines eligibility and compliance into a transparent score."""
from __future__ import annotations
from typing import Any


class BidAnalysisAgent:
    """Build a weighted decision-support assessment from Member 2's agent outputs.

    The weights are configurable and the score is not a probability of winning.
    UNKNOWN eligibility checks reduce confidence and trigger review, rather than
    being treated as failures.
    """

    def __init__(self, eligibility_weight: float = 0.65, document_weight: float = 0.35):
        if eligibility_weight < 0 or document_weight < 0:
            raise ValueError("Weights cannot be negative.")
        if eligibility_weight + document_weight <= 0:
            raise ValueError("At least one weight must be positive.")
        total = eligibility_weight + document_weight
        self.eligibility_weight = eligibility_weight / total
        self.document_weight = document_weight / total

    def analyze(
        self,
        eligibility_result: dict[str, Any],
        compliance_result: dict[str, Any],
        tender: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        eligibility_score = eligibility_result.get("eligibility_score")
        document_score = compliance_result.get("document_readiness_score")

        components = []
        if eligibility_score is not None:
            components.append((float(eligibility_score), self.eligibility_weight))
        if document_score is not None:
            components.append((float(document_score), self.document_weight))

        if components:
            effective_weight = sum(weight for _, weight in components)
            overall = round(sum(score * weight for score, weight in components) / effective_weight, 1)
        else:
            overall = None

        failed = eligibility_result.get("failed_checks", []) or []
        unknown = eligibility_result.get("unknown_checks", []) or []
        checklist = compliance_result.get("checklist", []) or []
        missing_docs = [
            item.get("required_document", "Unnamed document")
            for item in checklist if item.get("status") == "MISSING"
        ]

        if failed or missing_docs:
            recommendation = "ACTION_REQUIRED"
        elif unknown:
            recommendation = "NEEDS_HUMAN_REVIEW"
        elif overall is not None and overall >= 80:
            recommendation = "STRONG_CANDIDATE"
        elif overall is not None:
            recommendation = "REVIEW_BEFORE_BIDDING"
        else:
            recommendation = "INSUFFICIENT_DATA"

        strengths = [
            f'{item.get("requirement", item.get("key", "Requirement"))} passed.'
            for item in eligibility_result.get("checks", []) or []
            if item.get("status") == "PASS"
        ]
        risks = [
            f'{item.get("requirement", item.get("key", "Requirement"))}: {item.get("explanation", "Needs review")}'
            for item in failed + unknown
        ]
        risks.extend(f"Required document missing: {name}" for name in missing_docs)

        return {
            "tender_id": (tender or {}).get("tender_id") or eligibility_result.get("tender_id"),
            "tender_title": (tender or {}).get("title", "Untitled tender"),
            "company_name": eligibility_result.get("company_name") or compliance_result.get("company_name", "Company"),
            "eligibility_score": eligibility_score,
            "document_readiness_score": document_score,
            "overall_score": overall,
            "recommendation": recommendation,
            "strengths": strengths,
            "risks": risks,
            "missing_documents": missing_docs,
            "unknown_eligibility_checks": unknown,
            "deadline": (tender or {}).get("deadline"),
            "human_review_required": True,
            "score_note": "Weighted readiness indicator, not a probability of winning or a legal eligibility determination.",
        }


if __name__ == "__main__":
    import json
    eligibility = {
        "company_name": "Demo IT Solutions", "tender_id": "BP-2026-001",
        "eligibility_score": 100.0, "outcome": "MEETS_CHECKED_CRITERIA",
        "checks": [{"requirement": "Turnover", "status": "PASS"}],
        "failed_checks": [], "unknown_checks": [],
    }
    compliance = {
        "company_name": "Demo IT Solutions", "document_readiness_score": 75.0,
        "missing_count": 1, "checklist": [
            {"required_document": "PAN card", "status": "AVAILABLE"},
            {"required_document": "OEM authorization", "status": "MISSING"},
        ],
    }
    print(json.dumps(BidAnalysisAgent().analyze(eligibility, compliance, {
        "tender_id": "BP-2026-001", "title": "Supply of Computer Equipment",
        "deadline": "2026-11-05"
    }), indent=2))
