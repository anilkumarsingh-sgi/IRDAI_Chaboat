# 🚀 IRDAI Chatbot - Streamlit Cloud Deployment Guide

This guide explains how to deploy the IRDAI Regulatory Chatbot to **Streamlit Cloud** with an **unlimited free LLM** (Groq) and custom dataset support.

---

## ✅ Prerequisites

- GitHub account (for code repository)
- Streamlit Cloud account (free at https://share.streamlit.io)
- Groq API key (free at https://groq.com)
- HuggingFace account (optional backup)

---

## 🎯 Step-by-Step Deployment

### 1. Prepare Your Repository

```bash
# Clone or create your Streamlit app repo on GitHub
git init
git add .
git commit -m "Initial IRDAI chatbot setup"
git push origin main
```

**Files needed in repository:**
```
├── app.py                    # Main Streamlit app
├── hf_client.py             # LLM client (Groq/HF/Ollama)
├── rag_pipeline.py          # RAG vector search
├── crawler.py               # IRDAI web crawler
├── requirements.txt         # Python dependencies
├── .streamlit/
│   ├── config.toml         # Streamlit config
│   └── secrets.toml.example # Secrets template
├── data/                    # Pre-crawled data (optional)
│   ├── crawled_data.json
│   └── pdfs/
└── README.md               # Setup instructions
```

### 2. Get Groq API Key (FREE)

**Best option for unlimited free LLM:**

1. Go to https://groq.com
2. Sign up (free)
3. Navigate to **API Keys** section
4. Create new API key
5. Copy the key (starts with `gsk_`)

> **Why Groq?**
> - ✅ Completely free
> - ✅ Unlimited requests
> - ✅ Very fast (500+ tokens/second)
> - ✅ 2 high-quality models available
> - ✅ Best for Streamlit Cloud

### 3. Deploy to Streamlit Cloud

#### Method A: Direct GitHub Connection (Recommended)

1. Go to https://share.streamlit.io
2. Click **"Create app"**
3. Select your GitHub repository
4. Choose branch: `main`
5. Set main file path: `app.py`
6. Click **"Deploy"**

#### Method B: Manual Upload

1. Upload files to Streamlit Cloud via the web interface
2. Let Streamlit install dependencies from `requirements.txt`

### 4. Configure Secrets in Streamlit Cloud

**After deployment, add your API keys:**

1. Go to your app settings:  
   `https://share.streamlit.io/YOUR_USERNAME/YOUR_APP/settings/secrets`

2. Copy this template and replace with your keys:

```toml
# Primary: Groq (FREE, UNLIMITED) - RECOMMENDED
GROQ_API_KEY = "gsk_YOUR_ACTUAL_KEY_HERE"

# Fallback: HuggingFace (limited free tier)
HF_API_KEY = "hf_YOUR_ACTUAL_KEY_HERE"
```

3. Save secrets
4. Streamlit will automatically restart your app

### 5. Prepare Your Data

#### Option A: Pre-index Your Data Locally

Before deployment, run crawler:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Crawl IRDAI website & create vector index
python run_crawler.py

# 3. This creates:
#    data/crawled_data.json
#    data/pdfs/
#    data/vectorstore/irdai.faiss
```

**Upload this data to GitHub** → Streamlit Cloud will have it ready!

#### Option B: Let Users Upload Data

Users can upload:
- JSON file (crawled_data.json)
- PDF files
- Or specify folder path from their system

#### Option C: Use Default IRDAI Data

App comes with default IRDAI regulatory data pre-configured.

### 6. Test Your Deployment

1. After deployment completes, click **"Open app"**
2. Wait for knowledge base to load
3. Test with a question:
   - "What are IRDAI guidelines for health insurance?"
   - "How to file an IRDAI complaint?"
4. Verify Groq API is responding

---

## 🔧 Configuration Reference

### Environment Variables (Local)

Create `.env` file:

```env
# Local development
GROQ_API_KEY=gsk_your_key_here
HF_API_KEY=hf_your_key_here
OLLAMA_BASE_URL=http://localhost:11434
```

### Streamlit Secrets (Cloud)

Access at: `https://share.streamlit.io/YOUR_USERNAME/YOUR_APP/settings/secrets`

```toml
GROQ_API_KEY = "gsk_..."
HF_API_KEY = "hf_..."
```

### .streamlit/config.toml

Performance optimizations for cloud:

```toml
[theme]
primaryColor = "#003087"
font = "sans serif"

[server]
maxUploadSize = 200
enableXsrfProtection = true

[client]
showErrorDetails = true
toolbarMode = "minimal"
```

---

## 📱 Using the App

### For Users

1. **Select LLM Provider**: Choose Groq (recommended) or HuggingFace
2. **Select Data Source**:
   - Default IRDAI data
   - Upload your own files
   - Specify local folder path
   - Google Drive folder
3. **Ask Questions**: Type queries about IRDAI regulations
4. **View Sources**: See referenced documents on the right

### For Developers

#### Customizing Data

```python
# In app.py - use custom data directory
st.session_state.data_dir = "/path/to/your/data"
```

#### Adding More Models

Edit `hf_client.py`:

```python
GROQ_MODELS = {
    "mixtral-8x7b-32768": "Mixtral 8x7B",
    "llama2-70b-4096": "Llama 2 70B",
    # Add more Groq models...
}
```

#### Changing Embedding Model

In `rag_pipeline.py`:

```python
model_name = "sentence-transformers/all-MiniLM-L6-v2"  # Change this
self.embedder = SentenceTransformer(model_name)
```

---

## 🐛 Troubleshooting

### Issue: "No API key found"

**Solution:**
1. Check Streamlit Cloud secrets are configured correctly
2. For local: Create `.env` file with your keys
3. Restart the app after adding secrets

### Issue: "Model loading..."

**Cause:** Hugging Face model is cold-starting

**Solution:**
1. Switch to Groq (faster, always available)
2. Wait 30-60 seconds for model to warm up
3. Try again

### Issue: "Knowledge base not indexed"

**Solution:**
1. Click **"▶ Crawl"** button in sidebar
2. Select sections you want
3. Wait for crawling to complete
4. Click **"🔧 Reindex"** to build vector index

### Issue: "Rate limited"

**Cause:** Too many requests to HF API (free tier limited)

**Solution:**
1. Switch to Groq (unlimited free tier)
2. Or upgrade HuggingFace plan

### Issue: Slow Response Time

**Solutions:**
1. Use Groq (fastest) instead of HF
2. Reduce top-k context chunks (sidebar setting)
3. Use smaller model: Mixtral 8x7B instead of Llama 2 70B

---

## 📊 Costs & Limits

| Provider | Cost | Limits | Speed | Quality |
|----------|------|--------|-------|---------|
| **Groq** | FREE ✅ | Unlimited | Fastest | Great |
| HuggingFace | FREE (limited) | ~30k calls/month | Slow | Good |
| Ollama | FREE | Unlimited (local) | Medium | Great |

> **Recommendation**: Use Groq for production Streamlit Cloud deployments

---

## 🚀 Advanced Features

### Auto-Update Scheduler

Enable 24h auto-update in sidebar:

```python
from scheduler import start_scheduler
if auto_update:
    start_scheduler()
```

This re-indexes IRDAI data daily.

### Export Chat History

Users can download chat history as JSON:

```
💾 Export Chat button (bottom of sidebar)
```

### Handle Custom Data Paths

Users can specify system paths:

```
📁 Data Source → Local Folder → Enter path
```

> **Cloud Note:** Streamlit Cloud can't access system paths. Use file upload instead.

---

## 📞 Support & Resources

| Resource | Link |
|----------|------|
| Groq API Docs | https://console.groq.com/docs |
| Streamlit Docs | https://docs.streamlit.io |
| IRDAI Official | https://irdai.gov.in |
| HuggingFace API | https://huggingface.co/inference-api |

---

## ✨ Next Steps

1. **Deploy to Streamlit Cloud** → 5 minutes
2. **Add Groq API key** → Instant
3. **Test the chatbot** → 1 minute
4. **Customize for your needs** → Ongoing

```bash
# Deploy in 3 commands:
git add .
git commit -m "IRDAI chatbot ready for cloud"
git push origin main
# Then deploy via share.streamlit.io
```

---

**Happy deploying! 🚀**

For questions, check the [main README](README.md) or project documentation.
