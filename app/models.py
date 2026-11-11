from pydantic import BaseModel, Field, field_validator


class TriageOutput(BaseModel):
    """Structured schema for triage output.

    Enforces controlled values and rejects invalid output before it is used.
    """
    claim_id: str = Field(..., min_length=1)
    claim_type: str = Field(..., min_length=1)
    urgency: str = Field(...)
    missing_documents: list[str] = Field(default_factory=list)
    fraud_flag: bool
    fraud_rationale: str = Field(..., min_length=1)
    human_review_required: bool

    @field_validator("claim_type")
    @classmethod
    def validate_claim_type(cls, value: str) -> str:
        allowed = {"home", "motor"}
        if value not in allowed:
            raise ValueError(f"claim_type must be one of {sorted(allowed)}")
        return value

    @field_validator("urgency")
    @classmethod
    def validate_urgency(cls, value: str) -> str:
        allowed = {"LOW", "MEDIUM", "HIGH"}
        normalized = value.upper()
        if normalized not in allowed:
            raise ValueError(f"urgency must be one of {sorted(allowed)}")
        return normalized

    @field_validator("missing_documents")
    @classmethod
    def validate_missing_documents(cls, value: list[str]) -> list[str]:
        return sorted(set(value))

    @field_validator("fraud_rationale")
    @classmethod
    def validate_fraud_rationale(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("fraud_rationale cannot be empty")
        return value
