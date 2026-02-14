"""
Celery tasks for data ingestion and processing.
"""
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True, name='data_ingestion.fetch_noaa_data')
def fetch_noaa_data(self):
    """
    Fetch ocean data from NOAA ERDDAP.
    This task is scheduled to run periodically.
    """
    logger.info("Starting NOAA data fetch...")
    try:
        from data_ingestion.services.noaa_service import fetch_latest_noaa_data
        result = fetch_latest_noaa_data()
        logger.info(f"NOAA data fetch completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"Error fetching NOAA data: {exc}")
        raise self.retry(exc=exc, countdown=300, max_retries=3)


@shared_task(bind=True, name='data_ingestion.fetch_copernicus_data')
def fetch_copernicus_data(self):
    """
    Fetch ocean data from Copernicus Marine Service.
    """
    logger.info("Starting Copernicus data fetch...")
    try:
        from data_ingestion.services.copernicus_service import fetch_latest_copernicus_data
        result = fetch_latest_copernicus_data()
        logger.info(f"Copernicus data fetch completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"Error fetching Copernicus data: {exc}")
        raise self.retry(exc=exc, countdown=300, max_retries=3)


@shared_task(bind=True, name='data_ingestion.cleanup_old_data')
def cleanup_old_data(self):
    """
    Remove data older than the configured retention period.
    """
    logger.info("Starting data cleanup...")
    try:
        from data_ingestion.services.cleanup_service import cleanup_expired_data
        result = cleanup_expired_data()
        logger.info(f"Data cleanup completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"Error during cleanup: {exc}")
        raise


@shared_task(name='celery.test_task')
def test_task():
    """
    Simple test task to verify Celery is working.
    """
    logger.info("Test task executed successfully!")
    return "Celery is working!"
