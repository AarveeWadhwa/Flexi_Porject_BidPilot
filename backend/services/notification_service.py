
"""Format deadline/corrigendum alerts. Delivery integrations can be added later."""
from __future__ import annotations
from typing import Any


def format_tender_alert(change_result: dict[str, Any]) -> str | None:
    if not change_result.get("has_changes"):
        return None
    tender_id = change_result.get("tender_id", "Unknown tender")
    lines = [f"BidPilot alert — {tender_id}"]
    lines.extend(f"- {message}" for message in change_result.get("alert_messages", []))
    lines.append("Action: review the official tender notice/corrigendum before relying on this update.")
    return "\n".join(lines)
