"""
Background scheduler service for periodic tasks
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .orderbook_service import orderbook_service

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        logger.info("✓ Background scheduler started")
    
    def start_orderbook_updates(self):
        """Start periodic order book updates every 5 minutes"""
        try:
            # Schedule periodic updates every 5 minutes
            # First run will happen 5 minutes after startup
            self.scheduler.add_job(
                func=orderbook_service.fetch_and_cache_all,
                trigger=IntervalTrigger(minutes=5),
                id='orderbook_updates',
                name='Fetch and cache order books',
                replace_existing=True
            )
            logger.info("✓ Order book background updates scheduled (every 5 minutes, first run in 5 minutes)")
        except Exception as e:
            logger.error(f"Failed to start order book updates: {e}")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("✓ Background scheduler stopped")

# Global scheduler instance
scheduler_service = SchedulerService()
