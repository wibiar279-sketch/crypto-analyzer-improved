#!/bin/bash

# Railway startup script for Crypto Analyzer Backend

echo "🚀 Starting Crypto Analyzer Backend..."

# Navigate to backend directory
cd backend

# Run database migrations if needed
if [ -n "$DATABASE_URL" ]; then
    echo "📊 Running database migrations..."
    flask db upgrade || echo "⚠️  No migrations to run or migration failed"
fi

# Start the application with Gunicorn
echo "🌐 Starting Gunicorn server..."
exec gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} --timeout 120 --access-logfile - --error-logfile - src.main:app
