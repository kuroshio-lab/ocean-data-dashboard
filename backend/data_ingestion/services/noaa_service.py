"""
Service for fetching ocean data from NOAA ERDDAP.

IMPORTANT DATA AVAILABILITY NOTE:
================================
The default dataset 'cwwcNDBCMet' (NOAA NDBC Meteorological) provides:
- ✓ Water temperature (wtmp - sea surface temperature)
- ✗ Salinity (NOT available in this dataset)

For salinity data, consider these alternatives:
- Copernicus Marine Service (requires free registration)
- NASA OceanColor (some products include salinity)
- NOAA HYCOM models (different ERDDAP dataset)

Field mappings for cwwcNDBCMet:
- station: Buoy station ID
- latitude/longitude: Location
- time: Timestamp (UTC)
- wtmp: Water temperature (Sea Surface Temperature) in Celsius
- atmp: Air temperature in Celsius
- wspd: Wind speed
- bar: Barometric pressure
- etc.

See: https://coastwatch.pfeg.noaa.gov/erddap/tabledap/cwwcNDBCMet.html
"""

import requests
import logging
from datetime import datetime, timedelta
from urllib.parse import quote
from django.conf import settings
from django.utils import timezone
from api.models import (
    DataSource,
    Location,
    TemperatureObservation,
    SalinityObservation,
    IngestionLog,
)

logger = logging.getLogger(__name__)


class NOAAERDDAPService:
    """
    Service class for interacting with NOAA ERDDAP API.
    """

    def __init__(self):
        self.base_url = settings.DATA_INGESTION["NOAA_ERDDAP_BASE_URL"]
        self.source, _ = DataSource.objects.get_or_create(
            name="NOAA ERDDAP",
            defaults={
                "url": self.base_url,
                "description": "NOAA Environmental Research Division Data Access Program",
                "is_active": True,
            },
        )

    def fetch_buoy_data(self, dataset_id="cwwcNDBCMet", days_back=1):
        """
        Fetch buoy data from NOAA ERDDAP.

        Args:
            dataset_id: ERDDAP dataset identifier
            days_back: Number of days to fetch historical data

        Returns:
            dict: Ingestion statistics
        """
        log = IngestionLog.objects.create(source=self.source, status="running")

        try:
            # Calculate time range
            end_time = timezone.now()
            start_time = end_time - timedelta(days=days_back)

            # Build ERDDAP query URL - explicitly request needed fields
            # ERDDAP format: ?field1,field2,field3&constraint1&constraint2
            start_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

            # Explicitly select fields we need (more efficient and ensures consistent response)
            fields = "station,latitude,longitude,time,wtmp"
            constraints = (
                f"&time>={quote(start_str, safe='')}&time<={quote(end_str, safe='')}"
            )
            url = f"{self.base_url}tabledap/{dataset_id}.json?{fields}{constraints}"

            logger.info(f"Fetching NOAA data from {url}")
            response = requests.get(url, timeout=60)
            response.raise_for_status()

            data = response.json()
            records_inserted = self._process_buoy_data(data)

            # Update log
            log.status = "success"
            log.completed_at = timezone.now()
            log.records_fetched = len(data.get("table", {}).get("rows", []))
            log.records_inserted = records_inserted
            log.save()

            # Update source last_fetch
            self.source.last_fetch = timezone.now()
            self.source.save()

            logger.info(
                f"NOAA data fetch completed: {records_inserted} records inserted"
            )

            return {
                "status": "success",
                "records_fetched": log.records_fetched,
                "records_inserted": records_inserted,
            }

        except Exception as e:
            logger.error(f"Error fetching NOAA data: {e}")
            log.status = "failed"
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
        columns = data.get("table", {}).get("columnNames", [])
        rows = data.get("table", {}).get("rows", [])

        logger.info(f"Available columns from NOAA: {columns}")
        logger.info(f"Fetched {len(rows)} rows from NOAA")
        try:
            time_idx = columns.index("time")
            lat_idx = columns.index("latitude")
            lon_idx = columns.index("longitude")
            station_idx = columns.index("station")
        except ValueError as e:
            logger.error(f"Missing required column: {e}")
            return 0

        # Try to find temperature and salinity columns
        # NOAA cwwcNDBCMet field mappings
        temp_idx = None
        salinity_idx = None

        # Water temperature - try common NOAA field names
        temp_fields = ["wtmp", "sea_surface_temperature", "sst", "water_temperature"]
        for field in temp_fields:
            if field in columns:
                temp_idx = columns.index(field)
                logger.info(f"Found temperature field: {field}")
                break

        # Salinity - NOTE: cwwcNDBCMet does NOT include salinity
        # We check for common salinity field names, but this dataset lacks salinity data
        salinity_fields = ["sal", "salinity", "sea_surface_salinity", "psu"]
        for field in salinity_fields:
            if field in columns:
                salinity_idx = columns.index(field)
                logger.info(f"Found salinity field: {field}")
                break

        if salinity_idx is None:
            logger.warning(
                "Salinity data not available in this NOAA dataset. "
                "Consider using a different dataset like 'cwwcNDBCSun' or "
                "Copernicus Marine Service for salinity data."
            )

        temp_records = 0
        salinity_records = 0

        for row in rows:
            try:
                # Get or create location
                location, _ = Location.objects.get_or_create(
                    latitude=float(row[lat_idx]),
                    longitude=float(row[lon_idx]),
                    defaults={
                        "name": f"Buoy {row[station_idx]}",
                        "region": "NOAA Network",
                    },
                )

                timestamp = datetime.fromisoformat(row[time_idx].replace("Z", "+00:00"))

                # Store temperature if available (convert from Celsius - NOAA provides in Celsius)
                if temp_idx is not None and row[temp_idx] not in [
                    None,
                    "NaN",
                    "",
                    "null",
                    "NULL",
                ]:
                    try:
                        temp_value = float(row[temp_idx])
                        # Validate reasonable ocean temperature range (-5 to 40 Celsius)
                        if -5 <= temp_value <= 40:
                            TemperatureObservation.objects.update_or_create(
                                location=location,
                                source=self.source,
                                timestamp=timestamp,
                                defaults={"temperature_celsius": temp_value},
                            )
                            temp_records += 1
                        else:
                            logger.warning(
                                f"Temperature value {temp_value}°C out of range, skipping"
                            )
                    except (ValueError, TypeError) as e:
                        logger.warning(
                            f"Invalid temperature value '{row[temp_idx]}': {e}"
                        )

                # Store salinity if available (cwwcNDBCMet typically does NOT have salinity)
                if salinity_idx is not None and row[salinity_idx] not in [
                    None,
                    "NaN",
                    "",
                    "null",
                    "NULL",
                ]:
                    try:
                        salinity_value = float(row[salinity_idx])
                        # Validate reasonable salinity range (0 to 45 PSU)
                        if 0 <= salinity_value <= 45:
                            SalinityObservation.objects.update_or_create(
                                location=location,
                                source=self.source,
                                timestamp=timestamp,
                                defaults={"salinity_psu": salinity_value},
                            )
                            salinity_records += 1
                        else:
                            logger.warning(
                                f"Salinity value {salinity_value} PSU out of range, skipping"
                            )
                    except (ValueError, TypeError) as e:
                        logger.warning(
                            f"Invalid salinity value '{row[salinity_idx]}': {e}"
                        )

            except (ValueError, IndexError) as e:
                logger.warning(f"Skipping row due to error: {e}")
                continue

        records_inserted = temp_records + salinity_records
        logger.info(
            f"Processed {len(rows)} rows: {temp_records} temperature records, {salinity_records} salinity records"
        )

        return records_inserted


def fetch_latest_noaa_data():
    """
    Convenience function for Celery tasks.
    """
    service = NOAAERDDAPService()
    return service.fetch_buoy_data(days_back=1)
