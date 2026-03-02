# ⚡ Quick Start - Deploy in 5 Minutes

Want to deploy the IRDAI Chatbot to **Streamlit Cloud** with unlimited free LLM? Follow these simple steps.

---

## Step 1: Get Free API Key (2 minutes)

1. Go to **https://groq.com**
2. Click **"Sign Up"**
3. Create account (email + password)
4. Go to **API Keys** from dashboard
5. Click **"Create API Key"**
6. Copy the key (starts with `gsk_`)
7. Save it somewhere safe

**That's your free, unlimited LLM key!** ✅

---

## Step 2: Fork on GitHub (1 minute)

1. If you don't have a GitHub account, create one: https://github.com/signup
2. Go to the IRDAI Chatbot repository
3. Click **"Fork"** (top right)
4. Now you have your own copy!

---

## Step 3: Deploy to Streamlit Cloud (2 minutes)

1. Go to **https://share.streamlit.io**
2. Click **"Sign up"** (or login if you have account)
3. Click **"Create app"**
4. Select your GitHub account
5. Choose the forked repository
6. Set **main file path** to: `app.py`
7. Choose **branch**: `main`
8. Click **"Deploy"**

Streamlit will start building... (takes 1-2 minutes)

---

## Step 4: Add Your API Key (1 minute)

Once deployed, Streamlit shows your app URL: `https://share.streamlit.io/YOUR_USERNAME/irdai-chatbot`

Now add the Groq API key:

1. Click **gear icon** (⚙️) → **Settings**
2. Go to **"Secrets"** tab
3. Paste this (replace with your actual key):

```toml
GROQ_API_KEY = "gsk_YOUR_KEY_HERE"
```

4. Click **"Save"**
5. Streamlit will restart automatically

---

## Step 5: Start Using! (Immediate)

1. Refresh your app page
2. In the sidebar, you'll see:
   - ✅ Groq API loaded
   - 🤖 Model selection
   - 📁 Data source options
3. Click the **"Local Folder"** option if you have custom data, or use **"Default (IRDAI)"**
4. Type a question in the chat box
5. Watch the AI respond! 🎉

---

## 🎯 What You Get

✅ Professional chatbot deployed to the cloud  
✅ Completely free (Groq API costs $0)  
✅ Unlimited requests (no rate limits)  
✅ Talk about IRDAI regulations, guidelines, etc.  
✅ Data persists between sessions  
✅ Works on mobile too!

---

## 📋 Sample Questions to Try

After deployment, ask your chatbot:

- "What are the capital requirements for a new insurance company?"
- "How do I file a complaint with IRDAI?"
- "What is Bima Sugam?"
- "Explain health insurance portability rules"
- "What are solvency margin requirements?"

---

## 🔥 Pro Tips

### Tip 1: Use Custom Data
In the sidebar, select **"📁 Local Folder"** and provide path to your dataset (if you have one).

### Tip 2: Multiple Versions
Create multiple apps from same repo (just fork again):
- One for testing
- One for production
- One for specific dataset

### Tip 3: Share Easily
Your app URL is publicly shareable:
```
https://share.streamlit.io/YOUR_USERNAME/irdai-chatbot
```

Send this link to colleagues/friends!

### Tip 4: Monitor Usage
Groq gives you free API usage monitor at https://console.groq.com

---

## ❌ Troubleshooting

### Problem: "No API key found"

**Solution:**
1. Go to your app settings → Secrets
2. Check that `GROQ_API_KEY` is there
3. Restart app (reload page)

### Problem: "Groq API error"

**Solution:**
1. Check if API key is correct (starts with `gsk_`)
2. Make sure you copied the full key
3. Verify at https://console.groq.com/keys

### Problem: "Knowledge base not indexed"

**Solution:**
1. Click **"▶ Crawl"** button in sidebar
2. Select some sections (e.g., "regulations")
3. Wait for crawl to finish
4. Click **"🔧 Reindex"**

### Problem: Slow responses

**Solution:**
1. Check your internet connection
2. Try again (Groq is fast, usually instant)
3. Reduce "Context chunks" in sidebar

---

## 🆘 Still Need Help?

1. Check main [README.md](README.md)
2. See detailed [STREAMLIT_CLOUD_GUIDE.md](STREAMLIT_CLOUD_GUIDE.md)
3. Visit Groq docs: https://console.groq.com/docs

---

## 🎉 You're Done!

Your IRDAI chatbot is now live on the cloud! Send the Streamlit URL to anyone and they can start chatting.

**Next steps:**
- Customize the description/title
- Add your own data
- Share with your team
- Enjoy unlimited free LLM! 🚀

---

**Happy chatting!** If you need more features, check out the full documentation in the repo.
