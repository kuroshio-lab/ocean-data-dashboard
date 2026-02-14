# Ocean Data Dashboard - Setup Guide

Your complete monorepo for the Ocean Data Dashboard MVP has been created! 🌊

## 📦 What's Been Created

### Complete Project Structure
```
ocean-dashboard/
├── backend/              # Django + DRF + Celery backend
├── frontend/             # Next.js + TypeScript frontend
├── infra/               # Docker & infrastructure configs
├── scripts/             # Helper scripts
├── .github/workflows/   # CI/CD pipelines
└── Documentation files
```

### Backend Features
✅ Django 5.0 with REST Framework
✅ PostgreSQL database models
✅ Celery + Redis for background jobs
✅ NOAA ERDDAP data ingestion service
✅ API endpoints for temperature, salinity, currents
✅ Swagger/ReDoc API documentation
✅ Django admin interface
✅ Sample data seeding command
✅ Comprehensive test setup

### Frontend Features
✅ Next.js 14 with TypeScript
✅ Tailwind CSS with custom ocean theme
✅ Recharts for data visualization
✅ Type-safe API client
✅ Responsive layout
✅ Temperature chart component
✅ Error handling & loading states

### DevOps & Infrastructure
✅ Docker Compose for local development
✅ Dockerfiles for backend & frontend
✅ GitHub Actions CI/CD pipeline
✅ Environment configuration templates
✅ Makefile for common operations
✅ Quick start script

### Documentation
✅ Main README with architecture
✅ Backend README
✅ Frontend README
✅ Contributing guidelines
✅ MIT License
✅ This setup guide!

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Navigate to the project**
   ```bash
   cd ocean-dashboard
   ```

2. **Run the quick start script**
   ```bash
   ./scripts/quickstart.sh
   ```

   This will:
   - Create environment files
   - Build Docker images
   - Start all services
   - Run database migrations
   - Prompt you to create a superuser

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api
   - Django Admin: http://localhost:8000/admin
   - API Docs: http://localhost:8000/api/docs

4. **Load some data**
   ```bash
   # Option A: Generate sample data (instant)
   docker-compose exec backend python manage.py seed_sample_data --days 7

   # Option B: Fetch real NOAA data (requires internet, takes 1-2 min)
   docker-compose exec backend python manage.py fetch_noaa_data
   ```

5. **Refresh the frontend** to see visualizations!

### Option 2: Manual Setup (No Docker)

#### Backend Setup

1. **Create Python virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL and Redis settings
   ```

4. **Setup database** (PostgreSQL must be running)
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Start Redis** (required for Celery)
   ```bash
   # Install Redis first, then:
   redis-server
   # Or use Docker: docker run -p 6379:6379 redis:7-alpine
   ```

6. **Start Celery worker** (in a new terminal)
   ```bash
   cd backend
   source venv/bin/activate
   celery -A celery_app worker --loglevel=info
   ```

7. **Start Django server**
   ```bash
   python manage.py runserver
   ```

#### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.local.example .env.local
   # Should be: NEXT_PUBLIC_API_URL=http://localhost:8000/api
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Open browser**: http://localhost:3000

## 📊 Generating Data

### Sample Data (Fast, No External Dependencies)
```bash
docker-compose exec backend python manage.py seed_sample_data --days 7 --points-per-day 24
```

This creates realistic synthetic data for 3 locations over 7 days.

### Real NOAA Data (Requires Internet)
```bash
docker-compose exec backend python manage.py fetch_noaa_data --days 1
```

This fetches actual buoy data from NOAA ERDDAP API.

## 🛠️ Common Commands

Using the Makefile:
```bash
make help              # Show all available commands
make docker-up         # Start all services
make docker-down       # Stop all services
make logs-backend      # View backend logs
make logs-frontend     # View frontend logs
make migrate           # Run database migrations
make fetch-data        # Fetch NOAA data
make test-backend      # Run backend tests
make test-frontend     # Run frontend tests
```

## 📁 Key Files to Know

### Configuration Files
- `docker-compose.yml` - Local development orchestration
- `backend/.env` - Backend configuration
- `frontend/.env.local` - Frontend configuration
- `Makefile` - Common operation shortcuts

### Entry Points
- `backend/manage.py` - Django management commands
- `frontend/src/pages/index.tsx` - Main frontend page
- `backend/api/views.py` - API endpoints
- `backend/data_ingestion/services/` - Data fetching services

### Important Scripts
- `scripts/quickstart.sh` - Automated setup
- `backend/manage.py fetch_noaa_data` - Manual data fetch
- `backend/manage.py seed_sample_data` - Generate test data

## 🧪 Testing

### Backend
```bash
# With Docker
docker-compose exec backend python manage.py test

# Without Docker
cd backend
python manage.py test
```

### Frontend
```bash
cd frontend
npm test
```

## 🐛 Troubleshooting

### "Frontend shows no data"
1. Check backend is running: `curl http://localhost:8000/api/sources/`
2. Generate data: `make fetch-data` or seed sample data
3. Check browser console for API errors
4. Verify NEXT_PUBLIC_API_URL in frontend/.env.local

### "Database connection error"
1. Ensure PostgreSQL is running
2. Check DATABASE_URL in backend/.env
3. Run migrations: `make migrate`

### "Celery tasks not running"
1. Ensure Redis is running: `redis-cli ping`
2. Check Celery worker logs: `make logs-celery`
3. Verify CELERY_BROKER_URL in backend/.env

### "Docker build fails"
1. Ensure Docker Desktop is running
2. Check Docker disk space: `docker system df`
3. Clean up: `docker system prune -a`

## 📚 Next Steps

### Week 2: Data Ingestion Pipeline (Current)
- [ ] Test NOAA integration with real data
- [ ] Implement Copernicus service (requires API access)
- [ ] Set up Celery Beat schedules
- [ ] Add error handling and retry logic

### Week 3: Frontend Visualizations
- [ ] Add salinity chart component
- [ ] Add currents visualization
- [ ] Create multi-location comparison
- [ ] Add date range picker
- [ ] Implement location selector

### Week 4: Deployment
- [ ] Set up AWS infrastructure (ECS, RDS, ElastiCache)
- [ ] Configure CloudWatch monitoring
- [ ] Set up GitHub Actions secrets
- [ ] Deploy to staging environment
- [ ] Production deployment with monitoring

### Week 5: Polish
- [ ] Add more data sources
- [ ] Improve error handling
- [ ] Add user authentication (optional)
- [ ] Performance optimization
- [ ] Documentation improvements

## 🤝 Contributing

See `CONTRIBUTING.md` for development guidelines.

## 📖 Documentation

- Main README: `README.md`
- Backend: `backend/README.md`
- Frontend: `frontend/README.md`
- API Docs: http://localhost:8000/api/docs/ (when running)

## 🆘 Getting Help

- Check the README files
- Review API documentation at /api/docs/
- Inspect browser console for frontend issues
- Check Docker logs: `docker-compose logs -f`
- Review Django admin: http://localhost:8000/admin/

## 🎉 Success Indicators

You'll know everything is working when:
1. ✅ Frontend loads at http://localhost:3000
2. ✅ Backend API responds at http://localhost:8000/api
3. ✅ Django admin accessible at http://localhost:8000/admin
4. ✅ Data appears in frontend after running seed or fetch commands
5. ✅ Charts display temperature/salinity data
6. ✅ Celery worker processes tasks (check logs)

## 🌊 Happy Coding!

You now have a fully configured Ocean Data Dashboard monorepo! Start by running the quick start script and generating some sample data. The MVP is ready for you to begin Week 2 of development.

For questions or issues, refer to the documentation or check the troubleshooting section above.

---

**Project Structure**: Monorepo
**Backend**: Django 5.0 + DRF + Celery
**Frontend**: Next.js 14 + TypeScript
**Database**: PostgreSQL 15
**Cache**: Redis 7
**Deployment**: Docker + AWS (ECS)
