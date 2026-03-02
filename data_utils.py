"""
Utility functions for handling different data sources
(Google Drive, local files, uploads)
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional
import requests

logger = logging.getLogger(__name__)


def download_from_gdrive(folder_id: str, output_dir: str) -> bool:
    """
    Download files from public Google Drive folder.
    
    Args:
        folder_id: Google Drive folder ID
        output_dir: Directory to save downloaded files
        
    Returns:
        True if successful, False otherwise
    """
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Using gdown library to download from Google Drive
        try:
            import gdown
        except ImportError:
            logger.warning("gdown not installed. Installing...")
            import subprocess
            subprocess.check_call(["pip", "install", "gdown"])
            import gdown
        
        # Download the entire folder
        gdown.download_folder(
            url=f"https://drive.google.com/drive/folders/{folder_id}",
            output=str(output_path),
            quiet=False,
            use_cookies=False
        )
        logger.info(f"✅ Downloaded from Google Drive folder: {folder_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download from Google Drive: {e}")
        return False


def validate_data_structure(data_dir: str) -> bool:
    """
    Validate that directory contains required data files.
    
    Args:
        data_dir: Path to data directory
        
    Returns:
        True if valid structure found
    """
    data_path = Path(data_dir)
    
    if not data_path.exists():
        logger.error(f"Directory not found: {data_dir}")
        return False
    
    # Check for required files
    has_json = (data_path / "crawled_data.json").exists()
    has_pdfs = (data_path / "pdfs").exists() and list((data_path / "pdfs").glob("*.pdf"))
    
    if not has_json and not has_pdfs:
        logger.warning(f"⚠️ No crawled_data.json or PDFs found in {data_dir}")
        return False
    
    logger.info(f"✅ Valid data structure found in {data_dir}")
    return True


def get_processed_data_dir(data_source: str, data_identifier: str = None) -> Optional[str]:
    """
    Process data source and return the path to data directory.
    
    Args:
        data_source: Type of source ('local', 'gdrive', 'upload', 'default')
        data_identifier: Path (local), folder ID (gdrive), etc.
        
    Returns:
        Path to processed data directory
    """
    if data_source == "default":
        return "data"
    
    if data_source == "local" and data_identifier:
        if validate_data_structure(data_identifier):
            return data_identifier
    
    elif data_source == "gdrive" and data_identifier:
        gdrive_cache_dir = Path("data/gdrive_cache") / data_identifier
        gdrive_cache_dir.mkdir(parents=True, exist_ok=True)
        
        if download_from_gdrive(data_identifier, str(gdrive_cache_dir)):
            return str(gdrive_cache_dir)
    
    elif data_source == "upload":
        upload_dir = "data/uploaded"
        if validate_data_structure(upload_dir):
            return upload_dir
    
    return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Test
    # test_folder = download_from_gdrive("1A4x5VzG3kH4jk5L6mN7oP8qR9sT0uV1w", "data/test_gdrive")
    # print(f"Success: {test_folder}")
