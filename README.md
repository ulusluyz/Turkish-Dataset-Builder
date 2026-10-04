# Turkish Dataset Builder

**Turkish Dataset Builder**, ham Türkçe verileri makine öğrenmesi ve dil modeli eğitimi için kullanılabilir, temiz, doğrulanmış ve yapılandırılmış datasetlere dönüştürmek için geliştirilmiş yerel bir veri işleme uygulamasıdır.

Sistem; metinleri teknik olarak temizler, Türkçe kalite sinyallerini analiz eder, bozuk ve anlamsız içerikleri ayırır, duplicate ve near-duplicate kayıtları temizler, veriyi `train / validation / test` olarak böler ve sonuçları doğrulanmış JSONL datasetleri halinde üretir.

> **Temel prensip:** Kaynak metnin anlamı korunur. Sistem metin üretmez, yeniden yazmaz ve paraphrase yapmaz.

---

## Özellikler

* TXT / TEXT
* Markdown
* JSON
* JSONL
* CSV
* TSV
* XML
* HTML / HTM
* YAML / YML
* PDF
* Otomatik JSON/JSONL text-field keşfi
* UTF-8 ve Türkçe karakter koruması
* Mojibake / encoding düzeltme
* Unicode NFC normalizasyonu
* HTML temizleme
* Markdown temizleme
* Whitespace ve kontrol karakteri temizleme
* Spam ve anlamsız veri tespiti
* Keyboard-mash / OCR garbage tespiti
* Türkçe kalite analizi
* 0–100 kalite skoru
* Exact duplicate temizleme
* SHA256 fingerprint
* MinHash + LSH near-duplicate temizleme
* SQLite tabanlı disk-backed index
* Yapılandırılabilir similarity threshold
* Çok kısa veri filtreleme
* Uzun metinleri paragraf/cümle sınırlarından bölme
* Train / Validation / Test split
* Split leakage kontrolü
* UTF-8 JSONL output
* Sharded dataset output
* Rejected data retention
* Quarantine sistemi
* Review Queue
* Before / After preview
* Local web GUI
* CLI
* Analyze / Dry-run modu
* SQLite checkpoint sistemi
* Resume desteği
* Hata toleranslı ingestion
* SHA256 manifest
* Dataset raporları
* Final dataset verification
* Deterministic / reproducible processing
* Streaming ve düşük RAM kullanımı

---

# Çalışma Ortamı

## Desteklenen işletim sistemi

Birincil ve doğrulanmış çalışma ortamı:

* **Debian 13 (Trixie)**
* **Linux x86_64 / amd64**

Sistem CPU üzerinde çalışır.

**GPU gerekli değildir.**

CUDA, ROCm veya herhangi bir yapay zekâ hızlandırıcısı kullanılmaz.

---

# Sistem Gereksinimleri

## Minimum

| Bileşen         | Gereksinim                                             |
| --------------- | ------------------------------------------------------ |
| İşletim sistemi | Debian 13 x86_64                                       |
| CPU             | 2 çekirdek                                             |
| RAM             | **2 GB**                                               |
| Disk            | **5 GB boş alan + dataset için gerekli alan**          |
| Python          | **3.13**                                               |
| GPU             | Gerekli değil                                          |
| İnternet        | Kurulum sırasında bağımlılık indirmek için gerekebilir |

2 GB RAM minimum çalışma hedefidir. Büyük datasetlerde işlem süresi ve disk kullanımı artabilir.

## Önerilen

| Bileşen         | Önerilen                         |
| --------------- | -------------------------------- |
| İşletim sistemi | Debian 13 x86_64                 |
| CPU             | 4+ çekirdek                      |
| RAM             | **8 GB+**                        |
| Disk            | **SSD / NVMe**                   |
| Boş disk        | Dataset boyutunun en az 2–3 katı |
| Python          | 3.13                             |
| GPU             | Gerekli değil                    |

Büyük datasetlerde SSD/NVMe kullanılması önerilir. Duplicate indexleri, checkpoint verileri, output shardları ve raporlar disk üzerinde tutulur.

---

# Bellek ve Streaming Mimarisi

Pipeline tüm dataseti RAM'e yüklemez.

Temel işlem akışı:

```text
Raw Input
    ↓
Streaming Reader
    ↓
Encoding / Unicode Cleaning
    ↓
HTML / Markdown Cleaning
    ↓
Quality Analysis
    ↓
Exact Dedup
    ↓
Near-Duplicate Detection
    ↓
Train / Validation / Test Split
    ↓
JSONL Sharding
    ↓
Manifest
    ↓
Final Validation
```

Exact duplicate ve near-duplicate indexleri SQLite üzerinde disk-backed olarak tutulur.

Bu nedenle dataset boyutunun RAM ile aynı oranda büyümesi hedeflenmez.

## Ölçülen Scaling Benchmark

Gerçek pipeline kullanılarak yapılan scaling testinde:

| Doküman |   Input | Initial RSS | Peak RSS |  Ölçülen hız |
| ------: | ------: | ----------: | -------: | -----------: |
|   1.000 | 0.38 MB |    22.38 MB | 23.50 MB | 261.8 docs/s |
|   2.500 | 0.96 MB |    23.50 MB | 23.88 MB | 262.6 docs/s |
|   5.000 | 1.92 MB |    23.88 MB | 23.83 MB | 259.2 docs/s |
|  10.000 | 3.84 MB |    23.83 MB | 24.89 MB | 260.3 docs/s |

Benchmark; ingestion, cleaning, quality scoring, exact SHA256 deduplication, MinHash/LSH near-deduplication, split, sharding, manifest ve final validation aşamalarını kapsamaktadır.

10.000 dokümana kadar yapılan ölçümlerde peak RSS yaklaşık **25 MB'ın altında** kalmıştır.

> Bu sonuçlar yalnızca ölçülen benchmark aralığını gösterir. Daha büyük datasetler için ölçülmemiş RAM kullanımına ilişkin garanti verilmez.

---

# Veri Kaynakları

Desteklenen formatlar:

```text
.txt
.text
.md
.markdown
.json
.jsonl
.csv
.tsv
.xml
.html
.htm
.yaml
.yml
.pdf
```

PDF desteği metin tabanlı PDF'ler içindir.

Görüntü tabanlı veya taranmış PDF'ler otomatik OCR ile dönüştürülmez. Uygun olmayan içerikler quarantine/review sürecine alınabilir.

---

# Türkçe Veri İşleme

Sistem Türkçe karakterleri korur:

```text
ç Ç
ğ Ğ
ı İ
ö Ö
ş Ş
ü Ü
```

ASCII ile yazılmış Türkçe metinler de kalite analizinde değerlendirilebilir:

```text
Bugun hava cok guzel.
```

Encoding kaynaklı bozulmalar için mojibake düzeltme uygulanabilir.

Örneğin:

```text
TÃ¼rkiye
```

şu hale getirilebilir:

```text
Türkiye
```

---

# Veri Kalitesi

Sistem aşağıdaki içerikleri tespit edip uygun şekilde filtreleyebilir:

* Boş içerik
* Çok kısa metin
* Sadece noktalama
* Sadece sayı
* Sadece URL
* Emoji-only içerik
* Tekrarlanan karakterler
* Keyboard mash
* OCR garbage
* Spam
* Otomatik oluşturulmuş anlamsız içerik
* Aşırı navigation / cookie / reklam içeriği
* Türkçe olmayan veya düşük güvenli içerik

Her kayıt için kalite sinyalleri hesaplanabilir.

---

# Duplicate Temizleme

## Exact Duplicate

SHA256 ve normalize edilmiş metin hashleri kullanılır.

```text
Document
   ↓
Normalize
   ↓
SHA256
   ↓
SQLite
   ↓
Duplicate / Unique
```

## Near Duplicate

Near-duplicate detection:

```text
Document
   ↓
Fingerprint
   ↓
MinHash
   ↓
LSH
   ↓
SQLite
   ↓
Similarity Decision
```

Varsayılan similarity threshold:

```yaml
near_duplicate_threshold: 0.80
```

Threshold yapılandırılabilir.

---

# Dataset Split

Varsayılan split:

```text
Train       98%
Validation   1%
Test         1%
```

Split işleminden önce duplicate temizliği uygulanır.

Aynı veya duplicate kayıtların farklı splitlere sızmasını önlemek için leakage kontrolü gerçekleştirilir.

---

# Çıktı Yapısı

Üretilen dataset genel olarak:

```text
dataset_output/
├── train/
│   ├── train-00000.jsonl
│   ├── train-00001.jsonl
│   └── ...
│
├── validation/
│   ├── validation-00000.jsonl
│   └── ...
│
├── test/
│   ├── test-00000.jsonl
│   └── ...
│
├── rejected/
│   ├── REJECT_TOO_SHORT.jsonl
│   ├── DUPLICATE.jsonl
│   ├── NEAR_DUPLICATE.jsonl
│   ├── SPAM.jsonl
│   └── ...
│
├── quarantine/
│
├── reports/
│   ├── dataset_report.json
│   ├── dataset_report.html
│   ├── quality_report.json
│   └── duplicate_report.json
│
└── manifest/
    ├── manifest.json
    └── SHA256SUMS
```

Rejected kayıtlar silinmez.

Her rejection mümkün olduğunca açık bir kodla kayıt altına alınır.

Örnek:

```text
REJECT_TOO_SHORT
DUPLICATE
NEAR_DUPLICATE
SPAM
INVALID_ENCODING
NON_TURKISH
EMPTY
CORRUPTED
```

---

# Source Truth

Bu proje bir **metin üretim sistemi değildir**.

Aşağıdaki işlemler kullanılmaz:

* LLM
* OpenAI API
* Harici AI API
* Paraphrasing
* Summarization
* Yapay metin üretimi
* Model tabanlı yeniden yazım

Kaynak kod üzerinde yapılan bağımsız source-truth auditinde veri işleme katmanında harici LLM API, OpenAI SDK, neural network, paraphrasing engine veya metin üretim sistemi tespit edilmemiştir.

Temizleme işlemleri teknik ve yapısaldır:

```text
Encoding correction
Unicode normalization
Whitespace normalization
HTML stripping
Markdown processing
Quality filtering
Duplicate detection
Dataset validation
```

Amaç:

> **Kaynak veriyi daha temiz ve eğitim için daha uygun hale getirmek; yeni bilgi üretmemektir.**

---

# GUI

Sistem localhost üzerinde çalışan web arayüzüne sahiptir.

Varsayılan adres:

```text
http://127.0.0.1:8000
```

GUI üzerinden:

* Input directory seçimi
* Output directory seçimi
* Analyze
* Configuration
* Build
* Progress / statistics
* Review Queue
* Before / After preview
* Reports

işlemleri yapılabilir.

Sunucu dışarıya açık bir web servisi olarak tasarlanmamıştır.

---

# CLI

Temel kullanım:

```bash
python3 -m dataset_cleaner \
    --input ./raw_data \
    --output ./dataset_output
```

Analyze:

```bash
python3 -m dataset_cleaner \
    --input ./raw_data \
    --output ./dataset_output \
    --analyze
```

Resume:

```bash
python3 -m dataset_cleaner \
    --input ./raw_data \
    --output ./dataset_output \
    --resume
```

GUI:

```bash
python3 -m dataset_cleaner --gui
```

Config:

```bash
python3 -m dataset_cleaner \
    --input ./raw_data \
    --output ./dataset_output \
    --config config.yaml
```

---

# Kurulum

Debian 13 üzerinde:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

Projeyi aldıktan sonra:

```bash
cd dataset-cleaner
```

Sanal ortam oluştur:

```bash
python3 -m venv .venv
```

Aktifleştir:

```bash
source .venv/bin/activate
```

Bağımlılıkları yükle:

```bash
pip install -r requirements.txt
```

---

# Çalıştırma

## GUI

```bash
./run.sh
```

veya:

```bash
python3 -m dataset_cleaner --gui
```

Ardından:

```text
http://127.0.0.1:8000
```

adresini aç.

## CLI

```bash
python3 -m dataset_cleaner \
    --input ./raw_data \
    --output ./dataset_output
```

---

# Analyze → Build İş Akışı

Önerilen kullanım:

```text
RAW DATA
   │
   ▼
ANALYZE
   │
   ├── Document count
   ├── Language statistics
   ├── Quality statistics
   ├── Duplicate statistics
   └── Rejection estimates
   │
   ▼
CONFIGURATION
   │
   ▼
BUILD
   │
   ▼
FINAL VALIDATION
   │
   ▼
FINAL DATASET
```

`Analyze` aşaması ham veriyi değiştirmez.

---

# Checkpoint / Resume

Pipeline SQLite checkpoint sistemi kullanır.

Uzun süren işlem kesilirse:

```bash
--resume
```

parametresi ile kaldığı yerden devam edilebilir.

Tek bir bozuk dosyanın tüm dataset işlemini durdurmaması hedeflenir; hata kayıtları ayrıca tutulur.

---

# Reproducibility

Varsayılan seed:

```yaml
seed: 42
```

Aynı:

* input
* configuration
* seed
* pipeline version

ile mümkün olduğunca deterministik output üretimi hedeflenir.

Output manifestlerinde SHA256 değerleri tutulur.

---

# Input Güvenliği

Ham input dosyaları işlem sırasında değiştirilmez.

Input dosyaları okuma modunda işlenir:

```text
READ ONLY
```

Dataset output ayrı bir dizine yazılır.

---

# Testler

Proje kapsamlı otomatik test suite içerir.

Test kapsamı:

* Encoding
* Turkish text
* Mojibake
* HTML
* Markdown
* JSON
* JSONL
* CSV
* TSV
* Deduplication
* Near-duplicate
* Spam
* Quality scoring
* Chunking
* Dataset split
* Leakage
* Manifest
* Streaming
* RAM
* Reproducibility
* Input immutability
* Pipeline
* Validation

Son doğrulama sırasında **18 test suite** başarıyla tamamlanmıştır.

Testleri çalıştır:

```bash
python3 -m unittest discover -s tests -v
```

---

# Final Audit Durumu

Bağımsız final audit sonucunda:

```text
VERIFIED:              50 / 51
PARTIALLY CONFIRMED:    1 / 51
NOT_PROVEN:             0
FAILED:                 0
```

## Kısmi gereksinim

Tek kısmi gereksinim:

```text
#35 — Parallel Processing
```

`max_workers` configuration seçeneği mevcut olmakla birlikte mevcut pipeline gerçek anlamda paralel CPU processing yapmamaktadır; pipeline tek CPU process üzerinde sequential çalışmaktadır.

Bu durum veri temizleme doğruluğunu etkilemez. Yalnızca yapılandırmada bulunan paralel işlem kapasitesinin mevcut sürümde henüz aktif olmadığını gösterir.

---

# Scaling Benchmark Sonucu

Benchmark sırasında aşağıdaki değerler ölçülmüştür:

```text
1,000 docs   → 261.8 docs/s
2,500 docs   → 262.6 docs/s
5,000 docs   → 259.2 docs/s
10,000 docs  → 260.3 docs/s
```

Peak RSS:

```text
1,000 docs   → 23.50 MB
2,500 docs   → 23.88 MB
5,000 docs   → 23.83 MB
10,000 docs  → 24.89 MB
```

Benchmark gerçek pipeline'ın tamamını kapsamaktadır.

100 GB veya daha büyük datasetler için benchmark yapılmadığından, bu ölçümlere dayanarak büyük datasetler için kesin RAM garantisi verilmez.

---

# Proje Raporları

Doğrulama, audit ve benchmark çıktıları `reports/` altında tutulur.

Önemli raporlar:

```text
reports/
├── FINAL_AUDIT_REPORT.md
├── benchmark.md
├── scaling_benchmark_results.json
└── PROJECT_NAME_AUDIT.md
```

Repository'deki mevcut rapor dosyaları sürüme göre ek doğrulama çıktıları da içerebilir.

---

# Proje Prensipleri

1. **Kaynak veri korunur.**
2. **Input dosyaları değiştirilmez.**
3. **LLM kullanılmaz.**
4. **Harici AI API kullanılmaz.**
5. **Metin yeniden yazılmaz.**
6. **Dataset RAM'e komple yüklenmez.**
7. **Duplicate kayıtlar izlenebilir şekilde kayıt altına alınır.**
8. **Near-duplicate kontrolü disk-backed olarak yapılır.**
9. **Dataset split işleminde leakage kontrol edilir.**
10. **Final dataset build sonrası tekrar doğrulanır.**
11. **İşlem sonuçları SHA256 manifest ile izlenebilir.**
12. **Aynı konfigürasyon ve seed ile reproducible output hedeflenir.**
13. **Input ve output birbirinden ayrı tutulur.**
14. **Temizleme işlemi kaynak metne yeni bilgi eklemez.**

---

# Durum

**Production-oriented initial release**

Turkish Dataset Builder; veri ingestion, cleaning, quality control, deduplication, dataset generation ve final validation süreçleri açısından bağımsız audit ve benchmark süreçlerinden geçirilmiştir.

Son audit:

```text
50 / 51 VERIFIED
1 / 51 PARTIALLY CONFIRMED
0 NOT_PROVEN
0 FAILED
```

Mevcut kısmi gereksinim:

```text
#35 — Parallel Processing
```

`max_workers` yapılandırması mevcut olmakla birlikte paralel CPU processing henüz aktif değildir.

Bunun dışındaki **50 gereksinim doğrulanmıştır.**

---

# Lisans

Bu proje için lisans bilgisi repository içerisindeki `LICENSE` dosyasına göre değerlendirilmelidir.
