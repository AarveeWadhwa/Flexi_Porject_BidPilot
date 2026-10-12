
"""Bid Preparation Agent: creates an action-oriented report for human approval."""
from __future__ import annotations
from typing import Any
from backend.models.report import BidReadinessReport


class BidPreparationAgent:
    """Creates a readiness report; it does not submit bids or fabricate evidence."""

    def prepare(
        self,
        analysis: dict[str, Any],
        tender: dict[str, Any] | None = None,
        compliance_result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        tender = tender or {}
        compliance_result = compliance_result or {}
        missing = analysis.get("missing_documents", []) or []
        actions = []

        for document in missing:
            actions.append(f"Obtain and verify: {document}.")
        for risk in analysis.get("risks", []) or []:
            if risk not in missing:
                actions.append(f"Review and resolve: {risk}")

        unknown = analysis.get("unknown_eligibility_checks", []) or []
        if unknown:
            actions.append("Manually verify all eligibility conditions marked UNKNOWN against the original tender.")
        if not actions:
            actions.append("Complete final document validation and have an authorized person review the bid package.")
        actions.extend([
            "Verify the latest tender notice and all corrigenda.",
            "Confirm submission deadline, required format, fees, and signing requirements.",
            "Obtain authorized human approval before any submission.",
        ])

        report = BidReadinessReport(
            tender_id=str(analysis.get("tender_id") or tender.get("tender_id") or "UNKNOWN"),
            tender_title=str(analysis.get("tender_title") or tender.get("title") or "Untitled tender"),
            company_name=str(analysis.get("company_name") or "Company"),
            recommendation=str(analysis.get("recommendation") or "INSUFFICIENT_DATA"),
            overall_score=analysis.get("overall_score"),
            eligibility_score=analysis.get("eligibility_score"),
            document_readiness_score=analysis.get("document_readiness_score"),
            deadline=analysis.get("deadline") or tender.get("deadline"),
            strengths=list(analysis.get("strengths", []) or []),
            risks=list(analysis.get("risks", []) or []),
            actions=actions,
            human_review_required=True,
        )
        result = report.to_dict()
        result["document_checklist"] = compliance_result.get("checklist", [])
        result["corrigendum_review_required"] = True
        return result


if __name__ == "__main__":
    import json
    analysis = {
        "tender_id": "BP-2026-001", "tender_title": "Supply of Computer Equipment",
        "company_name": "Demo IT Solutions", "recommendation": "ACTION_REQUIRED",
        "overall_score": 82.5, "eligibility_score": 100.0,
        "document_readiness_score": 50.0, "deadline": "2026-11-05",
        "strengths": ["Annual turnover passed."],
        "risks": ["Required document missing: OEM authorization"],
        "missing_documents": ["OEM authorization"], "unknown_eligibility_checks": [],
    }
    print(json.dumps(BidPreparationAgent().prepare(analysis), indent=2))
