#!/bin/bash
# Manual Deployment Script
# Use this to manually deploy without GitHub Actions
# Usage: bash deploy.sh

set -e

echo "=== Powerdealer Manual Deployment ==="

cd /opt/powerdealer

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create it from .env.example"
    exit 1
fi

# Load environment variables
source .env

# Login to registry (if using GitHub Container Registry)
if [ -n "$GITHUB_TOKEN" ]; then
    echo "$GITHUB_TOKEN" | docker login ghcr.io -u $DOCKER_USERNAME --password-stdin
fi

# Pull latest images
echo "Pulling latest images..."
docker-compose -f docker-compose.prod.yml pull

# Run migrations
echo "Running database migrations..."
docker-compose -f docker-compose.prod.yml run --rm backend python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
docker-compose -f docker-compose.prod.yml run --rm backend python manage.py collectstatic --noinput

# Restart services
echo "Restarting services..."
docker-compose -f docker-compose.prod.yml up -d --remove-orphans

# Cleanup old images
echo "Cleaning up old images..."
docker image prune -af --filter "until=24h"

# Health check
echo "Performing health check..."
sleep 10
if curl -sf http://localhost/health > /dev/null; then
    echo ""
    echo "=== Deployment Successful ==="
else
    echo ""
    echo "=== Warning: Health check failed ==="
    echo "Check logs with: docker-compose -f docker-compose.prod.yml logs"
fi
