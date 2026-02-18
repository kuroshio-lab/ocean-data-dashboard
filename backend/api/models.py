"""
Data models for ocean observations.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class DataSource(models.Model):
    """
    Represents a data source (NOAA, Copernicus, NASA, etc.)
    """

    name = models.CharField(max_length=100, unique=True)
    url = models.URLField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    last_fetch = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Data Source"
        verbose_name_plural = "Data Sources"

    def __str__(self):
        return self.name


class Location(models.Model):
    """
    Represents a geographic location for ocean measurements.
    """

    name = models.CharField(max_length=200)
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    depth_meters = models.FloatField(
        null=True,
        blank=True,
        help_text="Depth in meters (negative for below sea level)",
    )
    region = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ["latitude", "longitude", "depth_meters"]
        indexes = [
            models.Index(fields=["latitude", "longitude"]),
            models.Index(fields=["region"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"


class TemperatureObservation(models.Model):
    """
    Temperature measurements at specific locations and times.
    """

    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="temperature_observations"
    )
    source = models.ForeignKey(
        DataSource, on_delete=models.CASCADE, related_name="temperature_observations"
    )
    timestamp = models.DateTimeField(db_index=True)
    temperature_celsius = models.FloatField(help_text="Temperature in degrees Celsius")
    quality_flag = models.CharField(
        max_length=20, blank=True, help_text="Data quality indicator from source"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        unique_together = ["location", "source", "timestamp"]
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["location", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.location} - {self.temperature_celsius}°C at {self.timestamp}"


class SalinityObservation(models.Model):
    """
    Salinity measurements (PSU - Practical Salinity Units).
    """

    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="salinity_observations"
    )
    source = models.ForeignKey(
        DataSource, on_delete=models.CASCADE, related_name="salinity_observations"
    )
    timestamp = models.DateTimeField(db_index=True)
    salinity_psu = models.FloatField(
        help_text="Salinity in Practical Salinity Units (PSU)"
    )
    quality_flag = models.CharField(
        max_length=20, blank=True, help_text="Data quality indicator from source"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        unique_together = ["location", "source", "timestamp"]
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["location", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.location} - {self.salinity_psu} PSU at {self.timestamp}"


class CurrentObservation(models.Model):
    """
    Ocean current measurements (speed and direction).
    """

    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="current_observations"
    )
    source = models.ForeignKey(
        DataSource, on_delete=models.CASCADE, related_name="current_observations"
    )
    timestamp = models.DateTimeField(db_index=True)
    speed_ms = models.FloatField(help_text="Current speed in meters per second")
    direction_degrees = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(360)],
        help_text="Current direction in degrees (0-360, meteorological convention)",
    )
    u_component = models.FloatField(
        null=True, blank=True, help_text="East-west component (m/s)"
    )
    v_component = models.FloatField(
        null=True, blank=True, help_text="North-south component (m/s)"
    )
    quality_flag = models.CharField(
        max_length=20, blank=True, help_text="Data quality indicator from source"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        unique_together = ["location", "source", "timestamp"]
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["location", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.location} - {self.speed_ms} m/s at {self.timestamp}"


class IngestionLog(models.Model):
    """
    Tracks data ingestion jobs for monitoring and debugging.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    source = models.ForeignKey(
        DataSource, on_delete=models.CASCADE, related_name="ingestion_logs"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    records_fetched = models.IntegerField(default=0)
    records_inserted = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    task_id = models.CharField(max_length=255, blank=True, help_text="Celery task ID")

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["-started_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.source.name} - {self.status} at {self.started_at}"
