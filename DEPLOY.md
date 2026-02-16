# Powerdealer Deployment Guide

Complete guide for deploying Powerdealer to a Linux VPS using Docker, Nginx, and SSL.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         VPS                                  │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐     │
│  │  Nginx  │──▶│Frontend │   │ Backend │──▶│PostgreSQL│     │
│  │  :443   │◀──│  (Vue)  │   │ (Django)│   │  :5432   │     │
│  └────┬────┘   └─────────┘   └─────────┘   └──────────┘     │
│       │                                                      │
│       └──────────────▶ /api/ ──────────▶                    │
│                                                              │
│  ┌─────────┐                                                │
│  │ Certbot │ (SSL auto-renewal)                             │
│  └─────────┘                                                │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

- A VPS (Hostinger or similar) running Ubuntu 24.00+
- A domain name pointed to your VPS IP
- SSH access to the VPS
- A GitHub account (for container registry)

## Quick Start

### 1. Setup VPS

SSH into your VPS and run:

```bash
# Download and run setup script
curl -fsSL https://raw.githubusercontent.com/msayem7/PowerDealer/Deploy_Using_Docker/scripts/setup-vps.sh | sudo bash
```

Or manually:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
```

### 2. Configure Environment

```bash
cd /opt/powerdealer

# Copy example environment file
cp .env.example .env

# Generate Django secret key
python3 -c 'from secrets import token_urlsafe; print(token_urlsafe(50))'

# Edit configuration
nano .env
```

### 3. Deploy Application

```bash
# Pull and start services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Create superuser (optional)
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

### 4. Setup SSL

```bash
sudo bash /opt/powerdealer/scripts/init-ssl.sh yourdomain.com your@email.com
```

## GitHub Actions Setup

### Required Secrets

Add these secrets to your GitHub repository (Settings → Secrets → Actions):

| Secret | Description | Example |
|--------|-------------|---------|
| `VPS_HOST` | VPS IP address | `123.45.67.89` |
| `VPS_USER` | SSH username | `root` |
| `VPS_SSH_KEY` | Private SSH key | `-----BEGIN OPENSSH...` |
| `VITE_API_URL` | Frontend API URL | `https://yourdomain.com/api` |

### Deploy Keys Setup

1. Generate SSH key pair on your local machine:
   ```bash
   ssh-keygen -t ed25519 -C "github-actions-deploy" -f deploy_key
   ```

2. Add public key to VPS:
   ```bash
   cat deploy_key.pub >> ~/.ssh/authorized_keys
   ```

3. Add private key to GitHub Secrets as `VPS_SSH_KEY`

## Directory Structure on VPS

```
/opt/powerdealer/
├── .env                          # Environment configuration
├── docker-compose.prod.yml       # Production compose file
├── nginx/
│   ├── nginx.conf               # Main nginx config
│   └── conf.d/
│       └── default.conf         # Server block config
├── logs/                        # Application logs
└── backups/                     # Database backups
```

## Common Commands

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Restart Services

```bash
docker-compose -f docker-compose.prod.yml restart
```

### Database Operations

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# Database shell
docker-compose -f docker-compose.prod.yml exec db psql -U powerdealer powerdealer
```

### Backup

```bash
# Manual backup
bash /opt/powerdealer/scripts/backup.sh

# Setup daily cron job
echo "0 3 * * * /opt/powerdealer/scripts/backup.sh" | crontab -
```

### Update Deployment

```bash
cd /opt/powerdealer
bash scripts/deploy.sh
```

## Troubleshooting

### Container not starting

```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs backend
```

### SSL issues

```bash
# Check certificate status
docker-compose -f docker-compose.prod.yml exec certbot certbot certificates

# Force renewal
docker-compose -f docker-compose.prod.yml exec certbot certbot renew --force-renewal
```

### Database connection issues

```bash
# Check if database is healthy
docker-compose -f docker-compose.prod.yml exec db pg_isready -U powerdealer

# Check database logs
docker-compose -f docker-compose.prod.yml logs db
```

## Security Checklist

- [ ] Change default passwords
- [ ] Generate strong SECRET_KEY
- [ ] Enable UFW firewall
- [ ] Configure fail2ban
- [ ] Set DEBUG=False
- [ ] Use HTTPS only
- [ ] Regular backups
- [ ] Keep Docker images updated

## Monitoring

### Health Check Endpoint

```bash
curl https://yourdomain.com/api/health/
```

### Resource Usage

```bash
docker stats
```
