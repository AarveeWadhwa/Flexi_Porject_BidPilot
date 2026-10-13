
"""Typed structures and normalizers for extracted tender requirements."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class TenderRequirements:
    tender_id: str | None = None
    minimum_turnover_inr: float | None = None
    minimum_experience_years: float | None = None
    location_requirement: str | None = None
    certifications: list[str] = field(default_factory=list)
    documents_required: list[str] = field(default_factory=list)
    other_conditions: list[str] = field(default_factory=list)

    @classmethod
    def from_extraction(cls, extraction: dict[str, Any]) -> "TenderRequirements":
        """Convert Member 1's extraction-agent output into this normalized schema."""
        eligibility = extraction.get("eligibility") or {}
        return cls(
            tender_id=extraction.get("tender_id"),
            minimum_turnover_inr=parse_money_inr(eligibility.get("minimum_turnover")),
            minimum_experience_years=parse_years(eligibility.get("minimum_experience")),
            location_requirement=eligibility.get("location_requirement"),
            certifications=[str(x).strip() for x in extraction.get("certifications", []) if str(x).strip()],
            documents_required=[str(x).strip() for x in extraction.get("documents_required", []) if str(x).strip()],
            other_conditions=[str(x).strip() for x in eligibility.get("other_conditions", []) if str(x).strip()],
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def parse_money_inr(value: Any) -> float | None:
    """Convert common extracted strings such as '₹1 crore' to INR, if understood."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).lower().replace(",", "").replace("₹", "").strip()
    import re
    match = re.search(r"(\d+(?:\.\d+)?)\s*(crore|cr|lakh|lakhs|lac|lacs|million)?", text)
    if not match:
        return None
    amount = float(match.group(1))
    unit = match.group(2) or ""
    if unit in {"crore", "cr"}:
        amount *= 10_000_000
    elif unit in {"lakh", "lakhs", "lac", "lacs"}:
        amount *= 100_000
    elif unit == "million":
        amount *= 1_000_000
    return amount


def parse_years(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    import re
    match = re.search(r"(\d+(?:\.\d+)?)\s*(year|years|yr|yrs|month|months)", str(value).lower())
    if not match:
        return None
    number = float(match.group(1))
    return number / 12 if match.group(2).startswith("month") else number
