.PHONY: help setup backend-setup frontend-setup docker-build docker-up docker-down migrate test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Initial project setup (backend + frontend)
	@echo "Setting up Ocean Data Dashboard..."
	make backend-setup
	make frontend-setup
	@echo "✓ Setup complete! Run 'make docker-up' to start services."

backend-setup: ## Set up backend (Python environment)
	@echo "Setting up backend..."
	cd backend && python -m venv venv
	cd backend && source venv/bin/activate && pip install --upgrade pip
	cd backend && source venv/bin/activate && pip install -r requirements.txt
	cd backend && cp .env.example .env
	@echo "✓ Backend setup complete"

frontend-setup: ## Set up frontend (Node.js)
	@echo "Setting up frontend..."
	cd frontend && npm install
	cd frontend && cp .env.local.example .env.local
	@echo "✓ Frontend setup complete"

docker-build: ## Build Docker images
	@echo "Building Docker images..."
	docker-compose build

docker-up: ## Start all services with Docker Compose
	@echo "Starting services..."
	docker-compose up -d
	@echo "✓ Services started"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "Django Admin: http://localhost:8000/admin"

docker-down: ## Stop all services
	@echo "Stopping services..."
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

migrate: ## Run database migrations
	docker-compose exec backend python manage.py migrate

makemigrations: ## Create new migrations
	docker-compose exec backend python manage.py makemigrations

createsuperuser: ## Create Django superuser
	docker-compose exec backend python manage.py createsuperuser

shell: ## Open Django shell
	docker-compose exec backend python manage.py shell

fetch-data: ## Fetch data from NOAA
	docker-compose exec backend python manage.py fetch_noaa_data

test-backend: ## Run backend tests
	docker-compose exec backend python manage.py test

test-frontend: ## Run frontend tests
	cd frontend && npm test

lint-backend: ## Lint backend code
	cd backend && source venv/bin/activate && black . && isort . && flake8

lint-frontend: ## Lint frontend code
	cd frontend && npm run lint

format: ## Format all code
	make lint-backend
	cd frontend && npm run format

clean: ## Clean up generated files
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	cd frontend && rm -rf .next node_modules 2>/dev/null || true
	@echo "✓ Cleanup complete"

logs-backend: ## View backend logs
	docker-compose logs -f backend

logs-celery: ## View Celery worker logs
	docker-compose logs -f celery_worker

logs-frontend: ## View frontend logs
	docker-compose logs -f frontend

restart: ## Restart all services
	docker-compose restart

ps: ## Show running containers
	docker-compose ps

db-shell: ## Open PostgreSQL shell
	docker-compose exec db psql -U oceanuser -d oceandb

redis-shell: ## Open Redis CLI
	docker-compose exec redis redis-cli
