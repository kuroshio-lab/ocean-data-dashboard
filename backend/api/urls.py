"""
URL configuration for API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"sources", views.DataSourceViewSet, basename="datasource")
router.register(r"locations", views.LocationViewSet, basename="location")
router.register(
    r"temperature", views.TemperatureObservationViewSet, basename="temperature"
)
router.register(r"salinity", views.SalinityObservationViewSet, basename="salinity")
router.register(r"currents", views.CurrentObservationViewSet, basename="currents")
router.register(r"ingestion-logs", views.IngestionLogViewSet, basename="ingestion-logs")

app_name = "api"

urlpatterns = [
    path("", include(router.urls)),
]
