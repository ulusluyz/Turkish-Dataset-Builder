import unittest
from dataset_cleaner.quality.language import detect_turkish_language
from dataset_cleaner.quality.spam import check_spam_and_junk
from dataset_cleaner.quality.quality_score import compute_quality_score

class TestQuality(unittest.TestCase):
    def test_turkish_language_detection(self):
        tr_native = "Türkiye'nin başkenti Ankara'dır ve oldukça güzel bir şehirdir."
        score, code = detect_turkish_language(tr_native)
        self.assertEqual(code, "tr")
        self.assertGreaterEqual(score, 0.7)

        tr_ascii = "Bugun hava cok guzel, disari cikip gezmek istiyorum."
        score_ascii, code_ascii = detect_turkish_language(tr_ascii)
        self.assertEqual(code_ascii, "tr_ascii")

    def test_spam_detection(self):
        spam_text = "aaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        is_spam, reason = check_spam_and_junk(spam_text)
        self.assertTrue(is_spam)
        self.assertEqual(reason, "REPEATED_CHARACTERS")

    def test_quality_score(self):
        good_text = "Elektrik enerjisi, elektrik yüklerinin hareketinden kaynaklanan bir enerji türüdür."
        score, metrics = compute_quality_score(good_text)
        self.assertGreaterEqual(score, 60.0)
        self.assertFalse(metrics["is_spam"])

if __name__ == "__main__":
    unittest.main()
