#!/bin/bash
# Setup script for SafeGuard AI Project

set -e

echo "🚀 SafeGuard AI - Setup Script"
echo "=============================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python $(python3 --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads outputs DataModel/models

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js is required but not installed."
    echo "   Install from: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js $(node --version)"

# Install backend dependencies
if [ -d "backend" ]; then
    echo "📦 Installing backend dependencies..."
    cd backend
    npm install
    cd ..
fi

# Create .env if doesn't exist
if [ ! -f ".env" ]; then
    echo "🔧 Configuration..."
    cp .env.example .env
    echo "✏️  Created .env - Please update with your configuration"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Update .env configuration file"
echo "2. Run 'docker-compose up -d' to start services"
echo "3. Or run 'python app.py' for Python API only"
echo ""
