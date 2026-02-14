# Ocean Data Dashboard

A real-time oceanographic data visualization platform that ingests, stores, and displays ocean metrics from leading open-science providers.

## 🌊 About

Monitor the pulse of the ocean in real time. This dashboard collects and visualizes key ocean parameters (temperature, salinity, currents) from trusted scientific sources like NOAA ERDDAP, Copernicus Marine Service, and NASA OceanColor.

### Core Features
- **Real-time Data Ingestion**: Automated pipeline fetching oceanographic data
- **Interactive Visualizations**: Clean, responsive charts built with Recharts
- **Background Processing**: Celery-powered async data processing
- **REST API**: Django REST Framework endpoints for time-series data
- **Monitoring & Alerts**: CloudWatch integration for pipeline health

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Next.js   │────▶│  Django API  │────▶│ PostgreSQL  │
│  Frontend   │     │   + Celery   │     │  Database   │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Data Sources │
                    │ NOAA/NASA/EU │
                    └──────────────┘
```

## 📁 Project Structure

```
ocean-dashboard/
├── backend/              # Django + DRF + Celery
│   ├── api/             # API endpoints
│   ├── core/            # Django settings
│   ├── data_ingestion/  # ETL pipeline
│   └── celery_app/      # Celery configuration
├── frontend/            # Next.js + TypeScript
│   └── src/
│       ├── components/  # React components
│       ├── pages/       # Next.js pages
│       └── lib/         # Utilities
├── infra/               # Docker & IaC
│   ├── docker/          # Dockerfiles
│   └── terraform/       # AWS infrastructure
├── scripts/             # Setup & maintenance scripts
└── .github/workflows/   # CI/CD pipelines
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ocean-dashboard.git
cd ocean-dashboard
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

3. **Start Celery Worker** (in a new terminal)
```bash
cd backend
source venv/bin/activate
celery -A celery_app worker --loglevel=info
```

4. **Frontend Setup** (in a new terminal)
```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with your API URL
npm run dev
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/

### Docker Development

```bash
docker-compose up --build
```

## 🔧 Configuration

### Backend Environment Variables
```
DATABASE_URL=postgresql://user:password@localhost:5432/oceandb
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Frontend Environment Variables
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_NAME=Ocean Data Dashboard
```

## 📊 Data Sources

### Configured Sources
1. **NOAA ERDDAP**
   - Temperature, Salinity data
   - Real-time buoy measurements
   - API: https://coastwatch.pfeg.noaa.gov/erddap/

2. **Copernicus Marine Service**
   - Ocean currents
   - Global ocean physics
   - API: https://marine.copernicus.eu/

3. **NASA OceanColor**
   - Chlorophyll-a concentration
   - Ocean color data
   - API: https://oceancolor.gsfc.nasa.gov/

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm test
```

### End-to-End Tests
```bash
npm run test:e2e
```

## 🚢 Deployment

### AWS Deployment (ECS)
```bash
# Build and push Docker images
./scripts/build-and-push.sh

# Deploy infrastructure
cd infra/terraform
terraform init
terraform plan
terraform apply
```

### Environment-specific deployments
- **Development**: Auto-deploy on push to `develop` branch
- **Staging**: Auto-deploy on push to `staging` branch
- **Production**: Manual approval required for `main` branch

## 📈 Monitoring

- **CloudWatch**: Application logs and metrics
- **CloudWatch Alarms**: Ingestion failures, API errors
- **Sentry**: Error tracking (optional)

## 🛠️ Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and write tests
3. Commit: `git commit -m "feat: your feature description"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request
6. CI/CD pipeline runs tests automatically
7. Merge after approval

## 📝 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## 🗓️ MVP Roadmap

- [x] Week 1: Project setup and scaffolding
- [ ] Week 2: Data ingestion pipeline
- [ ] Week 3: Frontend visualizations
- [ ] Week 4: AWS deployment & monitoring
- [ ] Week 5: Polish and documentation

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- NOAA for oceanographic data
- Copernicus Marine Service
- NASA OceanColor program
- Open science community
