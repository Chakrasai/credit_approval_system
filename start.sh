#!/bin/bash

echo "🏦 Starting Credit Approval System..."
echo "🔧 Building and starting all services..."

# Build and start all services
docker-compose up --build

echo "✅ All services are running!"
echo "🌐 Django app: http://localhost:8000"
echo "🗄️  PostgreSQL: localhost:5432"
echo "🔴 Redis: localhost:6379"
echo ""
echo "Default superuser credentials:"
echo "Username: admin"
echo "Password: admin123"
