# -*- coding: utf-8 -*-
"""
Tests for TokenZero Engine, Ontology Layer, Rules Injector, and Kernel
"""

import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tokenzero import process_task, validate_action, OntologyViolation, inject_rules

class TestTokenZeroKernel(unittest.TestCase):
    def test_arithmetic_discount(self):
        res = process_task("15000円の15%引き")
        self.assertEqual(res["tier"], "Tier 0 (Formula-First)")
        self.assertEqual(res["result"], 12750)

    def test_arithmetic_tax(self):
        res = process_task("3000円の税込")
        self.assertEqual(res["tier"], "Tier 0 (Formula-First)")
        self.assertEqual(res["result"], 3300)

    def test_datetime_diff(self):
        res = process_task("2026-10-01から2026-10-10までの日数")
        self.assertEqual(res["tier"], "Tier 0 (Formula-First)")
        self.assertEqual(res["result"], 9)

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

class TestTokenZeroRules(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_inject_rules_all(self):
        results = inject_rules(self.test_dir, ["all"])
        self.assertTrue((self.test_dir / ".cursorrules").exists())
        self.assertTrue((self.test_dir / ".cursor/rules/tokenzero.mdc").exists())
        self.assertTrue((self.test_dir / ".windsurfrules").exists())
        self.assertTrue((self.test_dir / ".clinerules").exists())
        self.assertTrue((self.test_dir / "CLAUDE.md").exists())
        self.assertTrue((self.test_dir / "AGENTS.md").exists())

if __name__ == "__main__":
    unittest.main()
