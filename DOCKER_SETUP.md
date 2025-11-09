# 🐳 Docker Setup Guide for WildID

Complete guide for running WildID with Docker, including database and email services.

## 📋 Table of Contents

- [Quick Start (Development)](#quick-start-development)
- [Production Setup](#production-setup)
- [Configuration Files](#configuration-files)
- [Common Commands](#common-commands)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start (Development)

### Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

### Step 1: Clone and Configure

```bash
# Navigate to your project directory
cd Proof-Of-Concept-Demo

# Copy the Docker environment file
cp .env.docker .env

# Edit .env and add your Together.ai API key
# Minimal required: TOGETHER_API_KEY=your_key_here
```

### Step 2: Start Everything

```bash
# Start all services (app + database + email)
docker-compose -f docker-compose.full.yml up -d
```

This starts:
- **WildID App** on http://localhost:3000
- **PostgreSQL Database** on port 5432
- **Mailhog** email UI on http://localhost:8025

### Step 3: Verify It's Running

```bash
# Check service status
docker-compose -f docker-compose.full.yml ps

# View logs
docker-compose -f docker-compose.full.yml logs -f app
```

### Step 4: Test the App

1. Open http://localhost:3000
2. Click "Sign In"
3. Enter any email (e.g., test@example.com)
4. View the magic link at http://localhost:8025 (Mailhog)
5. Click the link to sign in
6. Upload an animal photo to test!

### Step 5: Stop Everything

```bash
# Stop all services
docker-compose -f docker-compose.full.yml down

# Stop and remove volumes (deletes database data)
docker-compose -f docker-compose.full.yml down -v
```

---

## 🏭 Production Setup

### Step 1: Prepare Environment

```bash
# Copy Docker environment template
cp .env.docker .env

# Edit .env with production values
nano .env
```

### Required Production Variables:

```env
# API Key (Required)
TOGETHER_API_KEY=your_actual_api_key

# Security (Required - Generate a strong key!)
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Database
POSTGRES_DB=wildid
POSTGRES_USER=wildid_user
POSTGRES_PASSWORD=your_strong_password_here

# Email (Example: Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### Step 2: Build and Run

```bash
# Build the production image
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Step 3: Initialize Database

The database tables are created automatically on first run!

```bash
# Check database initialization in logs
docker-compose -f docker-compose.prod.yml logs app | grep -i "database"
```

### Step 4: Set Up Reverse Proxy (Optional)

For production, use nginx or Traefik:

**nginx example:**

```nginx
server {
    listen 80;
    server_name wildid.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📁 Configuration Files

### Docker Compose Files

| File | Purpose | Use Case |
|------|---------|----------|
| `docker-compose.yml` | Simple production (no DB) | Testing, single container |
| `docker-compose.dev.yml` | Development mode | Code changes with hot reload |
| `docker-compose.full.yml` | **Full stack dev** | **Recommended for development** |
| `docker-compose.prod.yml` | **Production ready** | **Recommended for production** |

### File Structure

```
Proof-Of-Concept-Demo/
├── Dockerfile                    # Main Docker image
├── docker-compose.yml           # Simple compose
├── docker-compose.dev.yml       # Dev compose
├── docker-compose.full.yml      # Full stack (DB + Email)
├── docker-compose.prod.yml      # Production ready
├── .dockerignore                # Files to exclude from build
├── .env.docker                  # Environment template
├── .env                         # Your actual environment (git-ignored)
└── DOCKER_SETUP.md              # This guide
```

---

## 🔧 Common Commands

### Starting Services

```bash
# Development (full stack with hot reload)
docker-compose -f docker-compose.full.yml up -d

# Production
docker-compose -f docker-compose.prod.yml up -d

# Build and start (after code changes)
docker-compose -f docker-compose.full.yml up -d --build
```

### Viewing Logs

```bash
# All services
docker-compose -f docker-compose.full.yml logs -f

# Just the app
docker-compose -f docker-compose.full.yml logs -f app

# Just the database
docker-compose -f docker-compose.full.yml logs -f db

# Last 100 lines
docker-compose -f docker-compose.full.yml logs --tail=100
```

### Managing Services

```bash
# Stop services (keep data)
docker-compose -f docker-compose.full.yml stop

# Start stopped services
docker-compose -f docker-compose.full.yml start

# Restart a service
docker-compose -f docker-compose.full.yml restart app

# Stop and remove (keep volumes)
docker-compose -f docker-compose.full.yml down

# Stop and remove everything (INCLUDING DATA!)
docker-compose -f docker-compose.full.yml down -v
```

### Database Operations

```bash
# Access PostgreSQL shell
docker exec -it wildid-db psql -U wildid_user -d wildid

# Backup database
docker exec wildid-db pg_dump -U wildid_user wildid > backup.sql

# Restore database
docker exec -i wildid-db psql -U wildid_user wildid < backup.sql

# View database tables
docker exec wildid-db psql -U wildid_user -d wildid -c "\dt"
```

### Container Operations

```bash
# Access app container shell
docker exec -it wildid-app bash

# Run Python commands in container
docker exec wildid-app python -c "from models import db; print('DB works!')"

# View container resource usage
docker stats

# Inspect container
docker inspect wildid-app
```

### Cleaning Up

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes (CAREFUL - deletes data!)
docker volume prune

# Remove everything (NUCLEAR OPTION)
docker system prune -a --volumes
```

---

## 🎯 Development Workflow

### Making Code Changes

The full development setup (`docker-compose.full.yml`) mounts your code as a volume, so changes are reflected immediately:

```bash
# Start with volume mount
docker-compose -f docker-compose.full.yml up -d

# Edit code in your IDE
# Changes are picked up automatically (Flask auto-reload)

# View logs to see changes
docker-compose -f docker-compose.full.yml logs -f app
```

### Testing Database Changes

```bash
# Stop app
docker-compose -f docker-compose.full.yml stop app

# Access database
docker exec -it wildid-db psql -U wildid_user -d wildid

# Make changes, then restart app
docker-compose -f docker-compose.full.yml start app
```

### Viewing Emails

```bash
# Mailhog web UI (auto-started with full compose)
open http://localhost:8025

# Or check app logs for printed magic links
docker-compose -f docker-compose.full.yml logs -f app | grep "MAGIC LINK"
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Error: port 3000 is already allocated
# Solution: Stop the conflicting service or change port

# Change port in docker-compose file:
ports:
  - "3001:3000"  # Use 3001 externally instead
```

### Database Connection Issues

```bash
# Check if database is running
docker-compose -f docker-compose.full.yml ps db

# Check database logs
docker-compose -f docker-compose.full.yml logs db

# Verify connection string in app
docker-compose -f docker-compose.full.yml exec app env | grep DATABASE_URL

# Common issue: Database not ready when app starts
# Solution: Restart app after DB is healthy
docker-compose -f docker-compose.full.yml restart app
```

### Email Not Sending

```bash
# Check Mailhog is running
docker-compose -f docker-compose.full.yml ps mailhog

# Access Mailhog UI
open http://localhost:8025

# Check app email configuration
docker-compose -f docker-compose.full.yml exec app env | grep MAIL

# View email errors in logs
docker-compose -f docker-compose.full.yml logs app | grep -i mail
```

### Container Won't Start

```bash
# View detailed logs
docker-compose -f docker-compose.full.yml logs app

# Check health status
docker-compose -f docker-compose.full.yml ps

# Rebuild image
docker-compose -f docker-compose.full.yml up -d --build

# Start in foreground to see errors
docker-compose -f docker-compose.full.yml up app
```

### Permission Issues

```bash
# If you get permission errors with volumes
# Fix ownership (Linux/Mac)
sudo chown -R $USER:$USER uploads/

# Or run with root temporarily (not recommended for production)
docker-compose -f docker-compose.full.yml run --user root app bash
```

### Out of Disk Space

```bash
# Check Docker disk usage
docker system df

# Clean up
docker system prune -a

# Remove unused volumes (CAREFUL!)
docker volume prune
```

### Database Reset

```bash
# Stop everything
docker-compose -f docker-compose.full.yml down

# Remove database volume
docker volume rm proof-of-concept-demo_postgres_data

# Restart (database will be recreated)
docker-compose -f docker-compose.full.yml up -d
```

---

## 🔒 Security Best Practices

### For Production:

1. **Use Strong Secrets**
   ```bash
   # Generate secure SECRET_KEY
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Secure Database**
   - Use strong database password
   - Don't expose database port externally
   - Use SSL for database connections

3. **Use Real Email Service**
   - Don't use Mailhog in production
   - Configure proper SMTP credentials
   - Use app passwords, not regular passwords

4. **Environment Variables**
   - Never commit `.env` file
   - Use secrets management (Docker Secrets, Vault)
   - Rotate keys regularly

5. **Network Security**
   - Use reverse proxy (nginx, Traefik)
   - Enable HTTPS/TLS
   - Configure firewall rules

6. **Monitoring**
   ```bash
   # Set up health checks
   docker-compose -f docker-compose.prod.yml ps
   
   # Monitor logs
   docker-compose -f docker-compose.prod.yml logs -f --tail=100
   ```

---

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Check service health
curl http://localhost:3000/health

# Container health status
docker ps --filter "name=wildid"

# Detailed inspection
docker inspect --format='{{json .State.Health}}' wildid-app | jq
```

### Backup Strategy

```bash
# Backup database
docker exec wildid-db pg_dump -U wildid_user wildid | gzip > backup_$(date +%Y%m%d).sql.gz

# Backup uploads folder
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/

# Backup environment (careful with secrets!)
cp .env .env.backup
```

### Log Rotation

```bash
# Configure Docker logging
# Add to docker-compose.yml:
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## 🚢 Deployment Platforms

### Deploy to various platforms:

**Docker Cloud / Docker Swarm:**
```bash
docker stack deploy -c docker-compose.prod.yml wildid
```

**AWS ECS:**
- Use `docker-compose.prod.yml` as reference
- Configure ECS task definition
- Set up RDS for PostgreSQL
- Use SES for email

**Google Cloud Run:**
- Build and push image to GCR
- Configure Cloud SQL
- Set environment variables

**Azure Container Instances:**
- Push image to ACR
- Configure Azure Database for PostgreSQL
- Deploy container with environment variables

**DigitalOcean App Platform:**
- Push code to GitHub
- Connect repository
- Configure environment variables
- Auto-deploys on push

---

## 📝 Summary

**For Development:**
```bash
docker-compose -f docker-compose.full.yml up -d
# Includes: App + PostgreSQL + Mailhog
# Access: http://localhost:3000
# Emails: http://localhost:8025
```

**For Production:**
```bash
docker-compose -f docker-compose.prod.yml up -d
# Includes: App + PostgreSQL
# Configure real email service in .env
# Set up reverse proxy for HTTPS
```

**Key Commands:**
```bash
# View logs
docker-compose -f docker-compose.full.yml logs -f app

# Restart after changes
docker-compose -f docker-compose.full.yml restart app

# Stop everything
docker-compose -f docker-compose.full.yml down
```

Need help? Check the logs first, then refer to the Troubleshooting section above!

---

## 🆘 Getting Help

If you encounter issues:

1. Check logs: `docker-compose -f docker-compose.full.yml logs -f`
2. Verify services: `docker-compose -f docker-compose.full.yml ps`
3. Check environment: `docker-compose -f docker-compose.full.yml exec app env`
4. Test connectivity: `docker-compose -f docker-compose.full.yml exec app ping db`
5. Review this guide's troubleshooting section

Happy Dockerizing! 🐳


