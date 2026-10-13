
"""Deadline and corrigendum agent: detects changes between tender snapshots."""
from __future__ import annotations
from datetime import datetime
from typing import Any


DATE_FORMATS = (
    "%Y-%m-%d", "%d-%b-%Y", "%d-%B-%Y", "%d/%m/%Y", "%d-%m-%Y",
    "%d %b %Y", "%d %B %Y", "%m/%d/%Y",
)


def normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    value = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return None


class DeadlineCorrigendumAgent:
    """Compares old and new tender records and reports meaningful changes."""

    TRACKED_FIELDS = {
        "deadline": "Bid submission deadline",
        "estimated_value": "Estimated tender value",
        "title": "Tender title",
        "status": "Tender status",
        "corrigendum_id": "Corrigendum reference",
        "source_url": "Tender source URL",
    }

    def compare(self, previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
        changes = []
        for field, label in self.TRACKED_FIELDS.items():
            old_value = previous.get(field)
            new_value = current.get(field)
            if field == "deadline":
                old_norm = normalize_date(old_value)
                new_norm = normalize_date(new_value)
                changed = old_norm != new_norm and (old_norm is not None or new_norm is not None)
                if changed:
                    changes.append({
                        "field": field, "label": label,
                        "old_value": old_value, "new_value": new_value,
                        "message": f"Deadline changed from {old_value or 'not listed'} to {new_value or 'not listed'}.",
                    })
            elif old_value != new_value and (old_value is not None or new_value is not None):
                changes.append({
                    "field": field, "label": label,
                    "old_value": old_value, "new_value": new_value,
                    "message": f"{label} changed from {old_value or 'not listed'} to {new_value or 'not listed'}.",
                })

        return {
            "tender_id": current.get("tender_id") or previous.get("tender_id"),
            "has_changes": bool(changes),
            "changes": changes,
            "alert_messages": [change["message"] for change in changes],
            "human_review_required": bool(changes),
        }


if __name__ == "__main__":
    import json
    old = {"tender_id": "BP-2026-001", "deadline": "2026-11-05", "corrigendum_id": None}
    new = {"tender_id": "BP-2026-001", "deadline": "2026-11-12", "corrigendum_id": "Corrigendum-02"}
    print(json.dumps(DeadlineCorrigendumAgent().compare(old, new), indent=2))
