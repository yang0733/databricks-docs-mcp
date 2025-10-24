"""Scheduler for automatic documentation refresh."""

import logging
from datetime import datetime, time
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from databricks_docs_mcp.storage.cache import DocCache
from databricks_docs_mcp.embeddings.search import SemanticSearch
from databricks_docs_mcp.crawler.scraper import DocScraper

logger = logging.getLogger(__name__)


class DocRefreshScheduler:
    """Manages automatic documentation refresh."""
    
    def __init__(
        self,
        cache: DocCache,
        search_engine: SemanticSearch,
        refresh_time: time = time(hour=2, minute=0),  # 2 AM by default
    ):
        """Initialize scheduler.
        
        Args:
            cache: Document cache
            search_engine: Semantic search engine
            refresh_time: Time of day to run refresh (default: 2 AM)
        """
        self.cache = cache
        self.search_engine = search_engine
        self.refresh_time = refresh_time
        
        self.scheduler = AsyncIOScheduler()
        self.scraper: Optional[DocScraper] = None
        
        # Track refresh status
        self.last_refresh: Optional[datetime] = None
        self.refresh_in_progress = False
        self.last_refresh_stats = {}
    
    def start(self):
        """Start the scheduler."""
        logger.info(f"Starting refresh scheduler (daily at {self.refresh_time})")
        
        # Schedule daily refresh
        self.scheduler.add_job(
            self.refresh_documentation,
            trigger=CronTrigger(
                hour=self.refresh_time.hour,
                minute=self.refresh_time.minute,
            ),
            id="daily_doc_refresh",
            name="Daily Documentation Refresh",
            replace_existing=True,
        )
        
        self.scheduler.start()
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        logger.info("Stopping scheduler")
        self.scheduler.shutdown()
    
    async def refresh_documentation(self):
        """Perform documentation refresh (called by scheduler)."""
        if self.refresh_in_progress:
            logger.warning("Refresh already in progress, skipping")
            return
        
        try:
            self.refresh_in_progress = True
            start_time = datetime.now()
            
            logger.info("=" * 60)
            logger.info("Starting scheduled documentation refresh")
            logger.info("=" * 60)
            
            # Create scraper
            self.scraper = DocScraper(cache=self.cache)
            
            # Perform incremental update
            pages_updated = self.scraper.incremental_update()
            
            # Re-index updated pages
            logger.info("Re-indexing updated pages")
            self.search_engine.index_all_pages()
            
            # Update stats
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.last_refresh = end_time
            self.last_refresh_stats = {
                "timestamp": end_time.isoformat(),
                "pages_updated": pages_updated,
                "duration_seconds": duration,
                "status": "success",
            }
            
            logger.info("=" * 60)
            logger.info(f"Refresh complete: {pages_updated} pages updated in {duration:.1f}s")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Refresh failed: {e}", exc_info=True)
            self.last_refresh_stats = {
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e),
            }
        finally:
            self.refresh_in_progress = False
    
    def trigger_manual_refresh(self):
        """Trigger an immediate refresh (manual)."""
        if self.refresh_in_progress:
            return {
                "status": "already_running",
                "message": "Refresh is already in progress",
            }
        
        # Schedule immediate execution
        self.scheduler.add_job(
            self.refresh_documentation,
            id="manual_refresh",
            replace_existing=True,
        )
        
        return {
            "status": "scheduled",
            "message": "Manual refresh has been triggered",
        }
    
    def get_status(self) -> dict:
        """Get refresh status.
        
        Returns:
            Dict with refresh status information
        """
        next_run = None
        job = self.scheduler.get_job("daily_doc_refresh")
        if job:
            next_run = job.next_run_time
        
        return {
            "scheduler_running": self.scheduler.running,
            "refresh_in_progress": self.refresh_in_progress,
            "last_refresh": self.last_refresh.isoformat() if self.last_refresh else None,
            "next_scheduled_refresh": next_run.isoformat() if next_run else None,
            "last_refresh_stats": self.last_refresh_stats,
        }

