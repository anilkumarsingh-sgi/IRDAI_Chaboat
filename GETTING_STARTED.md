# 🎯 Getting Started - Choose Your Path

Your IRDAI Chatbot is now professionally configured and ready for **zero-cost cloud deployment**. Choose your path below:

---

## 🚀 Path 1: Deploy to Streamlit Cloud (Recommended - 5 minutes)

**Best for:** Everyone who wants instant cloud deployment

1. **Read:** [QUICKSTART.md](QUICKSTART.md) - 5 minute guide
2. **Execute:** Follow the 4 simple steps
3. **Done:** Your chatbot is live! ✨

**What you'll get:**
- Public URL anyone can share
- Free hosting on Streamlit Cloud
- Free unlimited LLM (Groq)
- Automatic HTTPS

---

## 💻 Path 2: Run Locally (Development - 2 minutes)

**Best for:** Windows/Mac/Linux users who want to test locally

### Prerequisites
- Python 3.9+ installed
- Git (optional)

### Steps

```bash
# 1. Clone or download the repository
git clone <repo-url>  # or download ZIP
cd IRDAI_chatboat_new

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API key
# Create a file named .env in the same directory with:
# GROQ_API_KEY=gsk_your_key_here
# 
# Or set environment variable:
# Windows: set GROQ_API_KEY=gsk_...
# Mac/Linux: export GROQ_API_KEY=gsk_...

# 4. Run the app
streamlit run app.py
```

**Opens at:** http://localhost:8501

**That's it!** You can now:
- Chat about IRDAI regulations
- Upload custom datasets
- Test different models
- Crawl IRDAI website (if you want)

---

## 🐳 Path 3: Docker Deployment (Advanced - 3 minutes)

**Best for:** DevOps, Docker, or containerized environments

### Prerequisites
- Docker installed
- Docker Compose installed

### Steps

```bash
# 1. Add your API key to .env file
echo "GROQ_API_KEY=gsk_your_key_here" > .env

# 2. Build and run with Docker Compose
docker-compose up --build

# 3. Open http://localhost:8501
```

**Benefits:**
- Consistent environment everywhere
- Easy CI/CD integration
- Production-ready

---

## ✅ Which Path Should I Choose?

| Goal | Path | Time | Difficulty | Cost |
|------|------|------|------------|------|
| **Public chatbot ASAP** | Streamlit Cloud | 5 min | Easy | $0 |
| **Test locally first** | Local | 2 min | Easy | $0 |
| **Production deployment** | Docker | 5 min | Medium | $0+ |
| **Customize heavily** | Local | 10 min | Medium | $0 |

---

## 📋 Pre-Deployment Checklist

Before you start, make sure you have:

- [ ] **Groq API Key** (get free at groq.com)
- [ ] **GitHub account** (for Streamlit Cloud - optional)
- [ ] **Python 3.9+** (for local - optional)
- [ ] **Internet connection** (for everything!)

---

## 🔑 Getting Your Free API Key

### Groq API (Recommended)

```
1. Go to https://groq.com
2. Click "Sign Up" (free)
3. Verify email
4. Go to API Keys
5. Create new key
6. Copy the key (starts with gsk_)
7. Save it safely
```

Takes **2 minutes**, completely free, unlimited requests!

### HuggingFace API (Optional Backup)

```
1. Go to https://huggingface.co/settings/tokens
2. Create new token
3. Copy the token (starts with hf_)
4. Save it safely
```

Optional, for fallback if Groq unavailable (rare).

---

## 🎓 Understanding Your Chatbot

### What It Does
- Searches IRDAI regulatory documents
- Finds relevant passages using AI
- Generates answers with citations
- Works completely offline after indexing

### How It Works
```
Your Question
    ↓
Vector Search (FAISS)
    ↓
Find relevant documents
    ↓
Send to LLM with context
    ↓
LLM generates answer
    ↓
You get response + sources
```

No data is sent to IRDAI or external servers (except LLM API).

### Security
- Your questions go to Groq API (HTTPS encrypted)
- Document data stays local
- No personal data collection
- Open source code (audit it yourself)

---

## 🎯 Sample Questions to Try

After deployment, test with these:

1. **"What are capital requirements for new insurance company?"**
2. **"How do I file a complaint with IRDAI?"**
3. **"What is Bima Sugam?"**
4. **"Explain health insurance portability rules"**
5. **"What are solvency margin requirements?"**

Expected: Answers with citations to official documents

---

## ⚙️ Configuration Options

### Via App Sidebar
- LLM Provider (Groq/HF/Ollama)
- Model selection
- Context chunks (3-10)
- Max tokens (256-2048)
- Temperature (0.0-1.0)
- Data source selection

### Via .env File (Local)
```env
GROQ_API_KEY=gsk_...
HF_API_KEY=hf_...
OLLAMA_BASE_URL=http://localhost:11434
```

### Via Streamlit Secrets (Cloud)
```toml
GROQ_API_KEY = "gsk_..."
HF_API_KEY = "hf_..."
```

---

## 🐛 Common Issues & Solutions

### Issue: "No API key found"

**Solution:**
```bash
# Local: Create .env file
GROQ_API_KEY=gsk_your_actual_key

# Cloud: Add to Streamlit secrets
GROQ_API_KEY = "gsk_your_actual_key"
```

### Issue: "Model not loaded yet"

**Cause:** First request to HF model  
**Solution:** Wait 30 seconds, try again

### Issue: "Knowledge base not indexed"

**Solution:**
1. Click "▶ Crawl" in sidebar
2. Select sections
3. Wait for crawl
4. Click "🔧 Reindex"

### Issue: "Slow responses"

**Solutions:**
1. Try Groq (faster than HF)
2. Reduce context chunks
3. Check internet speed
4. Use Mixtral (faster model)

---

## 📚 Documentation Guide

### For Quick Start
→ [QUICKSTART.md](QUICKSTART.md)

### For Cloud Deployment
→ [STREAMLIT_CLOUD_GUIDE.md](STREAMLIT_CLOUD_GUIDE.md)

### For What's New
→ [WHATS_NEW.md](WHATS_NEW.md)

### For Project Overview
→ [README.md](README.md)

### For API Setup Details
→ [API_SETUP.md](API_SETUP.md)

### For Configuration
→ [CONFIG.md](CONFIG.md)

---

## 💡 Pro Tips

### Tip 1: Use Groq
- Fastest responses
- No rate limits
- Best quality
- Completely free

### Tip 2: Pre-crawl Data
- Faster responses after indexing
- Include with your deployment
- Shared across users

### Tip 3: Share Your App
- Streamlit URL is public
- Easy to share via link
- No authentication needed
- Great for demos

### Tip 4: Monitor API Usage
- Groq: https://console.groq.com/usage
- HF: https://huggingface.co/usage

### Tip 5: Customize Prompt
- Edit system prompt in `hf_client.py`
- Add domain-specific instructions
- Fine-tune responses

---

## 🆘 Need Help?

### Quick Issues
Check [Troubleshooting](TROUBLESHOOTING.md)

### Setup Issues
Check [API_SETUP.md](API_SETUP.md)

### Deployment Issues
Check [STREAMLIT_CLOUD_GUIDE.md](STREAMLIT_CLOUD_GUIDE.md)

### Understanding Code
Check [README.md](README.md) → Architecture section

---

## 🎉 Ready to Go?

### My Recommendation:
1. **Get Groq key** (2 min) - groq.com
2. **Follow QUICKSTART** (5 min) - [QUICKSTART.md](QUICKSTART.md)
3. **Deploy** (1 min) - Click deploy button
4. **Ask questions** (Now!) - Start chatting

**Total time: ~8 minutes**

---

## Next Steps

Choose one:

```
┌─────────────────────────────────────────────┐
│ 1. Deploy to Cloud                          │
│    → Read QUICKSTART.md                     │
│    → Takes 5 minutes                        │
│    → You're live!                           │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ 2. Run Locally                              │
│    → Command line install                   │
│    → Takes 2 minutes                        │
│    → Good for testing                       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ 3. Read Everything                          │
│    → Start with README.md                   │
│    → Then WHATS_NEW.md                      │
│    → Then STREAMLIT_CLOUD_GUIDE.md         │
└─────────────────────────────────────────────┘
```

---

## 🚀 Let's Go!

### For Streamlit Cloud Users:
→ Open [QUICKSTART.md](QUICKSTART.md) and follow the 5 steps

### For Local Development:
→ Run the commands in "Path 2" above

### For Docker:
→ Run the commands in "Path 3" above

---

**Your professional IRDAI chatbot is ready!** 🎉

Questions? Check the docs or open an issue.

**Happy chatting!** 💬
