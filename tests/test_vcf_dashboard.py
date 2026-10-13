import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcf_dashboard import build_markdown, load_checklist, summarize

class DashboardTests(unittest.TestCase):
    def load_sample(self):
        return load_checklist(ROOT / "docs/vcf9-readiness-checklist.csv", ROOT / "data/checklist_status.csv")

    def test_sample_has_no_go_for_missing_blocking_evidence(self):
        summary = summarize(self.load_sample())
        self.assertEqual(summary["decision"], "NO-GO")
        self.assertGreater(len(summary["blockers"]), 0)

    def test_go_requires_all_evidence_or_justified_na(self):
        rows = [
            {"status": "Complete", "evidence_reference": "REF-1", "blocking": True, "completion_notes": ""},
            {"status": "Not Applicable", "evidence_reference": "", "blocking": False, "completion_notes": "Not in scope"},
        ]
        self.assertEqual(summarize(rows)["decision"], "GO")

    def test_in_progress_without_blockers_is_review(self):
        rows = [{"status": "In Progress", "evidence_reference": "REF-1", "blocking": False, "completion_notes": ""}]
        self.assertEqual(summarize(rows)["decision"], "REVIEW")

    def test_markdown_discloses_scope(self):
        rows = self.load_sample()
        report = build_markdown(rows, summarize(rows))
        self.assertIn("does not validate live VCF health", report)
        self.assertIn("NO-GO", report)

    def test_unknown_status_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "status.csv"
            p.write_text("check_id,status,evidence_reference,completion_notes\nUNKNOWN,Complete,REF,Test\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown check_id"):
                load_checklist(ROOT / "docs/vcf9-readiness-checklist.csv", p)

    def test_expanded_checklist_includes_explicit_operational_controls(self):
        rows = self.load_sample()
        ids = {row["check_id"] for row in rows}
        self.assertGreaterEqual(len(rows), 20)
        self.assertTrue({"CHG-002", "BACKUP-002", "CAP-002", "HEALTH-002", "CHG-003"}.issubset(ids))

    def test_conceptual_architecture_diagram_exists_and_discloses_scope(self):
        diagram = ROOT / "docs/images/vcf-conceptual-architecture.svg"
        self.assertTrue(diagram.is_file())
        content = diagram.read_text(encoding="utf-8")
        self.assertIn("Conceptual Architecture", content)
        self.assertIn("no live integration", content)

if __name__ == "__main__":
    unittest.main()
