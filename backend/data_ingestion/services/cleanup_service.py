"""
Service for cleaning up old ocean data observations.
"""
import logging
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from api.models import (
    TemperatureObservation,
    SalinityObservation,
    CurrentObservation,
    IngestionLog
)

logger = logging.getLogger(__name__)


def cleanup_expired_data():
    """
    Remove observations older than the configured retention period.
    
    Returns:
        dict: Cleanup statistics
    """
    retention_days = settings.DATA_INGESTION.get('DATA_RETENTION_DAYS', 365)
    cutoff_date = timezone.now() - timedelta(days=retention_days)
    
    logger.info(f"Starting data cleanup for records older than {cutoff_date}")
    
    stats = {
        'temperature_deleted': 0,
        'salinity_deleted': 0,
        'currents_deleted': 0,
        'logs_deleted': 0,
        'cutoff_date': cutoff_date.isoformat()
    }
    
    try:
        # Delete old temperature observations
        temp_deleted, _ = TemperatureObservation.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()
        stats['temperature_deleted'] = temp_deleted
        
        # Delete old salinity observations
        salinity_deleted, _ = SalinityObservation.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()
        stats['salinity_deleted'] = salinity_deleted
        
        # Delete old current observations
        currents_deleted, _ = CurrentObservation.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()
        stats['currents_deleted'] = currents_deleted
        
        # Clean up old ingestion logs (keep 90 days)
        log_cutoff = timezone.now() - timedelta(days=90)
        logs_deleted, _ = IngestionLog.objects.filter(
            started_at__lt=log_cutoff
        ).delete()
        stats['logs_deleted'] = logs_deleted
        
        total_deleted = (
            stats['temperature_deleted'] +
            stats['salinity_deleted'] +
            stats['currents_deleted']
        )
        
        logger.info(f"Data cleanup completed: {total_deleted} observations deleted")
        
        return stats
        
    except Exception as e:
        logger.error(f"Error during data cleanup: {e}")
        raise
