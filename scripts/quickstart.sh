#!/bin/bash

# Ocean Data Dashboard - Quick Start Script
# This script helps you get the project up and running quickly

set -e

echo "🌊 Ocean Data Dashboard - Quick Start"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Check if .env files exist
if [ ! -f backend/.env ]; then
    echo "Creating backend .env file..."
    cp backend/.env.example backend/.env
    echo "✓ Backend .env created (please review and update if needed)"
fi

if [ ! -f frontend/.env.local ]; then
    echo "Creating frontend .env.local file..."
    cp frontend/.env.local.example frontend/.env.local
    echo "✓ Frontend .env.local created"
fi

echo ""
echo "Building Docker images..."
docker-compose build

echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for database to be ready..."
sleep 5

echo ""
echo "Creating database migrations..."
docker-compose exec -T backend python manage.py makemigrations api data_ingestion

echo ""
echo "Running database migrations..."
docker-compose exec -T backend python manage.py migrate

echo ""
echo "Creating Django superuser..."
echo "You'll be prompted to create an admin account:"
docker-compose exec backend python manage.py createsuperuser || echo "Superuser creation skipped"

echo ""
echo "======================================"
echo "🎉 Setup complete!"
echo ""
echo "Services are running at:"
echo "  - Frontend:     http://localhost:3000"
echo "  - Backend API:  http://localhost:8000/api"
echo "  - Django Admin: http://localhost:8000/admin"
echo "  - API Docs:     http://localhost:8000/api/docs"
echo ""
echo "To fetch ocean data, run:"
echo "  docker-compose exec backend python manage.py fetch_noaa_data"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
echo "For more commands, see the Makefile or README.md"
echo "======================================"
