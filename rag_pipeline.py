"""
RAG Pipeline for IRDAI Chatbot
- Loads crawled HTML text + PDFs
- Chunks documents
- Embeds with sentence-transformers
- Stores in FAISS vector index
- Retrieves top-k context for LLM
"""

import os
import re
import json
import pickle
import logging
import hashlib
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# Default data directories (can be overridden)
# Main IRDAI data directory - contains crawled_data.json, pdfs/, vectorstore/
DEFAULT_DATA_DIR = Path("data")
DEFAULT_PDF_DIR = Path("data/pdfs")
DEFAULT_VS_DIR = Path("data/vectorstore")
DEFAULT_VS_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_SIZE    = 600    # tokens approx
CHUNK_OVERLAP = 100
TOP_K         = 5


# ─── PDF text extractor ───────────────────────────────────────────────────────
def extract_pdf_text(pdf_path: str) -> str:
    try:
        import pypdf
        text_parts = []
        with open(pdf_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
        return "\n".join(text_parts)
    except Exception as e:
        logger.warning(f"pypdf failed for {pdf_path}: {e}")
        return ""


# ─── Text chunker ─────────────────────────────────────────────────────────────
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping word-level chunks."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if len(chunk.strip()) > 50:  # skip tiny chunks
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


# ─── Document loader ──────────────────────────────────────────────────────────
def load_all_documents(data_dir: Optional[str] = None) -> List[Dict]:
    """Load crawled HTML pages + PDFs into unified document list.
    
    Args:
        data_dir: Path to data directory. If None, uses default.
    """
    documents = []
    
    # Use provided data_dir or default
    if data_dir:
        DATA_DIR = Path(data_dir)
        PDF_DIR = Path(data_dir) / "pdfs"
    else:
        DATA_DIR = DEFAULT_DATA_DIR
        PDF_DIR = DEFAULT_PDF_DIR

    # 1) HTML/text from crawler
    crawled_file = DATA_DIR / "crawled_data.json"
    if crawled_file.exists():
        with open(crawled_file, encoding="utf-8") as f:
            pages = json.load(f)
        for page in pages:
            if not page.get("text"):
                continue
            # Add table text
            table_text = ""
            for tbl in page.get("tables", []):
                for row in tbl:
                    table_text += " | ".join(row) + "\n"

            full_text = page["text"]
            if table_text:
                full_text += "\n\nTABLES:\n" + table_text

            documents.append({
                "source": page["url"],
                "title": page.get("title", ""),
                "section": page.get("section", ""),
                "text": full_text,
                "type": "webpage",
                "crawled_at": page.get("crawled_at", ""),
            })
        logger.info(f"Loaded {len(pages)} HTML pages")

    # 2) PDFs
    pdf_count = 0
    for pdf_path in PDF_DIR.rglob("*.pdf"):
        text = extract_pdf_text(str(pdf_path))
        if text and len(text.strip()) > 100:
            section = pdf_path.parent.name
            documents.append({
                "source": str(pdf_path),
                "title": pdf_path.stem.replace("_", " ").replace("-", " "),
                "section": section,
                "text": text,
                "type": "pdf",
                "crawled_at": datetime.fromtimestamp(pdf_path.stat().st_mtime).isoformat(),
            })
            pdf_count += 1
    logger.info(f"Loaded {pdf_count} PDFs")

    return documents


# ─── Vector Store ─────────────────────────────────────────────────────────────
class IRDAIVectorStore:
    def __init__(self):
        self.embeddings = None  # numpy array instead of FAISS index
        self.chunks: List[str] = []
        self.metadata: List[Dict] = []
        self.embedder = None
        self._load_embedder()

    def _load_embedder(self):
        try:
            from sentence_transformers import SentenceTransformer
            # Use a faster, smaller model for better performance
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            logger.info(f"Loading embedder: {model_name}")
            self.embedder = SentenceTransformer(model_name, device="cpu")
            logger.info("✅ Embedder loaded")
        except Exception as e:
            logger.error(f"Embedder load failed: {e}")

    def build(self, documents: List[Dict]):
        """Chunk documents, embed, build numpy-based vector index."""
        logger.info(f"Building vector store from {len(documents)} documents...")
        self.chunks = []
        self.metadata = []

        for doc in documents:
            text_chunks = chunk_text(doc["text"])
            for chunk in text_chunks:
                self.chunks.append(chunk)
                self.metadata.append({
                    "source": doc["source"],
                    "title": doc["title"],
                    "section": doc["section"],
                    "type": doc["type"],
                    "crawled_at": doc.get("crawled_at", ""),
                })

        logger.info(f"Total chunks: {len(self.chunks)}")

        # Embed in batches with progress
        batch_size = 128  # Larger batch for faster processing
        all_embeddings = []
        total_batches = (len(self.chunks) + batch_size - 1) // batch_size
        for i in range(0, len(self.chunks), batch_size):
            batch = self.chunks[i : i + batch_size]
            embs = self.embedder.encode(batch, show_progress_bar=False, normalize_embeddings=True, convert_to_numpy=True)
            all_embeddings.append(embs)
            current_batch = (i // batch_size) + 1
            if current_batch % max(1, total_batches // 5) == 0 or current_batch == total_batches:
                logger.info(f"  Embedded {min(i+batch_size, len(self.chunks))}/{len(self.chunks)}")

        self.embeddings = np.vstack(all_embeddings).astype("float32")
        dim = self.embeddings.shape[1]

        self._save()
        logger.info(f"✅ Vector store built: {len(self.chunks)} vectors, dim={dim}")

    def _save(self, vs_dir: Optional[Path] = None):
        save_dir = vs_dir or DEFAULT_VS_DIR
        save_dir.mkdir(parents=True, exist_ok=True)
        # Save embeddings as numpy file
        np.save(save_dir / "embeddings.npy", self.embeddings)
        with open(save_dir / "chunks.pkl", "wb") as f:
            pickle.dump(self.chunks, f)
        with open(save_dir / "metadata.pkl", "wb") as f:
            pickle.dump(self.metadata, f)
        logger.info("💾 Vector store saved")

    def load(self, vs_dir: Optional[Path] = None) -> bool:
        """Load from disk.
        
        Args:
            vs_dir: Path to vector store directory. If None, uses default.
        """
        load_dir = vs_dir or DEFAULT_VS_DIR
        emb_path = load_dir / "embeddings.npy"
        if not emb_path.exists():
            return False
        try:
            self.embeddings = np.load(str(emb_path))
            with open(load_dir / "chunks.pkl", "rb") as f:
                self.chunks = pickle.load(f)
            with open(load_dir / "metadata.pkl", "rb") as f:
                self.metadata = pickle.load(f)
            logger.info(f"✅ Vector store loaded: {len(self.chunks)} vectors")
            return True
        except Exception as e:
            logger.error(f"Load failed: {e}")
            return False

    def search(self, query: str, k: int = TOP_K) -> List[Tuple[str, Dict, float]]:
        """Return top-k (chunk, metadata, score) for query."""
        if self.embeddings is None or self.embedder is None:
            return []
        
        # Encode query
        q_emb = self.embedder.encode([query], normalize_embeddings=True).astype("float32")[0]
        
        # Compute cosine similarity (dot product on normalized vectors)
        scores = np.dot(self.embeddings, q_emb)
        
        # Get top-k indices
        top_indices = np.argsort(-scores)[:k]
        
        results = []
        for idx in top_indices:
            if idx < len(self.chunks):
                results.append((self.chunks[idx], self.metadata[idx], float(scores[idx])))
        return results

    @property
    def is_ready(self) -> bool:
        return self.embeddings is not None and len(self.chunks) > 0

    @property
    def stats(self) -> Dict:
        return {
            "total_vectors": len(self.chunks) if self.embeddings is not None else 0,
            "total_chunks": len(self.chunks),
            "sections": list({m["section"] for m in self.metadata}),
        }


# ─── Singleton ────────────────────────────────────────────────────────────────
_vs_instance: Optional[IRDAIVectorStore] = None
_current_data_dir: Optional[str] = None

def get_vector_store(data_dir: Optional[str] = None) -> IRDAIVectorStore:
    """Get or create vector store with optional custom data directory.
    
    Args:
        data_dir: Path to data directory. If None, uses default.
    """
    global _vs_instance, _current_data_dir
    
    # If data_dir changed, reset instance
    if data_dir != _current_data_dir:
        _vs_instance = None
        _current_data_dir = data_dir
    
    if _vs_instance is None:
        _vs_instance = IRDAIVectorStore()
        vs_dir = Path(data_dir) / "vectorstore" if data_dir else None
        if not _vs_instance.load(vs_dir):
            logger.info("No existing index — will build from documents")
            docs = load_all_documents(data_dir)
            if docs:
                _vs_instance.build(docs)
                _vs_instance._save(vs_dir)
    return _vs_instance


def rebuild_vector_store(data_dir: Optional[str] = None) -> IRDAIVectorStore:
    """Rebuild vector store from scratch with optional custom data directory.
    
    Args:
        data_dir: Path to data directory. If None, uses default.
    """
    global _vs_instance, _current_data_dir
    _vs_instance = IRDAIVectorStore()
    _current_data_dir = data_dir
    docs = load_all_documents(data_dir)
    vs_dir = Path(data_dir) / "vectorstore" if data_dir else None
    _vs_instance.build(docs)
    _vs_instance._save(vs_dir)
    return _vs_instance
