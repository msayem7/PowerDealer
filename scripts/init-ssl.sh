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

# Start services without SSL first (for Let's Encrypt challenge)
echo "Starting services for SSL challenge..."
docker-compose -f docker-compose.prod.yml up -d nginx

# Wait for nginx to start
sleep 5

# Obtain certificate
echo "Obtaining SSL certificate..."
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

# Generate SSL configuration from template
echo "Generating SSL nginx configuration..."
envsubst '${DOMAIN_NAME}' < /opt/powerdealer/nginx/conf.d/default.conf.template > /opt/powerdealer/nginx/conf.d/default.conf

# Restart nginx with SSL configuration
echo "Restarting nginx with SSL..."
docker-compose -f docker-compose.prod.yml restart nginx

echo ""
echo "=== SSL Setup Complete ==="
echo ""
echo "Your site should now be accessible at:"
echo "  https://$DOMAIN"
echo "  https://www.$DOMAIN"
echo ""
echo "SSL certificate will auto-renew via certbot container."
echo ""
