import unittest
from dataset_cleaner.cleaning.encoding import fix_mojibake
from dataset_cleaner.cleaning.unicode import normalize_unicode
from dataset_cleaner.cleaning.whitespace import normalize_whitespace, unescape_entities
from dataset_cleaner.cleaning.html_cleaner import clean_html_content
from dataset_cleaner.cleaning.text_cleaner import clean_text_pipeline

class TestCleaning(unittest.TestCase):
    def test_mojibake(self):
        bad_text = "Ã§Ã¶Ã¼ÅŸÄŸÄ±Ã‡Ã–ÃÜ"
        fixed, was_modified = fix_mojibake(bad_text)
        self.assertTrue(was_modified)
        self.assertEqual(fixed, "çöüşğıÇÖÜ")

    def test_html_cleaning(self):
        html_input = "<html><head><script>alert('xss')</script></head><body><p>Merhaba <b>dünya</b>!</p></body></html>"
        cleaned = clean_html_content(html_input)
        self.assertNotIn("<script>", cleaned)
        self.assertNotIn("<p>", cleaned)
        self.assertIn("Merhaba", cleaned)
        self.assertIn("dünya", cleaned)

    def test_whitespace_and_entities(self):
        raw = "Merhaba &amp; Selam!   \n\n\n\n   Nasılsınız?  "
        unescaped = unescape_entities(raw)
        norm = normalize_whitespace(unescaped)
        self.assertEqual(norm, "Merhaba & Selam!\n\nNasılsınız?")

    def test_full_pipeline(self):
        raw = "<p>Ã§ok gÃ¼zel bir gÃ¼n!</p>"
        cleaned, meta = clean_text_pipeline(raw, file_type="html")
        self.assertIn("çok güzel bir gün!", cleaned)

if __name__ == "__main__":
    unittest.main()
