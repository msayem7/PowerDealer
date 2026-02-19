#!/bin/bash
# VPS Initial Setup Script for Powerdealer
# Run this script on a fresh Hostinger VPS (Ubuntu/Debian)
# Usage: sudo bash setup-vps.sh

set -e

echo "=== Powerdealer VPS Setup Script ==="

# Update system
echo "Updating system packages..."
apt-get update && apt-get upgrade -y

# Install required packages
echo "Installing required packages..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    ufw \
    fail2ban

# Install Docker
echo "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    # Add current user to docker group
    usermod -aG docker $SUDO_USER || true
fi

# Install Docker Compose
echo "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Setup directories
echo "Setting up project directories..."
mkdir -p /opt/powerdealer
mkdir -p /opt/powerdealer/nginx/conf.d
mkdir -p /opt/powerdealer/logs

# Configure firewall
echo "Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

# Configure fail2ban
echo "Configuring fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban

# Enable Docker service
echo "Enabling Docker service..."
systemctl enable docker
systemctl start docker

# Create environment file template
echo "Creating environment file template..."
cat > /opt/powerdealer/.env.example << 'EOF'
# Domain Configuration
DOMAIN_NAME=yourdomain.com

# Docker Registry
DOCKER_REGISTRY=ghcr.io
DOCKER_USERNAME=msayem7
IMAGE_TAG=latest

# Django Settings
SECRET_KEY=your-super-secret-key-generate-with-python
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
POSTGRES_DB=powerdealer
POSTGRES_USER=powerdealer
POSTGRES_PASSWORD=your-strong-database-password

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Frontend API URL (used during build)
VITE_API_URL=https://yourdomain.com/api
EOF

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and configure values:"
echo "   cp /opt/powerdealer/.env.example /opt/powerdealer/.env"
echo "   nano /opt/powerdealer/.env"
echo ""
echo "2. Generate a Django secret key:"
echo "   python3 -c 'from secrets import token_urlsafe; print(token_urlsafe(50))'"
echo ""
echo "3. Copy docker-compose.prod.yml and nginx config to /opt/powerdealer"
echo ""
echo "4. Run the init-ssl.sh script to obtain SSL certificate"
echo ""
echo "5. Start the application:"
echo "   cd /opt/powerdealer && docker-compose -f docker-compose.prod.yml up -d"
echo ""
