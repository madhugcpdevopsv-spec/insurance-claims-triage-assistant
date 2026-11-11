from fastapi import FastAPI, HTTPException

from app.agent import triage_claim
from app.models import TriageOutput

app = FastAPI(
    title="Insurance Claims Triage Assistant",
    version="0.1.0",
    description="Synthetic training API for claims triage assistance.",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "insurance-claims-triage-assistant",
    }


@app.get("/")
def root():
    return {"message": "Insurance Claims Triage Assistant API is running."}


@app.get("/triage", response_model=TriageOutput)
def triage(claim_id: str):
    """Return a validated triage assessment for a synthetic claim.

    This API provides triage assistance only. It never makes a final claim,
    payment, or fraud determination.
    """
    try:
        result = triage_claim(claim_id)
        # Validate before returning; auxiliary tool data is not part of API output.
        return TriageOutput.model_validate(
            {key: value for key, value in result.items() if key != "tool_results"}
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
