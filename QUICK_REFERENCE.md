# Ocean Data Dashboard - Quick Reference

## 🚀 Getting Started (5 minutes)

```bash
cd ocean-dashboard
./scripts/quickstart.sh
docker-compose exec backend python manage.py seed_sample_data --days 7
# Open http://localhost:3000
```

## 📂 Project Structure

```
ocean-dashboard/
├── backend/          Django + DRF + Celery
├── frontend/         Next.js + TypeScript  
├── infra/docker/     Dockerfiles
├── .github/          CI/CD workflows
└── scripts/          Helper scripts
```

## 🔑 Essential Commands

### Docker Operations
```bash
make docker-up          # Start everything
make docker-down        # Stop everything
make docker-logs        # View all logs
make restart            # Restart services
```

### Database
```bash
make migrate            # Run migrations
make makemigrations     # Create migrations
make createsuperuser    # Create admin user
make db-shell          # PostgreSQL shell
```

### Data Management
```bash
make fetch-data                    # Fetch NOAA data
docker-compose exec backend \
  python manage.py seed_sample_data  # Generate test data
```

### Development
```bash
make logs-backend       # Backend logs
make logs-frontend      # Frontend logs
make logs-celery       # Celery worker logs
make test-backend      # Run backend tests
make test-frontend     # Run frontend tests
```

### Code Quality
```bash
make lint-backend      # Format Python code
make lint-frontend     # Lint TypeScript
make format           # Format all code
```

## 🌐 URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main application |
| API Root | http://localhost:8000/api/ | REST API |
| Admin | http://localhost:8000/admin/ | Django admin |
| API Docs | http://localhost:8000/api/docs/ | Swagger UI |
| ReDoc | http://localhost:8000/api/redoc/ | API documentation |

## 📊 API Endpoints

```
GET /api/sources/                      # Data sources
GET /api/locations/                    # Monitoring locations
GET /api/temperature/                  # Temperature observations
GET /api/temperature/time_series/      # Chart data
GET /api/salinity/                     # Salinity observations
GET /api/currents/                     # Current observations
GET /api/ingestion-logs/               # Data fetch logs
GET /api/ingestion-logs/summary/       # Ingestion stats
```

## 🔧 Environment Variables

### Backend (.env)
```bash
DATABASE_URL=postgresql://oceanuser:oceanpass@localhost:5432/oceandb
REDIS_URL=redis://localhost:6379/0
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_NAME=Ocean Data Dashboard
```

## 📝 Common Tasks

### Add a new API endpoint
1. Edit `backend/api/models.py` - Add model
2. Run `make makemigrations && make migrate`
3. Edit `backend/api/serializers.py` - Add serializer
4. Edit `backend/api/views.py` - Add viewset
5. Edit `backend/api/urls.py` - Register route

### Add a new chart component
1. Create file in `frontend/src/components/`
2. Import and use in `frontend/src/pages/index.tsx`
3. Use API client from `frontend/src/lib/api.ts`

### Add a data source
1. Create service in `backend/data_ingestion/services/`
2. Add task in `backend/celery_app/tasks.py`
3. Create management command in `backend/data_ingestion/management/commands/`

## 🐛 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| No data showing | Run `make fetch-data` or seed sample data |
| Port already in use | Change ports in docker-compose.yml |
| Database error | Check PostgreSQL is running, run migrations |
| Celery not working | Ensure Redis is running |
| Frontend won't build | Delete .next folder, reinstall node_modules |
| Docker build fails | Run `docker system prune -a` |

## 📦 File Locations

| What | Where |
|------|-------|
| API views | `backend/api/views.py` |
| Data models | `backend/api/models.py` |
| Data ingestion | `backend/data_ingestion/services/` |
| Celery tasks | `backend/celery_app/tasks.py` |
| Frontend pages | `frontend/src/pages/` |
| React components | `frontend/src/components/` |
| API client | `frontend/src/lib/api.ts` |
| Type definitions | `frontend/src/types/index.ts` |

## 🧪 Testing

```bash
# Backend
docker-compose exec backend python manage.py test

# Frontend  
cd frontend && npm test

# With coverage
cd backend && coverage run manage.py test && coverage report
```

## 📚 Documentation

- Setup Guide: `SETUP_GUIDE.md`
- Contributing: `CONTRIBUTING.md`
- Backend: `backend/README.md`
- Frontend: `frontend/README.md`

## 🎯 Development Checklist

- [ ] Run quickstart script
- [ ] Create superuser
- [ ] Generate sample data
- [ ] Access frontend at :3000
- [ ] Access admin at :8000/admin
- [ ] Check API docs at :8000/api/docs
- [ ] View backend logs
- [ ] Run tests

## 💡 Pro Tips

1. Use `make help` to see all available commands
2. Keep Docker Desktop running for best performance
3. Use `docker-compose exec` to run commands in containers
4. Check logs with `-f` flag for real-time updates
5. Generate sample data for quick testing
6. Use Makefile instead of remembering long commands
7. Set up pre-commit hooks for code quality
8. Enable Sentry for production error tracking

## 🔗 Resources

- Django Docs: https://docs.djangoproject.com/
- DRF Docs: https://www.django-rest-framework.org/
- Next.js Docs: https://nextjs.org/docs
- Celery Docs: https://docs.celeryproject.org/
- Docker Docs: https://docs.docker.com/
- NOAA ERDDAP: https://coastwatch.pfeg.noaa.gov/erddap/

---

**Quick Start**: `./scripts/quickstart.sh`  
**Seed Data**: `docker-compose exec backend python manage.py seed_sample_data --days 7`  
**View Frontend**: http://localhost:3000
