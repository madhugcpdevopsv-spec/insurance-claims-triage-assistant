from time import perf_counter
from typing import Any, Dict, List, Optional

from app.data.claims import get_claim


def check_claim_history(claim_id: str) -> Dict[str, Any]:
    """Check synthetic claim history for a claim.

    Returns previous claims count, completeness, success/failure,
    latency, and any errors.
    """
    started = perf_counter()

    try:
        claim = get_claim(claim_id)
        if claim is None:
            raise ValueError(f"Claim {claim_id} not found in synthetic dataset.")

        previous_claims = int(claim.get("previous_claims", 0) or 0)
        history_completeness = "complete" if previous_claims > 0 else "incomplete"

        if claim.get("claim_type") == "motor" and previous_claims >= 2:
            history_completeness = "complete"

        result = {
            "claim_id": claim_id,
            "success": True,
            "previous_claims": previous_claims,
            "history_completeness": history_completeness,
            "latency_ms": round((perf_counter() - started) * 1000, 2),
            "errors": [],
        }
        return result

    except Exception as exc:  # pragma: no cover - intentionally broad for safety validation
        return {
            "claim_id": claim_id,
            "success": False,
            "previous_claims": 0,
            "history_completeness": "unknown",
            "latency_ms": round((perf_counter() - started) * 1000, 2),
            "errors": [str(exc)],
        }
