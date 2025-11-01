# 🐳 Docker Quick Start

Get WildID running with Docker in 5 minutes!

## One-Command Setup (Development)

```bash
# 1. Copy environment template
cp env.docker.template .env

# 2. Add your Together.ai API key to .env
# Edit the TOGETHER_API_KEY line

# 3. Start everything
docker-compose -f docker-compose.full.yml up -d
```

That's it! Now you have:
- ✅ WildID App: http://localhost:3000
- ✅ PostgreSQL Database (auto-configured)
- ✅ Mailhog Email UI: http://localhost:8025

## Test It Out

1. Visit http://localhost:3000
2. Click "Sign In"
3. Enter any email (e.g., test@example.com)
4. Check http://localhost:8025 for the magic link
5. Click the link to sign in
6. Upload an animal photo!

## View Logs

```bash
# All logs
docker-compose -f docker-compose.full.yml logs -f

# Just the app
docker-compose -f docker-compose.full.yml logs -f app
```

## Stop Everything

```bash
# Stop (keeps data)
docker-compose -f docker-compose.full.yml down

# Stop and delete data
docker-compose -f docker-compose.full.yml down -v
```

## What's Running?

```bash
docker-compose -f docker-compose.full.yml ps
```

## Troubleshooting

**Port already in use?**
```bash
# Check what's using the port
netstat -ano | findstr :3000

# Stop the service or change the port in docker-compose.full.yml
```

**Database not connecting?**
```bash
# Restart the app
docker-compose -f docker-compose.full.yml restart app
```

**Need to rebuild after code changes?**
```bash
docker-compose -f docker-compose.full.yml up -d --build
```

## Production Setup

For production, use the production compose file:

```bash
# 1. Copy and configure environment
cp env.docker.template .env

# 2. Update .env with production values:
#    - Strong SECRET_KEY
#    - Real email service (Gmail, SendGrid, etc.)
#    - Strong database password

# 3. Start production stack
docker-compose -f docker-compose.prod.yml up -d
```

For detailed instructions, see **DOCKER_SETUP.md**

## Docker Files Reference

| File | Purpose |
|------|---------|
| `docker-compose.full.yml` | Development (App + DB + Mailhog) |
| `docker-compose.prod.yml` | Production (App + DB) |
| `env.docker.template` | Environment variable template |
| `DOCKER_SETUP.md` | Comprehensive Docker guide |

## Common Commands Cheat Sheet

```bash
# Start
docker-compose -f docker-compose.full.yml up -d

# Stop
docker-compose -f docker-compose.full.yml down

# Restart
docker-compose -f docker-compose.full.yml restart

# Logs
docker-compose -f docker-compose.full.yml logs -f

# Status
docker-compose -f docker-compose.full.yml ps

# Rebuild
docker-compose -f docker-compose.full.yml up -d --build

# Access app shell
docker exec -it wildid-app bash

# Access database
docker exec -it wildid-db psql -U wildid_user -d wildid
```

---

**Need more help?** Check out **DOCKER_SETUP.md** for the complete guide!

