"""
Django admin configuration for ocean data models.
"""

from django.contrib import admin
from .models import (
    DataSource,
    Location,
    TemperatureObservation,
    SalinityObservation,
    CurrentObservation,
    IngestionLog,
)


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "last_fetch", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["name", "latitude", "longitude", "depth_meters", "region"]
    list_filter = ["region"]
    search_fields = ["name", "region"]
    readonly_fields = ["created_at"]


@admin.register(TemperatureObservation)
class TemperatureObservationAdmin(admin.ModelAdmin):
    list_display = [
        "location",
        "source",
        "timestamp",
        "temperature_celsius",
        "quality_flag",
    ]
    list_filter = ["source", "quality_flag", "timestamp"]
    search_fields = ["location__name"]
    readonly_fields = ["created_at"]
    date_hierarchy = "timestamp"


@admin.register(SalinityObservation)
class SalinityObservationAdmin(admin.ModelAdmin):
    list_display = ["location", "source", "timestamp", "salinity_psu", "quality_flag"]
    list_filter = ["source", "quality_flag", "timestamp"]
    search_fields = ["location__name"]
    readonly_fields = ["created_at"]
    date_hierarchy = "timestamp"


@admin.register(CurrentObservation)
class CurrentObservationAdmin(admin.ModelAdmin):
    list_display = [
        "location",
        "source",
        "timestamp",
        "speed_ms",
        "direction_degrees",
        "quality_flag",
    ]
    list_filter = ["source", "quality_flag", "timestamp"]
    search_fields = ["location__name"]
    readonly_fields = ["created_at"]
    date_hierarchy = "timestamp"


@admin.register(IngestionLog)
class IngestionLogAdmin(admin.ModelAdmin):
    list_display = [
        "source",
        "status",
        "started_at",
        "completed_at",
        "records_inserted",
    ]
    list_filter = ["status", "source", "started_at"]
    search_fields = ["source__name", "task_id", "error_message"]
    readonly_fields = ["started_at", "task_id"]
    date_hierarchy = "started_at"

    def has_add_permission(self, request):
        # Ingestion logs should only be created by the system
        return False
