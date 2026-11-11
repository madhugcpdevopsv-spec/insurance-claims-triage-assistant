"""Safety boundary for triage outputs.

This module rejects prohibited final-decision language. Safety events contain
only metadata and action categories, never the output text itself.
"""

from datetime import datetime, timezone
import re
from threading import Lock
from typing import Any, Dict, Mapping


_PROHIBITED_ACTION_PATTERNS = {
    "approve": re.compile(r"\bapprove(?:s|d|ing)?\b", re.IGNORECASE),
    "deny": re.compile(r"\bdeny(?:s|ing)?|denied\b", re.IGNORECASE),
    "pay": re.compile(r"\bpay(?:s|ing)?|paid\b", re.IGNORECASE),
    "reject_payment": re.compile(
        r"\breject(?:s|ed|ing)?\s+(?:the\s+)?payment\b", re.IGNORECASE
    ),
    "authorize_payment": re.compile(
        r"\bauthori[sz](?:e|es|ed|ing)\s+(?:the\s+)?(?:claim|payment|payout)\b",
        re.IGNORECASE,
    ),
}

# In-memory event store for this training step. Later observability steps can
# export these event records through metrics/traces or a durable event sink.
SAFETY_EVENTS: list[Dict[str, Any]] = []
_EVENTS_LOCK = Lock()


class SafetyViolation(Exception):
    """Raised when triage output attempts a prohibited final action."""

    def __init__(self, event: Dict[str, Any]):
        self.event = event
        super().__init__("Triage output rejected by safety validation.")


def _strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for nested in value.values():
            yield from _strings(nested)
    elif isinstance(value, (list, tuple, set)):
        for nested in value:
            yield from _strings(nested)


def validate_safety(output: Mapping[str, Any]) -> Dict[str, Any]:
    """Accept safe triage output or reject it and record a safety event.

    The validator scans all string values so an unexpected extra field cannot
    smuggle a final approve/deny/payment instruction past the boundary.
    """
    matched_actions = set()
    for text in _strings(output):
        for action, pattern in _PROHIBITED_ACTION_PATTERNS.items():
            if pattern.search(text):
                matched_actions.add(action)

    if matched_actions:
        event = {
            "event_type": "prohibited_action_attempt",
            "claim_id": str(output.get("claim_id", "unknown")),
            "detected_actions": sorted(matched_actions),
            "human_review_required": True,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
        }
        with _EVENTS_LOCK:
            SAFETY_EVENTS.append(event)
        raise SafetyViolation(event)

    return dict(output)
