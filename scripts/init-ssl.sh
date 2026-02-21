#!/bin/bash
# SSL Certificate Initialization Script
# Run this after initial deployment to obtain Let's Encrypt certificate
# Usage: sudo bash init-ssl.sh yourdomain.com your@email.com

set -e

DOMAIN=$1
EMAIL=$2

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "Usage: sudo bash init-ssl.sh <domain> <email>"
    echo "Example: sudo bash init-ssl.sh example.com admin@example.com"
    exit 1
fi

echo "=== SSL Certificate Setup for $DOMAIN ==="

cd /opt/powerdealer

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create it first."
    exit 1
fi

# Update domain in .env
sed -i "s/DOMAIN_NAME=.*/DOMAIN_NAME=$DOMAIN/" .env

# Check if certificate already exists
if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo "SSL certificate already exists for $DOMAIN"
    echo "Generating nginx configuration and restarting services..."
    
    # Generate SSL configuration from template
    envsubst '${DOMAIN_NAME}' < /opt/powerdealer/nginx/conf.d/default.conf.template > /opt/powerdealer/nginx/conf.d/default.conf
    
    # Restart all containers
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml up -d
    
    echo ""
    echo "=== SSL Setup Complete ==="
    echo "Your site is now accessible at: https://$DOMAIN"
    exit 0
fi

echo "No existing certificate found. Obtaining new certificate..."

# Stop all containers to free port 80
echo "Stopping containers to free port 80..."
docker-compose -f docker-compose.prod.yml down

# Wait for port 80 to be released
sleep 3

# Verify port 80 is free
if netstat -tuln 2>/dev/null | grep -q ':80 ' || ss -tuln 2>/dev/null | grep -q ':80 '; then
    echo "Warning: Port 80 appears to be in use. Attempting to proceed anyway..."
fi

# Obtain certificate using certbot standalone mode
# This runs certbot directly on the host, binding to port 80
echo "Obtaining SSL certificate via standalone mode..."
echo "This may take a moment..."

docker run --rm \
    -p 80:80 \
    -v certbot_conf:/etc/letsencrypt \
    -v certbot_www:/var/www/certbot \
    certbot/certbot:latest \
    certonly \
    --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN

# Verify certificate was obtained
if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo ""
    echo "Error: Certificate acquisition failed!"
    echo "Please check:"
    echo "  1. Domain $DOMAIN points to this server's IP"
    echo "  2. Port 80 is accessible from the internet"
    echo "  3. Firewall allows incoming HTTP traffic"
    exit 1
fi

echo "Certificate obtained successfully!"

# Generate SSL configuration from template
echo "Generating SSL nginx configuration..."
envsubst '${DOMAIN_NAME}' < /opt/powerdealer/nginx/conf.d/default.conf.template > /opt/powerdealer/nginx/conf.d/default.conf

# Start all containers with SSL configuration
echo "Starting all containers with SSL..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to start
sleep 5

# Verify nginx is running
if ! docker-compose -f docker-compose.prod.yml ps nginx | grep -q "Up"; then
    echo "Error: Nginx failed to start. Check logs with:"
    echo "  docker-compose -f docker-compose.prod.yml logs nginx"
    exit 1
fi

echo ""
echo "=== SSL Setup Complete ==="
echo ""
echo "Your site is now accessible at:"
echo "  https://$DOMAIN"
echo ""
echo "HTTP traffic will be automatically redirected to HTTPS."
echo "SSL certificate will auto-renew via certbot container."
echo ""
echo "To test SSL configuration, run:"
echo "  curl -I https://$DOMAIN"
echo ""
