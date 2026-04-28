#!/bin/bash
# Startup script for SafeGuard AI Project (Linux/Mac)

set -e

echo "🚀 SafeGuard AI - Multi-Threat Detection System"
echo "=============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads outputs DataModel/models

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✏️  Please update .env with your settings"
fi

# Pull/Build images
echo "🔨 Building Docker images..."
docker-compose build --no-cache

# Start services
echo "🟢 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check health
echo "🏥 Checking service health..."
for i in {1..30}; do
    if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
        echo "✅ Detection API is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Detection API health check failed"
    fi
    sleep 1
done

echo ""
echo "✅ SafeGuard AI is now running!"
echo ""
echo "📊 Access Points:"
echo "  • Frontend: http://localhost:80"
echo "  • Backend API: http://localhost:3000"
echo "  • Detection API: http://localhost:5000"
echo "  • MongoDB: localhost:27017"
echo ""
echo "📝 View logs:"
echo "  • All: docker-compose logs -f"
echo "  • Backend: docker-compose logs -f backend"
echo "  • Detection API: docker-compose logs -f detection-api"
echo "  • MongoDB: docker-compose logs -f mongo"
echo ""
echo "🛑 To stop all services:"
echo "  • docker-compose down"
echo ""
