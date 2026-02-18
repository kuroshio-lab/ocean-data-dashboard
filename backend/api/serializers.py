"""
Serializers for API models.
"""

from rest_framework import serializers
from .models import (
    DataSource,
    Location,
    TemperatureObservation,
    SalinityObservation,
    CurrentObservation,
    IngestionLog,
)


class DataSourceSerializer(serializers.ModelSerializer):
    """Serializer for DataSource model."""

    class Meta:
        model = DataSource
        fields = [
            "id",
            "name",
            "url",
            "description",
            "is_active",
            "last_fetch",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "last_fetch"]


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location model."""

    class Meta:
        model = Location
        fields = [
            "id",
            "name",
            "latitude",
            "longitude",
            "depth_meters",
            "region",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class TemperatureObservationSerializer(serializers.ModelSerializer):
    """Serializer for TemperatureObservation model."""

    location_name = serializers.CharField(source="location.name", read_only=True)
    source_name = serializers.CharField(source="source.name", read_only=True)

    class Meta:
        model = TemperatureObservation
        fields = [
            "id",
            "location",
            "location_name",
            "source",
            "source_name",
            "timestamp",
            "temperature_celsius",
            "quality_flag",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class SalinityObservationSerializer(serializers.ModelSerializer):
    """Serializer for SalinityObservation model."""

    location_name = serializers.CharField(source="location.name", read_only=True)
    source_name = serializers.CharField(source="source.name", read_only=True)

    class Meta:
        model = SalinityObservation
        fields = [
            "id",
            "location",
            "location_name",
            "source",
            "source_name",
            "timestamp",
            "salinity_psu",
            "quality_flag",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class CurrentObservationSerializer(serializers.ModelSerializer):
    """Serializer for CurrentObservation model."""

    location_name = serializers.CharField(source="location.name", read_only=True)
    source_name = serializers.CharField(source="source.name", read_only=True)

    class Meta:
        model = CurrentObservation
        fields = [
            "id",
            "location",
            "location_name",
            "source",
            "source_name",
            "timestamp",
            "speed_ms",
            "direction_degrees",
            "u_component",
            "v_component",
            "quality_flag",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class IngestionLogSerializer(serializers.ModelSerializer):
    """Serializer for IngestionLog model."""

    source_name = serializers.CharField(source="source.name", read_only=True)
    duration_seconds = serializers.SerializerMethodField()

    class Meta:
        model = IngestionLog
        fields = [
            "id",
            "source",
            "source_name",
            "status",
            "started_at",
            "completed_at",
            "duration_seconds",
            "records_fetched",
            "records_inserted",
            "error_message",
            "task_id",
        ]
        read_only_fields = ["started_at"]

    def get_duration_seconds(self, obj):
        """Calculate duration of ingestion job."""
        if obj.completed_at and obj.started_at:
            delta = obj.completed_at - obj.started_at
            return round(delta.total_seconds(), 2)
        return None


class TimeSeriesDataSerializer(serializers.Serializer):
    """
    Generic serializer for time-series data aggregations.
    Used for chart data endpoints.
    """

    timestamp = serializers.DateTimeField()
    value = serializers.FloatField()
    location = serializers.CharField(required=False)
    variable = serializers.CharField(required=False)

    class Meta:
        read_only_fields = ["timestamp", "value", "location", "variable"]
