from time import perf_counter
from typing import Any, Dict, Optional

from app.data.claims import get_claim


def check_policy_coverage(claim_id: str) -> Dict[str, Any]:
    """Check synthetic policy coverage for a claim.

    The function is deterministic and backed by synthetic data only.
    It returns coverage status, category, latency, and any errors.
    """
    started = perf_counter()

    try:
        claim = get_claim(claim_id)
        if claim is None:
            raise ValueError(f"Claim {claim_id} not found in synthetic dataset.")

        claim_type = claim.get("claim_type")
        if claim_type not in {"home", "motor"}:
            raise ValueError(f"Unsupported claim type for claim {claim_id}: {claim_type}")

        policy_active = bool(claim.get("policy_active", False))
        estimate = float(claim.get("estimated_loss", 0) or 0)

        if not policy_active:
            coverage_result = "inactive_policy"
            coverage_category = f"{claim_type}_policy_inactive"
        elif claim_type == "home" and estimate > 15000:
            coverage_result = "covered_high_value_review"
            coverage_category = "home_high_value"
        elif claim_type == "motor" and estimate > 10000:
            coverage_result = "covered_elevated_review"
            coverage_category = "motor_high_value"
        else:
            coverage_result = "covered"
            coverage_category = f"{claim_type}_standard"

        return {
            "claim_id": claim_id,
            "success": True,
            "coverage_result": coverage_result,
            "coverage_category": coverage_category,
            "latency_ms": round((perf_counter() - started) * 1000, 2),
            "errors": [],
        }

    except Exception as exc:  # pragma: no cover - intentionally broad for safety validation
        return {
            "claim_id": claim_id,
            "success": False,
            "coverage_result": "unknown",
            "coverage_category": "error",
            "latency_ms": round((perf_counter() - started) * 1000, 2),
            "errors": [str(exc)],
        }
