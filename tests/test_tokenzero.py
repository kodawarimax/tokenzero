# -*- coding: utf-8 -*-
"""
Tests for TokenZero Engine & Ontology Layer
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.ontology import validate_action, OntologyViolation

class TestTokenZeroOntology(unittest.TestCase):
    def test_invoice_discount_valid(self):
        res = validate_action("Invoice", "apply_discount", {"amount": 10000, "discount_rate": 0.20, "client_name": "TestCorp"})
        self.assertEqual(res["status"], "APPROVED")
        self.assertEqual(res["discounted_amount"], 8000.0)

    def test_invoice_discount_exceeded(self):
        with self.assertRaises(OntologyViolation):
            validate_action("Invoice", "apply_discount", {"amount": 10000, "discount_rate": 0.50})

    def test_task_state_transition_valid(self):
        res = validate_action("TaskState", "transition_state", {"task_id": "T-1", "current_status": "DRAFT", "next_status": "REVIEW"})
        self.assertEqual(res["status"], "APPROVED")
        self.assertEqual(res["to_status"], "REVIEW")

    def test_task_state_transition_invalid_jump(self):
        with self.assertRaises(OntologyViolation):
            # DRAFT -> APPROVED への飛び級は禁止
            validate_action("TaskState", "transition_state", {"task_id": "T-1", "current_status": "DRAFT", "next_status": "APPROVED"})

if __name__ == "__main__":
    unittest.main()
