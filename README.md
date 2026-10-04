# Turkish Dataset Builder

Debian 13 (x86_64 CPU) üzerinde tamamen yerel çalışan, büyük miktardaki ham Türkçe veriyi yapay zekâ model eğitimi için temiz, tutarlı, kaliteli ve standartlaştırılmış dataset haline getiren profesyonel yerel masaüstü / web uygulaması ve CLI motoru.

---

## Architecture Overview

Turkish Dataset Builder, bellek kullanımını corpus boyutundan bağımsız sabit seviyede tutmak için akışlı okuma (streaming), disk tabanlı SQLite indeksleme (SHA256 exact dedup & MinHash LSH near-dedup) ve sharded JSONL çıktı mekanizması kullanır.

```
HAM VERİ
  ↓
Dosya Keşfi (.txt, .md, .json, .jsonl, .csv, .tsv, .html, .xml, .yaml, .pdf)
  ↓
Akışlı Format Okuma & Otomatik Alan Tespiti
  ↓
Mojibake Düzeltme & Unicode NFC Normalizasyonu
  ↓
HTML / Web & Markdown Temizleme
  ↓
Bozuk / Spam / Anlamsız Veri Filtreleme
  ↓
Türkçe Kalite Kontrolü & 0-100 Şeffaf Skorlama
  ↓
Disk Tabanlı Exact (SHA256) & Near-Duplicate (MinHash LSH) Deduplication
  ↓
Cümle / Paragraf Sınırında Chunking
  ↓
Seed Bazlı Train / Validation / Test Bölümleme (Sızıntısız)
  ↓
Sharded JSONL Çıktı & SHA256 Manifest
  ↓
HTML / JSON Raporlama & Post-Build Doğrulama Pass
```

---

## Installation on Debian 13

### Requirements
- Debian 13 (x86_64)
- Python 3.10+
- Virtual environment (`python3-venv`)

### Setup Commands
```bash
# 1. Virtual environment oluşturun
python3 -m venv .venv

# 2. Virtual environment'ı aktif edin
source .venv/bin/activate

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Uygulamayı çalıştırın
./run.sh --gui
```

---

## Usage Instructions

### 1. Web GUI Kullanımı (127.0.0.1:8000)
Uygulama yerel web arayüzünü başlatmak için:
```bash
python3 -m dataset_cleaner --gui
```
Tarayıcınızda `http://127.0.0.1:8000` adresine gidin.

Adımlar:
1. **Ham Veri Klasörü (RAW Input Directory)** ve **Hedef Dataset Klasörü** yollarını girin.
2. **1. ANALYZE** butonuna basarak verinizi inceleyin (dry-run).
3. Ayarlar bölümünden min/max uzunluk, threshold ve split oranlarını yapılandırın.
4. **2. BUILD DATASET** butonuna basarak temizlik pipeline'ını çalıştırın.

### 2. CLI Kullanımı
```bash
# Kuru çalıştırma / Analiz modu:
python3 -m dataset_cleaner --input /path/to/raw --output /path/to/output --analyze

# Tam dataset üretimi:
python3 -m dataset_cleaner --input /path/to/raw --output /path/to/output --config config.yaml

# Yarıda kesilen işlemi devam ettirme (Resume):
python3 -m dataset_cleaner --input /path/to/raw --output /path/to/output --resume
```

---

## Testing & Verification

Automated test suite'ini çalıştırmak için:
```bash
python3 -m unittest discover tests
```

Raporlar `reports/` klasörü altında oluşturulur:
- `reports/requirements_verification.md`
- `reports/benchmark.md`
- `reports/FINAL_AUDIT_REPORT.md`
- `reports/PROJECT_NAME_AUDIT.md`
