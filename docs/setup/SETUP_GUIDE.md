# Setup Guide

This guide will help you set up and run the StreamBox streaming platform.

## Table of Contents
1. [Requirements](#requirements)
2. [Quick Start](#quick-start)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Database Setup](#database-setup)
6. [Configuration](#configuration)
7. [Running the Application](#running-the-application)

## Requirements

### System Requirements
- OS: Linux, macOS, or Windows (WSL2)
- RAM: 2GB minimum, 4GB recommended
- Disk: 2GB for code and dependencies

### Software
- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL 12+ (or SQLite for development)
- Docker & Docker Compose (optional but recommended)
- Git

### Verify Installation
```bash
python --version        # Should be 3.11+
node --version          # Should be 18+
npm --version           # Should be 9+
git --version
```

## Quick Start

### Option 1: Docker Compose (Easiest)

```bash
# Clone the repository
git clone <repository-url> MovieB
cd MovieB

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Start services
docker-compose up -d

# Wait for services to be ready
docker-compose ps

# Check frontend logs
docker-compose logs -f frontend

# Check backend logs
docker-compose logs -f backend
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs

### Option 2: Manual Setup

Jump to [Backend Setup](#backend-setup) and [Frontend Setup](#frontend-setup) below.

## Backend Setup

### Step 1: Navigate to Backend Directory
```bash
cd backend
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit environment file
nano .env  # or use your preferred editor
```

Edit the following variables:
```env
# Development settings
DEBUG=true
ENVIRONMENT=development

# Database (for development, SQLite is fine)
DATABASE_URL=sqlite:///./database.db

# JWT Secret (change this!)
JWT_SECRET_KEY=your-development-secret-key

# API Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://localhost:5173
```

### Step 5: Initialize Database
```bash
# Create tables
python -c "from app.core.database import init_db; init_db()"

# Verify database connection
python -c "from app.core.database import SessionLocal; db = SessionLocal(); print('Database connected!')"
```

### Step 6: Run Development Server
```bash
# Start FastAPI development server
uvicorn app.main:app --reload

# Or
python -m uvicorn app.main:app --reload
```

Server will be available at `http://localhost:8000`

### Verify Backend
```bash
# In a new terminal
curl http://localhost:8000/health

# Expected response
# {"status":"healthy","app":"StreamBox","version":"1.0.0","environment":"development"}
```

## Frontend Setup

### Step 1: Navigate to Frontend Directory
```bash
cd frontend
```

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Configure Environment
```bash
# Copy example environment file
cp .env.example .env.local

# Edit environment file
nano .env.local  # or use your preferred editor
```

Edit the following variables:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=StreamBox
```

### Step 4: Run Development Server
```bash
npm run dev
```

Server will be available at `http://localhost:3000`

### Verify Frontend
Open http://localhost:3000 in your browser - you should see the StreamBox homepage.

## Database Setup

### Option 1: SQLite (Development)
No setup needed! SQLite database is created automatically.

### Option 2: PostgreSQL (Recommended for Production)

#### Install PostgreSQL
```bash
# On Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# On macOS with Homebrew
brew install postgresql

# On Windows
# Download and install from https://www.postgresql.org/download/windows/
```

#### Create Database and User
```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE streambox;

# Create user
CREATE USER streambox_user WITH PASSWORD 'secure_password';

# Grant privileges
ALTER ROLE streambox_user SET client_encoding TO 'utf8';
ALTER ROLE streambox_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE streambox_user SET default_transaction_deferrable TO on;
ALTER ROLE streambox_user SET default_transaction_read_only TO off;
GRANT ALL PRIVILEGES ON DATABASE streambox TO streambox_user;

# Exit psql
\q
```

#### Update Backend Configuration
Edit `backend/.env`:
```env
DATABASE_URL=postgresql://streambox_user:secure_password@localhost:5432/streambox
```

#### Initialize Database
```bash
cd backend
python -c "from app.core.database import init_db; init_db()"
```

## Configuration

### Backend Configuration (.env)

Key environment variables:

```env
# Application
APP_NAME=StreamBox
DEBUG=false
ENVIRONMENT=production

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/streambox

# JWT
JWT_SECRET_KEY=your-super-secret-key-512-chars-minimum
JWT_EXPIRATION_HOURS=24
REFRESH_TOKEN_EXPIRATION_DAYS=30

# OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Security
ENABLE_RECAPTCHA=false
ENABLE_TURNSTILE=false

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Storage
STORAGE_PROVIDER=local  # local, s3, r2, b2
```

### Frontend Configuration (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=StreamBox
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

## Running the Application

### Terminal 1: Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

### Access the Application
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs

## First Time Setup

### Create Admin User (Optional)
1. Go to http://localhost:3000/auth/register
2. Register with your email
3. After registration, promote user to admin:

```bash
# In Python shell or script
from app.core.database import SessionLocal
from app.models import User, UserRole

db = SessionLocal()
user = db.query(User).filter(User.email == "your-email@example.com").first()
if user:
    user.role = UserRole.ADMIN
    db.add(user)
    db.commit()
    print("User promoted to admin!")
```

### Add Sample Content (Optional)
```bash
# Use the API or admin panel to add movies/shows
# Check the API documentation: http://localhost:8000/api/v1/docs
```

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version

# Verify virtual environment is activated
which python  # Should show path to venv

# Try reinstalling dependencies
pip install --force-reinstall -r requirements.txt

# Check if port 8000 is in use
lsof -i :8000
```

### Frontend won't start
```bash
# Check Node version
node --version

# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check if port 3000 is in use
lsof -i :3000
```

### Database connection error
```bash
# Check if database service is running
# For PostgreSQL
sudo systemctl status postgresql

# For Docker
docker-compose ps postgres

# Test connection
psql -U streambox_user -h localhost -d streambox
```

### API returning 401 Unauthorized
- Check if token is valid
- Clear browser cookies/storage
- Try logging in again
- Check JWT_SECRET_KEY is set correctly

## Next Steps

1. ✅ Backend running
2. ✅ Frontend running
3. 📚 Read [API Documentation](./API_DOCUMENTATION.md)
4. 🚀 Explore [Deployment Guide](./DEPLOYMENT_GUIDE.md)
5. 🎨 Customize the platform
6. 🔧 Add content to your platform
7. 📊 Set up admin panel

## Getting Help

- Check [MAIN_README.md](../../MAIN_README.md)
- Read API docs at http://localhost:8000/api/v1/docs
- Browse [API Documentation](./API_DOCUMENTATION.md)
- Open an issue on GitHub

---

**You're all set! Happy streaming! 🎬**
