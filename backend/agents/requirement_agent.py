
"""Tender Requirement Extraction Agent using transparent rule-based extraction.

The agent records evidence snippets and warnings. It is a baseline that can later
be enhanced with an LLM/RAG workflow, while keeping human verification mandatory.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from backend.services.document_parser import extract_text


def _first_match(patterns: list[str], text: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip(" .,:;\n")
    return None


def _evidence(text: str, keyword: str, radius: int = 100) -> list[str]:
    snippets = []
    for match in list(re.finditer(re.escape(keyword), text, flags=re.IGNORECASE))[:3]:
        start = max(0, match.start() - radius)
        end = min(len(text), match.end() + radius)
        snippets.append(re.sub(r"\s+", " ", text[start:end]).strip())
    return snippets


class TenderRequirementAgent:
    """Extracts common tender requirements from document text."""

    def extract(self, text: str, tender_id: str | None = None) -> dict[str, Any]:
        if not text or not text.strip():
            raise ValueError("Tender text is empty.")

        turnover = _first_match([
            r"(?:minimum|required)\s+(?:annual\s+)?turnover\s*(?:of|:|is)?\s*(₹?\s?[\d,.]+\s*(?:crore|lakh|lakhs|cr|lac|lacs|million)?(?:\s*(?:INR|rupees))?)",
            r"turnover.{0,50}?(₹\s?[\d,.]+\s*(?:crore|lakh|lakhs|cr|lac|lacs)?)",
        ], text)
        experience = _first_match([
            r"(?:minimum|required)\s+(?:work\s+)?experience\s*(?:of|:|is)?\s*(\d+\s*(?:years?|months?))",
            r"(\d+\s*(?:years?|months?))\s+(?:of\s+)?(?:relevant\s+)?experience",
        ], text)
        deadline = _first_match([
            r"(?:bid\s+submission\s+)?(?:last\s+date|deadline|due\s+date|closing\s+date)\s*(?:for\s+submission)?\s*[:\-]?\s*((?:\d{1,2}[-/ ](?:\d{1,2}|[A-Za-z]{3,9})[-/ ,]*\d{2,4})|(?:\d{4}-\d{2}-\d{2}))",
        ], text)
        emd = _first_match([
            r"(?:earnest\s+money\s+deposit|EMD)\s*(?:of|:|is)?\s*(₹?\s?[\d,]+(?:\.\d{1,2})?)",
        ], text)
        tender_fee = _first_match([
            r"(?:tender\s+fee|tender\s+document\s+fee)\s*(?:of|:|is)?\s*(₹?\s?[\d,]+(?:\.\d{1,2})?)",
        ], text)
        location = _first_match([
            r"(?:delivery|work|service)\s+location\s*[:\-]\s*([^\n.;]{2,80})",
            r"(?:only\s+for|within)\s+([A-Z][A-Za-z ,]{2,50})\s+(?:based|registered|located)\s+(?:companies|bidders|firms)",
        ], text)

        certification_matches = re.findall(
            r"\b(ISO\s*[\- ]?\d{3,5}(?:\s*:\s*\d{4})?|BIS|CMMI|MSME|Udyam|GST registration|OEM authorization)\b",
            text, flags=re.IGNORECASE
        )
        document_candidates = [
            "PAN card", "GST certificate", "GST registration", "audited financial statements",
            "turnover certificate", "experience certificate", "ISO certificate",
            "OEM authorization", "EMD receipt", "technical bid", "financial bid",
            "company registration certificate", "Udyam certificate"
        ]
        documents = [
            name for name in document_candidates
            if re.search(re.escape(name), text, flags=re.IGNORECASE)
        ]

        technical = []
        for line in text.splitlines():
            cleaned = re.sub(r"\s+", " ", line).strip(" •-\t")
            if cleaned and re.search(
                r"\b(specification|technical|capacity|warranty|delivery|compatible|standard|quantity)\b",
                cleaned, flags=re.IGNORECASE
            ):
                technical.append(cleaned[:300])

        financial = []
        if emd:
            financial.append({"type": "EMD", "value": emd})
        if tender_fee:
            financial.append({"type": "Tender fee", "value": tender_fee})

        evidence = {}
        for key, keyword in [
            ("turnover", "turnover"), ("experience", "experience"),
            ("deadline", "deadline"), ("emd", "EMD"),
            ("certifications", "ISO"), ("documents", "certificate")
        ]:
            snippets = _evidence(text, keyword)
            if snippets:
                evidence[key] = snippets

        eligibility = {
            "minimum_turnover": turnover,
            "minimum_experience": experience,
            "location_requirement": location,
            "other_conditions": [],
        }
        deadlines = {"bid_submission_deadline": deadline}
        warnings = [
            "Rule-based extraction may miss requirements or misread context.",
            "Verify every extracted value against the original tender and any corrigenda.",
        ]
        for field, value in [
            ("minimum turnover", turnover), ("minimum experience", experience),
            ("bid submission deadline", deadline)
        ]:
            if not value:
                warnings.append(f"No clear {field} was detected; check the document manually.")

        return {
            "tender_id": tender_id,
            "eligibility": eligibility,
            "technical_requirements": technical,
            "financial_requirements": financial,
            "certifications": sorted({item.upper() for item in certification_matches}),
            "documents_required": documents,
            "deadlines": deadlines,
            "evaluation_criteria": _first_match([
                r"(?:evaluation criteria|evaluation method)\s*[:\-]?\s*([^\n.]{5,200})"
            ], text),
            "evidence": evidence,
            "warnings": warnings,
        }


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m backend.agents.requirement_agent <tender.txt|tender.pdf>")
        raise SystemExit(2)
    path = Path(sys.argv[1])
    text = extract_text(path)
    result = TenderRequirementAgent().extract(text, tender_id=path.stem)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
