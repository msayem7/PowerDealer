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
    docker-compose -f docker-compose.prod.yml restart nginx
    
    echo ""
    echo "=== SSL Setup Complete ==="
    echo "Your site is accessible at: https://$DOMAIN"
    exit 0
fi

# Step 1: Stop nginx to free port 80 for certbot standalone
echo "Stopping nginx container to free port 80..."
docker-compose -f docker-compose.prod.yml stop nginx

# Step 2: Obtain certificate using certbot standalone mode
echo "Obtaining SSL certificate using standalone mode..."
docker-compose -f docker-compose.prod.yml run --rm --service-ports certbot certonly \
    --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN

# Step 3: Generate SSL configuration from template
echo "Generating SSL nginx configuration..."
envsubst '${DOMAIN_NAME}' < /opt/powerdealer/nginx/conf.d/default.conf.template > /opt/powerdealer/nginx/conf.d/default.conf

# Step 4: Restart all containers
echo "Restarting all containers with SSL configuration..."
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "=== SSL Setup Complete ==="
echo ""
echo "Your site should now be accessible at:"
echo "  https://$DOMAIN"
echo ""
echo "HTTP traffic will be automatically redirected to HTTPS."
echo "SSL certificate will auto-renew via certbot container."
echo ""
