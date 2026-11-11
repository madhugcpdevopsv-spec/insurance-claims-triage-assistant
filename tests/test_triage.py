import unittest

from pydantic import ValidationError

from app.agent import triage_claim
from app.models import TriageOutput


class TriageWorkflowTests(unittest.TestCase):
    def test_normal_low_urgency_claim(self):
        result = triage_claim("CLM-1003")
        self.assertEqual(result["urgency"], "LOW")
        self.assertEqual(result["missing_documents"], [])
        self.assertIsInstance(TriageOutput.model_validate(result), TriageOutput)

    def test_urgent_claim_requires_human_review(self):
        result = triage_claim("CLM-1001")
        self.assertEqual(result["urgency"], "HIGH")
        self.assertTrue(result["human_review_required"])
        self.assertEqual(result["missing_documents"], [])

    def test_incomplete_claim_identifies_missing_document(self):
        result = triage_claim("CLM-1002")
        self.assertEqual(result["missing_documents"], ["repair_estimate"])
        self.assertTrue(result["human_review_required"])

    def test_invalid_claim_id_is_rejected(self):
        with self.assertRaises(ValueError):
            triage_claim("CLM-9999")

    def test_invalid_urgency_is_rejected_by_schema(self):
        invalid = {
            "claim_id": "CLM-1001",
            "claim_type": "home",
            "urgency": "URGENT",
            "missing_documents": [],
            "fraud_flag": False,
            "fraud_rationale": "Synthetic test rationale.",
            "human_review_required": True,
        }
        with self.assertRaises(ValidationError):
            TriageOutput.model_validate(invalid)


if __name__ == "__main__":
    unittest.main()
