from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.jobs.sync_job import run_sync_jobs
from app.jobs.alert_job import process_alerts
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

scheduler = BackgroundScheduler()

def start_scheduler():
    try:
        scheduler.add_job(
            run_sync_jobs,
            trigger=IntervalTrigger(minutes=settings.SYNC_INTERVAL_MINUTES),
            id="sync_all_accounts",
            name="Sync all linked accounts",
            replace_existing=True
        )
        
        scheduler.add_job(
            process_alerts,
            trigger=IntervalTrigger(minutes=1),
            id="process_alerts",
            name="Process pending alerts",
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Scheduler started successfully")
    except Exception as e:
        logger.error(f"Scheduler start error: {e}")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
