#!/bin/bash

echo "🚀 Starting QR Scanner Application..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  echo "   PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "✓ PostgreSQL is ready!"
echo "🏃 Starting Flask application..."

# Start the Flask application
python app.py
