from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

HUMAN_HANDOFF_QUEUE: List[Dict[str, Any]] = []


def create_human_handoff(
    claim_id: str,
    urgency: str,
    missing_documents: Optional[List[str]] = None,
    fraud_flag: bool = False,
    fraud_rationale: str = "",
    trace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a simulated human-review task for a validated triage result.

    The task never decides the claim. It creates a queue item for an investigator
    to review the synthetic triage output and make the real insurance decision.
    """
    normalized_urgency = str(urgency or "MEDIUM").upper()
    if normalized_urgency not in {"LOW", "MEDIUM", "HIGH"}:
        raise ValueError(f"Unsupported urgency value: {urgency}")

    required_review = bool(
        normalized_urgency == "HIGH"
        or fraud_flag
        or bool(missing_documents)
        or True
    )

    handoff = {
        "task_id": f"HANDOFF-{uuid4().hex[:8].upper()}",
        "claim_id": claim_id,
        "urgency": normalized_urgency,
        "missing_documents": list(missing_documents or []),
        "fraud_flag": bool(fraud_flag),
        "fraud_rationale": fraud_rationale,
        "trace_id": trace_id or f"TRACE-{uuid4().hex[:12].upper()}",
        "review_required": required_review,
        "status": "queued",
        "reviewer": "human_investigator",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "outcome": "pending",
    }

    HUMAN_HANDOFF_QUEUE.append(handoff)
    return handoff
