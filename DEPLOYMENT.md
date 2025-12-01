# SpendScope Deployment Guide

This guide covers multiple deployment options for the SpendScope personal finance aggregator platform.

## 📋 Prerequisites

Before deploying, ensure you have:
- PostgreSQL database instance
- Redis instance
- Python 3.9 or higher
- Git

## 🚀 Deployment Options

### Option 1: Deploy on Render (Recommended for Beginners)

Render provides free hosting for web services with easy PostgreSQL and Redis setup.

#### Step 1: Prepare Your Repository

1. **Add a `render.yaml` file** (Blueprint):
   ```yaml
   services:
     - type: web
       name: spendscope-api
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: DATABASE_URL
           fromDatabase:
             name: spendscope-db
             property: connectionString
         - key: REDIS_URL
           fromService:
             name: spendscope-redis
             type: redis
             property: connectionString
         - key: SECRET_KEY
           generateValue: true
         - key: DEBUG
           value: false
   
   databases:
     - name: spendscope-db
       databaseName: spendscope
       user: spendscope
   
   services:
     - type: redis
       name: spendscope-redis
       ipAllowList: []
   ```

2. **Update `requirements.txt`** to include production server:
   ```bash
   echo "gunicorn==21.2.0" >> requirements.txt
   ```

#### Step 2: Deploy on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically:
   - Create the web service
   - Provision PostgreSQL database
   - Provision Redis instance
   - Set up environment variables

---

### Option 2: Deploy on Railway

Railway offers simple deployment with automatic PostgreSQL and Redis provisioning.

#### Step 1: Create `railway.toml`

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

#### Step 2: Deploy

1. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Login and deploy:
   ```bash
   railway login
   railway init
   railway add --plugin postgresql
   railway add --plugin redis
   railway up
   ```

3. Set environment variables:
   ```bash
   railway variables set SECRET_KEY=$(openssl rand -hex 32)
   railway variables set DEBUG=false
   ```

---

### Option 3: Deploy on Heroku

#### Step 1: Create Required Files

1. **Create `Procfile`:**
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   worker: python -m app.jobs.scheduler
   ```

2. **Create `runtime.txt`:**
   ```
   python-3.11.0
   ```

#### Step 2: Deploy

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login and create app
heroku login
heroku create spendscope-api

# Add PostgreSQL and Redis
heroku addons:create heroku-postgresql:essential-0
heroku addons:create heroku-redis:mini

# Set environment variables
heroku config:set SECRET_KEY=$(openssl rand -hex 32)
heroku config:set DEBUG=false

# Deploy
git push heroku main

# Scale workers
heroku ps:scale web=1 worker=1
```

---

### Option 4: Deploy on DigitalOcean App Platform

#### Step 1: Create `.do/app.yaml`

```yaml
name: spendscope
services:
  - name: api
    source_dir: /
    environment_slug: python
    github:
      repo: yourusername/spendscope
      branch: main
    build_command: pip install -r requirements.txt
    run_command: uvicorn app.main:app --host 0.0.0.0 --port 8080
    http_port: 8080
    instance_count: 1
    instance_size_slug: basic-xxs
    envs:
      - key: DEBUG
        value: "false"
      - key: SECRET_KEY
        type: SECRET
        value: ${SECRET_KEY}

databases:
  - name: spendscope-db
    engine: PG
    version: "15"
    
  - name: spendscope-redis
    engine: REDIS
    version: "7"
```

#### Step 2: Deploy

1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click **"Create App"**
3. Connect your GitHub repository
4. Use the app spec from `.do/app.yaml`

---

### Option 5: Deploy on AWS (EC2 + RDS + ElastiCache)

This is more advanced but offers full control.

#### Step 1: Set Up Infrastructure

1. **Launch EC2 Instance** (Ubuntu 22.04 LTS)
2. **Create RDS PostgreSQL Database**
3. **Create ElastiCache Redis Cluster**
4. **Configure Security Groups** to allow traffic

#### Step 2: SSH into EC2 and Set Up

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.11 python3.11-venv python3-pip nginx supervisor -y

# Clone repository
git clone https://github.com/yourusername/spendscope.git
cd spendscope

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

#### Step 3: Create Environment File

```bash
nano .env
```

Add:
```env
DATABASE_URL=postgresql://user:password@your-rds-endpoint:5432/spendscope
REDIS_URL=redis://your-elasticache-endpoint:6379
SECRET_KEY=your-secret-key-here
DEBUG=false
```

#### Step 4: Configure Supervisor

```bash
sudo nano /etc/supervisor/conf.d/spendscope.conf
```

Add:
```ini
[program:spendscope-api]
directory=/home/ubuntu/spendscope
command=/home/ubuntu/spendscope/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
user=ubuntu
autostart=true
autorestart=true
stderr_logfile=/var/log/spendscope/api.err.log
stdout_logfile=/var/log/spendscope/api.out.log

[program:spendscope-scheduler]
directory=/home/ubuntu/spendscope
command=/home/ubuntu/spendscope/venv/bin/python -m app.jobs.scheduler
user=ubuntu
autostart=true
autorestart=true
stderr_logfile=/var/log/spendscope/scheduler.err.log
stdout_logfile=/var/log/spendscope/scheduler.out.log
```

```bash
# Create log directory
sudo mkdir -p /var/log/spendscope

# Start supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

#### Step 5: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/spendscope
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/spendscope /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 6: Set Up SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

### Option 6: Deploy with Docker

#### Step 1: Create `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Step 2: Create `docker-compose.yml`

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/spendscope
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
    depends_on:
      - db
      - redis
    restart: unless-stopped

  scheduler:
    build: .
    command: python -m app.jobs.scheduler
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/spendscope
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=spendscope
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

#### Step 3: Deploy

```bash
# Create .env file
echo "SECRET_KEY=$(openssl rand -hex 32)" > .env

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f

# Run database migrations (if needed)
docker-compose exec api alembic upgrade head
```

---

## 🔒 Environment Variables

Required environment variables for all deployment methods:

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Redis
REDIS_URL=redis://host:6379

# Security
SECRET_KEY=your-secret-key-here

# Application
DEBUG=false
APP_NAME=SpendScope
API_VERSION=1.0.0
MAX_WORKERS=4

# Optional
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

---

## 🔧 Post-Deployment Steps

### 1. Run Database Migrations

If using Alembic:
```bash
alembic upgrade head
```

### 2. Verify Health Check

```bash
curl https://your-domain.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-01T10:00:00"
}
```

### 3. Test API Documentation

Visit:
- Swagger UI: `https://your-domain.com/docs`
- ReDoc: `https://your-domain.com/redoc`

### 4. Monitor Logs

- Check application logs for errors
- Monitor scheduler job execution
- Verify database connections

### 5. Set Up Monitoring (Optional)

Consider integrating:
- **Sentry** for error tracking
- **Datadog** or **New Relic** for performance monitoring
- **Uptime Robot** for uptime monitoring

---

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql $DATABASE_URL -c "SELECT 1"
```

### Redis Connection Issues

```bash
# Test Redis connection
redis-cli -u $REDIS_URL ping
```

### Application Won't Start

1. Check logs for detailed error messages
2. Verify all environment variables are set
3. Ensure database and Redis are accessible
4. Check port availability

### Scheduler Not Running

1. Verify worker/scheduler process is running
2. Check Redis connection
3. Review scheduler logs

---

## 📊 Performance Optimization

### For Production:

1. **Use a production ASGI server**: Gunicorn with Uvicorn workers
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Enable database connection pooling** (already in SQLAlchemy)

3. **Configure Redis persistence** for important data

4. **Set up CDN** for static assets (if any)

5. **Enable compression** in Nginx/load balancer

---

## 🔄 CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Render
      env:
        RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
        RENDER_SERVICE_ID: ${{ secrets.RENDER_SERVICE_ID }}
      run: |
        curl -X POST \
          -H "Authorization: Bearer $RENDER_API_KEY" \
          https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys
```

---

## 📞 Support

For deployment issues:
1. Check the logs first
2. Review this guide
3. Consult platform-specific documentation
4. Open an issue on GitHub

---

**🎉 Your SpendScope application is now deployed and ready to use!**
