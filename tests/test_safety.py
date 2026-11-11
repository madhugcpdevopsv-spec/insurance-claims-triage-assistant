import unittest

from app.safety import SAFETY_EVENTS, SafetyViolation, validate_safety


class SafetyValidationTests(unittest.TestCase):
    def setUp(self):
        SAFETY_EVENTS.clear()

    def test_safe_triage_output_is_accepted(self):
        output = {
            "claim_id": "CLM-1001",
            "urgency": "HIGH",
            "fraud_rationale": "Requires additional human investigation.",
        }
        self.assertEqual(validate_safety(output), output)
        self.assertEqual(SAFETY_EVENTS, [])

    def test_prohibited_action_is_rejected_and_event_recorded(self):
        output = {
            "claim_id": "CLM-1001",
            "urgency": "HIGH",
            "recommendation": "Approve payment for this claim.",
        }
        with self.assertRaises(SafetyViolation) as raised:
            validate_safety(output)

        self.assertEqual(raised.exception.event["claim_id"], "CLM-1001")
        self.assertIn("approve", raised.exception.event["detected_actions"])
        self.assertIn("pay", raised.exception.event["detected_actions"])
        self.assertTrue(raised.exception.event["human_review_required"])
        self.assertEqual(len(SAFETY_EVENTS), 1)
        self.assertNotIn("recommendation", SAFETY_EVENTS[0])

    def test_deny_and_reject_payment_are_rejected(self):
        for instruction in ("Deny the claim", "Reject payment"):
            with self.subTest(instruction=instruction):
                with self.assertRaises(SafetyViolation):
                    validate_safety({"claim_id": "CLM-1002", "action": instruction})


if __name__ == "__main__":
    unittest.main()
