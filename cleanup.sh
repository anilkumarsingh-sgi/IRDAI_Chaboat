#!/bin/bash
# ========== WORKSPACE CLEANUP SCRIPT ==========
# Run this AFTER closing all terminal windows
# This removes unnecessary files keeping only source code and documentation

echo "Cleaning up workspace..."
echo ""

# Remove Python cache
if [ -d "__pycache__" ]; then
    echo "Removing __pycache__..."
    rm -rf __pycache__
fi

# Remove virtual environment
if [ -d "IRDAI_GPT" ]; then
    echo "Removing IRDAI_GPT (use pip install -r requirements.txt instead)..."
    rm -rf IRDAI_GPT
fi

# Remove data folder (PDFs, vectorstore)
if [ -d "data" ]; then
    echo "Removing data folder (PDFs and vectorstore will be regenerated)..."
    rm -rf data
fi

# Remove logs
if [ -d "logs" ]; then
    echo "Removing logs..."
    rm -rf logs
fi

# Remove any .pyc files
echo "Removing .pyc files..."
find . -type f -name "*.pyc" -delete

# Remove .pyo files
echo "Removing .pyo files..."
find . -type f -name "*.pyo" -delete

echo ""
echo "========== CLEANUP COMPLETE =========="
echo ""
echo "REMOVED:"
echo "  - __pycache__ (Python cache files)"
echo "  - IRDAI_GPT (virtual environment)"
echo "  - data/ (crawled PDFs, vectorstore, etc.)"
echo "  - logs/ (log files)"
echo "  - *.pyc, *.pyo (Python compiled files)"
echo ""
echo "KEPT:"
echo "  - All source code (*.py files)"
echo "  - All documentation (*.md files)"
echo "  - Configuration files (.env, .streamlit/)"
echo "  - requirements.txt (for pip install)"
echo "  - Dockerfile and docker-compose.yml"
echo ""
echo "Workspace is now lean and ready for deployment!"
echo ""
