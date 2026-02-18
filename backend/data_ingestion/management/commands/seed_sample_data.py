"""
Management command to seed the database with sample data.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from api.models import DataSource, Location, TemperatureObservation, SalinityObservation


class Command(BaseCommand):
    help = "Seed database with sample ocean data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=7,
            help="Number of days of sample data to generate (default: 7)",
        )
        parser.add_argument(
            "--points-per-day",
            type=int,
            default=24,
            help="Number of data points per day (default: 24)",
        )

    def handle(self, *args, **options):
        days = options["days"]
        points_per_day = options["points_per_day"]

        self.stdout.write(
            self.style.SUCCESS(
                f"Generating {days} days of sample data with {points_per_day} points per day..."
            )
        )

        # Create or get data source
        source, created = DataSource.objects.get_or_create(
            name="Sample Data",
            defaults={
                "url": "http://example.com",
                "description": "Synthetic sample data for testing",
                "is_active": True,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS("✓ Created sample data source"))

        # Create sample locations
        locations_data = [
            {
                "name": "California Coast",
                "latitude": 36.9741,
                "longitude": -122.0308,
                "region": "Pacific Ocean",
                "temp_base": 15.0,
                "salinity_base": 33.5,
            },
            {
                "name": "Gulf of Mexico",
                "latitude": 27.5,
                "longitude": -90.5,
                "region": "Gulf of Mexico",
                "temp_base": 24.0,
                "salinity_base": 36.0,
            },
            {
                "name": "New England Coast",
                "latitude": 42.3,
                "longitude": -70.8,
                "region": "Atlantic Ocean",
                "temp_base": 12.0,
                "salinity_base": 32.0,
            },
        ]

        locations = []
        for loc_data in locations_data:
            location, created = Location.objects.get_or_create(
                name=loc_data["name"],
                latitude=loc_data["latitude"],
                longitude=loc_data["longitude"],
                defaults={"region": loc_data["region"]},
            )
            locations.append(
                {
                    "location": location,
                    "temp_base": loc_data["temp_base"],
                    "salinity_base": loc_data["salinity_base"],
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created location: {loc_data["name"]}')
                )

        # Generate time series data
        total_points = days * points_per_day
        current_time = timezone.now() - timedelta(days=days)
        time_increment = timedelta(hours=24 / points_per_day)

        temp_count = 0
        salinity_count = 0

        for i in range(total_points):
            timestamp = current_time + (time_increment * i)

            for loc_data in locations:
                location = loc_data["location"]

                # Generate temperature with seasonal variation and noise
                day_of_year = timestamp.timetuple().tm_yday
                seasonal_variation = 5 * math.sin(2 * math.pi * day_of_year / 365)
                temp = (
                    loc_data["temp_base"] + seasonal_variation + random.uniform(-2, 2)
                )

                TemperatureObservation.objects.create(
                    location=location,
                    source=source,
                    timestamp=timestamp,
                    temperature_celsius=round(temp, 2),
                )
                temp_count += 1

                # Generate salinity with slight variation
                salinity = loc_data["salinity_base"] + random.uniform(-0.5, 0.5)

                SalinityObservation.objects.create(
                    location=location,
                    source=source,
                    timestamp=timestamp,
                    salinity_psu=round(salinity, 2),
                )
                salinity_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Successfully generated sample data:")
        )
        self.stdout.write(f"  - {len(locations)} locations")
        self.stdout.write(f"  - {temp_count} temperature observations")
        self.stdout.write(f"  - {salinity_count} salinity observations")
        self.stdout.write(f"  - {days} days of data")


import math  # Import at the top in actual implementation
