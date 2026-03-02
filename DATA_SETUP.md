# 📂 Data Directory Setup Guide

## ✅ Current Status

Your chatbot is now configured to use: **`E:\IRDAI_chatboat_new\data`**

This directory contains all IRDAI-related data for the chatbot.

---

## 📁 Directory Structure

```
data/
├── crawled_data.json      ← Main IRDAI content (text, tables, metadata)
├── pdfs/                  ← All PDF documents
│   ├── regulations/
│   ├── circulars/
│   ├── guidelines/
│   ├── annual-reports/
│   └── ... (other IRDAI sections)
├── vectorstore/           ← Fast search index (auto-generated)
│   ├── irdai.faiss        ← Vector index
│   ├── chunks.pkl
│   └── metadata.pkl
├── excel/                 ← Spreadsheet data
├── word/                  ← Word documents
├── chroma_db/             ← Alternative vector database
└── irdai_tracker.db       ← Crawler status tracking
```

---

## 🚀 How to Populate Your Data

### Option 1: Automatic Crawler (Recommended) ✨

The chatbot has a **built-in web crawler** that automatically fetches IRDAI data:

**Step 1: Run the crawler**
```bash
python run_crawler.py
```

**Step 2: What it does**
- √ Downloads content from irdai.gov.in
- √ Extracts text from 16+ sections (regulations, circulars, guidelines, etc.)
- √ Downloads all PDF documents
- √ Saves to `data/crawled_data.json`
- √ Stores PDFs in `data/pdfs/`

**Step 3: Wait for completion**
- Typical time: 5-30 minutes (depending on IRDAI website)
- Output: 1,000+ documents ready for search

**Step 4: Rebuild search index**
```bash
# Open the app and click "🔧 Reindex" button in sidebar
streamlit run app.py
```

---

### Option 2: Manual Setup (If Crawler Fails)

If the crawler doesn't work, manually add files:

#### A. Create `crawled_data.json`

Create `data/crawled_data.json` with this structure:

```json
[
  {
    "url": "https://irdai.gov.in/regulations/life",
    "title": "Life Insurance Regulation 2015",
    "section": "regulations",
    "text": "The Life Insurance Regulation, 2015...",
    "tables": [],
    "crawled_at": "2024-01-15T10:30:00"
  },
  {
    "url": "https://irdai.gov.in/circulars/motor",
    "title": "Motor Insurance Circular 2024",
    "section": "circulars",
    "text": "Motor Insurance changes effective from...",
    "tables": [],
    "crawled_at": "2024-01-15T10:35:00"
  }
]
```

#### B. Add PDF Files

1. Create folder: `data/pdfs/regulations/`
2. Copy PDF files:
   ```
   data/pdfs/regulations/Insurance_Act_1938.pdf
   data/pdfs/regulations/Life_Insurance_2015.pdf
   ```

#### C. Rebuild Index

In app sidebar:
1. Select "Local Folder"
2. Enter path: `E:\IRDAI_chatboat_new\data`
3. Click "🔧 Reindex"

---

### Option 3: Upload Custom Data

If you have your own IRDAI data:

**Step 1: Prepare files**
- JSON file with your content
- Any associated PDFs

**Step 2: Use app's upload feature**
```
In sidebar:
  → Select "Upload Files"
  → Upload JSON + PDFs
  → App auto-indexes them
```

---

## 🔍 What Data Gets Indexed?

The chatbot can search through:

| Type | Location | Content |
|------|----------|---------|
| **HTML/Text** | `crawled_data.json` | Regulations, guidelines, FAQs |
| **PDFs** | `pdfs/` folder | Official documents, reports |
| **Tables** | In JSON file | Regulatory data, statistics |
| **Metadata** | Each document | Source URL, date, section |

---

## ⚡ Quick Verification

Check if data is connected:

**In terminal:**
```bash
# Check if data folder exists
dir E:\IRDAI_chatboat_new\data

# Check if crawled data exists
type E:\IRDAI_chatboat_new\data\crawled_data.json

# Count PDFs
dir E:\IRDAI_chatboat_new\data\pdfs /s /b | find /c ".pdf"
```

**In app:**
1. Open: `streamlit run app.py`
2. Check sidebar stats: Shows number of documents indexed
3. Try a search query
4. You should see results ✅

---

## 🔧 Configuration

The chatbot is configured in two files:

**File: `rag_pipeline.py`** (lines 23-26)
```python
DEFAULT_DATA_DIR = Path("data")          # Main data folder
DEFAULT_PDF_DIR = Path("data/pdfs")      # PDFs location
DEFAULT_VS_DIR = Path("data/vectorstore")  # Search index
```

**File: `app.py`** (line 333)
```python
vs_path = Path("data/vectorstore/irdai.faiss")  # Default index location
```

✅ **These are already configured correctly!**

---

## 🔄 Auto-Update Schedule

The chatbot can auto-crawl new IRDAI data:

**In app sidebar:**
1. Toggle "⏰ Auto-refresh (24h)"
2. App runs crawler daily
3. Keeps data fresh automatically

---

## 📊 Data Size Expectations

| Component | Size | Notes |
|-----------|------|-------|
| `crawled_data.json` | 5-10 MB | Text content |
| `pdfs/` folder | 1-3 GB | All IRDAI PDFs |
| `vectorstore/` | 200-500 MB | Search index |
| **Total** | **1-3.5 GB** | Depends on coverage |

---

## 🐛 Troubleshooting

### "Knowledge base not indexed"

**Cause:** `crawled_data.json` or `irdai.faiss` doesn't exist

**Solution:**
```bash
# 1. Run crawler to create crawled_data.json
python run_crawler.py

# 2. In app, click "🔧 Reindex"

# 3. Wait for index creation
```

### "Slow search responses"

**Cause:** Large vector index or slow embedding

**Solution:**
1. Check `data/vectorstore/` size
2. Try deleting old vectorstore:
   ```bash
   rmdir /s /q data\vectorstore
   ```
3. Click "🔧 Reindex" to rebuild fresh

### "Missing IRDAI documents"

**Cause:** Crawler didn't download all sections

**Solution:**
```bash
# Re-run with verbose logging
python run_crawler.py --verbose

# Or manually add PDFs to data/pdfs/
```

### "Wrong data location"

**Cause:** Different data folder path

**Solution:**
1. In app: Select "Local Folder"
2. Enter full path: `E:\IRDAI_chatboat_new\data`
3. Click "🔧 Reindex"

---

## 📝 Next Steps

1. ✅ **Confirm data path is set:** `E:\IRDAI_chatboat_new\data`
2. ✅ **Run crawler:** `python run_crawler.py`
3. ✅ **Start app:** `streamlit run app.py`
4. ✅ **Test search:** Try a query about IRDAI regulations
5. ✅ **Enable auto-refresh:** Toggle in sidebar (optional)

---

## 💡 Tips

- **First run slower?** Normal - building index takes time (5-15 min)
- **Want to clear cache?** Delete `data/vectorstore/` folder
- **Need custom data?** Use "Local Folder" or "Upload Files" option
- **Check status?** Look at app sidebar - shows "Knowledge base ready" ✅

---

## 📞 Support

Lost something? Check:
- `data/crawled_data.json` - Should exist after crawl
- `data/pdfs/` - Should have PDFs in subfolders
- `data/vectorstore/` - Created after first index

All good? **Your chatbot is ready to answer IRDAI questions!** 🚀

