import os
import unittest
import tempfile
from dataset_cleaner.ingestion.file_discovery import discover_files
from dataset_cleaner.ingestion.readers import read_document_stream

class TestIngestion(unittest.TestCase):
    def test_file_discovery_and_readers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            txt_path = os.path.join(tmpdir, "sample.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("Merhaba dünya! Bu bir Türkçe test dosyasıdır.")

            jsonl_path = os.path.join(tmpdir, "sample.jsonl")
            with open(jsonl_path, "w", encoding="utf-8") as f:
                f.write('{"title": "Başlık 1", "content": "İçerik 1"}\n')
                f.write('{"title": "Başlık 2", "content": "İçerik 2"}\n')

            discovered = list(discover_files(tmpdir))
            self.assertEqual(len(discovered), 2)

            txt_docs = list(read_document_stream(txt_path, "txt"))
            self.assertEqual(len(txt_docs), 1)
            self.assertIn("Merhaba dünya", txt_docs[0].text)

            jsonl_docs = list(read_document_stream(jsonl_path, "jsonl"))
            self.assertEqual(len(jsonl_docs), 2)
            self.assertEqual(jsonl_docs[0].text, "İçerik 1")

if __name__ == "__main__":
    unittest.main()
