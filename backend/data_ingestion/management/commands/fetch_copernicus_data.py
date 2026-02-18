"""
Management command to fetch ocean salinity data from Copernicus Marine Service.
"""

from django.core.management.base import BaseCommand
from data_ingestion.services.copernicus_service import (
    CopernicusMarineService,
    fetch_latest_copernicus_data,
)


class Command(BaseCommand):
    help = "Fetch ocean salinity data from Copernicus Marine Service"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=1,
            help="Number of days of historical data to fetch (default: 1)",
        )
        parser.add_argument(
            "--sample",
            action="store_true",
            help="Generate sample data instead of fetching from API (for testing)",
        )
        parser.add_argument(
            "--min-lat",
            type=float,
            default=20,
            help="Minimum latitude for bounding box (default: 20)",
        )
        parser.add_argument(
            "--max-lat",
            type=float,
            default=60,
            help="Maximum latitude for bounding box (default: 60)",
        )
        parser.add_argument(
            "--min-lon",
            type=float,
            default=-80,
            help="Minimum longitude for bounding box (default: -80)",
        )
        parser.add_argument(
            "--max-lon",
            type=float,
            default=0,
            help="Maximum longitude for bounding box (default: 0)",
        )

    def handle(self, *args, **options):
        days = options["days"]
        use_sample = options["sample"]

        bounding_box = {
            "min_lat": options["min_lat"],
            "max_lat": options["max_lat"],
            "min_lon": options["min_lon"],
            "max_lon": options["max_lon"],
        }

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting Copernicus salinity data fetch for last {days} day(s)..."
            )
        )

        if use_sample:
            self.stdout.write(
                self.style.WARNING(
                    "Using SAMPLE DATA mode (no API credentials required)"
                )
            )

        try:
            service = CopernicusMarineService()

            if use_sample:
                result = fetch_latest_copernicus_data(use_sample=True)
            else:
                result = service.fetch_salinity_data(
                    days_back=days, bounding_box=bounding_box
                )

            if result["status"] == "skipped":
                self.stdout.write(self.style.WARNING(f"⚠ {result['message']}"))
                self.stdout.write(
                    self.style.WARNING(
                        "Use --sample flag to generate test data, or set COPERNICUS_API_USERNAME and COPERNICUS_API_PASSWORD environment variables."
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Fetch completed: {result['records_inserted']} salinity records inserted"
                    )
                )
                if "message" in result:
                    self.stdout.write(self.style.NOTICE(f"  {result['message']}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error: {str(e)}"))
            raise
