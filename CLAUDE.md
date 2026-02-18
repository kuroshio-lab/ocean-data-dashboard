# CLAUDE.md

Guidance for working with this repository.

## Project Overview

**Ocean Data Dashboard** is an open-source, full-stack application for visualizing real-time oceanographic data. Solo-maintained and designed for contributors to get running quickly.

- **Backend**: Django REST API + Celery (async data ingestion)
- **Frontend**: Next.js + TypeScript + Recharts
- **Data**: PostgreSQL + Redis (hosted on AWS/GCP/Azure)
- **Data Sources**: NOAA ERDDAP, Copernicus Marine, NASA OceanColor

## Quick Start (Docker Only)

Everything runs in containers. No local Python/Node setup needed.

```bash
docker-compose up -d

# Once running:
# - Backend: http://localhost:8000
# - Frontend: http://localhost:3000
# - Django admin: http://localhost:8000/admin/
# - API docs: http://localhost:8000/api/docs/

# Create a superuser (optional, for Django admin)
docker-compose exec backend python manage.py createsuperuser
```

## Architecture Diagram

```
Frontend (3000) → Backend API (8000) → PostgreSQL + Redis
                                            ↓
                                    Celery workers fetch external APIs
                                    (NOAA, Copernicus, NASA)
```

### Core Concepts

- **Observations**: TemperatureObservation, SalinityObservation, CurrentObservation, ChlorophyllObservation (each tied to a location, timestamp, data source)
- **Data Ingestion**: Celery Beat triggers periodic fetches. Services normalize external API data. Results stored in PostgreSQL.
- **Retention**: Data older than `DATA_RETENTION_DAYS` is cleaned up daily (default: 365 days)

## Important Commands

All commands run **inside containers** via `docker-compose exec`:

```bash
# Backend (Django/Celery)
docker-compose exec backend python manage.py migrate          # Apply migrations
docker-compose exec backend python manage.py makemigrations   # Create migrations
docker-compose exec backend python manage.py test             # Run tests
docker-compose exec backend pytest                            # Or pytest

# Frontend (npm)
docker-compose exec frontend npm run lint
docker-compose exec frontend npm run type-check

# Celery worker logs (separate terminal)
docker-compose logs -f celery-worker

# Celery Beat logs (for scheduled tasks)
docker-compose logs -f celery-beat
```

## Folder-Specific Rules

For detailed guidance on development tasks:

- **Backend tasks** (Django models, API, Celery, data ingestion) → read `backend/CLAUDE.md`
- **Frontend tasks** (React components, API integration, styling) → read `frontend/CLAUDE.md`
- **Infrastructure tasks** (Docker, deployment, environment setup) → read `infra/CLAUDE.md`

## Key Principles

1. **Everything via Docker**: No local environment setup. Ensures consistency across contributors' machines.
2. **Zero friction**: `docker-compose up -d` and you're ready to code.
3. **Cost-conscious**: Running on AWS/GCP/Azure? We optimize for managed services (RDS, Cloud SQL, etc.).
4. **Simple > complex**: Solo-maintained means every line of code must justify its existence.
5. **Open-source first**: Assume contributors have varying experience levels. Docs should be clear and accessible.

## Development Workflow

1. Fork/clone the repo
2. Create a feature branch
3. Run `docker-compose up -d`
4. Make your changes (edits to local files sync into containers)
5. Run tests: `docker-compose exec backend python manage.py test`
6. Submit PR

## File Structure

```
backend/              # Django project (read backend/CLAUDE.md for details)
frontend/            # Next.js project (read frontend/CLAUDE.md for details)
infra/               # Docker & deployment (read infra/CLAUDE.md for details)
docker-compose.yml   # Defines all services (backend, frontend, postgres, redis, celery)
```

## Need Help?

- API documentation: http://localhost:8000/api/docs/ (Swagger UI)
- Django admin: http://localhost:8000/admin/
- Check logs: `docker-compose logs [service-name]`

---

**Next steps**: Check the folder-specific CLAUDE.md files for detailed development guidance.
