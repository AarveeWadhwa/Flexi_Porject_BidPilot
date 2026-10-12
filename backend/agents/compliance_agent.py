
"""Compliance & Document Agent: match tender document requirements to company records."""
from __future__ import annotations
import re
from typing import Any
from backend.models.company import CompanyProfile


ALIASES = {
    "pan card": {"pan", "pan card", "permanent account number"},
    "gst certificate": {"gst", "gst certificate", "gst registration", "gst registration certificate"},
    "iso certificate": {"iso", "iso certificate", "iso certification"},
    "turnover certificate": {"turnover certificate", "ca turnover certificate", "chartered accountant turnover certificate"},
    "experience certificate": {"experience certificate", "work completion certificate", "completion certificate"},
    "audited financial statements": {"audited financial statements", "audited accounts", "financial statements"},
    "oem authorization": {"oem authorization", "manufacturer authorization", "authorized dealer letter"},
    "emd receipt": {"emd receipt", "earnest money deposit receipt", "emd proof"},
    "technical bid": {"technical bid", "technical proposal"},
    "financial bid": {"financial bid", "price bid", "commercial bid"},
    "company registration certificate": {"company registration certificate", "incorporation certificate", "registration certificate"},
    "udyam certificate": {"udyam certificate", "msme certificate", "udyam registration"},
}


def normalize_document_name(value: str) -> str:
    value = re.sub(r"[_\-]+", " ", str(value).lower())
    value = re.sub(r"\.(pdf|docx?|png|jpe?g)$", "", value)
    return " ".join(re.findall(r"[a-z0-9]+", value))


class ComplianceAgent:
    """Compare the extracted tender checklist against a company's document inventory."""

    def evaluate(
        self,
        required_documents: list[str],
        company: CompanyProfile | dict[str, Any],
    ) -> dict[str, Any]:
        company = company if isinstance(company, CompanyProfile) else CompanyProfile.from_dict(company)
        available = company.available_documents
        available_norm = [normalize_document_name(x) for x in available]

        checklist = []
        for required in required_documents:
            req_norm = normalize_document_name(required)
            alias_set = ALIASES.get(req_norm, {req_norm})
            normalized_aliases = {normalize_document_name(x) for x in alias_set}
            matched = [
                original for original, norm in zip(available, available_norm)
                if norm in normalized_aliases
                or any(alias in norm or norm in alias for alias in normalized_aliases if alias and norm)
            ]
            status = "AVAILABLE" if matched else "MISSING"
            checklist.append({
                "required_document": required,
                "status": status,
                "matched_company_documents": matched,
                "action": "Verify document validity and expiry." if matched else "Obtain or upload this document before bid submission.",
            })

        available_count = sum(item["status"] == "AVAILABLE" for item in checklist)
        total = len(checklist)
        score = round(available_count / total * 100, 1) if total else None
        return {
            "company_name": company.company_name,
            "required_document_count": total,
            "available_count": available_count,
            "missing_count": total - available_count,
            "document_readiness_score": score,
            "checklist": checklist,
            "disclaimer": "A filename match does not verify authenticity, validity, expiry, or tender-specific acceptability.",
        }


if __name__ == "__main__":
    import json
    profile = {
        "company_name": "Demo IT Solutions",
        "available_documents": ["PAN.pdf", "GST Registration Certificate.pdf", "ISO Certificate.pdf"],
    }
    required = ["PAN card", "GST certificate", "ISO certificate", "OEM authorization"]
    print(json.dumps(ComplianceAgent().evaluate(required, profile), indent=2))
