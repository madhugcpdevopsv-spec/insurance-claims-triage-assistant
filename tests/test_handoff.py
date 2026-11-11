import unittest

from app.handoff import HUMAN_HANDOFF_QUEUE, create_human_handoff


class HumanHandoffTests(unittest.TestCase):
    def setUp(self):
        HUMAN_HANDOFF_QUEUE.clear()

    def test_high_urgency_claim_creates_handoff(self):
        handoff = create_human_handoff(
            claim_id="CLM-1001",
            urgency="HIGH",
            missing_documents=[],
            fraud_flag=False,
            fraud_rationale="High urgency requires human review.",
        )
        self.assertTrue(handoff["review_required"])
        self.assertEqual(len(HUMAN_HANDOFF_QUEUE), 1)
        self.assertEqual(HUMAN_HANDOFF_QUEUE[0]["claim_id"], "CLM-1001")

    def test_fraud_flagged_claim_creates_handoff(self):
        handoff = create_human_handoff(
            claim_id="CLM-1004",
            urgency="MEDIUM",
            missing_documents=[],
            fraud_flag=True,
            fraud_rationale="Historical signals require review.",
        )
        self.assertTrue(handoff["fraud_flag"])
        self.assertTrue(handoff["review_required"])
        self.assertEqual(handoff["status"], "queued")

    def test_low_risk_claim_still_generates_review_task(self):
        handoff = create_human_handoff(
            claim_id="CLM-1006",
            urgency="LOW",
            missing_documents=[],
            fraud_flag=False,
            fraud_rationale="No elevated indicators detected.",
        )
        self.assertTrue(handoff["review_required"])
        self.assertEqual(handoff["status"], "queued")


if __name__ == "__main__":
    unittest.main()
