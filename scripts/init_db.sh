#!/bin/bash
# Database initialization script

set -e

echo "Initializing LLMScope database..."

# Wait for PostgreSQL to be ready
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d postgres -c '\q'; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - creating database"

# Create database if it doesn't exist
PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d postgres <<-EOSQL
    SELECT 'CREATE DATABASE llmscope'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'llmscope')\gexec
EOSQL

echo "Running migrations..."

# Run Alembic migrations
cd /app/backend
alembic upgrade head

echo "Database initialization complete!"
