"""
Service for fetching ocean salinity data from Copernicus Marine Service.

This service uses the Copernicus Marine Toolbox to fetch salinity data.
Installation: pip install copernicus-marine

Required environment variables:
- COPERNICUS_API_USERNAME: Your Copernicus Marine username
- COPERNICUS_API_PASSWORD: Your Copernicus Marine password
"""

import os
import logging
import tempfile
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from django.conf import settings
from django.utils import timezone
from api.models import DataSource, Location, SalinityObservation, IngestionLog

logger = logging.getLogger(__name__)


class CopernicusMarineService:
    """
    Service class for fetching salinity data from Copernicus Marine Service.

    Uses the 'cmems_mod_glo_phy-so_an_0.083deg_PT1H-m' dataset which provides
    global ocean salinity data at 0.083 degree resolution, hourly.

    Dataset details:
    - Variable: so (sea water salinity)
    - Unit: PSU (Practical Salinity Units)
    - Resolution: 0.083° x 0.083°
    - Temporal resolution: Hourly
    """

    # Default dataset for salinity
    SALINITY_DATASET = "cmems_mod_glo_phy-so_an_0.083deg_PT1H-m"

    def __init__(self):
        self.username = getattr(settings, "COPERNICUS_USERNAME", None) or os.getenv(
            "COPERNICUS_API_USERNAME"
        )
        self.password = getattr(settings, "COPERNICUS_PASSWORD", None) or os.getenv(
            "COPERNICUS_API_PASSWORD"
        )

        self.source, created = DataSource.objects.get_or_create(
            name="Copernicus Marine",
            defaults={
                "url": "https://marine.copernicus.eu/",
                "description": "Copernicus Marine Service - Ocean Salinity (PSU)",
                "is_active": bool(self.username and self.password),
            },
        )

        # Update is_active status based on credentials
        if not created and self.source.is_active != bool(
            self.username and self.password
        ):
            self.source.is_active = bool(self.username and self.password)
            self.source.save()

    def _get_copernicus_client(self):
        """
        Get Copernicus Marine Toolbox client if available.
        Falls back to direct API if toolbox not installed.
        """
        try:
            import copernicus_marine

            return copernicus_marine
        except ImportError:
            logger.warning("copernicus-marine package not installed. Using direct API.")
            return None

    def fetch_salinity_data(
        self, days_back: int = 1, bounding_box: Optional[Dict] = None
    ):
        """
        Fetch salinity data from Copernicus Marine Service.

        Args:
            days_back: Number of days of historical data to fetch
            bounding_box: Optional dict with 'min_lon', 'max_lon', 'min_lat', 'max_lat'
                         Defaults to global coverage if not specified

        Returns:
            dict: Ingestion statistics
        """
        if not self.username or not self.password:
            logger.warning(
                "Copernicus credentials not configured. Set COPERNICUS_API_USERNAME and COPERNICUS_API_PASSWORD"
            )
            return {
                "status": "skipped",
                "message": "Copernicus credentials not configured",
            }

        log = IngestionLog.objects.create(source=self.source, status="running")

        try:
            # Calculate time range
            end_time = timezone.now()
            start_time = end_time - timedelta(days=days_back)

            logger.info(
                f"Fetching Copernicus salinity data from {start_time} to {end_time}"
            )

            # Fetch data using the toolbox
            records_inserted = self._fetch_with_toolbox(
                start_time=start_time, end_time=end_time, bounding_box=bounding_box
            )

            # Update log
            log.status = "success"
            log.completed_at = timezone.now()
            log.records_fetched = records_inserted
            log.records_inserted = records_inserted
            log.save()

            # Update source
            self.source.last_fetch = timezone.now()
            self.source.save()

            logger.info(
                f"Copernicus salinity fetch completed: {records_inserted} records"
            )

            return {
                "status": "success",
                "records_fetched": records_inserted,
                "records_inserted": records_inserted,
            }

        except Exception as e:
            logger.error(f"Error fetching Copernicus data: {e}")
            log.status = "failed"
            log.completed_at = timezone.now()
            log.error_message = str(e)
            log.save()
            raise

    def _fetch_with_toolbox(
        self,
        start_time: datetime,
        end_time: datetime,
        bounding_box: Optional[Dict] = None,
    ):
        """
        Fetch data using Copernicus Marine Toolbox.

        Returns number of records inserted.
        """
        client = self._get_copernicus_client()

        if client is None:
            # Fallback: Try using xarray with direct download
            return self._fetch_with_xarray(start_time, end_time, bounding_box)

        try:
            import pandas as pd
            import xarray as xr
            import tempfile
            import os

            # Create temporary directory for downloads
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = os.path.join(tmpdir, "salinity_data.nc")

                # Define bounding box (global if not specified)
                if bounding_box is None:
                    # Default to a reasonable subset (North Atlantic region where NOAA buoys are)
                    bounding_box = {
                        "min_lon": -80,
                        "max_lon": 0,
                        "min_lat": 20,
                        "max_lat": 60,
                    }

                # Download subset using copernicus-marine subset command
                logger.info("Downloading Copernicus salinity data...")

                try:
                    # Try using the Python API
                    client.subset(
                        dataset_id=self.SALINITY_DATASET,
                        variables=["so"],
                        minimum_longitude=bounding_box["min_lon"],
                        maximum_longitude=bounding_box["max_lon"],
                        minimum_latitude=bounding_box["min_lat"],
                        maximum_latitude=bounding_box["max_lat"],
                        start_datetime=start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                        end_datetime=end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                        output_filename=output_file,
                        username=self.username,
                        password=self.password,
                    )
                except Exception as e:
                    logger.warning(f"Copernicus subset API failed: {e}")
                    return 0

                # Process the downloaded NetCDF file
                if os.path.exists(output_file):
                    return self._process_netcdf_file(output_file)
                else:
                    logger.warning("No data file was downloaded")
                    return 0

        except ImportError as e:
            logger.warning(f"Missing dependency: {e}")
            return self._fetch_with_xarray(start_time, end_time, bounding_box)

    def _fetch_with_xarray(
        self,
        start_time: datetime,
        end_time: datetime,
        bounding_box: Optional[Dict] = None,
    ):
        """
        Alternative fetch method using xarray to access Copernicus THREDDS server.
        This doesn't require the copernicus-marine package.
        """
        try:
            import xarray as xr
            import pandas as pd

            # Copernicus Marine THREDDS URL for the salinity dataset
            # This requires authentication
            base_url = "https://nrt.cmems-du.eu/thredds/dodsC/cmems_mod_glo_phy-so_an_0.083deg_PT1H-m"

            logger.info(f"Accessing Copernicus via THREDDS: {base_url}")

            # Open dataset with authentication
            store = xr.backends.PydapDataStore.open(
                base_url, session=self._create_auth_session()
            )
            ds = xr.open_dataset(store)

            # Subset by time
            ds_subset = ds.sel(time=slice(start_time, end_time))

            # Subset by space if bounding box provided
            if bounding_box:
                ds_subset = ds_subset.sel(
                    longitude=slice(bounding_box["min_lon"], bounding_box["max_lon"]),
                    latitude=slice(bounding_box["min_lat"], bounding_box["max_lat"]),
                )

            # Process the data
            return self._process_xarray_dataset(ds_subset)

        except Exception as e:
            logger.error(f"xarray fetch failed: {e}")
            return 0

    def _create_auth_session(self):
        """Create authenticated session for THREDDS access."""
        from pydap.client import open_url
        from pydap.cas.get_cookies import setup_session

        # Copernicus CAS authentication
        cas_url = "https://cmems-cas.cls.fr/cas/login"
        session = setup_session(cas_url, self.username, self.password)
        return session

    def _process_netcdf_file(self, filepath: str) -> int:
        """
        Process a NetCDF file and store salinity data in database.

        Returns number of records inserted.
        """
        try:
            import xarray as xr

            ds = xr.open_dataset(filepath)
            return self._process_xarray_dataset(ds)

        except Exception as e:
            logger.error(f"Error processing NetCDF file: {e}")
            return 0

    def _process_xarray_dataset(self, ds) -> int:
        """
        Process an xarray Dataset and store salinity observations.

        Returns number of records inserted.
        """
        import pandas as pd

        records_inserted = 0

        try:
            # Get the salinity variable (usually 'so' in Copernicus datasets)
            salinity_var = "so" if "so" in ds.data_vars else None

            if not salinity_var:
                logger.error(
                    f"Salinity variable not found in dataset. Available: {list(ds.data_vars)}"
                )
                return 0

            logger.info(f"Processing salinity data from variable: {salinity_var}")

            # Convert to DataFrame
            # This assumes the dataset has dimensions: time, latitude, longitude
            df = ds[salinity_var].to_dataframe().reset_index()

            # Rename columns to standard names
            if "latitude" in df.columns:
                df = df.rename(columns={"latitude": "lat"})
            if "longitude" in df.columns:
                df = df.rename(columns={"longitude": "lon"})
            if "time" in df.columns:
                df = df.rename(columns={"time": "timestamp"})

            # Filter out NaN values
            df = df.dropna(subset=[salinity_var])

            logger.info(f"Processing {len(df)} salinity observations")

            # Group by location to reduce database queries
            for _, row in df.iterrows():
                try:
                    # Get or create location
                    location, _ = Location.objects.get_or_create(
                        latitude=float(row["lat"]),
                        longitude=float(row["lon"]),
                        defaults={
                            "name": f"Grid {row['lat']:.2f}, {row['lon']:.2f}",
                            "region": "Copernicus Global",
                        },
                    )

                    # Parse timestamp
                    if isinstance(row["timestamp"], pd.Timestamp):
                        timestamp = row["timestamp"].to_pydatetime()
                    else:
                        timestamp = pd.to_datetime(row["timestamp"])

                    # Make timezone-aware
                    if timezone.is_naive(timestamp):
                        timestamp = timezone.make_aware(timestamp)

                    # Validate salinity value
                    salinity_psu = float(row[salinity_var])
                    if not (0 <= salinity_psu <= 50):
                        continue

                    # Create observation
                    SalinityObservation.objects.update_or_create(
                        location=location,
                        source=self.source,
                        timestamp=timestamp,
                        defaults={"salinity_psu": salinity_psu},
                    )
                    records_inserted += 1

                except (ValueError, KeyError) as e:
                    logger.warning(f"Skipping row due to error: {e}")
                    continue

            return records_inserted

        except Exception as e:
            logger.error(f"Error processing dataset: {e}")
            return records_inserted

    def _sample_data_fallback(self, days_back: int = 1) -> int:
        """
        Generate sample salinity data for testing without API credentials.
        This creates realistic synthetic data for development purposes.
        """
        import random
        from datetime import timedelta

        records_inserted = 0
        end_time = timezone.now()
        start_time = end_time - timedelta(days=days_back)

        # Generate data for some sample locations
        sample_locations = [
            {"lat": 36.5, "lon": -122.5, "name": "Monterey Bay"},
            {"lat": 34.0, "lon": -119.0, "name": "Santa Barbara"},
            {"lat": 32.5, "lon": -117.5, "name": "San Diego"},
        ]

        logger.info(f"Generating {days_back} days of sample salinity data")

        for loc_data in sample_locations:
            location, _ = Location.objects.get_or_create(
                latitude=loc_data["lat"],
                longitude=loc_data["lon"],
                defaults={"name": loc_data["name"], "region": "Copernicus Sample"},
            )

            # Generate hourly data
            current_time = start_time
            while current_time < end_time:
                # Realistic salinity range for coastal California: 33-35 PSU
                base_salinity = 34.0
                variation = random.uniform(-0.8, 0.8)
                salinity_psu = base_salinity + variation

                SalinityObservation.objects.update_or_create(
                    location=location,
                    source=self.source,
                    timestamp=current_time,
                    defaults={"salinity_psu": round(salinity_psu, 3)},
                )
                records_inserted += 1

                current_time += timedelta(hours=1)

        logger.info(f"Generated {records_inserted} sample salinity records")
        return records_inserted


def fetch_latest_copernicus_data(use_sample: bool = False):
    """
    Convenience function for fetching Copernicus salinity data.

    Args:
        use_sample: If True, generate sample data instead of fetching from API

    Returns:
        dict: Ingestion statistics
    """
    service = CopernicusMarineService()

    if use_sample or not service.username:
        records = service._sample_data_fallback(days_back=1)
        return {
            "status": "success (sample data)",
            "records_inserted": records,
            "message": "Sample data generated (set COPERNICUS_API_USERNAME/PASSWORD for real data)",
        }

    return service.fetch_salinity_data(days_back=1)
