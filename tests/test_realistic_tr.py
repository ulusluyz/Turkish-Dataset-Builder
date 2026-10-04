import os
import json
import unittest
import tempfile
from dataset_cleaner.pipeline import ProcessingPipeline

class TestRealisticTurkishCorpus(unittest.TestCase):
    def test_realistic_tr_corpus_pipeline(self):
        with tempfile.TemporaryDirectory() as raw_dir, tempfile.TemporaryDirectory() as out_dir:
            # 1. Clean TR text
            with open(os.path.join(raw_dir, "clean_tr.txt"), "w", encoding="utf-8") as f:
                f.write("Türkiye'nin başkenti Ankara'dır. Ankara, İç Anadolu Bölgesi'nde yer alır ve tarihi zengindir. " * 3)

            # 2. ASCII TR text
            with open(os.path.join(raw_dir, "ascii_tr.txt"), "w", encoding="utf-8") as f:
                f.write("Bugun hava cok guzel, disari cikip biraz yürümek ve temiz hava almak istiyorum. " * 3)

            # 3. Mojibake text
            with open(os.path.join(raw_dir, "mojibake.txt"), "w", encoding="utf-8") as f:
                f.write("Ã§ok gÃ¼zel bir gÃ¼n! ÄŸÃ¼venli bir ÅŸekilde temizleme yapÄ±lmalÄ±dÄ±r. " * 3)

            # 4. HTML text
            with open(os.path.join(raw_dir, "web_article.html"), "w", encoding="utf-8") as f:
                f.write("<html><head><script>alert('test')</script></head><body><h1>Başlık</h1><p>Elektrik enerjisi yüklerin hareketinden oluşur. </p><footer>Copyright 2024</footer></body></html>")

            # 5. Markdown with code
            with open(os.path.join(raw_dir, "doc.md"), "w", encoding="utf-8") as f:
                f.write("# Python Eğitimi\n\nPython dilinde döngüler `for` ve `while` ile yazılır. " * 3)

            # 6. JSON / JSONL
            with open(os.path.join(raw_dir, "qa.jsonl"), "w", encoding="utf-8") as f:
                f.write(json.dumps({"question": "Yapay zeka nedir?", "answer": "Yapay zeka, makinelerin insan zekasını taklit etmesidir. " * 3}) + "\n")

            # 7. Exact duplicate of clean_tr
            with open(os.path.join(raw_dir, "clean_tr_dup.txt"), "w", encoding="utf-8") as f:
                f.write("  Türkiye'nin başkenti Ankara'dır. Ankara, İç Anadolu Bölgesi'nde yer alır ve tarihi zengindir.   " * 3)

            # 8. Near duplicate of clean_tr
            with open(os.path.join(raw_dir, "clean_tr_near.txt"), "w", encoding="utf-8") as f:
                f.write("Türkiye'nin başkenti Ankara ilidir. Ankara, İç Anadolu Bölgesi'nde yer almaktadır ve tarihi zengindir. " * 3)

            # 9. Spam & keyboard mash
            with open(os.path.join(raw_dir, "spam.txt"), "w", encoding="utf-8") as f:
                f.write("asdfghjklşlkjhgfdsa\naaaaaaaaaaaaaaaaaaaaaaaaaa\nBahis oyna casino bonus kazan!")

            # 10. Non-TR text
            with open(os.path.join(raw_dir, "english.txt"), "w", encoding="utf-8") as f:
                f.write("The quick brown fox jumps over the lazy dog. Machine learning models require clean text corpora. " * 3)

            config = {
                "dataset": {"train_ratio": 0.8, "validation_ratio": 0.1, "test_ratio": 0.1, "seed": 42},
                "cleaning": {"fix_mojibake": True, "clean_html": True},
                "quality": {"auto_reject_below": 40, "review_below": 60},
                "deduplication": {"enable_exact_dedup": True, "enable_near_dedup": True, "near_dedup_threshold": 0.80}
            }

            pipeline = ProcessingPipeline(raw_dir, out_dir, config)
            stats = pipeline.run_build()

            self.assertEqual(stats["status"], "BUILD SUCCESSFUL")
            self.assertGreaterEqual(stats["exact_duplicates"], 1)
            self.assertGreaterEqual(stats["near_duplicates"], 1)
            self.assertGreaterEqual(stats["spam"], 1)
            self.assertGreaterEqual(stats["non_turkish"], 1)

if __name__ == "__main__":
    unittest.main()
