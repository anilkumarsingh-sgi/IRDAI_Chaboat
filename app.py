"""
IRDAI Industry Chatbot — Streamlit Application
================================================
Industry-grade chatbot powered by:
  * IRDAI website crawler (all sections)
  * FAISS vector store (RAG)
  * Groq Inference API (FREE UNLIMITED LLM)
  * HuggingFace API (Fallback)
  * Auto-update scheduler
"""

import os, sys, json, time, logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file (local) or use Streamlit secrets (cloud)
load_dotenv()

st.set_page_config(
    page_title="IRDAI Regulatory Chatbot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

Path("logs").mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
:root{--blue:#003087;--orange:#F47920;--light:#E8F0FE;--border:#D1D9E0}
body{font-family:'Segoe UI',sans-serif}
.irdai-header{background:linear-gradient(135deg,#003087,#0070D2);color:#fff;padding:1.5rem 2rem;border-radius:12px;margin-bottom:1.5rem;display:flex;align-items:center;gap:1.5rem;box-shadow:0 4px 20px rgba(0,48,135,.3)}
.irdai-header h1{margin:0;font-size:1.8rem;font-weight:700}
.irdai-header p{margin:.3rem 0 0;opacity:.85;font-size:.95rem}
.irdai-logo{font-size:3rem}
.chat-container{max-height:60vh;overflow-y:auto;padding:1rem;background:#FAFBFC;border:1px solid var(--border);border-radius:12px;margin-bottom:1rem}
.msg-user{background:var(--blue);color:#fff;padding:.8rem 1.2rem;border-radius:18px 18px 4px 18px;margin:.5rem 0 .5rem 15%;font-size:.95rem;box-shadow:0 2px 8px rgba(0,48,135,.2)}
.msg-assistant{background:#fff;color:#1A1A2E;padding:1rem 1.3rem;border-radius:18px 18px 18px 4px;margin:.5rem 15% .5rem 0;border:1px solid var(--border);font-size:.95rem;line-height:1.65;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.msg-meta{font-size:.72rem;color:#888;margin-top:.4rem}
.msg-sources{background:var(--light);border-left:3px solid var(--blue);padding:.6rem 1rem;border-radius:0 8px 8px 0;margin-top:.8rem;font-size:.8rem}
.msg-sources strong{color:var(--blue)}
.stat-card{background:#fff;border:1px solid var(--border);border-radius:10px;padding:1rem 1.2rem;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.05)}
.stat-card .number{font-size:2rem;font-weight:700;color:var(--blue)}
.stat-card .label{font-size:.8rem;color:#666;margin-top:.2rem}
.badge{display:inline-block;padding:.2rem .7rem;border-radius:20px;font-size:.78rem;font-weight:600}
.badge-green{background:#D4EDDA;color:#155724}
.badge-yellow{background:#FFF3CD;color:#856404}
.disclaimer{background:#FFF8E1;border:1px solid #FFE082;border-radius:8px;padding:.8rem 1rem;font-size:.8rem;color:#5D4037;margin-top:1rem}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
# Get API keys from environment or Streamlit secrets (for cloud deployment)
def get_api_keys():
    """Get API keys from environment or Streamlit secrets."""
    keys = {
        "groq": os.getenv("GROQ_API_KEY", ""),
        "hf": os.getenv("HF_API_KEY", ""),
    }
    
    # Try Streamlit secrets (cloud deployment)
    if hasattr(st, "secrets"):
        try:
            keys["groq"] = keys["groq"] or st.secrets.get("GROQ_API_KEY", "")
            keys["hf"] = keys["hf"] or st.secrets.get("HF_API_KEY", "")
        except:
            pass
    
    return keys

def get_hf_api_key():
    """Get HF API key from environment or Streamlit secrets."""
    # Try .env file first (local development)
    api_key = os.getenv("HF_API_KEY", "")
    # If not found, try Streamlit secrets (cloud deployment)
    if not api_key and hasattr(st, "secrets"):
        try:
            api_key = st.secrets.get("HF_API_KEY", "")
        except:
            pass
    return api_key

api_keys = get_api_keys()

defaults = {
    "messages": [],
    "vs_ready": False,
    "vs_stats": {},
    "chat_count": 0,
    "groq_api_key": api_keys["groq"],
    "hf_api_key": api_keys["hf"],
    "selected_q": "",
    "data_dir": None,  # Start with None, default to 'data' folder when needed
    "llm_provider": "groq" if api_keys["groq"] else "hf",  # Default to Groq if available
    "trigger_submit": False,
    "voice_active": False,
    "llm_model": "",
    # Analytics
    "session_start_time": datetime.now(),
    "queries_answered": 0,
    "avg_response_time": 0,
    "feedback_score": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Load resources ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_vs(data_dir: Optional[str] = None):
    from rag_pipeline import get_vector_store
    return get_vector_store(data_dir=data_dir)

@st.cache_resource(show_spinner=False)
def load_llm(provider: str = "groq", groq_key: str = "", hf_key: str = ""):
    from hf_client import LLMClient
    
    api_key = ""
    if provider == "groq":
        api_key = groq_key
    elif provider == "hf":
        api_key = hf_key
    
    return LLMClient(api_key=api_key, provider=provider)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ IRDAI Chatbot")
    
    # Prepared By Panel
    st.markdown("""
    <div style="background: linear-gradient(135deg, #003087, #0070D2); color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; text-align: center;">
        <strong style="font-size: 0.9rem;">📋 Prepared By</strong><br/>
        <span style="font-size: 0.85rem; font-weight: 600;">Shriram General Insurance</span><br/>
        <span style="font-size: 0.8rem; color: #E8F0FE;">(Dr. Anil Kumar Singh)</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    st.markdown("#### 🔑 LLM Configuration")
    
    # Provider selection
    provider_choice = st.radio(
        "LLM Provider",
        ["🔥 Groq (FREE & FAST)", "🤗 HuggingFace"],
        help="Groq: Free, unlimited, 500+ tokens/sec. Recommended for cloud."
    )
    
    if provider_choice.startswith("🔥"):
        st.session_state.llm_provider = "groq"
        
        if st.session_state.groq_api_key:
            st.success("✅ Groq API key loaded")
            show_override = st.checkbox("Change Groq key", key="override_groq")
            if show_override:
                groq_key = st.text_input("Groq API Key", value="", type="password", placeholder="gsk_...")
                if groq_key and groq_key != st.session_state.groq_api_key:
                    st.session_state.groq_api_key = groq_key
                    st.cache_resource.clear()
        else:
            st.warning("⚠️ No Groq API key found")
            groq_key = st.text_input(
                "Groq API Key",
                value="",
                type="password",
                placeholder="Get free key at groq.com"
            )
            if groq_key:
                st.session_state.groq_api_key = groq_key
                st.cache_resource.clear()
                st.success("✅ Groq key configured!")
        
        st.markdown(
            "[Get Free Groq API Key ↗](https://groq.com)",
            unsafe_allow_html=True
        )
    
    else:  # HuggingFace
        st.session_state.llm_provider = "hf"
        
        if st.session_state.hf_api_key:
            st.success("✅ HF API key loaded")
            show_override = st.checkbox("Change HF key", key="override_hf")
            if show_override:
                hf_key = st.text_input("HF API Key", value="", type="password", placeholder="hf_...")
                if hf_key and hf_key != st.session_state.hf_api_key:
                    st.session_state.hf_api_key = hf_key
                    st.cache_resource.clear()
        else:
            st.warning("⚠️ No HF API key found (note: free tier is limited)")
            hf_key = st.text_input(
                "HF API Key",
                value="",
                type="password",
                placeholder="Get key at huggingface.co"
            )
            if hf_key:
                st.session_state.hf_api_key = hf_key
                st.cache_resource.clear()
                st.success("✅ HF key configured!")
        
        st.markdown(
            "[Get HuggingFace API Key ↗](https://huggingface.co/settings/tokens)",
            unsafe_allow_html=True
        )
    
    data_source = st.radio(
        "Choose data source:",
        ["Default (IRDAI)", "Local Folder", "Google Drive", "Upload Files"],
        help="Select where your data comes from"
    )
    
    if data_source == "Local Folder":
        data_dir = st.text_input(
            "Folder Path",
            value=st.session_state.data_dir or "",
            placeholder="e.g. C:\\data\\irdai or /home/user/irdai",
            help="Path to folder containing crawled_data.json and pdfs/ subfolder"
        )
        if data_dir and data_dir.strip():
            data_dir = data_dir.strip()
            if data_dir != st.session_state.data_dir:
                st.session_state.data_dir = data_dir
                st.cache_resource.clear()
                st.info(f"✅ Data folder set to: {data_dir}")
                st.info("Click 🔧 Reindex below to build the knowledge base")
        elif data_dir == "" and st.session_state.data_dir:
            st.session_state.data_dir = None
            st.cache_resource.clear()
    
    elif data_source == "Google Drive":
        st.info("📌 To use Google Drive data:")
        st.markdown("""
        1. Share your Google Drive folder with public access (anyone with link)
        2. Get the folder ID from the URL: `https://drive.google.com/drive/folders/FOLDER_ID`
        3. Paste it below
        """)
        gdrive_folder_id = st.text_input(
            "Google Drive Folder ID",
            placeholder="e.g. 1A4x5VzG3kH4jk5L6mN7oP8qR9sT0uV1w",
            help="The folder should contain crawled_data.json and pdfs/"
        )
        if gdrive_folder_id:
            try:
                # Create Google Drive data directory
                gdrive_data_path = f"gdrive://{gdrive_folder_id}"
                if gdrive_data_path != st.session_state.data_dir:
                    st.session_state.data_dir = gdrive_data_path
                    st.cache_resource.clear()
                    st.success(f"✅ Google Drive folder set!")
            except Exception as e:
                st.error(f"Error: {e}")
    
    elif data_source == "Upload Files":
        st.info("📌 Upload your data files:")
        uploaded_files = st.file_uploader(
            "Upload JSON and PDF files",
            type=["json", "pdf"],
            accept_multiple_files=True,
            help="Upload your crawled_data.json and PDF files"
        )
        if uploaded_files:
            # Create temp directory for uploaded files
            temp_dir = Path("data/uploaded")
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Save uploaded files
            for file in uploaded_files:
                file_path = temp_dir / file.name
                file_path.write_bytes(file.read())
            
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded!")
            st.session_state.data_dir = str(temp_dir.parent)
            st.cache_resource.clear()
    
    else:  # Default (IRDAI)
        if st.session_state.data_dir:
            st.session_state.data_dir = None
            st.cache_resource.clear()
        st.info("Using default IRDAI regulatory data")

    st.markdown("#### 🤖 Model Selection")
    
    if st.session_state.llm_provider == "groq":
        from hf_client import GROQ_MODELS
        model_names = list(GROQ_MODELS.keys())
        descriptions = list(GROQ_MODELS.values())
        model_options = [f"🔥 {name}: {desc}" for name, desc in zip(model_names, descriptions)]
        
        selected_model_display = st.selectbox(
            "Groq Model",
            model_options,
            help="Mixtral 8x7B: Fastest. Llama 2 70B: Best quality."
        )
        st.session_state.llm_model = selected_model_display.split(":")[0].replace("🔥 ", "").strip()
    else:
        from hf_client import HF_MODELS
        model_names = list(HF_MODELS.keys())
        
        default_model = "mistralai/Mistral-7B-Instruct-v0.1"
        model_choice = st.selectbox(
            "HuggingFace Model",
            model_names,
            index=model_names.index(default_model) if default_model in model_names else 0
        )
        st.session_state.llm_model = model_choice

    st.markdown("#### ⚙️ Settings")
    top_k     = st.slider("Context chunks (top-k)", 1, 5, 3)  # Reduced: 5→3 to avoid context overflow
    max_tokens= st.slider("Max tokens", 256, 1024, 600)  # Reduced: 2048→1024, default 800→600 for Groq limit
    temperature=st.slider("Temperature", 0.0, 1.0, 0.3, 0.05)

    st.markdown("#### 📚 Knowledge Base")
    if st.session_state.vs_ready:
        vs_s = st.session_state.vs_stats
        st.markdown(f'<span class="badge badge-green">✅ Ready — {vs_s.get("total_vectors",0):,} vectors</span>', unsafe_allow_html=True)
        st.caption(f"Sections: {', '.join(vs_s.get('sections',[]))[:100]}")
    else:
        st.markdown('<span class="badge badge-yellow">⚠️ Not indexed yet</span>', unsafe_allow_html=True)

    st.markdown("#### 🕷️ Crawler")
    from crawler import IRDAI_SECTIONS
    section_labels = [s.split("/")[-1] for s in IRDAI_SECTIONS]
    selected_labels = st.multiselect("Sections", section_labels, default=section_labels[:5])
    selected_paths  = [s for s in IRDAI_SECTIONS if s.split("/")[-1] in selected_labels]

    col1, col2 = st.columns(2)
    with col1: start_crawl = st.button("▶ Crawl", use_container_width=True, type="primary")
    with col2: rebuild_idx = st.button("🔧 Reindex", use_container_width=True)

    auto_update = st.toggle("Auto-update (24h)", False)

    st.markdown("---")
    if st.session_state.messages:
        st.download_button(
            "💾 Export Chat",
            json.dumps(st.session_state.messages, indent=2),
            file_name=f"irdai_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True,
        )
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Init resources ────────────────────────────────────────────────────────────
# Lazy load vector store - check if index exists without building
from pathlib import Path
index_exists = False
# Use provided data_dir or default to the 'data' folder in the current directory
if st.session_state.data_dir:
    vs_path = Path(st.session_state.data_dir) / "vectorstore" / "irdai.faiss"
else:
    # Default to local 'data' folder (e.g., e:\IRDAI_chatboat_new\data)
    vs_path = Path("data/vectorstore/embeddings.npy")
index_exists = vs_path.exists()

if index_exists:
    with st.spinner("Loading knowledge base..."):
        try:
            vs = load_vs(st.session_state.data_dir)
            if vs.is_ready:
                st.session_state.vs_ready = True
                st.session_state.vs_stats = vs.stats
            else:
                vs = None
                st.session_state.vs_ready = False
        except Exception as e:
            st.warning(f"Could not load vectorstore: {e}")
            vs = None
            st.session_state.vs_ready = False
else:
    vs = None
    st.session_state.vs_ready = False

hf = load_llm(
    provider=st.session_state.llm_provider,
    groq_key=st.session_state.groq_api_key,
    hf_key=st.session_state.hf_api_key
)

# ── Crawl actions ─────────────────────────────────────────────────────────────
if start_crawl:
    with st.status("🕷️ Crawling IRDAI...", expanded=True) as s:
        try:
            from crawler import IRDAICrawler
            c = IRDAICrawler()
            c.run(sections=selected_paths)
            st.write(f"✅ {c.stats['pages_crawled']} pages, {c.stats['pdfs_downloaded']} PDFs")
            st.write("🔧 Building index...")
            from rag_pipeline import rebuild_vector_store
            new_vs = rebuild_vector_store(st.session_state.data_dir)
            st.cache_resource.clear()
            st.session_state.vs_ready = True
            st.session_state.vs_stats = new_vs.stats
            s.update(label="✅ Done!", state="complete")
            st.rerun()
        except Exception as e:
            s.update(label=f"❌ {e}", state="error")

if rebuild_idx:
    if not st.session_state.data_dir:
        st.error("❌ No data folder selected. Please select 'Local Folder' and provide a path first.")
    else:
        with st.spinner(f"Rebuilding index from {st.session_state.data_dir}..."):
            try:
                from rag_pipeline import rebuild_vector_store
                new_vs = rebuild_vector_store(st.session_state.data_dir)
                st.cache_resource.clear()
                
                if new_vs.is_ready and len(new_vs.chunks) > 0:
                    st.session_state.vs_ready = True
                    st.session_state.vs_stats = new_vs.stats
                    st.success(f"✅ Rebuilt! {len(new_vs.chunks):,} chunks indexed")
                    st.rerun()
                else:
                    st.warning(f"⚠️ No documents found in {st.session_state.data_dir}")
                    st.info("Make sure the folder contains PDFs in a 'pdfs/' subfolder or crawled_data.json")
            except Exception as e:
                st.error(f"❌ Error rebuilding index: {str(e)[:200]}")

if auto_update:
    from scheduler import start_scheduler
    start_scheduler()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="irdai-header">
  <div class="irdai-logo">🛡️</div>
  <div>
    <h1>IRDAI Regulatory Intelligence Chatbot</h1>
    <p>Industry-grade AI assistant • Regulations • Circulars • Guidelines • Annual Reports</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── API Availability Notice ────────────────────────────────────────────────────
with st.container():
    import os
    if not os.getenv("GROQ_API_KEY"):
        st.info(
            "💡 **Tip:** For better model availability and faster responses, "
            "set up a free Groq API key (groq.com) in the sidebar's API Keys section."
        )

# ── Stats row ─────────────────────────────────────────────────────────────────
c1,c2,c3,c4 = st.columns(4)
vs_s = st.session_state.vs_stats
with c1: st.markdown(f'<div class="stat-card"><div class="number">{vs_s.get("total_vectors",0):,}</div><div class="label">Indexed Chunks</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="stat-card"><div class="number">{len(vs_s.get("sections",[]))}</div><div class="label">Sections</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="stat-card"><div class="number">{st.session_state.chat_count}</div><div class="label">Questions Asked</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="stat-card"><div class="number" style="font-size:1.3rem">{"🟢 Ready" if st.session_state.vs_ready else "🟡 Pending"}</div><div class="label">Knowledge Base</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Quick Questions ───────────────────────────────────────────────────────────
QUICK_QS = [
    "Capital requirements for insurance company?",
    "How to file IRDAI complaint?",
    "Latest motor insurance regulations?",
    "What is Bima Sugam?",
    "Health insurance portability rules?",
]
st.markdown("**💡 Quick Questions:**")
qcols = st.columns(5)
for i, q in enumerate(QUICK_QS):
    with qcols[i]:
        if st.button(q, key=f"qq_{i}", use_container_width=True):
            st.session_state.selected_q = q
            st.session_state.trigger_submit = True
            st.rerun()

# ── Chat + Context layout ─────────────────────────────────────────────────────
chat_col, ctx_col = st.columns([2, 1])

with chat_col:
    st.markdown("### 💬 Chat")

    # Check if knowledge base needs to be loaded
    if not st.session_state.vs_ready and vs is None:
        st.warning("⚠️ Knowledge base not indexed yet. Build it using the 🔧 Reindex button in the sidebar.")
        st.info("Once indexed, you can start asking questions.")
    
    # Render messages
    html = '<div class="chat-container">'
    if not st.session_state.messages:
        html += """<div style="text-align:center;color:#888;padding:3rem 1rem">
            <div style="font-size:3rem">🛡️</div>
            <h3 style="color:#003087">Welcome to IRDAI Regulatory Chatbot</h3>
            <p>Ask about IRDAI regulations, circulars, guidelines, consumer rights, compliance requirements.</p>
        </div>"""
    for msg in st.session_state.messages:
        role, content, ts = msg["role"], msg["content"], msg.get("timestamp","")
        if role == "user":
            # Escape HTML for user messages
            import html as html_module
            escaped_content = html_module.escape(content)
            html += f'<div class="msg-user">{escaped_content}<div class="msg-meta">You • {ts}</div></div>'
        else:
            srcs_html = ""
            if msg.get("sources"):
                items = "".join(f'<div>📄 {(s.get("title") or s.get("source",""))[:55]} <span style="color:#888">({s.get("section","")})</span></div>' for s in msg["sources"][:3])
                srcs_html = f'<div class="msg-sources"><strong>Sources:</strong>{items}</div>'
            # Escape HTML for assistant messages and convert newlines to <br>
            import html as html_module
            escaped_content = html_module.escape(content)
            content_html = escaped_content.replace("\n", "<br>")
            html += f'<div class="msg-assistant">{content_html}{srcs_html}<div class="msg-meta">IRDAI Bot • {ts}</div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

    # Input form
    col_text, col_voice = st.columns([4, 1])
    
    with col_text:
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Your question",
                value=st.session_state.selected_q,
                placeholder="e.g. What are solvency margin requirements for life insurers?",
            )
            submitted = st.form_submit_button("Send ➤", use_container_width=True, type="primary")
    
    with col_voice:
        st.write("")
        if st.button("🎤 Voice", use_container_width=True, help="Click to record in any language"):
            st.session_state.voice_active = True
    
    # Voice input handler with multi-language support
    if st.session_state.get("voice_active"):
        st.info("🎙️ Recording... Speak in English, Hindi, Marathi or any language")
        
        # Language selection
        voice_lang = st.selectbox(
            "Language (optional):",
            ["Auto-detect", "English (en-US)", "Hindi (hi-IN)", "Marathi (mr-IN)", "Tamil (ta-IN)", "Telugu (te-IN)"],
            key="voice_lang"
        )
        
        audio_data = st.audio_input("Record your question", label_visibility="collapsed")
        if audio_data:
            try:
                import speech_recognition as sr
                from io import BytesIO
                import numpy as np
                
                recognizer = sr.Recognizer()
                
                # Convert audio bytes to WAV format for better compatibility
                audio_bytes = BytesIO(audio_data.getvalue())
                
                # Map language selector to language code
                lang_map = {
                    "Auto-detect": "en-US",
                    "English (en-US)": "en-US",
                    "Hindi (hi-IN)": "hi-IN",
                    "Marathi (mr-IN)": "mr-IN",
                    "Tamil (ta-IN)": "ta-IN",
                    "Telugu (te-IN)": "te-IN",
                }
                
                lang_code = lang_map.get(voice_lang, "en-US")
                
                with st.spinner("🔄 Converting speech to text..."):
                    try:
                        # Use AudioFile context manager correctly
                        with sr.AudioFile(audio_bytes) as source:
                            audio = recognizer.record(source)
                        
                        # Recognize speech
                        text = recognizer.recognize_google(audio, language=lang_code)
                        st.success(f"✅ Recognized ({voice_lang}): '{text}'")
                        
                        # Translate to English if needed
                        if voice_lang not in ["Auto-detect", "English (en-US)"]:
                            with st.spinner("🌐 Translating to English..."):
                                try:
                                    import requests
                                    response = requests.post(
                                        'https://api.mymemory.translated.net/get',
                                        params={'q': text, 'langpair': f'{lang_code.split("-")[0]}|en'},
                                        timeout=5
                                    )
                                    if response.status_code == 200:
                                        translated = response.json()['responseData']['translatedText']
                                        st.success(f"✅ Translated to English: '{translated}'")
                                        text = translated
                                    else:
                                        st.warning(f"⚠️ Translation skipped. Using: '{text}'")
                                except Exception as trans_err:
                                    st.warning(f"⚠️ Translation failed. Using original: '{text}'")
                        
                        # Store the question and trigger submission
                        st.session_state.selected_q = text
                        st.session_state.voice_active = False
                        st.rerun()
                        
                    except sr.UnknownValueError:
                        st.error("❌ Could not understand audio. Please speak clearly and try again.")
                        st.session_state.voice_active = False
                    except sr.RequestError as e:
                        st.error(f"❌ Speech recognition error: {str(e)[:100]}. Please try typing instead.")
                        st.session_state.voice_active = False
            except Exception as e:
                st.error(f"❌ Voice error: {str(e)[:150]}. Please type your question instead.")
                st.session_state.voice_active = False

    # Process (auto-trigger if quick question selected or form submitted)
    submitted = submitted or st.session_state.get("trigger_submit", False)
    st.session_state.trigger_submit = False
    
    if submitted and user_input.strip():
        q = user_input.strip()
        ts = datetime.now().strftime("%H:%M")
        st.session_state.messages.append({"role":"user","content":q,"timestamp":ts})
        st.session_state.chat_count += 1

        with st.spinner("🔍 Searching knowledge base..."):
            sources = []
            # Load vector store on demand if not already loaded
            if vs is None and index_exists:
                vs = load_vs(st.session_state.data_dir)
            
            if vs and vs.is_ready:
                results = vs.search(q, k=top_k)
                context = "\n\n".join(f"[{m['title'] or m['source']}]\n{chunk}" for chunk,m,_ in results)
                sources = [m for _,m,_ in results]
            else:
                context = "Knowledge base not yet indexed. Please run the crawler first via the sidebar."

        with st.spinner("🤖 Generating response..."):
            hf.model = st.session_state.llm_model or hf.model
            answer = hf.ask(q, context, max_tokens=max_tokens, temperature=temperature)

        st.session_state.messages.append({
            "role":"assistant","content":answer,
            "sources":sources,"timestamp":datetime.now().strftime("%H:%M")
        })
        # Reset voice state and selected_q after successful submission
        st.session_state.selected_q = ""
        st.session_state.voice_active = False
        st.rerun()

with ctx_col:
    st.markdown("### 📋 Sources")
    last_user = next((m for m in reversed(st.session_state.messages) if m["role"]=="user"), None)
    if last_user:
        # Load vector store on demand if not already loaded
        if vs is None and index_exists:
            vs = load_vs(st.session_state.data_dir)
        
        if vs and vs.is_ready:
            for i,(chunk,meta,score) in enumerate(vs.search(last_user["content"],k=3),1):
                with st.expander(f"📄 {(meta.get('title') or 'Doc')[:35]}... ({score:.2f})"):
                    st.markdown(f"**Section:** `{meta.get('section','N/A')}`")
                    st.markdown(f"**Type:** `{meta.get('type','N/A')}`")
                    if str(meta.get('source','')).startswith('http'):
                        st.markdown(f"[Open Source ↗]({meta['source']})")
                    st.markdown(f"> {chunk[:350]}...")
    else:
        st.info("Sources will appear here after asking a question.")

    st.markdown("---")
    st.markdown("### 🗂️ Sections")
    for sec in sorted(st.session_state.vs_stats.get("sections",[])):
        st.markdown(f"- 📁 `{sec}`")

    st.markdown("---")
    st.markdown("### 📡 Crawler Log")
    log_path = Path("logs/crawler.log")
    if log_path.exists():
        lines = log_path.read_text().splitlines()
        st.code("\n".join(lines[-12:]), language=None)
    else:
        st.caption("No log yet — run the crawler.")

# ── Disclaimer & Analytics Footer ────────────────────────────────────────────────────────────────
# Calculate session metrics
session_duration = (datetime.now() - st.session_state.get("session_start_time", datetime.now())).total_seconds()
session_minutes = int(session_duration // 60)

# Analytics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Questions Asked", st.session_state.chat_count, delta=None)
with col2:
    st.metric("Session Time", f"{session_minutes}m", delta=None)
with col3:
    model_name = st.session_state.llm_model or "Default"
    st.metric("Model", model_name.split("/")[-1][:15], delta=None)
with col4:
    kb_status = "✅ Ready" if st.session_state.vs_ready else "⏳ Loading"
    st.metric("Knowledge Base", kb_status, delta=None)

st.markdown("""
<div class="disclaimer">
<strong>⚠️ Legal Disclaimer:</strong> This chatbot provides informational guidance based on IRDAI official documents. 
It is <strong>not a substitute for legal or professional advice</strong>. Always verify critical information 
at <a href="https://irdai.gov.in" target="_blank" style="color: #003087; font-weight: bold;">irdai.gov.in</a>.

<strong>Accuracy:</strong> While we strive for accuracy, IRDAI regulations can be updated. For the latest information, 
consult official IRDAI publications.
</div>

<div style="text-align:center; color:#666; font-size:.75rem; padding:2rem 0 1rem; border-top: 1px solid #ddd; margin-top: 1rem;">
<strong>IRDAI Regulatory Intelligence Chatbot</strong> • Powered by Groq API (Free Unlimited) • Vector Search • Llama 3.1 LLM<br/>
Version 2.0 (Industry) • Knowledge Base: {total_chunks:,} Chunks • Last Updated: {last_updated}<br/>
<a href="https://irdai.gov.in" target="_blank" style="color: #003087; text-decoration: none;">📖 IRDAI Official Portal</a> • 
<a href="https://github.com" target="_blank" style="color: #003087; text-decoration: none;">💻 GitHub</a> • 
© 2026 IRDAI Compliance Assistant
</div>
""".format(
    total_chunks=st.session_state.vs_stats.get("total_vectors", 0),
    last_updated=datetime.now().strftime("%B %d, %Y")
), unsafe_allow_html=True)
