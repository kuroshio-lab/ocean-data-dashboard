# backend/CLAUDE.md

Guidance for Django backend development. **Public API = Security & Cost-consciousness First.**

## Architecture Overview

```
External APIs (NOAA, Copernicus, NASA)
    ↓
Celery Tasks / Lambda (data ingestion)
    ↓
PostgreSQL (30-day rolling window)
    ↓
Django REST API (rate-limited, cached)
    ↓
Frontend / Public consumers
```

### Key Stack
- **Framework**: Django REST Framework (DRF)
- **Async Tasks**: Celery + Celery Beat (local), AWS Lambda (production)
- **Caching**: Redis (time-series data, aggregations, locations)
- **Database**: PostgreSQL (observations, locations, metadata)
- **Data Retention**: Keep last 30 days only (monthly aggressive cleanup)

## Security: First Principles

Since the API is **public and has no login**, security constraints are essential:

### 1. Rate Limiting (Mandatory)
All endpoints must have rate limiting. Strategy:

```
Global: 100 requests/minute per IP
Per-endpoint:
  - /observations/list → 100 req/min (cheap)
  - /observations/time-series → 10 req/min (expensive, hits cache or DB)
  - /locations → 50 req/min (cached)
```

**Implementation**:
- Use `djangorestframework-simplejwt` + `django-ratelimit` OR `drf-spectacular` with rate limit middleware
- Return `429 Too Many Requests` with `Retry-After` header
- Rate limit key: client IP (X-Forwarded-For for proxies)
- Exempt internal services (mark with `@skip_ratelimit` if needed)

### 2. Input Validation & Parsing
Treat all incoming data as untrusted:

- **Coordinates**: Validate latitude (-90 to 90), longitude (-180 to 180)
- **Dates**: Parse as ISO 8601 only. Reject malformed input.
- **Depth**: Positive numbers only, reasonable bounds (0-11000m)
- **Query parameters**: Whitelist allowed fields. Reject unknown params.

Example:
```python
class ObservationFilterSerializer(serializers.Serializer):
    location_id = serializers.IntegerField(required=False)
    start_date = serializers.DateField(required=False, format='iso-8601')
    end_date = serializers.DateField(required=False, format='iso-8601')

    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and start > end:
            raise ValidationError("start_date must be before end_date")
        return data
```

### 3. Cost Protection
Prevent expensive queries:

- Limit time-series query window: max 7 days per request
- Enforce `limit` parameter: max 1000 rows, default 100
- Cache aggregations (daily, hourly) instead of raw observations
- Reject queries older than 30 days (data is deleted anyway)

## Caching Strategy (Cost-Critical)

Cache priorities (to minimize external API calls & database queries):

### High Priority (Cache 6-24 hours)
- **Daily aggregations**: Min/max/avg temperature, salinity per location per day
  - Most user-facing dashboards use this
  - Pre-compute via Celery task after data ingestion
  - Cache key: `aggregation:{location_id}:{date}:{metric}`

### Medium Priority (Cache 1 hour)
- **Location list**: All available locations + metadata
  - Rarely changes
  - Cache key: `locations:all`

### Medium Priority (Cache 5 minutes)
- **Last-known values**: Most recent observation per location
  - Frontend dashboards refresh frequently
  - Cache key: `latest:{location_id}:{observation_type}`

### Don't Cache
- **Raw time-series data** (unless client explicitly requests, in which case aggregate first)
- **User-specific data** (none exists, but note for future)

Cache invalidation:
- On new data ingestion: Invalidate `latest:*` and daily aggregation for that location
- Hourly: Flush all caches (safe fallback)

## Data Retention & Cleanup

**Monthly aggressive cleanup** to minimize storage costs:

- Keep last 30 days of observations only
- Schedule: First day of month at 2 AM UTC
- Task: `backend/celery_app/tasks.py` → `cleanup_old_observations()`
- Query: `Observation.objects.filter(timestamp__lt=now() - 30days).delete()`

⚠️ **Consequence**: No historical trends beyond 30 days. This is intentional for cost optimization. If users need trends, consider:
- Time-series database (InfluxDB) for historical archival
- AWS S3 for parquet data backups
- Document this limitation clearly

## Celery Task Design

All tasks must be **idempotent** and **complete within 1 day**:

### Task Structure
```python
@shared_task(bind=True, max_retries=3)
def fetch_temperature_data(self):
    """Idempotent: safe to run multiple times."""
    try:
        service = NOAAService()
        data = service.fetch()  # Last 6 hours of data
        for obs in data:
            TemperatureObservation.objects.update_or_create(
                location=obs.location,
                timestamp=obs.timestamp,
                defaults={'value': obs.value, 'quality_flag': obs.quality_flag}
            )
        # Invalidate cache
        cache.delete_pattern('latest:temperature:*')
        cache.delete_pattern('aggregation:*')
    except Exception as exc:
        self.retry(countdown=60, exc=exc)
```

### Celery Beat Schedule
Local (Docker): Every 6 hours for most data, daily for expensive endpoints
Lambda (future): Same schedule, but executed via CloudWatch events

```python
# backend/core/settings.py
CELERY_BEAT_SCHEDULE = {
    'fetch-temperature': {
        'task': 'celery_app.tasks.fetch_temperature_data',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    'fetch-chlorophyll': {
        'task': 'celery_app.tasks.fetch_chlorophyll_data',
        'schedule': crontab(minute=0, hour=2),  # Daily at 2 AM UTC
    },
    'cleanup-old-data': {
        'task': 'celery_app.tasks.cleanup_old_observations',
        'schedule': crontab(day_of_month=1, hour=2, minute=0),  # 1st of month
    },
}
```

## API Endpoints (Public)

All endpoints are public and rate-limited:

### GET /api/locations/
Returns list of available locations.
```
Response: 200 OK
[
  {
    "id": 1,
    "name": "Kuroshio Current",
    "latitude": 30.5,
    "longitude": 135.0,
    "depth": 100
  }
]
Cache: 1 hour
Rate limit: 50 req/min
```

### GET /api/observations/latest/
Returns most recent observation per location.
```
Query params: ?location_id=1&observation_type=temperature
Response: 200 OK
[
  {
    "location_id": 1,
    "timestamp": "2026-02-18T12:00:00Z",
    "value": 18.5,
    "quality_flag": "good",
    "source": "NOAA"
  }
]
Cache: 5 minutes
Rate limit: 100 req/min
```

### GET /api/observations/aggregated/
Returns daily aggregations (min/max/avg).
```
Query params: ?location_id=1&start_date=2026-02-01&end_date=2026-02-18&observation_type=temperature
Response: 200 OK
[
  {
    "date": "2026-02-18",
    "location_id": 1,
    "min": 17.2,
    "max": 19.1,
    "avg": 18.4,
    "count": 24
  }
]
Cache: 6 hours
Rate limit: 10 req/min (expensive aggregation query)
Max date range: 7 days
```

## Database Models (Security)

All observations have:
- `location` (ForeignKey to Location)
- `timestamp` (IndexedDateTimeField, enforced as UTC)
- `source` (DataSource, e.g., NOAA)
- `quality_flag` (enum: 'good', 'questionable', 'bad')
- Observation-specific field (e.g., `temperature` for TemperatureObservation)

Indexes:
- `(location, timestamp)` for time-series queries
- `timestamp` alone for cleanup queries
- `source` for filtering by data provider

⚠️ **Query design**: Always filter by location or timestamp to avoid full table scans.

## Testing Backend

All endpoints must be tested:

```bash
docker-compose exec backend python manage.py test api
docker-compose exec backend python manage.py test data_ingestion
```

Focus areas:
- Rate limiting kicks in after N requests
- Input validation rejects bad coordinates/dates
- Caching returns same data for repeated requests
- Celery tasks are idempotent (can run multiple times)
- Data cleanup deletes data older than 30 days

## Common Tasks

### Adding a New Observation Type
1. Create model in `api/models.py` (extend `BaseObservation`)
2. Create serializer in `api/serializers.py`
3. Create ViewSet in `api/views.py` + register in `urls.py`
4. Create service in `data_ingestion/services/new_source.py`
5. Create Celery task in `celery_app/tasks.py`
6. Add to `CELERY_BEAT_SCHEDULE` in `core/settings.py`
7. Add tests in `tests/`

### Debugging a Data Ingestion Task
```bash
# Check Celery worker logs
docker-compose logs -f celery-worker

# Run task manually for testing
docker-compose exec backend python manage.py shell
>>> from celery_app.tasks import fetch_temperature_data
>>> fetch_temperature_data()

# Check IngestionLog in Django admin
# http://localhost:8000/admin/data_ingestion/ingestionlog/
```

### Checking Cache Hit Rate
```bash
docker-compose exec backend python manage.py shell
>>> from django.core.cache import cache
>>> cache.get('locations:all')  # Hit = data, Miss = None
```

## Important Notes

### Cost Implications
- **30-day retention**: Aggressive storage savings, but no long-term trends
- **Caching everything**: Reduces expensive external API calls (major cost driver)
- **Aggregations only**: Avoid raw time-series in responses; pre-aggregate
- **Rate limiting**: Prevents runaway queries that spike cloud DB costs

### Production Deployment (AWS/GCP/Azure)
- Use managed PostgreSQL (RDS, Cloud SQL) with auto-scaling
- Redis managed service (ElastiCache, Cloud Memorystore)
- Celery workers on auto-scaling groups
- CloudWatch alarms for task failures
- DDoS protection: CloudFlare or cloud provider WAF

### Environment Variables (see infra/CLAUDE.md)
- `DJANGO_DEBUG=False` in production
- `DJANGO_SECRET_KEY` → strong random value
- `RATE_LIMIT_ENABLED=True`
- `CACHE_TTL_LOCATIONS=3600` (seconds)
- `CACHE_TTL_LATEST=300`

---

**See infra/CLAUDE.md** for Docker, environment setup, and cloud deployment.
