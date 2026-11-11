from datetime import date
from typing import Dict, List, Optional

CLAIMS: List[Dict[str, object]] = [
    {
        "claim_id": "CLM-1001",
        "claim_type": "home",
        "description": "Severe storm damage to roof and living room ceiling after hailstorm.",
        "estimated_loss": 18500,
        "documents": [
            "policy_document",
            "photos",
            "repair_estimate",
            "incident_report"
        ],
        "policy_active": True,
        "previous_claims": 1,
        "incident_date": "2026-10-12",
        "reported_date": "2026-10-13",
        "claim_status": "open",
        "severity": "HIGH"
    },
    {
        "claim_id": "CLM-1002",
        "claim_type": "motor",
        "description": "Rear-end collision with moderate body damage and a damaged headlight.",
        "estimated_loss": 4200,
        "documents": [
            "policy_document",
            "photos"
        ],
        "policy_active": True,
        "previous_claims": 0,
        "incident_date": "2026-10-08",
        "reported_date": "2026-10-09",
        "claim_status": "open",
        "severity": "MEDIUM"
    },
    {
        "claim_id": "CLM-1003",
        "claim_type": "home",
        "description": "Water leak from kitchen pipe causing minor ceiling staining.",
        "estimated_loss": 1200,
        "documents": [
            "policy_document",
            "photos",
            "repair_estimate"
        ],
        "policy_active": True,
        "previous_claims": 0,
        "incident_date": "2026-09-20",
        "reported_date": "2026-09-21",
        "claim_status": "open",
        "severity": "LOW"
    },
    {
        "claim_id": "CLM-1004",
        "claim_type": "motor",
        "description": "Vehicle theft reported from residential car park with no witness statement.",
        "estimated_loss": 26000,
        "documents": [
            "policy_document",
            "police_report"
        ],
        "policy_active": True,
        "previous_claims": 2,
        "incident_date": "2026-10-15",
        "reported_date": "2026-10-16",
        "claim_status": "investigation",
        "severity": "HIGH"
    },
    {
        "claim_id": "CLM-1005",
        "claim_type": "home",
        "description": "Fire alarm activation with smoke and soot damage in a two-bedroom property.",
        "estimated_loss": 9600,
        "documents": [
            "policy_document",
            "fire_service_report",
            "photos"
        ],
        "policy_active": True,
        "previous_claims": 3,
        "incident_date": "2026-10-17",
        "reported_date": "2026-10-18",
        "claim_status": "review",
        "severity": "HIGH"
    },
    {
        "claim_id": "CLM-1006",
        "claim_type": "motor",
        "description": "Minor scrape on front bumper after parking incident in supermarket lot.",
        "estimated_loss": 850,
        "documents": [
            "policy_document",
            "photos",
            "repair_estimate"
        ],
        "policy_active": True,
        "previous_claims": 0,
        "incident_date": "2026-10-18",
        "reported_date": "2026-10-19",
        "claim_status": "open",
        "severity": "LOW"
    }
]


def get_claim(claim_id: str) -> Optional[Dict[str, object]]:
    """Return a single synthetic claim by claim_id."""
    for claim in CLAIMS:
        if claim["claim_id"] == claim_id:
            return dict(claim)
    return None


def list_claims(claim_type: Optional[str] = None) -> List[Dict[str, object]]:
    """Return all synthetic claims, optionally filtered by type."""
    results = CLAIMS
    if claim_type:
        results = [claim for claim in CLAIMS if claim["claim_type"] == claim_type]
    return [dict(claim) for claim in results]


def claim_exists(claim_id: str) -> bool:
    """Check whether a claim ID is present in the dataset."""
    return get_claim(claim_id) is not None
