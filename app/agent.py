from typing import Any, Dict, List

from opentelemetry.trace import Status, StatusCode

from app.data.claims import get_claim
from app.handoff import create_human_handoff
from app.models import TriageOutput
from app.safety import validate_safety
from app.tools.history import check_claim_history
from app.tools.policy import check_policy_coverage
from app.tracing import current_trace_id, tracer


REQUIRED_DOCUMENTS = {
    "home": ["policy_document", "photos", "repair_estimate"],
    "motor": ["policy_document", "photos", "repair_estimate"],
}


def triage_claim(claim_id: str) -> Dict[str, Any]:
    """Assess a synthetic claim and record a trace for each workflow stage.

    This rule-based training baseline is not a production decision system.
    It never makes a final claim, payment, or fraud determination.
    """
    with tracer.start_as_current_span("claim_triage") as root_span:
        root_span.set_attribute("claim.id", claim_id)
        root_span.set_attribute("app.workflow", "insurance_claim_triage")
        root_span.set_attribute("app.prompt_version", "rules-v1")
        root_span.set_attribute("app.model_version", "not-used-rule-based-baseline")

        try:
            with tracer.start_as_current_span("claim_intake") as intake_span:
                claim = get_claim(claim_id)
                if claim is None:
                    intake_span.set_attribute("claim.intake.success", False)
                    raise ValueError(f"Claim {claim_id} not found in synthetic dataset.")
                claim_type = str(claim["claim_type"])
                intake_span.set_attribute("claim.intake.success", True)
                intake_span.set_attribute("claim.type", claim_type)
                root_span.set_attribute("claim.type", claim_type)

            with tracer.start_as_current_span("check_policy_coverage") as policy_span:
                policy = check_policy_coverage(claim_id)
                policy_span.set_attribute("tool.success", policy["success"])
                policy_span.set_attribute("tool.latency_ms", policy["latency_ms"])
                policy_span.set_attribute("coverage.category", policy["coverage_category"])

            with tracer.start_as_current_span("check_claim_history") as history_span:
                history = check_claim_history(claim_id)
                history_span.set_attribute("tool.success", history["success"])
                history_span.set_attribute("tool.latency_ms", history["latency_ms"])
                history_span.set_attribute("claim_history.previous_claims", history["previous_claims"])
                history_span.set_attribute(
                    "claim_history.completeness", history["history_completeness"]
                )

            with tracer.start_as_current_span("triage_assessment") as assessment_span:
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
                assessment_span.set_attribute("triage.urgency", urgency)
                assessment_span.set_attribute("fraud.flag", fraud_flag)
                assessment_span.set_attribute("missing_document_count", len(missing_documents))

            output = TriageOutput.model_validate(
                {
                    "claim_id": claim_id,
                    "claim_type": claim_type,
                    "urgency": urgency,
                    "missing_documents": missing_documents,
                    "fraud_flag": fraud_flag,
                    "fraud_rationale": fraud_rationale,
                    # Human review is mandatory for every claim in this training system.
                    "human_review_required": True,
                }
            )

            with tracer.start_as_current_span("safety_validation") as safety_span:
                safe_output = validate_safety(output.model_dump())
                safety_span.set_attribute("validation.success", True)

            with tracer.start_as_current_span("human_handoff") as handoff_span:
                handoff = create_human_handoff(
                    claim_id=claim_id,
                    urgency=urgency,
                    missing_documents=missing_documents,
                    fraud_flag=fraud_flag,
                    fraud_rationale=fraud_rationale,
                    trace_id=current_trace_id(),
                )
                handoff_span.set_attribute("handoff.success", True)
                handoff_span.set_attribute("human_review_required", True)

            root_span.set_attribute("triage.urgency", urgency)
            root_span.set_attribute("fraud.flag", fraud_flag)
            root_span.set_attribute("missing_document_count", len(missing_documents))
            root_span.set_attribute("human_review_required", True)
            root_span.set_attribute("validation.success", True)
            root_span.set_attribute("handoff.success", True)
            root_span.set_status(Status(StatusCode.OK))

            return {
                **safe_output,
                "human_handoff": handoff,
                "tool_results": {
                    "policy_coverage": policy,
                    "claim_history": history,
                },
            }
        except Exception as exc:
            root_span.record_exception(exc)
            root_span.set_status(Status(StatusCode.ERROR, "triage failed"))
            raise
