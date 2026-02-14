"""
Service for fetching ocean data from NOAA ERDDAP.
"""
import requests
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from api.models import (
    DataSource,
    Location,
    TemperatureObservation,
    SalinityObservation,
    IngestionLog
)

logger = logging.getLogger(__name__)


class NOAAERDDAPService:
    """
    Service class for interacting with NOAA ERDDAP API.
    """
    
    def __init__(self):
        self.base_url = settings.DATA_INGESTION['NOAA_ERDDAP_BASE_URL']
        self.source, _ = DataSource.objects.get_or_create(
            name='NOAA ERDDAP',
            defaults={
                'url': self.base_url,
                'description': 'NOAA Environmental Research Division Data Access Program',
                'is_active': True
            }
        )
    
    def fetch_buoy_data(self, dataset_id='cwwcNDBCMet', days_back=1):
        """
        Fetch buoy data from NOAA ERDDAP.
        
        Args:
            dataset_id: ERDDAP dataset identifier
            days_back: Number of days to fetch historical data
        
        Returns:
            dict: Ingestion statistics
        """
        log = IngestionLog.objects.create(
            source=self.source,
            status='running'
        )
        
        try:
            # Calculate time range
            end_time = timezone.now()
            start_time = end_time - timedelta(days=days_back)
            
            # Build ERDDAP query URL
            url = f"{self.base_url}tabledap/{dataset_id}.json"
            params = {
                'time>=': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'time<=': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            }
            
            logger.info(f"Fetching NOAA data from {url}")
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            records_inserted = self._process_buoy_data(data)
            
            # Update log
            log.status = 'success'
            log.completed_at = timezone.now()
            log.records_fetched = len(data.get('table', {}).get('rows', []))
            log.records_inserted = records_inserted
            log.save()
            
            # Update source last_fetch
            self.source.last_fetch = timezone.now()
            self.source.save()
            
            logger.info(f"NOAA data fetch completed: {records_inserted} records inserted")
            
            return {
                'status': 'success',
                'records_fetched': log.records_fetched,
                'records_inserted': records_inserted
            }
            
        except Exception as e:
            logger.error(f"Error fetching NOAA data: {e}")
            log.status = 'failed'
            log.completed_at = timezone.now()
            log.error_message = str(e)
            log.save()
            
            raise
    
    def _process_buoy_data(self, data):
        """
        Process and store buoy data in the database.
        """
        records_inserted = 0
        
        # Extract column names and rows
        columns = data.get('table', {}).get('columnNames', [])
        rows = data.get('table', {}).get('rows', [])
        
        # Create index mapping
        try:
            time_idx = columns.index('time')
            lat_idx = columns.index('latitude')
            lon_idx = columns.index('longitude')
            station_idx = columns.index('station')
        except ValueError as e:
            logger.error(f"Missing required column: {e}")
            return 0
        
        # Try to find temperature and salinity columns
        temp_idx = columns.index('wtmp') if 'wtmp' in columns else None
        salinity_idx = columns.index('sal') if 'sal' in columns else None
        
        for row in rows:
            try:
                # Get or create location
                location, _ = Location.objects.get_or_create(
                    latitude=float(row[lat_idx]),
                    longitude=float(row[lon_idx]),
                    defaults={
                        'name': f"Buoy {row[station_idx]}",
                        'region': 'NOAA Network'
                    }
                )
                
                timestamp = datetime.fromisoformat(row[time_idx].replace('Z', '+00:00'))
                
                # Store temperature if available
                if temp_idx and row[temp_idx] not in [None, 'NaN', '']:
                    TemperatureObservation.objects.update_or_create(
                        location=location,
                        source=self.source,
                        timestamp=timestamp,
                        defaults={
                            'temperature_celsius': float(row[temp_idx])
                        }
                    )
                    records_inserted += 1
                
                # Store salinity if available
                if salinity_idx and row[salinity_idx] not in [None, 'NaN', '']:
                    SalinityObservation.objects.update_or_create(
                        location=location,
                        source=self.source,
                        timestamp=timestamp,
                        defaults={
                            'salinity_psu': float(row[salinity_idx])
                        }
                    )
                    records_inserted += 1
                    
            except (ValueError, IndexError) as e:
                logger.warning(f"Skipping row due to error: {e}")
                continue
        
        return records_inserted


def fetch_latest_noaa_data():
    """
    Convenience function for Celery tasks.
    """
    service = NOAAERDDAPService()
    return service.fetch_buoy_data(days_back=1)
