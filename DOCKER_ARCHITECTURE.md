# 🏗️ Docker Architecture Overview

Visual guide to understand how WildID runs in Docker.

## 📊 Architecture Diagram

### Development Stack (`docker-compose.full.yml`)

```
┌─────────────────────────────────────────────────────────┐
│                     Host Machine                        │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │          Docker Network: wildid-network           │  │
│  │                                                    │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────┐ │  │
│  │  │             │  │              │  │         │ │  │
│  │  │   WildID    │  │  PostgreSQL  │  │ Mailhog │ │  │
│  │  │     App     │  │   Database   │  │  SMTP   │ │  │
│  │  │             │  │              │  │         │ │  │
│  │  │  Port 3000  │  │  Port 5432   │  │Port 1025│ │  │
│  │  │             │  │              │  │Port 8025│ │  │
│  │  └──────┬──────┘  └──────┬───────┘  └────┬────┘ │  │
│  │         │                │               │      │  │
│  │         └────────────────┴───────────────┘      │  │
│  │                                                  │  │
│  └──────────────────────────────────────────────────┘  │
│         │                 │               │            │
│         │                 │               │            │
│      Port 3000         Port 5432      Port 8025        │
│         │                 │               │            │
└─────────┼─────────────────┼───────────────┼────────────┘
          │                 │               │
          ▼                 ▼               ▼
    localhost:3000   localhost:5432  localhost:8025
    (Web Interface)  (DB Access)     (Email UI)
```

### Production Stack (`docker-compose.prod.yml`)

```
┌─────────────────────────────────────────────┐
│            Host Machine (Production)        │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │   Docker Network: wildid-network      │ │
│  │                                       │ │
│  │  ┌─────────────┐  ┌──────────────┐  │ │
│  │  │             │  │              │  │ │
│  │  │   WildID    │  │  PostgreSQL  │  │ │
│  │  │     App     │  │   Database   │  │ │
│  │  │             │  │              │  │ │
│  │  │  Port 3000  │  │  Port 5432   │  │ │
│  │  │             │  │  (Internal)  │  │ │
│  │  └──────┬──────┘  └──────┬───────┘  │ │
│  │         │                │          │ │
│  │         └────────────────┘          │ │
│  │                                     │ │
│  └───────────────────────────────────────┘ │
│         │                                   │
│      Port 3000                              │
│         │                                   │
└─────────┼───────────────────────────────────┘
          │
          ▼
   Reverse Proxy (nginx/Traefik)
          │
          ▼
   HTTPS (yourdomain.com)
```

## 🔌 Service Communication

### How Services Talk to Each Other

```
User Browser
    │
    │ HTTP Request
    ▼
WildID App (Container)
    │
    ├──► PostgreSQL (Container)    [Database queries]
    │       └── Volume: postgres_data (persistent)
    │
    ├──► Mailhog (Container)       [Send emails - DEV only]
    │       └── Web UI: localhost:8025
    │
    └──► External Services
            ├── Together.ai API    [Animal identification]
            └── Email SMTP Server  [Magic links - PROD]
```

## 📦 Container Details

### WildID App Container

```yaml
Image: Built from Dockerfile
Base: Python 3.12-slim
Ports: 3000 (exposed)
Environment:
  - TOGETHER_API_KEY
  - DATABASE_URL
  - MAIL_SERVER
  - SECRET_KEY
Volumes:
  - ./uploads (images)
  - ./flask_session (sessions)
  - ./ (code - dev only)
Networks: wildid-network
```

### PostgreSQL Container

```yaml
Image: postgres:15-alpine
Port: 5432 (internal only)
Environment:
  - POSTGRES_DB=wildid
  - POSTGRES_USER=wildid_user
  - POSTGRES_PASSWORD=***
Volumes:
  - postgres_data (persistent)
Networks: wildid-network
```

### Mailhog Container (Dev Only)

```yaml
Image: mailhog/mailhog
Ports:
  - 1025 (SMTP)
  - 8025 (Web UI)
Networks: wildid-network
```

## 💾 Data Persistence

### What Gets Saved Where

```
┌─────────────────────────────────────────┐
│         Docker Volumes                  │
├─────────────────────────────────────────┤
│                                         │
│  postgres_data/                         │
│  ├── User accounts                      │
│  ├── Identification history             │
│  └── Login tokens                       │
│                                         │
│  flask_session/                         │
│  └── User sessions                      │
│                                         │
├─────────────────────────────────────────┤
│       Host Bind Mounts                  │
├─────────────────────────────────────────┤
│                                         │
│  ./uploads/                             │
│  └── Uploaded images (temporary)        │
│                                         │
│  ./ (Dev only)                          │
│  └── Source code (live reload)          │
│                                         │
└─────────────────────────────────────────┘
```

### Backup Strategy

```bash
# Database backup
docker exec wildid-db pg_dump -U wildid_user wildid > backup.sql

# Volume backup
docker run --rm -v proof-of-concept-demo_postgres_data:/data \
  -v $(pwd):/backup alpine tar czf /backup/db_backup.tar.gz /data
```

## 🌊 Data Flow

### User Sign-In Flow

```
1. User enters email
   │
   ▼
2. App generates magic link token
   │
   ▼
3. Token saved to PostgreSQL
   │
   ▼
4. Email sent via Mailhog (dev) or SMTP (prod)
   │
   ▼
5. User clicks magic link
   │
   ▼
6. App verifies token from PostgreSQL
   │
   ▼
7. Session created in flask_session/
   │
   ▼
8. User logged in
```

### Animal Identification Flow

```
1. User uploads image
   │
   ▼
2. Image saved to ./uploads/ (temporary)
   │
   ▼
3. Image sent to Together.ai API
   │
   ▼
4. AI returns identification
   │
   ▼
5. If logged in: Saved to PostgreSQL
   │   ├── Species info
   │   ├── Image (base64)
   │   └── Timestamp
   │
   ▼
6. Temporary image deleted from ./uploads/
   │
   ▼
7. Results shown to user
```

## 🔒 Security Architecture

### Network Isolation

```
Internet
    │
    ▼
Host Firewall
    │
    ▼
Docker Bridge Network (wildid-network)
    │
    ├──► WildID App (Port 3000 exposed)
    │
    ├──► PostgreSQL (Internal only - NOT exposed)
    │
    └──► Mailhog (Dev only - NOT in production)
```

### Environment Variables Flow

```
.env file (on host)
    │
    ▼
Docker Compose reads .env
    │
    ▼
Sets environment variables in containers
    │
    ├──► App container
    │    └── Python app reads via os.getenv()
    │
    └──► DB container
         └── PostgreSQL uses for initialization
```

## 📈 Scaling Options

### Horizontal Scaling

```
         ┌─────────────┐
         │ Load Balancer│
         └──────┬───────┘
                │
        ┬───────┴───────┬
        │               │
   ┌────▼────┐    ┌────▼────┐
   │  App 1  │    │  App 2  │
   └────┬────┘    └────┬────┘
        │               │
        └───────┬───────┘
                │
         ┌──────▼───────┐
         │  PostgreSQL  │
         │   (Primary)  │
         └──────────────┘
```

### Docker Swarm Example

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml wildid

# Scale app containers
docker service scale wildid_app=3
```

## 🔧 Development vs Production

### Key Differences

| Feature | Development | Production |
|---------|------------|------------|
| **Database** | PostgreSQL (local) | PostgreSQL (RDS/managed) |
| **Email** | Mailhog (captured) | Real SMTP (Gmail/SendGrid) |
| **Code** | Live reload (mounted) | Baked into image |
| **Secrets** | .env file | Secrets manager |
| **Logs** | Console + file | Centralized logging |
| **SSL** | None | Required (reverse proxy) |
| **Volumes** | Local bind mounts | Named volumes |

### Environment Toggle

```bash
# Development
docker-compose -f docker-compose.full.yml up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

## 🛠️ Monitoring & Health

### Health Check Flow

```
Docker Engine
    │
    │ Every 30 seconds
    ▼
Container health check
    │
    ├──► curl http://localhost:3000/health
    │
    ├──► Success → Container: healthy
    │
    └──► Failure → Container: unhealthy
             │
             └──► After 3 failures → Container restarted
```

### Monitoring Commands

```bash
# Real-time stats
docker stats

# Health status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Detailed health
docker inspect wildid-app --format='{{json .State.Health}}'
```

## 🚀 Deployment Pipeline

### CI/CD Flow

```
1. Code Push (GitHub)
   │
   ▼
2. CI Server (GitHub Actions)
   │
   ├──► Run tests
   ├──► Build Docker image
   ├──► Push to registry
   └──► Tag with version
   │
   ▼
3. Production Server
   │
   ├──► Pull new image
   ├──► Backup database
   ├──► Rolling update
   └──► Health check
   │
   ▼
4. Verify deployment
```

### Example GitHub Actions

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build image
        run: docker build -t wildid:${{ github.sha }} .
      - name: Push to registry
        run: docker push wildid:${{ github.sha }}
      - name: Deploy
        run: |
          docker-compose -f docker-compose.prod.yml pull
          docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Resource Requirements

### Minimum Resources

```
┌──────────────────┬──────────┬──────────┬──────────┐
│ Service          │ CPU      │ Memory   │ Storage  │
├──────────────────┼──────────┼──────────┼──────────┤
│ WildID App       │ 0.5 core │ 512 MB   │ 1 GB     │
│ PostgreSQL       │ 0.5 core │ 256 MB   │ 5 GB     │
│ Mailhog (dev)    │ 0.1 core │ 64 MB    │ 100 MB   │
├──────────────────┼──────────┼──────────┼──────────┤
│ Total (dev)      │ 1.1 core │ 832 MB   │ 6 GB     │
│ Total (prod)     │ 1.0 core │ 768 MB   │ 6 GB     │
└──────────────────┴──────────┴──────────┴──────────┘
```

### Recommended Resources

```
┌──────────────────┬──────────┬──────────┬──────────┐
│ Service          │ CPU      │ Memory   │ Storage  │
├──────────────────┼──────────┼──────────┼──────────┤
│ WildID App       │ 1 core   │ 1 GB     │ 5 GB     │
│ PostgreSQL       │ 1 core   │ 1 GB     │ 20 GB    │
├──────────────────┼──────────┼──────────┼──────────┤
│ Total (prod)     │ 2 cores  │ 2 GB     │ 25 GB    │
└──────────────────┴──────────┴──────────┴──────────┘
```

## 🎯 Summary

**What you get with Docker:**
- ✅ Complete stack in one command
- ✅ Consistent dev/prod environments
- ✅ Easy scaling and updates
- ✅ Isolated services
- ✅ Persistent data
- ✅ Health monitoring
- ✅ Easy backups

**Quick Commands:**
```bash
# Start: docker-compose -f docker-compose.full.yml up -d
# Stop:  docker-compose -f docker-compose.full.yml down
# Logs:  docker-compose -f docker-compose.full.yml logs -f
```

For detailed instructions, see **DOCKER_SETUP.md** or **DOCKER_QUICKSTART.md**

