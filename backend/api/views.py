"""
API views for ocean data.
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count, Max, Min
from datetime import datetime, timedelta

from .models import (
    DataSource,
    Location,
    TemperatureObservation,
    SalinityObservation,
    CurrentObservation,
    IngestionLog,
)
from .serializers import (
    DataSourceSerializer,
    LocationSerializer,
    TemperatureObservationSerializer,
    SalinityObservationSerializer,
    CurrentObservationSerializer,
    IngestionLogSerializer,
    TimeSeriesDataSerializer,
)


class DataSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for data sources.
    """

    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["is_active"]
    search_fields = ["name", "description"]


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for locations.
    """

    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["region"]
    search_fields = ["name", "region"]
    ordering_fields = ["name", "latitude", "longitude"]


class TemperatureObservationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for temperature observations.
    """

    queryset = TemperatureObservation.objects.select_related("location", "source")
    serializer_class = TemperatureObservationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["location", "source"]
    ordering_fields = ["timestamp", "temperature_celsius"]

    def get_queryset(self):
        """
        Optionally filter by date range.
        """
        queryset = super().get_queryset()

        # Date range filtering
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        return queryset

    @action(detail=False, methods=["get"])
    def time_series(self, request):
        """
        Get aggregated time-series data for charting.
        """
        location_id = request.query_params.get("location")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        queryset = self.get_queryset()

        if location_id:
            queryset = queryset.filter(location_id=location_id)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        # Group by hour and calculate average
        data = (
            queryset.values("timestamp")
            .annotate(value=Avg("temperature_celsius"))
            .order_by("timestamp")
        )

        serializer = TimeSeriesDataSerializer(data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """
        Get statistical summary of temperature data.
        """
        queryset = self.get_queryset()

        stats = queryset.aggregate(
            avg_temperature=Avg("temperature_celsius"),
            min_temperature=Min("temperature_celsius"),
            max_temperature=Max("temperature_celsius"),
            total_observations=Count("id"),
        )

        return Response(stats)


class SalinityObservationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for salinity observations.
    """

    queryset = SalinityObservation.objects.select_related("location", "source")
    serializer_class = SalinityObservationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["location", "source"]
    ordering_fields = ["timestamp", "salinity_psu"]

    def get_queryset(self):
        """
        Optionally filter by date range.
        """
        queryset = super().get_queryset()

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        return queryset

    @action(detail=False, methods=["get"])
    def time_series(self, request):
        """
        Get aggregated time-series data for charting.
        """
        location_id = request.query_params.get("location")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        queryset = self.get_queryset()

        if location_id:
            queryset = queryset.filter(location_id=location_id)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        data = (
            queryset.values("timestamp")
            .annotate(value=Avg("salinity_psu"))
            .order_by("timestamp")
        )

        serializer = TimeSeriesDataSerializer(data, many=True)
        return Response(serializer.data)


class CurrentObservationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for current observations.
    """

    queryset = CurrentObservation.objects.select_related("location", "source")
    serializer_class = CurrentObservationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["location", "source"]
    ordering_fields = ["timestamp", "speed_ms"]

    def get_queryset(self):
        """
        Optionally filter by date range.
        """
        queryset = super().get_queryset()

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        return queryset

    @action(detail=False, methods=["get"])
    def time_series(self, request):
        """
        Get aggregated time-series data for charting.
        """
        location_id = request.query_params.get("location")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        queryset = self.get_queryset()

        if location_id:
            queryset = queryset.filter(location_id=location_id)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        data = (
            queryset.values("timestamp")
            .annotate(value=Avg("speed_ms"))
            .order_by("timestamp")
        )

        serializer = TimeSeriesDataSerializer(data, many=True)
        return Response(serializer.data)


class IngestionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for ingestion logs (monitoring).
    """

    queryset = IngestionLog.objects.select_related("source")
    serializer_class = IngestionLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["source", "status"]
    ordering_fields = ["started_at", "completed_at"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        Get summary statistics of ingestion jobs.
        """
        last_24h = datetime.now() - timedelta(hours=24)

        summary = {
            "total_jobs": IngestionLog.objects.count(),
            "last_24h": IngestionLog.objects.filter(started_at__gte=last_24h).count(),
            "success_rate": self._calculate_success_rate(),
            "recent_failures": IngestionLog.objects.filter(status="failed")
            .order_by("-started_at")[:5]
            .values("source__name", "started_at", "error_message"),
        }

        return Response(summary)

    def _calculate_success_rate(self):
        """Calculate success rate of ingestion jobs."""
        total = IngestionLog.objects.count()
        if total == 0:
            return 0

        successful = IngestionLog.objects.filter(status="success").count()
        return round((successful / total) * 100, 2)
