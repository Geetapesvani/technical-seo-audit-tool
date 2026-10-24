import unittest
from seo_audit.audit import audit, check_row


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.base = {
            "url": "https://example.com/service",
            "status_code": "200",
            "title": "Professional Technical SEO Auditing Services Online",
            "meta_description": "A" * 125,
            "h1": "Technical SEO Auditing",
            "canonical": "https://example.com/service",
            "indexability": "Indexable",
        }

    def test_clean_row(self):
        self.assertEqual(check_row(self.base), [])

    def test_missing_title_and_h1(self):
        row = {**self.base, "title": "", "h1": ""}
        names = [issue[0] for issue in check_row(row)]
        self.assertIn("Missing title", names)
        self.assertIn("Missing H1", names)

    def test_duplicate_titles(self):
        duplicate = {**self.base, "url": "https://example.com/second"}
        results = audit([self.base, duplicate])
        self.assertEqual(sum(item["issue"] == "Duplicate title" for item in results), 2)

    def test_invalid_status(self):
        row = {**self.base, "status_code": "unknown"}
        self.assertIn("Invalid status code", [i[0] for i in check_row(row)])

    def test_noindex_review(self):
        row = {**self.base, "indexability": "noindex"}
        self.assertIn("Page marked non-indexable", [i[0] for i in check_row(row)])


if __name__ == "__main__":
    unittest.main()
