# Production Dashboard Deployment Guide

**Version**: v1.3.13 - Production Edition  
**Date**: January 6, 2026  
**Status**: STAGE 2 COMPLETE

---

## 📋 Overview

This guide covers deploying the Regime Intelligence Dashboard to production with:
- ✅ Authentication & authorization
- ✅ HTTPS/SSL encryption
- ✅ Production WSGI server (Gunicorn)
- ✅ Reverse proxy (Nginx)
- ✅ Monitoring & logging
- ✅ Automatic restarts (systemd)

---

## 🔐 Security Features

### 1. **Authentication**
- Login required for all dashboard access
- Password hashing with Werkzeug
- Session management with secure cookies
- CSRF protection built-in

### 2. **Session Security**
- HTTPS-only cookies (`SESSION_COOKIE_SECURE`)
- HttpOnly cookies (prevent JavaScript access)
- SameSite=Lax (CSRF protection)
- 24-hour session lifetime

### 3. **Environment Variables**
- `SECRET_KEY`: Flask secret key (auto-generated if not set)
- `PRODUCTION`: Set to `true` for production mode
- `PORT`: Server port (default: 5002)

---

## 🚀 Deployment Options

### Option 1: Development Mode (Current)

```bash
# Simple development server (for testing only)
cd /home/user/webapp/working_directory/phase3_intraday_deployment
python regime_dashboard_production.py
```

**Access**: http://localhost:5002  
**Credentials**: admin / change_me_in_production  
**Note**: ⚠️ NOT for production use

---

### Option 2: Production with Gunicorn

#### Step 1: Install Gunicorn

```bash
pip install gunicorn
```

#### Step 2: Start Server

```bash
# Basic
gunicorn regime_dashboard_production:app

# With configuration
gunicorn -c wsgi_config.py regime_dashboard_production:app

# Custom settings
gunicorn \
  --bind 0.0.0.0:5002 \
  --workers 4 \
  --timeout 120 \
  --access-logfile /var/log/regime-dashboard/access.log \
  --error-logfile /var/log/regime-dashboard/error.log \
  regime_dashboard_production:app
```

#### Step 3: Set Environment Variables

```bash
export PRODUCTION=true
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export PORT=5002
```

---

### Option 3: Production with Nginx Reverse Proxy

#### Step 1: Install Nginx

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install nginx

# CentOS/RHEL
sudo yum install nginx
```

#### Step 2: Configure Nginx

Create `/etc/nginx/sites-available/regime-dashboard`:

```nginx
upstream regime_dashboard {
    server 127.0.0.1:5002 fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Logging
    access_log /var/log/nginx/regime-dashboard-access.log;
    error_log /var/log/nginx/regime-dashboard-error.log;
    
    # Proxy settings
    location / {
        proxy_pass http://regime_dashboard;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }
    
    # Health check
    location /api/health {
        proxy_pass http://regime_dashboard;
        access_log off;
    }
}
```

#### Step 3: Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/regime-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

### Option 4: Production with systemd (Auto-restart)

#### Step 1: Create systemd Service

Create `/etc/systemd/system/regime-dashboard.service`:

```ini
[Unit]
Description=Regime Intelligence Dashboard
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/home/user/webapp/working_directory/phase3_intraday_deployment
Environment="PRODUCTION=true"
Environment="SECRET_KEY=your-secret-key-here"
Environment="PORT=5002"
ExecStart=/usr/bin/gunicorn \
    -c wsgi_config.py \
    regime_dashboard_production:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Step 2: Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable regime-dashboard
sudo systemctl start regime-dashboard
sudo systemctl status regime-dashboard
```

#### Step 3: Manage Service

```bash
# View logs
sudo journalctl -u regime-dashboard -f

# Restart
sudo systemctl restart regime-dashboard

# Stop
sudo systemctl stop regime-dashboard
```

---

## 🔒 SSL/HTTPS Setup

### Option A: Let's Encrypt (Free)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

### Option B: Self-Signed (Development)

```bash
# Generate certificate
openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem -out cert.pem \
  -days 365 -nodes \
  -subj "/CN=your-domain.com"
```

### Option C: Commercial Certificate

1. Purchase from CA (DigiCert, GlobalSign, etc.)
2. Follow CA instructions
3. Install certificate in Nginx config

---

## 👥 User Management

### Add New Users

Edit `regime_dashboard_production.py`:

```python
from werkzeug.security import generate_password_hash

USERS = {
    'admin': generate_password_hash('secure_password_here'),
    'analyst': generate_password_hash('another_password'),
    'trader': generate_password_hash('different_password'),
}
```

### Change Default Password

```bash
python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your_password'))"
```

Copy output and update `USERS` dictionary.

---

## 📊 Monitoring & Logging

### Application Logs

```bash
# Gunicorn logs
tail -f /var/log/regime-dashboard/access.log
tail -f /var/log/regime-dashboard/error.log

# Systemd logs
sudo journalctl -u regime-dashboard -f
```

### Health Check Endpoint

```bash
# Check health
curl http://localhost:5002/api/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2026-01-06T11:00:00",
  "components": {
    "market_data_fetcher": true,
    "regime_detector": true,
    "enhanced_data": true,
    "feature_engineer": true
  }
}
```

### Monitoring Tools

**Option 1: Prometheus**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'regime-dashboard'
    static_configs:
      - targets: ['localhost:5002']
```

**Option 2: Uptime Kuma**
- Web-based monitoring
- Alerts via email/Slack/Discord
- Simple setup

**Option 3: DataDog/New Relic**
- Enterprise monitoring
- APM features
- Cloud-hosted

---

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create log directory
RUN mkdir -p /var/log/regime-dashboard

# Expose port
EXPOSE 5002

# Run with Gunicorn
CMD ["gunicorn", "-c", "wsgi_config.py", "regime_dashboard_production:app"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  dashboard:
    build: .
    container_name: regime-dashboard
    ports:
      - "5002:5002"
    environment:
      - PRODUCTION=true
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./logs:/var/log/regime-dashboard
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    container_name: regime-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - dashboard
    restart: unless-stopped
```

### Deploy

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## ☁️ Cloud Deployment

### AWS (EC2 + ELB)

1. **Launch EC2 instance** (Ubuntu 20.04)
2. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3-pip nginx
   pip3 install gunicorn flask werkzeug
   ```
3. **Deploy application**
4. **Configure Nginx** (as above)
5. **Set up ELB** for HTTPS termination
6. **Configure security groups** (port 80, 443)

### Google Cloud (App Engine)

Create `app.yaml`:

```yaml
runtime: python39
entrypoint: gunicorn -b :$PORT regime_dashboard_production:app

env_variables:
  PRODUCTION: 'true'
  SECRET_KEY: 'your-secret-key'

automatic_scaling:
  min_instances: 1
  max_instances: 5
```

Deploy:

```bash
gcloud app deploy
```

### Azure (App Service)

```bash
# Create resource group
az group create --name regime-dashboard --location eastus

# Create app service plan
az appservice plan create --name dashboard-plan --resource-group regime-dashboard --sku B1 --is-linux

# Create web app
az webapp create --resource-group regime-dashboard --plan dashboard-plan --name regime-dashboard --runtime "PYTHON:3.9"

# Deploy
az webapp deployment source config-local-git --name regime-dashboard --resource-group regime-dashboard
git remote add azure <deployment-url>
git push azure main
```

### Heroku

```bash
# Create app
heroku create regime-dashboard

# Set environment variables
heroku config:set PRODUCTION=true
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Deploy
git push heroku main

# Open
heroku open
```

---

## 🔧 Troubleshooting

### Issue: 502 Bad Gateway

**Cause**: Gunicorn not running or wrong port

**Fix**:
```bash
# Check if Gunicorn is running
ps aux | grep gunicorn

# Check port
netstat -tlnp | grep 5002

# Restart
sudo systemctl restart regime-dashboard
```

### Issue: Permission Denied (Logs)

**Cause**: Log directory permissions

**Fix**:
```bash
sudo mkdir -p /var/log/regime-dashboard
sudo chown -R www-data:www-data /var/log/regime-dashboard
sudo chmod 755 /var/log/regime-dashboard
```

### Issue: Session Not Persisting

**Cause**: Missing SECRET_KEY or insecure cookie settings

**Fix**:
```bash
# Set SECRET_KEY
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# For HTTPS, ensure:
# SESSION_COOKIE_SECURE = True
# Only set if using HTTPS
```

### Issue: Slow Dashboard Load

**Cause**: Market data fetch timeout

**Fix**:
```python
# In market_data_fetcher.py, increase timeout
self.cache_duration = 300  # 5 minutes

# Or reduce data sources
```

---

## 📈 Performance Optimization

### 1. Enable Caching

```python
# Redis caching
import redis
cache = redis.Redis(host='localhost', port=6379, db=0)

@app.route('/api/regime-data')
def get_regime_data():
    cache_key = 'regime_data'
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # Fetch data
    data = fetch_data()
    cache.setex(cache_key, 300, json.dumps(data))
    return jsonify(data)
```

### 2. Worker Tuning

```python
# wsgi_config.py
workers = 4  # (2 x CPU cores) + 1
worker_connections = 1000
timeout = 120
```

### 3. Database Connection Pooling

If using database:
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:pass@localhost/db',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

---

## ✅ Deployment Checklist

- [ ] Change default password
- [ ] Set SECRET_KEY environment variable
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (allow 80, 443)
- [ ] Set up log rotation
- [ ] Configure monitoring
- [ ] Test health check endpoint
- [ ] Set up automatic backups
- [ ] Configure alerting
- [ ] Document access credentials
- [ ] Test auto-restart (systemd)
- [ ] Load test application
- [ ] Set up CI/CD pipeline
- [ ] Configure rate limiting
- [ ] Enable CORS if needed
- [ ] Set up disaster recovery

---

## 📞 Support

**Documentation**: This file  
**Issues**: GitHub Issues  
**Email**: support@trading-system.com  
**Slack**: #regime-dashboard

---

## 📚 Additional Resources

- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.0.x/security/)
- [Gunicorn Deployment](https://docs.gunicorn.org/en/stable/deploy.html)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/getting-started/)
- [systemd Service](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

**Version**: v1.3.13 - Production Edition  
**Date**: January 6, 2026  
**Status**: ✅ STAGE 2 COMPLETE - PRODUCTION READY
