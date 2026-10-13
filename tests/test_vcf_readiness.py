import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from vcf_readiness import assess_change, build_report, load_inventory

class ReadinessTests(unittest.TestCase):
    def test_missing_owner_or_rollback_is_blocked(self):
        self.assertEqual(assess_change({"owner": "", "rollback_plan": ""})["status"], "BLOCKED")
    def test_pending_approval_needs_review(self):
        change = {k:"recorded" for k in ("owner","maintenance_window","backup_evidence","health_check_evidence","compatibility_reference","rollback_plan")}
        change["change_approval"] = "Pending"
        self.assertEqual(assess_change(change)["status"], "REVIEW")
    def test_approved_complete_checklist(self):
        change = {k:"recorded" for k in ("owner","maintenance_window","backup_evidence","health_check_evidence","compatibility_reference","rollback_plan","change_approval")}
        change["change_approval"] = "Approved"
        self.assertEqual(assess_change(change)["status"], "READY")
    def test_sample_report_labels_synthetic_scope(self):
        root = Path(__file__).resolve().parents[1]
        report = build_report(load_inventory(root / "data/sample_environment.json"))
        self.assertIn("Synthetic portfolio lab", report)
        self.assertIn("BLOCKED", report)

if __name__ == "__main__":
    unittest.main()
