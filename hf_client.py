"""
LLM Client for IRDAI Chatbot
Supports multiple APIs:
  1. Groq (FREE, UNLIMITED, RECOMMENDED) - Best performance
  2. HuggingFace Inference API - Fallback option
  3. Ollama - For local deployment
"""

import os
import re
import logging
import requests
import hashlib
from typing import Iterator, Optional
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# API Keys - Load from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
HF_API_KEY = os.getenv("HF_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Simple response cache (in-memory)
_response_cache = {}
_cache_ttl = 3600  # 1 hour

def _get_cache_key(question: str, context: str) -> str:
    """Generate cache key from question"""
    return hashlib.md5(question.encode()).hexdigest()

def _get_cached_response(question: str) -> Optional[str]:
    """Get response from cache if available and not expired"""
    key = _get_cache_key(question, "")
    if key in _response_cache:
        response_data = _response_cache[key]
        # Check if not expired
        if (datetime.now() - response_data['timestamp']).total_seconds() < _cache_ttl:
            logger.info(f"✅ Cache hit for: {question[:50]}...")
            return response_data['response']
        else:
            del _response_cache[key]
    return None

def _cache_response(question: str, response: str):
    """Cache response for future queries"""
    key = _get_cache_key(question, "")
    _response_cache[key] = {
        'response': response,
        'timestamp': datetime.now(),
        'question': question[:100]
    }

# Models by provider
GROQ_MODELS = {
    "llama-3.1-8b-instant": "Llama 3.1 8B (Fast, Recommended)",
    "llama-3.3-70b-versatile": "Llama 3.3 70B (More Powerful)",
}

HF_MODELS = {
    "mistralai/Mistral-7B-Instruct-v0.1": "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
    "gpt2": "https://api-inference.huggingface.co/models/gpt2",
}

# All available models (for UI display)
MODELS = {
    **{f"groq/{k}": f"🔥 Groq: {v}" for k, v in GROQ_MODELS.items()},
    **{k: f"🤗 HF: {k}" for k in HF_MODELS.keys()},
}


SYSTEM_PROMPT = """You are an expert AI assistant for IRDAI (Insurance Regulatory and Development Authority of India) compliance and insurance regulations.

[CORE INSTRUCTIONS]
ACCURACY FIRST:
- Answer ONLY from provided context - never add external knowledge
- Cite exact regulation/section numbers
- Use precise legal language
- Flag ambiguities immediately

RESPONSE FORMAT:
1. DIRECT ANSWER (1-2 sentences)
2. REGULATION CITATION (section/regulation name)
3. KEY DETAILS (bullet points if multiple)
4. IMPORTANT NOTE (if applicable)

STYLE GUIDELINES:
- Professional, precise, concise
- Use technical terminology
- No assumptions or interpretations beyond document scope
- If unsure: "Not found in provided documents. Check irdai.gov.in"

INVALID REQUESTS:
- For non-IRDAI questions, respond: "This is outside IRDAI domain. Focus on insurance regulations."

[CITATION FORMAT]
When citing: Use "IRDAI [Type] [Year]: [Section]"
Example: "IRDAI Regulations 2016, Section 4.2"
"""




class LLMClient:
    """Universal LLM client supporting Groq, HF, and Ollama"""
    
    def __init__(self, api_key: str = "", provider: str = "groq", model: str = ""):
        """
        Initialize LLM client.
        
        Args:
            api_key: API key for the provider
            provider: 'groq', 'hf', or 'ollama'
            model: Model name/ID
        """
        self.api_key = api_key
        self.provider = provider
        self.model = model or self._get_default_model(provider)
        
        # Validate and set up
        self._validate_and_setup()
    
    def _get_default_model(self, provider: str) -> str:
        """Get default model for provider"""
        if provider == "groq":
            return "llama-3.1-8b-instant"  # Fast and reliable
        elif provider == "hf":
            return "mistralai/Mistral-7B-Instruct-v0.1"
        elif provider == "ollama":
            return "mistral"
        return ""
    
    def _validate_and_setup(self):
        """Validate provider and API key"""
        if self.provider == "groq" and not self.api_key:
            # Try to get from environment
            self.api_key = GROQ_API_KEY
            if not self.api_key:
                logger.warning("⚠️ No Groq API key found. Get one free at https://groq.com")
        
        elif self.provider == "hf" and not self.api_key:
            self.api_key = HF_API_KEY
            if not self.api_key:
                logger.warning("⚠️ No HF API key. Get one at https://huggingface.co/settings/tokens")
        
        elif self.provider == "ollama":
            if not self._check_ollama():
                logger.warning("⚠️ Ollama not running. Start with: ollama serve")
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is running"""
        try:
            resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
            return resp.status_code == 200
        except:
            return False
    
    def _build_prompt(self, question: str, context: str) -> str:
        """Build prompt for the model. Truncate context to prevent request overflow (Groq 413 error)."""
        # Truncate context to max 2500 chars to avoid exceeding Groq API limits
        max_context_chars = 2500
        if len(context) > max_context_chars:
            context = context[:max_context_chars] + "...\n[Context truncated due to length]"
        
        return f"""<s>[INST] <<SYS>>
{SYSTEM_PROMPT}
<</SYS>>

Use the following IRDAI document extracts to answer SPECIFICALLY AND TO-THE-POINT.

CONTEXT:
{context}

QUESTION: {question}

ANSWER DIRECTLY - Be specific, concise, and address the exact question. [/INST]
"""

    def ask(self, question: str, context: str, max_tokens: int = 1024, temperature: float = 0.3) -> str:
        """Ask a question and get a response"""
        # Check cache first
        cached = _get_cached_response(question)
        if cached:
            return cached
        
        if self.provider == "groq":
            response = self._ask_groq(question, context, max_tokens, temperature)
        elif self.provider == "hf":
            response = self._ask_hf(question, context, max_tokens, temperature)
        elif self.provider == "ollama":
            response = self._ask_ollama(question, context, max_tokens, temperature)
        else:
            response = "❌ Unknown provider. Use 'groq', 'hf', or 'ollama'."
        
        # Cache successful responses
        if response and not response.startswith("❌") and not response.startswith("⚠️"):
            _cache_response(question, response)
        
        return response
    
    def _ask_groq(self, question: str, context: str, max_tokens: int, temperature: float) -> str:
        """Use Groq API with production-grade error handling and response formatting"""
        if not self.api_key:
            return "⚠️ Groq API key not configured. Get free key at https://groq.com"
        
        prompt = self._build_prompt(question, context)
        
        try:
            from groq import Groq
            
            client = Groq(api_key=self.api_key)
            
            # Request with proper error handling
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=min(max_tokens, 2048),
                temperature=temperature,
                timeout=60,
            )
            
            text = response.choices[0].message.content.strip()
            logger.info(f"✅ Groq response generated ({len(text)} chars)")
            
            # Add metadata for production use
            formatted_response = self._format_response(text, question)
            return formatted_response
        
        except Exception as e:
            error_msg = str(e).lower()
            
            # Production-grade error handling
            if "401" in error_msg or "unauthorized" in error_msg:
                logger.error(f"AUTH_ERROR: Invalid Groq API key")
                return "❌ **Authentication Error**: Invalid Groq API key.\n\nAction: Update your Groq API key at https://groq.com"
            
            elif "413" in error_msg or "request too large" in error_msg:
                logger.error(f"REQUEST_SIZE: Context too large for model")
                return "❌ **Request Too Large**: The document context exceeds model limits.\n\nTry: Reduce the number of context chunks in Settings (top-k: 1-2)"
            
            elif "429" in error_msg or "rate limit" in error_msg:
                logger.warning(f"RATE_LIMIT: Too many requests")
                return "⏸️ **Rate Limited**: Too many requests. Please wait 30 seconds and try again."
            
            elif "timeout" in error_msg or "timed out" in error_msg:
                logger.warning(f"TIMEOUT: Request took too long")
                return "⏱️ **Request Timeout**: Server taking too long to respond. Try again in a moment."
            
            elif "404" in error_msg:
                logger.error(f"NOT_FOUND: Model {self.model} not available")
                return f"❌ **Model Error**: {self.model} is not available. Try another model from Settings."
            
            else:
                logger.error(f"UNKNOWN_ERROR: {str(e)[:200]}")
                return f"❌ **Error**: {str(e)[:150]}\n\nPlease try again or contact support."
    
    def _format_response(self, text: str, question: str) -> str:
        """Format response with professional structure"""
        # Clean text
        text = text.strip()
        
        # Ensure it starts with clear answer
        if not text.startswith("**") and not text.startswith("#"):
            # Add formatting if response is plain
            lines = text.split('\n')
            if len(lines) > 1:
                # Multi-line response - format it
                return text
        
        return text
    
    def _ask_hf(self, question: str, context: str, max_tokens: int, temperature: float) -> str:
        """Use HuggingFace Inference API (fallback)"""
        if not self.api_key:
            return "⚠️ HF API key not configured. Get one at https://huggingface.co/settings/tokens"
        
        prompt = self._build_prompt(question, context)
        model_url = HF_MODELS.get(self.model)
        
        if not model_url:
            return f"❌ Unknown HF model: {self.model}"
        
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": min(max_tokens, 512),
                    "temperature": temperature,
                },
            }
            
            resp = requests.post(model_url, headers=headers, json=payload, timeout=120)
            resp.raise_for_status()
            
            data = resp.json()
            if isinstance(data, list) and data:
                text = data[0].get("generated_text", "")
            elif isinstance(data, dict):
                text = data.get("generated_text", str(data))
            else:
                text = str(data)
            
            logger.info("✅ HF response generated")
            return self._clean(text)
        
        except requests.exceptions.Timeout:
            return "⏱️ HF request timed out. Try again."
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            if status == 503:
                return "⏳ Model loading. Wait 30 seconds and try again."
            elif status == 401:
                return "❌ Invalid HF API key"
            elif status == 429:
                return "⚠️ Rate limited. Wait a moment."
            else:
                return f"❌ HF error {status}"
        except Exception as e:
            logger.error(f"HF error: {e}")
            return f"❌ Error: {str(e)[:100]}"
    
    def _ask_ollama(self, question: str, context: str, max_tokens: int, temperature: float) -> str:
        """Use Ollama (local)"""
        prompt = self._build_prompt(question, context)
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature,
            }
            
            resp = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            
            data = resp.json()
            text = data.get("response", "")
            logger.info("✅ Ollama response generated")
            return self._clean(text)
        
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return f"❌ Ollama error: {str(e)}"
    
    def _clean(self, text: str) -> str:
        """Remove prompt echoing and artifacts"""
        text = re.sub(r"\[/?INST\]", "", text)
        text = re.sub(r"<</?SYS>>", "", text)
        text = text.strip()
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text
    
    def _offline_fallback(self, question: str, context: str) -> str:
        """Fallback when AI is unavailable"""
        context_snippet = context[:500].strip()
        
        if not context_snippet:
            return (
                "⚠️ AI Response Unavailable\n\n"
                "I couldn't reach the AI service. Please:\n"
                "1. Check your internet connection\n"
                "2. Verify API key in sidebar\n"
                "3. Check https://status.groq.com or https://status.huggingface.co\n\n"
                "See **Sources** panel for documents."
            )
        
        return (
            "⚠️ AI Models Temporarily Unavailable\n\n"
            "Here's relevant content from documents:\n\n"
            f"**From Documents:**\n{context_snippet}...\n\n"
            "**Solutions:**\n"
            "1. Check internet connection\n"
            "2. Verify API configuration\n"
            "3. Try refreshing the page\n\n"
            "See **Sources** panel on right."
        )


# Singleton helper
_client: Optional[LLMClient] = None

def get_llm_client(api_key: str = "", provider: str = "groq", model: str = "") -> LLMClient:
    """Get or create LLM client"""
    global _client
    if _client is None:
        _client = LLMClient(api_key=api_key, provider=provider, model=model)
    return _client


# Backward compatibility - keep old name
HFClient = LLMClient

def get_hf_client() -> LLMClient:
    """Backward compatible function"""
    return get_llm_client()
