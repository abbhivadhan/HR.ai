#!/bin/bash

# AI-HR Platform Development Setup Script

echo "🚀 Setting up AI-HR Platform development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend environment file..."
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env from template"
fi

# Start the development environment
echo "🐳 Starting Docker containers..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service health..."

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running at http://localhost:8000"
else
    echo "⚠️  Backend might still be starting up..."
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running at http://localhost:3000"
else
    echo "⚠️  Frontend might still be starting up..."
fi

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📋 Available services:"
echo "   • Frontend: http://localhost:3000"
echo "   • Backend API: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • PostgreSQL: localhost:5432"
echo "   • Redis: localhost:6379"
echo "   • MongoDB: localhost:27017"
echo ""
echo "🛠  Useful commands:"
echo "   • View logs: docker-compose logs -f"
echo "   • Stop services: docker-compose down"
echo "   • Run tests: make test"
echo ""