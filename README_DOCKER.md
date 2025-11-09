# 🐳 WildID Docker Setup - Complete Guide

Everything you need to run WildID with Docker, including user accounts, database, and email.

## 🎯 What's Included

Your WildID app now has complete Docker support with:

- ✅ **Full Development Stack** - App + PostgreSQL + Mailhog
- ✅ **Production Ready** - Optimized for deployment
- ✅ **Database Included** - PostgreSQL with automatic initialization
- ✅ **Email Testing** - Mailhog for magic link testing
- ✅ **One Command Setup** - Get running in 60 seconds
- ✅ **Persistent Data** - Your data survives restarts
- ✅ **Health Monitoring** - Automatic health checks

## 🚀 Quick Start (60 seconds!)

```bash
# 1. Copy environment template
cp env.docker.template .env

# 2. Edit .env and add your Together.ai API key
# (Minimum: just add TOGETHER_API_KEY)

# 3. Start everything
docker-compose -f docker-compose.full.yml up -d

# 4. Open your browser
# App: http://localhost:3000
# Emails: http://localhost:8025
```

**That's it!** You now have a complete running system with:
- WildID web app with user accounts
- PostgreSQL database (auto-configured)
- Mailhog email testing

## 📁 Docker Files Overview

### Configuration Files

| File | Purpose | When to Use |
|------|---------|-------------|
| **`docker-compose.full.yml`** | Complete dev stack | **Recommended for development** |
| **`docker-compose.prod.yml`** | Production ready | **Recommended for production** |
| `docker-compose.yml` | Legacy simple setup | Basic testing only |
| `docker-compose.dev.yml` | Legacy dev setup | Basic testing only |
| `Dockerfile` | Image definition | Builds the app container |
| `.dockerignore` | Build exclusions | Optimizes build speed |
| `env.docker.template` | Environment template | Copy to `.env` and customize |

### Documentation Files

| File | Content | For Who |
|------|---------|---------|
| **`DOCKER_QUICKSTART.md`** | 5-minute setup | **Start here!** |
| **`DOCKER_SETUP.md`** | Comprehensive guide | Detailed reference |
| `DOCKER_ARCHITECTURE.md` | System architecture | Understanding internals |
| `README_DOCKER.md` | This file | Overview |

## 💡 Common Use Cases

### Development (Most Common)

```bash
# Start full development stack
docker-compose -f docker-compose.full.yml up -d

# View logs
docker-compose -f docker-compose.full.yml logs -f app

# Stop when done
docker-compose -f docker-compose.full.yml down
```

**Access:**
- App: http://localhost:3000
- Mailhog: http://localhost:8025
- Database: localhost:5432 (if needed)

### Production Deployment

```bash
# Configure environment
cp env.docker.template .env
# Edit .env with production values

# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Making Code Changes (Dev)

Code changes are automatically picked up (hot reload):

```bash
# Already running with docker-compose.full.yml
# Just edit your code - changes are live!

# Restart if needed
docker-compose -f docker-compose.full.yml restart app
```

### Database Operations

```bash
# Access database shell
docker exec -it wildid-db psql -U wildid_user -d wildid

# Backup database
docker exec wildid-db pg_dump -U wildid_user wildid > backup.sql

# View tables
docker exec wildid-db psql -U wildid_user -d wildid -c "\dt"
```

## 🔍 Troubleshooting

### Port Already in Use

```bash
# Error: port 3000 is already allocated
# Solution: Stop other service or change port in docker-compose file

# Windows: Find process using port
netstat -ano | findstr :3000

# Kill process or change port in docker-compose.full.yml:
ports:
  - "3001:3000"  # Use different external port
```

### Database Connection Failed

```bash
# Wait for database to be ready, then restart app
docker-compose -f docker-compose.full.yml restart app

# Or check database status
docker-compose -f docker-compose.full.yml logs db
```

### Magic Links Not Working

```bash
# Check Mailhog UI
open http://localhost:8025

# Or check logs for printed links
docker-compose -f docker-compose.full.yml logs app | grep "MAGIC LINK"
```

### Need Clean Start

```bash
# Stop and remove everything (keeps data)
docker-compose -f docker-compose.full.yml down

# Stop and remove INCLUDING data (fresh start)
docker-compose -f docker-compose.full.yml down -v

# Start again
docker-compose -f docker-compose.full.yml up -d
```

## 🔧 Configuration

### Minimum Configuration (.env)

```env
# Only this is required to run!
TOGETHER_API_KEY=your_api_key_here
```

Everything else has sensible defaults.

### Full Configuration (.env)

```env
# API Keys
TOGETHER_API_KEY=your_api_key_here

# Security
SECRET_KEY=your-secret-key

# Database (auto-configured for dev)
POSTGRES_DB=wildid
POSTGRES_USER=wildid_user
POSTGRES_PASSWORD=secure_password

# Email (Mailhog for dev, real SMTP for prod)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## 📊 What's Running?

When you start with `docker-compose.full.yml`, you get:

```
┌──────────────────────────────────────┐
│  WildID App (Python/Flask)           │
│  Port: 3000                           │
│  URL: http://localhost:3000           │
└──────────┬───────────────────────────┘
           │
           ├─► PostgreSQL Database
           │   Port: 5432 (internal)
           │   Data: Saved in Docker volume
           │
           └─► Mailhog Email Server
               Port: 1025 (SMTP)
               Port: 8025 (Web UI)
               URL: http://localhost:8025
```

## 🎓 Learning Path

1. **Start Simple** → Use `DOCKER_QUICKSTART.md` (5 minutes)
2. **Understand More** → Read `DOCKER_SETUP.md` (detailed)
3. **Deep Dive** → Study `DOCKER_ARCHITECTURE.md` (internals)

## 📋 Cheat Sheet

```bash
# START
docker-compose -f docker-compose.full.yml up -d

# STOP
docker-compose -f docker-compose.full.yml down

# LOGS
docker-compose -f docker-compose.full.yml logs -f

# STATUS
docker-compose -f docker-compose.full.yml ps

# RESTART
docker-compose -f docker-compose.full.yml restart

# REBUILD (after dependency changes)
docker-compose -f docker-compose.full.yml up -d --build

# CLEAN START (deletes data!)
docker-compose -f docker-compose.full.yml down -v
docker-compose -f docker-compose.full.yml up -d

# ACCESS APP SHELL
docker exec -it wildid-app bash

# ACCESS DATABASE
docker exec -it wildid-db psql -U wildid_user -d wildid

# VIEW STATS
docker stats
```

## 🆚 Docker vs Local Setup

### Docker Advantages ✅
- One command setup
- Consistent environment
- Includes database and email
- Easy to reset/rebuild
- Production-like environment
- Isolated from your system

### Local Setup Advantages ✅
- Faster for small changes
- Direct file access
- Familiar debugging
- No Docker knowledge needed

**Recommendation:** Use Docker for full testing, local for quick iteration.

## 🔐 Production Checklist

Before deploying to production:

- [ ] Generate strong `SECRET_KEY`
- [ ] Set strong database password
- [ ] Configure real email service (Gmail/SendGrid/SES)
- [ ] Set up SSL/TLS (use reverse proxy)
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Enable database backups
- [ ] Set up monitoring
- [ ] Review security settings
- [ ] Test magic link emails work

## 🎉 Success Indicators

You know it's working when:

1. ✅ `docker-compose ps` shows all services as "Up (healthy)"
2. ✅ http://localhost:3000 loads the WildID homepage
3. ✅ You can sign in and receive magic link in Mailhog
4. ✅ You can upload an image and see results
5. ✅ Your history saves and appears after sign-in

## 🆘 Getting Help

If stuck:

1. Check `docker-compose -f docker-compose.full.yml logs -f`
2. Verify `.env` has your API key
3. Try `docker-compose -f docker-compose.full.yml down -v` and restart
4. Check the comprehensive `DOCKER_SETUP.md`
5. Review `DOCKER_ARCHITECTURE.md` for system understanding

## 📚 Additional Resources

- **Docker Documentation:** https://docs.docker.com/
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **Mailhog:** https://github.com/mailhog/MailHog
- **Flask Deployment:** https://flask.palletsprojects.com/en/latest/deploying/

## 🎯 Next Steps

1. **Get Running** - Use Quick Start above
2. **Test Features** - Try sign-in, upload, history
3. **Customize** - Adjust `.env` as needed
4. **Deploy** - Use production setup when ready

---

**Quick Command Summary:**
```bash
# Setup
cp env.docker.template .env
# Add your TOGETHER_API_KEY to .env

# Run
docker-compose -f docker-compose.full.yml up -d

# View
open http://localhost:3000
open http://localhost:8025

# Stop
docker-compose -f docker-compose.full.yml down
```

**That's it! You're ready to Docker! 🐳**

For questions, check `DOCKER_SETUP.md` for the complete guide.


