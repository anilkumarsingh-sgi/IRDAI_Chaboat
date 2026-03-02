"""
IRDAI Website Crawler
Crawls https://irdai.gov.in and downloads all content from each section.
Respects rate limits and stores structured data for the RAG pipeline.
"""

import os
import re
import json
import time
import hashlib
import logging
import requests
import traceback
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from pathlib import Path

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/crawler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ─── Config ───────────────────────────────────────────────────────────────────
BASE_URL = "https://irdai.gov.in"
DATA_DIR = Path("data/crawled")
PDF_DIR  = Path("data/pdfs")
DATA_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

DELAY = 1.5          # seconds between requests
MAX_PAGES = 1000     # safety cap (increased for comprehensive crawling)
MAX_PDF_SIZE_MB = 50

# All known IRDAI sections / nav paths (discovered from irdai.gov.in)
IRDAI_SECTIONS = [
    "/home",
    "/about-us1",
    "/regulations",
    "/guidelines1",
    "/about-enforcement",
    "/about-inspection",
    "/about-brokers",
    "/about-agency-distribution",
    "/press-releases",
    "/notifications/vacancies",
    "/careers1",
    "/organogram",
]


class IRDAICrawler:
    """Production-grade crawler for irdai.gov.in"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.visited: set[str] = set()
        self.crawled_data: list[dict] = []
        self.pdf_paths: list[str] = []
        self.errors: list[dict] = []
        self.stats = {
            "pages_crawled": 0,
            "pdfs_downloaded": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None,
        }

    # ── Core fetch ────────────────────────────────────────────────────────────
    def fetch(self, url: str, retries: int = 3) -> requests.Response | None:
        last_error = None
        for attempt in range(retries):
            try:
                resp = self.session.get(url, timeout=20, allow_redirects=True)
                resp.raise_for_status()
                return resp
            except requests.RequestException as e:
                last_error = e
                wait = (attempt + 1) * 2
                logger.warning(f"[{attempt+1}/{retries}] Error fetching {url}: {e}. Retrying in {wait}s")
                time.sleep(wait)
        self.stats["errors"] += 1
        self.errors.append({"url": url, "error": str(last_error), "time": datetime.now().isoformat()})
        return None

    # ── PDF downloader ─────────────────────────────────────────────────────────
    def download_pdf(self, url: str, section: str) -> Optional[str]:
        try:
            resp = self.session.get(url, timeout=30, stream=True)
            resp.raise_for_status()

            content_length = int(resp.headers.get("content-length", 0))
            if content_length > MAX_PDF_SIZE_MB * 1024 * 1024:
                logger.warning(f"Skipping large PDF ({content_length//1024//1024}MB): {url}")
                return None

            filename = url.split("/")[-1].split("?")[0]
            if not filename.endswith(".pdf"):
                filename = hashlib.md5(url.encode()).hexdigest()[:10] + ".pdf"

            safe_section = re.sub(r"[^\w\-]", "_", section)
            section_dir = PDF_DIR / safe_section
            section_dir.mkdir(exist_ok=True)

            filepath = section_dir / filename
            if filepath.exists():
                logger.info(f"PDF already exists: {filepath}")
                return str(filepath)

            with open(filepath, "wb") as f:
                downloaded = 0
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if downloaded > MAX_PDF_SIZE_MB * 1024 * 1024:
                        logger.warning(f"PDF too large mid-download, stopping: {url}")
                        break

            self.stats["pdfs_downloaded"] += 1
            logger.info(f"✅ PDF saved: {filepath.name}")
            return str(filepath)

        except Exception as e:
            logger.error(f"PDF download failed {url}: {e}")
            return None

    # ── Page parser ───────────────────────────────────────────────────────────
    def parse_page(self, url: str, html: str, section: str) -> dict:
        soup = BeautifulSoup(html, "lxml")

        # Remove nav/footer noise
        for tag in soup.find_all(["nav", "footer", "script", "style", "noscript"]):
            tag.decompose()

        title = ""
        if soup.find("title"):
            title = soup.find("title").get_text(strip=True)
        elif soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)

        # Extract main content text
        main = (
            soup.find("main") or
            soup.find("div", {"id": re.compile(r"main|content|body", re.I)}) or
            soup.find("div", {"class": re.compile(r"main|content|body", re.I)}) or
            soup.body or soup
        )
        text = main.get_text(separator="\n", strip=True) if main else soup.get_text(separator="\n", strip=True)
        # Clean whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)

        # Extract all links
        links = []
        pdf_links = []
        for a in soup.find_all("a", href=True):
            href = urljoin(url, a["href"])
            if urlparse(href).netloc in ("irdai.gov.in", "www.irdai.gov.in", ""):
                if href.lower().endswith(".pdf"):
                    pdf_links.append(href)
                else:
                    links.append(href)

        # Extract tables
        tables = []
        for tbl in soup.find_all("table"):
            rows = []
            for tr in tbl.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if cells:
                    rows.append(cells)
            if rows:
                tables.append(rows)

        return {
            "url": url,
            "title": title,
            "section": section,
            "text": text[:50000],  # cap at 50k chars
            "links": links,
            "pdf_links": pdf_links,
            "tables": tables,
            "crawled_at": datetime.now().isoformat(),
        }

    # ── Section crawler ────────────────────────────────────────────────────────
    def crawl_section(self, path: str):
        url = urljoin(BASE_URL, path)
        section_name = path.strip("/").split("/")[-1]
        
        # Check if section exists before attempting to crawl
        initial_resp = self.fetch(url, retries=1)
        if not initial_resp:
            logger.warning(f"⚠️ Section '{section_name}' not found (404 or unreachable): {url}")
            return
        
        queue = [url]
        section_pages = 0

        logger.info(f"\n{'='*60}\n🔍 Crawling section: {section_name}\n{'='*60}")

        while queue and self.stats["pages_crawled"] < MAX_PAGES:
            current_url = queue.pop(0)
            if current_url in self.visited:
                continue
            self.visited.add(current_url)

            # Only crawl irdai.gov.in
            parsed = urlparse(current_url)
            if parsed.netloc not in ("irdai.gov.in", "www.irdai.gov.in", ""):
                continue

            time.sleep(DELAY)

            resp = self.fetch(current_url)
            if not resp:
                continue

            content_type = resp.headers.get("content-type", "")
            if "pdf" in content_type or current_url.lower().endswith(".pdf"):
                path_saved = self.download_pdf(current_url, section_name)
                if path_saved:
                    self.pdf_paths.append(path_saved)
                continue

            if "html" not in content_type:
                continue

            page_data = self.parse_page(current_url, resp.text, section_name)
            self.crawled_data.append(page_data)
            self.stats["pages_crawled"] += 1
            section_pages += 1

            logger.info(
                f"  [{self.stats['pages_crawled']}] {page_data['title'][:60]} | "
                f"{len(page_data['text'])} chars | "
                f"{len(page_data['pdf_links'])} PDFs"
            )

            # Download PDFs found on this page
            for pdf_url in page_data["pdf_links"]:
                if pdf_url not in self.visited:
                    time.sleep(0.5)
                    path_saved = self.download_pdf(pdf_url, section_name)
                    if path_saved:
                        self.pdf_paths.append(path_saved)
                    self.visited.add(pdf_url)

            # Add internal links to queue (stay in section)
            for link in page_data["links"]:
                if link not in self.visited:
                    # Prioritise links within same section
                    path_parts = path.strip("/").split("/")
                    section_keyword = path_parts[0] if path_parts else section_name
                    if section_name in link or section_keyword in link:
                        queue.insert(0, link)
                    else:
                        queue.append(link)

        logger.info(f"  ✅ Section '{section_name}': {section_pages} pages crawled")

    # ── Save progress ──────────────────────────────────────────────────────────
    def save(self):
        out = DATA_DIR / "crawled_data.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(self.crawled_data, f, ensure_ascii=False, indent=2)

        meta = {
            "stats": self.stats,
            "pdf_paths": self.pdf_paths,
            "errors": self.errors,
        }
        with open(DATA_DIR / "crawl_meta.json", "w") as f:
            json.dump(meta, f, indent=2)

        logger.info(f"💾 Saved {len(self.crawled_data)} pages → {out}")

    # ── Main entry ─────────────────────────────────────────────────────────────
    def run(self, sections: list[str] | None = None):
        self.stats["start_time"] = datetime.now().isoformat()
        logger.info("🚀 IRDAI Crawler starting...")

        target_sections = sections or IRDAI_SECTIONS
        for section_path in target_sections:
            try:
                self.crawl_section(section_path)
                self.save()  # incremental save after each section
            except Exception as e:
                logger.error(f"Section {section_path} failed: {traceback.format_exc()}")

        self.stats["end_time"] = datetime.now().isoformat()
        self.save()

        logger.info(
            f"\n{'='*60}\n"
            f"✅ CRAWL COMPLETE\n"
            f"   Pages  : {self.stats['pages_crawled']}\n"
            f"   PDFs   : {self.stats['pdfs_downloaded']}\n"
            f"   Errors : {self.stats['errors']}\n"
            f"{'='*60}"
        )
        return self.crawled_data


if __name__ == "__main__":
    crawler = IRDAICrawler()
    crawler.run()
