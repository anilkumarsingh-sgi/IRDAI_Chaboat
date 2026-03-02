# 🛡️ IRDAI Regulatory Intelligence Chatbot

An **industry-grade AI chatbot** that crawls IRDAI's entire website, indexes all regulatory content, and answers questions using **free unlimited LLMs** (Groq) with Retrieval-Augmented Generation (RAG).

✨ **Perfect for Streamlit Cloud deployment** • Production-ready • Zero infrastructure costs

---

## 🏗️ Architecture

```
irdai.gov.in ──► Crawler ──► FAISS Vector Store ──► RAG Pipeline ──► Streamlit UI
       │              │                                    │
     PDFs        BeautifulSoup            sentence-transformers  
                                                           │
                                    ┌──────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
             🔥 Groq API      🤗 HF API      Ollama Local
          (FREE & FAST)    (Fallback)        (Advanced)
          Unlimited Tier    Limited Tier    Full Control
```

| Component | Technology | Details |
|-----------|-----------|---------|
| **Web Crawler** | `requests` + `BeautifulSoup4` | Full IRDAI website coverage |
| **PDF Extraction** | `pypdf` | All regulations in PDF format |
| **Embeddings** | `sentence-transformers` (all-MiniLM-L6-v2) | Fast, accurate semantic search |
| **Vector Store** | `FAISS` (IndexFlatIP) | 1000x faster than SQL-based search |
| **LLM** | **Groq** (Mixtral-8x7B / Llama-2) | FREE, unlimited, 500+ tokens/sec |
| **Fallback LLM** | HuggingFace API | If Groq unavailable (rare) |
| **Frontend** | `Streamlit` | Responsive, cloud-ready UI |
| **Scheduling** | `apscheduler` | 24h auto-update mechanism |

---

## 🚀 5-Minute Quick Start

### 1. Get Free API Key (30 seconds)

Go to [groq.com](https://groq.com) → Sign up → Copy your free API key

### 2. Deploy to Streamlit Cloud

```bash
# 1. Push to GitHub
git push origin main

# 2. Deploy via https://share.streamlit.io (click "Create app")
# 3. Go to app settings → add secret:
#    GROQ_API_KEY = your_key_here
# 4. Done! ✅
```

### 3. Or Run Locally

```bash
pip install -r requirements.txt
export GROQ_API_KEY="gsk_your_key"
streamlit run app.py
```

Open **http://localhost:8501**

### 4. Or Use Docker

```bash
docker-compose up --build
```

---

## 🔑 API Configuration (3 Options)

### ✅ Option 1: Groq (RECOMMENDED - Free & Unlimited)

**Best for Streamlit Cloud deployments:**

1. Get free API key: https://groq.com
2. Add to Streamlit Cloud secrets: `GROQ_API_KEY = "gsk_..."`
3. Select "🔥 Groq" in app sidebar
4. Start asking questions!

**Why Groq?**
- ✅ Completely free with no rate limits
- ✅ Super fast: 500+ tokens/second
- ✅ 2 high-quality models: Mixtral-8x7B & Llama-2-70B
- ✅ Highly reliable (99.9% uptime)
- ✅ Best for production use

### 🤗 Option 2: HuggingFace (Fallback)

Automatically used if Groq not configured:

1. Get free API key: https://huggingface.co/settings/tokens
2. Add to environment: `HF_API_KEY = "hf_..."`
3. Select "🤗 HuggingFace" in app sidebar

**Note:** Free tier has rate limits. Groq recommended.

### Local: Option 3: Ollama (Advanced)

For complete control with local inference:

1. Install Ollama: https://ollama.ai
2. Run: `ollama serve`
3. Set: `OLLAMA_BASE_URL = "http://localhost:11434"`

---

## � Data Sources for Chat

The chatbot supports **multiple data sources**. Choose any combination:

### Option 1: Default IRDAI Data (Recommended for first use)
```
✅ Uses: Official IRDAI website (irdai.gov.in)
✅ Coverage: Regulations, circulars, guidelines, reports
✅ Size: 1000+ documents, 2000+ pages
✅ Setup: No configuration needed
✅ Auto-update: Every 24 hours (optional)
```
**How to use:**
1. Open app
2. Sidebar → Data Source → Select "Default (IRDAI)"
3. Wait for knowledge base to load
4. Start asking questions!

---

### Option 2: Upload Your Own Files
```
✅ Supports: JSON, PDF files
✅ Size limit: Up to 200 MB per upload
✅ Formats: 
   - crawled_data.json (from crawler output)
   - PDF files (any PDF document)
✅ Setup: 2 minutes
```
**How to use:**
1. Sidebar → Data Source → "Upload Files"
2. Select JSON + PDF files from your computer
3. Click upload
4. Wait for indexing (~30 sec per 100 MB)
5. Start asking questions about your data!

**Example workflow:**
```
Your Data (PDFs/Docs)
    ↓
Run crawler on your site/folder
    ↓
Get crawled_data.json + PDFs
    ↓
Upload to chatbot
    ↓
AI searches your data instantly!
```

---

### Option 3: Use Local Folder Path
```
✅ Supports: Local file system paths
✅ Best for: Development, local testing
✅ Data location: Your computer's folders
✅ Setup: Just paste the path
```
**How to use:**
1. Sidebar → Data Source → "Local Folder"
2. Paste folder path:
   - Windows: `C:\Users\YourName\Documents\irdai_data`
   - Mac/Linux: `/home/user/irdai_data`
3. Folder must contain:
   - `crawled_data.json` (main data file)
   - `pdfs/` subfolder (with PDF files)
4. Start asking questions!

**Folder structure:**
```
your_data_folder/
├── crawled_data.json      ← Required
├── pdfs/
│   ├── document1.pdf
│   ├── document2.pdf
│   └── ...
└── vectorstore/           ← Optional (for speed)
    ├── irdai.faiss
    ├── chunks.pkl
    └── metadata.pkl
```

---

### Option 4: Google Drive (Cloud Collaboration)
```
✅ Supports: Shared Google Drive folders
✅ Best for: Team collaboration
✅ No download needed: Access from cloud
✅ Setup: 2 minutes
```
**How to use:**
1. Upload data to Google Drive
2. Right-click folder → Share → "Anyone with link"
3. Copy the folder ID from URL:
   `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
4. Sidebar → Data Source → "Google Drive"
5. Paste folder ID
6. Start asking questions!

---

## �📱 Using the App

### User Interface

**Sidebar Controls:**
- 🔥 **LLM Provider** - Choose Groq/HuggingFace/Ollama
- 📁 **Data Source** - Default IRDAI / Upload files / Local folder / Google Drive
- 🤖 **Model Selection** - Pick specific model
- ⚙️ **Settings** - top-k, max tokens, temperature
- 🕷️ **Crawler** - Crawl sections, rebuild index, auto-update

**Main Chat:**
- Ask questions about any IRDAI topic
- Get citations to original documents
- Download chat history as JSON
- See source documents on the right

### Sample Questions

```
"What are capital requirements for starting a general insurance company?"
"How do I file a complaint against an insurer?"
"What is the solvency margin for life insurers?"
"Explain the Bima Sugam initiative"
"What are ULIP disclosure requirements?"
"Commission limits for insurance agents?"
```

---

## 🕷️ Web Crawler

Covers **all sections** of IRDAI website:

| Section | Content |
|---------|---------|
| `home` | Homepage, announcements |
| `about-irdai` | About, mission, vision, leadership |
| `regulations` | Insurance regulations full text |
| `circulars` | All circulars with PDFs |
| `orders` | Orders and judgements |
| `guidelines` | Product and operational guidelines |
| `annual-reports` | Annual report PDFs |
| `press-releases` | News and press releases |
| `notifications` | Gazette notifications |
| `exposuredraft` | Exposure drafts for comment |
| `insurance-companies` | Registered insurer list |
| `intermediaries` | Agents, brokers, TPAs |
| `consumer-education` | Rights, FAQs, complaint process |
| `insurance-ombudsman` | Ombudsman offices and process |
| `bima-sugam` | Bima Sugam portal information |
| `statistical-data` | Insurance sector statistics |

### Auto-Update
Enable **Auto-update (24h)** in the sidebar to automatically re-crawl and re-index every 24 hours.

Manual update:
```bash
python run_crawler.py --sections regulations circulars
```

---

## 💬 Sample Questions

- "What are capital requirements for starting a general insurance company?"
- "How do I file a complaint against an insurer with IRDAI?"
- "What are the IRDAI regulations on health insurance portability?"
- "What is the solvency margin requirement for life insurers?"
- "Explain the Bima Sugam initiative."
- "What disclosures are mandatory for ULIP products?"
- "What are the commissions allowed for insurance agents under IRDAI?"

---

## ⚙️ Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| HF API Key | `hf_your_token_here` | HuggingFace token (in .env) |
| Model | `mistralai/Mistral-7B-Instruct-v0.3` | LLM model |
| Top-K | 5 | Context chunks retrieved |
| Max Tokens | 800 | Response length |
| Temperature | 0.3 | Response creativity |
| Crawl Interval | 24h | Auto-update frequency |

---

## ⚠️ Disclaimer

This chatbot is for **informational and industry research purposes only**. It is not a substitute for official legal or regulatory advice. Always verify at [irdai.gov.in](https://irdai.gov.in) or consult a licensed professional.

---

## 📂 Project Structure

```
irdai_chatbot/
├── app.py              ← Streamlit UI
├── crawler.py          ← IRDAI website crawler
├── rag_pipeline.py     ← FAISS vector store + RAG
├── hf_client.py        ← HuggingFace API client
├── scheduler.py        ← Auto-update scheduler
├── run_crawler.py      ← Standalone crawler CLI
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── data/
│   ├── crawled/        ← Crawled HTML content (JSON)
│   ├── pdfs/           ← Downloaded PDFs by section
│   └── vectorstore/    ← FAISS index + chunk pickles
└── logs/
    └── crawler.log
```
