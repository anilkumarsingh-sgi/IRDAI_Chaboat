#!/usr/bin/env python3
"""
Rebuild vectorstore from the data folder
Converts old FAISS format to new numpy format
"""

import logging
from pathlib import Path
from rag_pipeline import rebuild_vector_store

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Rebuild vectorstore from data folder
data_dir = Path("data")
logger.info(f"🔨 Rebuilding vectorstore from: {data_dir}")
logger.info(f"This process may take 5-15 minutes depending on document count...")

try:
    vs = rebuild_vector_store(str(data_dir))
    logger.info(f"✅ Vectorstore rebuilt successfully!")
    logger.info(f"📊 Total chunks indexed: {len(vs.chunks)}")
    logger.info(f"📁 Sections found: {vs.stats.get('sections', [])}")
    logger.info(f"📈 Total vectors: {vs.stats.get('total_vectors', 0)}")
    print("\n" + "="*60)
    print("✅ VECTORSTORE READY - Your chatbot can now answer from your data!")
    print("="*60)
except Exception as e:
    logger.error(f"❌ Rebuild failed: {e}")
    import traceback
    traceback.print_exc()
