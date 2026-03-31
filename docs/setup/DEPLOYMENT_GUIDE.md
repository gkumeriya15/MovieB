# Deployment Guide

This guide covers deploying StreamBox to various hosting platforms.

## Prerequisites
- Domain name (optional but recommended)
- SSL certificate (for HTTPS)
- Environment variables configured

## 1. Docker Deployment (Recommended)

### Local Development
```bash
docker-compose up -d
```

### Production Deployment

#### Using Docker Compose
```bash
# Build images
docker-compose -f docker-compose.yml build

# Start services
docker-compose -f docker-compose.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

#### Using Docker Stack (Swarm)
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml streambox

# Check status
docker stack services streambox
```

## 2. Vercel Deployment (Frontend)

### Step 1: Push to GitHub
```bash
git push origin main
```

### Step 2: Connect Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Select your GitHub repository
4. Configure project:
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

### Step 3: Environment Variables
Add in Vercel dashboard:
```
NEXT_PUBLIC_API_URL=https://your-api-domain.com/api/v1
NEXT_PUBLIC_APP_NAME=StreamBox
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-id
```

### Step 4: Deploy
```bash
git push origin main  # Auto-deploys
```

## 3. Render Deployment (Backend)

### Step 1: Create Web Service
1. Go to [render.com](https://render.com)
2. Click "New +"
3. Select "Web Service"
4. Connect GitHub repository

### Step 2: Configure
- **Name**: streambox-api
- **Root Directory**: backend
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`

### Step 3: Environment Variables
Set in dashboard:
```
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://user:password@host:5432/streambox
JWT_SECRET_KEY=your-secret-key
CORS_ORIGINS=https://frontend-domain.com
```

### Step 4: Deploy
Push to main branch - auto-deploys

## 4. Traditional VPS Setup (DigitalOcean/Linode)

### Prerequisites
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv nodejs npm postgresql nginx
```

### Backend Setup
```bash
# Create app directory
sudo mkdir -p /var/www/streambox/backend
sudo chown -R $USER:$USER /var/www/streambox

# Clone repository
cd /var/www/streambox
git clone your-repo.git .

# Create virtual environment
cd backend
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Configure environment
cp .env.example .env
nano .env  # Edit configuration
```

### Frontend Setup
```bash
cd /var/www/streambox/frontend

# Install dependencies
npm ci

# Build
npm run build

# Create PM2 config
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'streambox-frontend',
    script: 'npm',
    args: 'start',
    cwd: '/var/www/streambox/frontend',
  }]
}
EOF
```

### Systemd Service (Backend)
```bash
sudo tee /etc/systemd/system/streambox-backend.service << 'EOF'
[Unit]
Description=StreamBox Backend
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/streambox/backend
Environment="PATH=/var/www/streambox/backend/venv/bin"
ExecStart=/var/www/streambox/backend/venv/bin/gunicorn \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    -b 127.0.0.1:8000 \
    app.main:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable streambox-backend
sudo systemctl start streambox-backend
```

### Nginx Configuration
```bash
sudo tee /etc/nginx/sites-available/streambox << 'EOF'
upstream streambox_backend {
    server 127.0.0.1:8000;
}

upstream streambox_frontend {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # API
    location /api/ {
        proxy_pass http://streambox_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_request_buffering off;
    }

    # Frontend
    location / {
        proxy_pass http://streambox_frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
EOF

sudo ln -s /etc/nginx/sites-available/streambox /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Install SSL Certificate (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com
```

### Database Setup
```bash
sudo -u postgres createdb streambox
sudo -u postgres createuser streambox_user
sudo -u postgres psql -c "ALTER USER streambox_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE streambox TO streambox_user;"

# Backup database
pg_dump -U streambox_user streambox > backup.sql

# Restore database
psql -U streambox_user streambox < backup.sql
```

## 5. Cloudflare Setup

### DNS Configuration
1. Point your domain to Cloudflare nameservers
2. Add DNS records:
   - Type: A, Name: @, Content: your-server-ip
   - Type: CNAME, Name: www, Content: your-domain.com

### SSL/TLS
1. Go to SSL/TLS settings
2. Set to "Flexible" (at minimum) or "Full" with certificate

### Performance
- Enable Brotli compression
- Cache static assets
- Enable minification

### Security
- Enable DDoS protection
- Set security level to High
- Enable Web Application Firewall

## 6. Database Backup & Recovery

### Automated Backup
```bash
#!/bin/bash
# /usr/local/bin/backup-streambox.sh

BACKUP_DIR="/backups/streambox"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U streambox_user streambox | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup uploads (if applicable)
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/streambox/uploads/

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /usr/local/bin/backup-streambox.sh
```

## 7. Monitoring & Logs

### View Logs
```bash
# Backend
docker-compose logs -f backend

# Frontend  
docker-compose logs -f frontend

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Systemd service
sudo journalctl -u streambox-backend -f
```

### Health Checks
```bash
# API health
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# Database
pg_isready -U streambox_user -h localhost
```

## 8. Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Verify database connection
python manage.py dbshell

# Check port
lsof -i :8000
```

### Frontend not loading
```bash
# Check if running
docker-compose ps frontend

# Check logs
docker-compose logs frontend

# Verify API connectivity
curl $NEXT_PUBLIC_API_URL/health
```

### Database connection errors
```bash
# Test connection
psql -U streambox_user -h localhost -d streambox

# Check services
docker-compose ps postgres

# Recreate database
docker-compose down
docker volume rm movieb_postgres_data
docker-compose up postgres
```

## Production Checklist
- [ ] Set `DEBUG=false`
- [ ] Configure strong `JWT_SECRET_KEY`
- [ ] Set up HTTPS/SSL
- [ ] Configure PostgreSQL
- [ ] Enable rate limiting
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Set up error tracking
- [ ] Enable logging
- [ ] Configure CDN
- [ ] Set up health checks
- [ ] Configure alerts

---

For more help, see [README.md](../MAIN_README.md)
