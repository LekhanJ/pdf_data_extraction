# 📄 PDF Data Extraction Pipeline — Gemini Vision

> An AI-powered pipeline that extracts structured data from scanned, handwritten-style government PDFs using Google Gemini's multimodal vision capabilities — with zero OCR libraries.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-2.5--Pro-4285F4?style=for-the-badge&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen?style=for-the-badge)

---

## 📌 Overview

This project solves a real-world data digitization problem: **extracting structured voter records from scanned Marathi-language government PDFs** that traditional OCR tools cannot reliably parse.

The documents contain dense, visually complex layouts where data must be inferred from **spatial position and visual patterns** rather than explicit field labels. This pipeline converts each PDF page into a high-resolution image, sends it to **Google Gemini 2.5 Pro Vision**, and uses a carefully engineered prompt to extract all 14 structured fields per voter record — including bilingual name translation (Marathi → English).

**Real output:** 400+ clean voter records extracted from a scanned PDF, exported to structured JSON.

---

## 🎬 What It Does

```
Input:  scanned_voters.pdf   (Marathi government document, printed layout)
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     EXTRACTION PIPELINE                         │
│                                                                 │
│  PDF → High-Res PNG → Gemini Vision → JSON → Validation → Out   │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
Output: final_voter_data.json
[
  {
    "serial_no": "6",
    "voter_name": "बुवा सुनिता भगवान",
    "voter_name_en": "Buva Sunita Bhagwan",
    "relative_name": "बुवा भगवान",
    "relative_name_en": "Buva Bhagwan",
    "gender": "स्त्री",
    "gender_en": "Female",
    "age": "52",
    "house_no": "11",
    "voter_id": "BZS3084043",
    "area_code": "9/208/839",
    "photo_available": true,
    "nagar_parishad": "शिरपूर वरवाडे नगर परिषद",
    "prabhag_kramank": "२ - रसिकलाल पटेल नगर",
    "yadi_bhaag_kramank": "२०८ : ४ - सरस्वती कॉलनी नवीन वसाहत शिरपूर"
  },
  ... 400+ more records
]
```

---

## ✨ Key Features

| Feature | Details |
|---|---|
| **Vision-First Extraction** | No OCR libraries — Gemini reads images like a human would |
| **Spatial Reasoning Prompts** | Engineered prompts teach the model to follow positional layout, not just labels |
| **Bilingual Output** | Auto-translates Marathi names/gender to English in the same pass |
| **14-Field Schema** | Extracts serial no., voter ID, name, relative, gender, age, house no., area code, ward info, and more |
| **Chunk-Based Batching** | Processes PDFs in configurable page chunks to stay within API limits |
| **Retry with Backoff** | `tenacity` retries transient API failures (3 attempts, exponential backoff) |
| **JSON Schema Validation** | `jsonschema` validates every extracted record; invalid records are logged and skipped |
| **Automatic Cleanup** | Temp images deleted after each chunk; Gemini-uploaded files deleted from cloud |
| **Full Logging** | Dual-output logging to console + `extraction.log` for auditability |

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                            main.py                                   │
│                     (Orchestration Layer)                            │
│                                                                      │
│   1. Parse CLI args          argparse → pdf_path                     │
│   2. Get page count          pdfinfo_from_path() → total_pages       │
│   3. Batch loop              for start_page in range(1, limit,       │
│                                                  CHUNK_SIZE):        │
│      ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌────────────┐    │
│      │  Image   │  │   Gemini     │  │Validator │  │   Merge    │    │
│      │Converter │→ │   Client     │→ │          │→ │ all_data   │    │
│      └──────────┘  └──────────────┘  └──────────┘  └────────────┘    │
│   4. Export → output/final_voter_data.json                           │
│   5. Cleanup temp images                                             │
└──────────────────────────────────────────────────────────────────────┘
         │                    │                   │
         ▼                    ▼                   ▼
┌─────────────────┐  ┌──────────────────┐  ┌───────────────┐
│ image_converter │  │  gemini_client   │  │  validator    │
│     .py         │  │      .py         │  │     .py       │
│                 │  │                  │  │               │
│ convert_from_   │  │ upload_file()    │  │ jsonschema    │
│ path() →        │  │ generate_        │  │ .validate()   │
│ List[Path]      │  │ content()        │  │ per record    │
│                 │  │ json.loads()     │  │               │
│ DPI=300 (high   │  │                  │  │ drops invalid,│
│ res for small   │  │ @retry(3x exp    │  │ logs warning  │
│ Marathi text)   │  │  backoff)        │  │               │
└─────────────────┘  └──────────────────┘  └───────────────┘
         │                    │
         │                    ▼
         │           ┌──────────────────┐
         │           │   prompts.py     │
         │           │                  │
         │           │ System prompt    │
         │           │ teaching Gemini  │
         │           │ visual-spatial   │
         │           │ extraction rules │
         │           │ (14 fields,      │
         │           │ Marathi+English) │
         │           └──────────────────┘
         │
         ▼
┌─────────────────┐
│   config.py     │
│                 │
│ GOOGLE_API_KEY  │
│ MODEL_NAME      │
│ DPI=300         │
│ CHUNK_SIZE=1    │
│ POPPLER_PATH    │
│ VOTER_SCHEMA    │
│ TEMP/OUTPUT dir │
└─────────────────┘
```

---

## 📂 Project Structure

```
pdf_data_extraction/
│
├── main.py                  # Pipeline orchestrator — CLI entry point
├── config.py                # All settings, paths, and JSON schema definition
├── gemini_client.py         # Gemini Vision API wrapper with retry logic
├── image_converter.py       # PDF → high-res PNG via pdf2image/poppler
├── prompts.py               # Engineered system prompt for Gemini extraction
├── validator.py             # JSON schema validator (jsonschema)
├── utils.py                 # Helpers: load/save JSON files
├── check_models.py          # Utility script to list available Gemini models
├── test_images.py           # Debug tool: converts first 2 pages, saves to disk
│
├── output/
│   └── final_voter_data.json   # Structured extraction output (400+ records)
│
├── debug_images/
│   ├── debug_page_1.jpg        # Sample rasterized page (for visual QA)
│   └── debug_page_2.jpg
│
├── extraction.log              # Full run log with record counts and errors
├── requirements.txt
└── .env                        # API key (not committed to version control)
```

---

## 🧠 The Core Challenge: Spatial Reasoning, Not OCR

The voter PDF has a **positional layout** — there are no machine-readable field labels. Every box follows a consistent visual order:

```
┌────────────────────────────────────────────┐
│  [5]                  [BZS3084050]         │  ← serial_no, voter_id
│                       [9/208/838]          │  ← area_code
│  बोवा भगवान शामगिर बोवा                    │  ← voter_name (Marathi)
│  बोवा शामगिर                               │  ← relative_name
│  [11]   पुरुष   [57]                         │  ← house_no, gender, age
│                       [Photo Available]    │
└────────────────────────────────────────────┘
```

Standard OCR extracts text without understanding layout. Gemini Vision reads the **entire page image** and understands spatial relationships — which is why this approach works where Tesseract and similar tools fail.

The system prompt encodes these spatial rules explicitly:

```
❌ label-driven approach  →  breaks on this document
✅ position + pattern approach  →  works reliably
```

---

## 🔄 Pipeline Flow — Step by Step

```
1. CLI Input
   └─ python main.py voters.pdf

2. Page Count
   └─ pdfinfo_from_path() reads total pages from PDF metadata

3. Chunk Loop (CHUNK_SIZE pages at a time)
   │
   ├─ A. Convert chunk to images
   │      ImageConverter.convert_pdf_chunk()
   │      → pdf2image (poppler backend) at 300 DPI
   │      → saves to temp/page_0001.png, temp/page_0002.png ...
   │
   ├─ B. Upload to Gemini File API
   │      GeminiClient.process_image_batch()
   │      → genai.upload_file() for each image
   │      → model.generate_content([prompt, img1, img2...])
   │      → response_mime_type: "application/json" enforced
   │
   ├─ C. Parse JSON response
   │      → strips markdown fences if present
   │      → handles dict vs list edge cases
   │      → raises JSONDecodeError → triggers retry (up to 3x)
   │
   ├─ D. Validate records
   │      Validator.validate_batch()
   │      → jsonschema against VOTER_SCHEMA
   │      → drops invalid, logs warning, continues
   │
   ├─ E. Merge into all_voter_data list
   │
   └─ F. Cleanup
          → delete temp PNGs locally
          → genai.delete_file() on Gemini cloud

4. Export
   └─ json.dump(all_voter_data) → output/final_voter_data.json

5. Cleanup
   └─ shutil.rmtree(temp/) + recreate empty
```

---

## 📋 Extracted Data Schema

Each voter record contains **14 fields**:

| Field | Type | Description | Example |
|---|---|---|---|
| `serial_no` | string | Voter's index on the page | `"6"` |
| `voter_name` | string | Full name in Marathi | `"बुवा सुनिता भगवान"` |
| `voter_name_en` | string | Name translated to English | `"Buva Sunita Bhagwan"` |
| `relative_name` | string | Father's/husband's name (Marathi) | `"बुवा भगवान"` |
| `relative_name_en` | string | Relative name in English | `"Buva Bhagwan"` |
| `gender` | string | Gender in Marathi | `"स्त्री"` |
| `gender_en` | string | Gender in English | `"Female"` |
| `age` | string | Voter's age | `"52"` |
| `house_no` | string | House/plot number | `"11"` |
| `voter_id` | string | Unique voter ID (`[A-Z]{3}[0-9]+`) | `"BZS3084043"` |
| `area_code` | string | Electoral area code (`n/n/n`) | `"9/208/839"` |
| `photo_available` | boolean | Whether photo exists in document | `true` |
| `nagar_parishad` | string | Municipal council name | `"शिरपूर वरवाडे नगर परिषद"` |
| `prabhag_kramank` | string | Ward number + description | `"२ - रसिकलाल पटेल नगर"` |
| `yadi_bhaag_kramank` | string | Electoral roll section + location | `"२०८ : ४ - सरस्वती कॉलनी..."` |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- [Poppler](https://github.com/oschwartz10612/poppler-windows/releases/) (for `pdf2image`)
- A Google AI Studio API key with Gemini 2.5 Pro access

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/pdf-data-extraction.git
cd pdf-data-extraction

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
echo "GOOGLE_API_KEY=your_key_here" > .env

# 4. Set Poppler path in config.py
# Windows: POPPLER_PATH = r"C:\Program Files\poppler-XX.X.X\Library\bin"
# macOS/Linux: POPPLER_PATH = None  (install via brew install poppler or apt)
```

### Running

```bash
# Full extraction run
python main.py path/to/your/document.pdf

# Test image conversion quality on the first 2 pages before a full run
python test_images.py path/to/your/document.pdf

# Check which Gemini models are available on your account
python check_models.py
```

Output is saved to `output/final_voter_data.json`. Full logs in `extraction.log`.

---

## ⚙️ Configuration

All tunable parameters live in `config.py`:

| Parameter | Default | Description |
|---|---|---|
| `MODEL_NAME` | `gemini-2.5-pro` | Gemini model to use |
| `TEMPERATURE` | `0.0` | Fully deterministic — eliminates hallucination on structured data |
| `CHUNK_SIZE` | `1` | Pages per API call (increase for speed, lower for reliability) |
| `TOTAL_PAGES_TO_PROCESS` | `None` | Set an integer to limit pages (useful for testing runs) |
| `DPI` | `300` | Rasterization resolution — 300 DPI is critical for small Marathi text |

---

## 🛠️ Dependencies

| Library | Version | Purpose |
|---|---|---|
| `google-generativeai` | ≥0.7.2 | Gemini Vision API client |
| `pdf2image` | 1.17.0 | PDF → image rasterization (wraps Poppler/pdftoppm) |
| `Pillow` | 10.2.0 | Image handling and PNG saving |
| `jsonschema` | 4.21.1 | Output validation against VOTER_SCHEMA |
| `tenacity` | 8.2.3 | Retry decorator with exponential backoff |
| `python-dotenv` | 1.0.1 | Secure `.env` loading for API key management |

---

## 🔍 Technical Highlights

- **Multimodal AI over OCR** — The project deliberately avoids Tesseract, AWS Textract, and similar tools. The source documents are spatially structured and label-free, making positional visual reasoning the only reliable approach. Gemini 2.5 Pro Vision handles this natively.
- **Prompt engineering as core logic** — `prompts.py` is not a simple question — it encodes a complete visual parsing rulebook: which fields to extract, how to locate them by position, what to ignore (leading colons, decorative labels), and how to distinguish header-level fields from box-level fields.
- **Structured output enforcement** — Setting `response_mime_type: "application/json"` in the generation config forces Gemini to emit valid JSON, eliminating regex parsing. The code still handles markdown fence edge cases defensively.
- **Schema-driven validation pipeline** — `VOTER_SCHEMA` uses JSON Schema draft-7 with typed nullable fields and `enum` constraints on gender values, ensuring output is immediately database-ready with no manual cleaning.
- **Production-grade error handling** — Failed chunks are logged and skipped (not raised), Gemini-uploaded files are always deleted in `finally` blocks, and the `@retry` decorator handles transient failures without losing progress on previously processed chunks.
- **Bilingual extraction in one pass** — Marathi-to-English translation of names and gender happens inside the same Gemini call, with no secondary translation API or post-processing step required.

---

## 📈 Potential Extensions

- [ ] Add a `failed_chunks.json` queue to retry only failed pages without reprocessing the whole document
- [ ] Swap chunk-based batching for async parallel processing across multiple pages
- [ ] Build a FastAPI wrapper to expose the pipeline as a REST endpoint for document uploads
- [ ] Add deduplication on `voter_id` before final export
- [ ] Support multiple document formats by swapping `prompts.py` per document class (voter list, land records, etc.)
- [ ] Stream output to PostgreSQL or MongoDB instead of flat JSON
- [ ] Add per-field confidence scoring using logprobs when the Gemini API supports it

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Built to solve a real digitization problem — turning inaccessible scanned government records into clean, queryable data.
</p>
