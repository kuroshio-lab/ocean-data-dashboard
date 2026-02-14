# Ocean Data Dashboard - Backend

Django REST API for ocean data ingestion and visualization.

## Features

- **REST API**: Django REST Framework endpoints for ocean data
- **Data Ingestion**: Automated fetching from NOAA ERDDAP, Copernicus, NASA
- **Background Jobs**: Celery workers for async data processing
- **Database**: PostgreSQL for time-series data storage
- **API Documentation**: Auto-generated Swagger/ReDoc docs

## Tech Stack

- Django 5.0
- Django REST Framework
- Celery + Redis
- PostgreSQL
- Docker

## Setup

### Local Development (without Docker)

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Start Redis** (required for Celery)
```bash
# Install and start Redis, or use Docker:
docker run -p 6379:6379 redis:7-alpine
```

7. **Start Celery worker** (in a new terminal)
```bash
celery -A celery_app worker --loglevel=info
```

8. **Start development server**
```bash
python manage.py runserver
```

### Docker Development

See main README.md for Docker setup instructions.

## API Endpoints

Once running, visit:
- API Root: http://localhost:8000/api/
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Django Admin: http://localhost:8000/admin/

### Available Endpoints

```
GET  /api/sources/              # List data sources
GET  /api/locations/            # List monitoring locations
GET  /api/temperature/          # Temperature observations
GET  /api/temperature/time_series/  # Time-series data for charts
GET  /api/salinity/             # Salinity observations
GET  /api/currents/             # Current observations
GET  /api/ingestion-logs/       # Data ingestion logs
```

## Data Ingestion

### Fetch NOAA Data

```bash
# Fetch last 1 day of data
python manage.py fetch_noaa_data

# Fetch last 7 days
python manage.py fetch_noaa_data --days 7

# Specify dataset
python manage.py fetch_noaa_data --dataset cwwcNDBCMet
```

### Generate Sample Data

For testing without external APIs:

```bash
python manage.py seed_sample_data --days 7 --points-per-day 24
```

### Scheduled Tasks

Celery Beat automatically runs these tasks:
- Fetch NOAA data every 6 hours
- Fetch Copernicus data every 6 hours (when configured)
- Cleanup old data daily

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test api
python manage.py test data_ingestion

# With coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint
flake8 .
```

## Project Structure

```
backend/
├── api/                    # REST API app
│   ├── models.py          # Data models
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API views
│   └── urls.py            # URL routing
├── core/                  # Django settings
│   ├── settings.py        # Configuration
│   ├── urls.py            # Main URL config
│   └── celery.py          # Celery setup
├── data_ingestion/        # Data ingestion app
│   ├── services/          # Service classes for APIs
│   │   ├── noaa_service.py
│   │   ├── copernicus_service.py
│   │   └── cleanup_service.py
│   └── management/        # Management commands
│       └── commands/
├── celery_app/            # Celery tasks
│   └── tasks.py
└── manage.py
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `DJANGO_SECRET_KEY`: Secret key for Django
- `FETCH_INTERVAL_HOURS`: Data ingestion frequency
- `DATA_RETENTION_DAYS`: How long to keep data

## Troubleshooting

### Database connection errors
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Run migrations: `python manage.py migrate`

### Celery worker not processing tasks
- Ensure Redis is running
- Check CELERY_BROKER_URL in .env
- Restart Celery worker

### API returns empty data
- Run data ingestion: `python manage.py fetch_noaa_data`
- Or generate sample data: `python manage.py seed_sample_data`
- Check ingestion logs at /admin/

## Contributing

1. Create a feature branch
2. Write tests for new features
3. Ensure all tests pass
4. Format code with black and isort
5. Submit a pull request

## License

MIT
