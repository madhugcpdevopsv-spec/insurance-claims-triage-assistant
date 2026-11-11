from typing import Any, Dict, List

from app.data.claims import get_claim
from app.tools.history import check_claim_history
from app.tools.policy import check_policy_coverage


REQUIRED_DOCUMENTS = {
    "home": ["policy_document", "photos", "repair_estimate"],
    "motor": ["policy_document", "photos", "repair_estimate"],
}


def triage_claim(claim_id: str) -> Dict[str, Any]:
    """Produce a basic, deterministic triage assessment for a synthetic claim.

    This is an offline training baseline, not a production decision system.
    It uses the two synthetic tools and simple rules so orchestration can be
    exercised before model integration and strict schema validation are added.
    It never approves, denies, or authorizes payment for a claim.
    """
    claim = get_claim(claim_id)
    if claim is None:
        raise ValueError(f"Claim {claim_id} not found in synthetic dataset.")

    # Both required tools are called for each known claim.
    policy = check_policy_coverage(claim_id)
    history = check_claim_history(claim_id)

    claim_type = str(claim["claim_type"])
    documents = set(claim.get("documents", []))
    missing_documents: List[str] = [
        document
        for document in REQUIRED_DOCUMENTS[claim_type]
        if document not in documents
    ]

    urgency = str(claim.get("severity", "MEDIUM")).upper()
    if urgency not in {"LOW", "MEDIUM", "HIGH"}:
        urgency = "MEDIUM"

    previous_claims = history.get("previous_claims", 0)
    fraud_flag = bool(
        history.get("success")
        and (
            previous_claims >= 3
            or (
                previous_claims >= 2
                and claim.get("claim_status") in {"review", "investigation"}
            )
        )
    )
    fraud_rationale = (
        "Synthetic claim-history indicators warrant additional human investigation."
        if fraud_flag
        else "No elevated synthetic claim-history indicator identified; this is not a fraud determination."
    )

    # A failed tool lookup must not reduce the need for human attention.
    human_review_required = bool(
        urgency == "HIGH"
        or fraud_flag
        or missing_documents
        or not policy.get("success")
        or not history.get("success")
    )

    return {
        "claim_id": claim_id,
        "claim_type": claim_type,
        "urgency": urgency,
        "missing_documents": missing_documents,
        "fraud_flag": fraud_flag,
        "fraud_rationale": fraud_rationale,
        "human_review_required": human_review_required,
        "tool_results": {
            "policy_coverage": policy,
            "claim_history": history,
        },
    }
