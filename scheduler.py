"""
Background scheduler for automatic IRDAI website updates.
Runs crawler + rebuilds vector store on a schedule.
"""

import logging
import threading
import time
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

_scheduler_thread: threading.Thread | None = None
_is_running = False
_last_run: str = "Never"
_next_run: str = "Not scheduled"
_status: str = "idle"

CRAWL_INTERVAL_HOURS = 24  # re-crawl every 24 hours


def _crawl_and_rebuild():
    global _last_run, _status
    _status = "crawling"
    logger.info("🕷️  Scheduled crawl starting...")
    try:
        from crawler import IRDAICrawler
        from rag_pipeline import rebuild_vector_store

        crawler = IRDAICrawler()
        crawler.run()

        _status = "rebuilding index"
        logger.info("🔧 Rebuilding vector store...")
        rebuild_vector_store()

        _last_run = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _status = "idle"
        logger.info(f"✅ Scheduled update complete at {_last_run}")
    except Exception as e:
        logger.error(f"Scheduled crawl failed: {e}")
        _status = f"error: {e}"


def _scheduler_loop():
    global _is_running, _next_run
    interval_secs = CRAWL_INTERVAL_HOURS * 3600
    while _is_running:
        _next_run = datetime.fromtimestamp(time.time() + interval_secs).strftime("%Y-%m-%d %H:%M:%S")
        time.sleep(interval_secs)
        if _is_running:
            t = threading.Thread(target=_crawl_and_rebuild, daemon=True)
            t.start()
            t.join()


def start_scheduler():
    global _scheduler_thread, _is_running
    if _scheduler_thread and _scheduler_thread.is_alive():
        return
    _is_running = True
    _scheduler_thread = threading.Thread(target=_scheduler_loop, daemon=True)
    _scheduler_thread.start()
    logger.info(f"⏰ Scheduler started — crawl every {CRAWL_INTERVAL_HOURS}h")


def stop_scheduler():
    global _is_running
    _is_running = False


def trigger_manual_crawl():
    """Kick off an immediate crawl in a background thread."""
    t = threading.Thread(target=_crawl_and_rebuild, daemon=True)
    t.start()
    return t


def get_scheduler_status() -> dict:
    return {
        "is_running": _is_running,
        "last_run": _last_run,
        "next_run": _next_run,
        "status": _status,
    }
