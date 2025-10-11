#!/bin/bash
# PAI Agent Startup Script

echo "🚀 Starting PAI Agent..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env .env.example 2>/dev/null || echo "No .env.example found. Please create .env manually."
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check dependencies
echo "🔍 Checking dependencies..."

# Check PostgreSQL
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL found"
else
    echo "❌ PostgreSQL not found. Install with: sudo apt-get install postgresql"
fi

# Check Neo4j (optional)
if command -v neo4j &> /dev/null; then
    echo "✅ Neo4j found"
else
    echo "⚠️  Neo4j not found (optional). Install from: https://neo4j.com/download/"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
uv sync

# Run database migrations (if needed)
echo "🗄️  Setting up databases..."

# Start the agent
echo "🎉 Starting PAI Agent on ${HOST:-0.0.0.0}:${PORT:-8181}..."
uv run python main.py