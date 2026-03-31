# StreamBox - Full-Stack Streaming Platform

A comprehensive, production-ready streaming platform supporting Movies, TV Shows, Anime, K-Dramas, and Live Streaming.

## 🎬 Features

### Core Features
- ✅ User authentication & authorization (JWT + OAuth)
- ✅ Multi-user support with role-based access (Admin, Moderator, User)
- ✅ Content management (Movies, TV Shows, Anime, Live Streams)
- ✅ Video player with multiple format support
- ✅ User dashboard with watch history & watchlist
- ✅ Admin panel for content & user management
- ✅ Search & filtering system
- ✅ Comment & rating system

### Advanced Features
- 📊 Analytics & statistics
- 💾 Multiple storage provider support (Local, S3, R2, B2)
- 🔐 Security (reCAPTCHA, Turnstile, Rate limiting)
- 🌍 Multi-language support (ready)
- 📧 Email notifications (SMTP)
- 🎨 Customizable homepage sections
- 📱 Mobile-friendly UI
- 🚀 API-ready for mobile apps

### Deployment Options
- Docker & Docker Compose
- Vercel (Frontend)
- Render / Railway (Backend)
- Traditional VPS (Nginx + Gunicorn)
- Cloudflare Workers (Optional)

## 📁 Project Structure

```
MovieB/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── core/           # Configuration, security, database
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── middleware/     # Custom middleware
│   │   ├── utils/          # Helper functions
│   │   └── main.py         # FastAPI app entry point
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   └── wsgi.py            # WSGI entry point for deployment
│
├── frontend/               # Next.js React frontend
│   ├── src/
│   │   ├── pages/         # Next.js pages
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities & API client
│   │   └── styles/        # CSS styles
│   ├── package.json
│   ├── next.config.js
│   └── .env.example
│
├── admin-panel/           # Admin dashboard (optional separate app)
├── docs/                  # Documentation
├── deployment/            # Deployment configs
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile.backend     # Backend Docker image
└── Dockerfile.frontend    # Frontend Docker image
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (for containerized setup)
- PostgreSQL (for production)

### Quick Start with Docker

1. **Clone and Setup Environment**
```bash
cd MovieB

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Edit .env files with your configuration
nano backend/.env
nano frontend/.env.local
```

2. **Start Services**
```bash
docker-compose up -d
```

3. **Access Application**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/api/v1/docs

### Manual Setup

#### Backend Setup

1. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Initialize Database**
```bash
python -c "from app.core.database import init_db; init_db()"
```

4. **Run Development Server**
```bash
uvicorn app.main:app --reload
```

#### Frontend Setup

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Configure Environment**
```bash
cp .env.example .env.local
# Edit .env.local with API URL
```

3. **Run Development Server**
```bash
npm run dev
```

## 🔑 Key Endpoints

### Authentication
```
POST   /api/v1/auth/register          # User registration
POST   /api/v1/auth/login             # User login
POST   /api/v1/auth/refresh           # Refresh access token
GET    /api/v1/auth/me                # Get current user
POST   /api/v1/auth/logout            # Logout
```

### Content
```
GET    /api/v1/content/movies         # List movies
GET    /api/v1/content/tv-shows       # List TV shows
GET    /api/v1/content/anime          # List anime
GET    /api/v1/content/featured       # Featured content
GET    /api/v1/content/trending       # Trending content
GET    /api/v1/content/{id}           # Get content details
GET    /api/v1/content/search         # Search content
POST   /api/v1/content/{id}/add-to-watchlist
DELETE /api/v1/content/{id}/remove-from-watchlist
```

### Admin
```
GET    /api/v1/admin/users            # List users
PATCH  /api/v1/admin/users/{id}/role  # Change user role
POST   /api/v1/admin/content          # Create content
PATCH  /api/v1/admin/content/{id}     # Update content
DELETE /api/v1/admin/content/{id}     # Delete content
GET    /api/v1/admin/stats            # Get statistics
```

## 🏗️ Architecture

### Backend Architecture
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL / SQLite
- **ORM**: SQLAlchemy
- **Authentication**: JWT + OAuth2
- **API Documentation**: Swagger/OpenAPI

### Frontend Architecture
- **Framework**: Next.js 14
- **UI Library**: React 18
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Authentication**: JWT + Cookies

## 🔐 Security Features

### Implemented
- ✅ JWT-based authentication
- ✅ Password hashing (bcrypt)
- ✅ Role-based access control (RBAC)
- ✅ Rate limiting
- ✅ CORS configuration
- ✅ SQL injection prevention (SQLAlchemy)
- ✅ GZIP compression

### Optional (Configurable)
- ⚙️ reCAPTCHA v2 & v3
- ⚙️ Cloudflare Turnstile
- ⚙️ Cloudflare DDoS protection
- ⚙️ SSL/TLS encryption

## 📊 Database Schema

### Main Tables
- `user` - User accounts and authentication
- `content` - Movies, TV shows, anime, live streams
- `episode` - TV show and anime episodes
- `video` - Video stream sources
- `subtitle` - Subtitle tracks
- `watch_history` - User watch history
- `comment` - User comments on content
- `notification` - User notifications
- `advertisement` - Ads and promotions
- `system_setting` - Configuration

[See full schema in backend/app/models/models.py]

## 🚢 Deployment

### Docker Compose (Recommended for Development)
```bash
docker-compose up -d
```

### Render.com (Backend)
1. Link your GitHub repository
2. Set environment variables
3. Deploy with start command: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`

### Vercel (Frontend)
1. Connect GitHub repository
2. Set environment variables
3. Deploy from dashboard

### Traditional VPS Setup
See [DEPLOYMENT_GUIDE.md](./docs/setup/DEPLOYMENT_GUIDE.md)

## 📚 API Documentation

Full API documentation available at `/api/v1/docs` (Swagger UI) or `/api/v1/redoc` (ReDoc)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Submit a pull request

## 📄 License

This project is licensed under the Unlicense - see LICENSE file for details.

## 🙋 Support

For issues and questions:
- Open an issue on GitHub
- Check documentation in `/docs`
- Review API docs at `/api/v1/docs`

## 🗺️ Roadmap

- [ ] Mobile app (React Native)
- [ ] Live streaming integration
- [ ] Advanced search filters
- [ ] Recommendation engine
- [ ] Payment integration
- [ ] Multi-language UI
- [ ] Advanced analytics
- [ ] CDN integration

---

**Happy Streaming! 🎬**
