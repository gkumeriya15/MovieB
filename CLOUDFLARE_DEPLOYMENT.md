# MovieBox Deployment Guide - Cloudflare Pages + Render Backend

This guide covers deploying MovieBox with a separate frontend (Cloudflare Pages) and backend (Render).

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│          Cloudflare Pages (Frontend)                │
│  - React/Next.js application                        │
│  - Static HTML, CSS, JS                             │
│  - Edge caching                                     │
│  CDN: https://movieb-frontend.pages.dev             │
└────────────────┬────────────────────────────────────┘
                 │ API Calls
                 │ (CORS enabled)
                 │
    ┌────────────▼─────────────┐
    │  Cloudflare Worker       │
    │  (Optional API Proxy)    │
    │  - Caching              │
    │  - Rate limiting        │
    │  - Error handling       │
    └────────────┬────────────┘
                 │
    ┌────────────▼──────────────────────┐
    │   Render FastAPI Backend          │
    │   https://movieb-rsoz.onrender.com│
    │   - Python FastAPI                │
    │   - Database                      │
    │   - Authentication                │
    │   - Streaming endpoints           │
    └───────────────────────────────────┘
```

## Prerequisites

- Node.js 18+ and npm
- Cloudflare account
- Render account (already deployed)
- Git
- Wrangler CLI: `npm install -g wrangler`

## Step 1: Local Development Setup

### 1.1 Install Dependencies

```bash
# Install frontend dependencies
cd frontend
npm install

# Install Cloudflare Worker dependencies (if using custom worker)
cd ../cloudflare-worker
npm install  # Usually no deps needed
```

### 1.2 Configure Environment

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=https://movieb-rsoz.onrender.com/api/v1
NEXT_PUBLIC_APP_NAME=MovieBox
NEXT_PUBLIC_DEBUG_MODE=false
```

### 1.3 Run Development Server

```bash
cd frontend
npm run dev
# Opens at http://localhost:3000
```

Test the API integration:
```bash
# Search endpoint
curl "https://movieb-rsoz.onrender.com/api/v1/search?q=inception"

# Details endpoint
curl "https://movieb-rsoz.onrender.com/api/v1/details/[id]"

# Episodes endpoint
curl "https://movieb-rsoz.onrender.com/api/v1/episodes/[id]"

# Stream endpoint
curl "https://movieb-rsoz.onrender.com/api/v1/stream/[id]"
```

## Step 2: Build Optimization

### 2.1 Build Frontend for Production

```bash
cd frontend
npm run build

# Output generated in:
# - Next.js: .next/ directory (or dist/ with export)
# - Static files can be deployed to any CDN
```

### 2.2 Configure for Static Export (Optional)

Edit `frontend/next.config.js`:

```javascript
const nextConfig = {
  output: 'export',  // Enable static export
  reactStrictMode: true,
  swcMinify: true,
  images: {
    unoptimized: true,  // Required for static export
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://movieb-rsoz.onrender.com/api/v1',
  },
}

module.exports = nextConfig
```

## Step 3: Cloudflare Pages Deployment

### 3.1 Connect Repository to Cloudflare Pages

**Option A: Via Cloudflare Dashboard**

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Select **Pages** → **Create a project**
3. Connect your GitHub repository
4. Configure build settings:
   - **Framework preset**: Next.js
   - **Build command**: `npm run build`
   - **Build output directory**: `frontend/.next/export` (or `.next`)
   - **Root directory**: `frontend`

5. Set environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://movieb-rsoz.onrender.com/api/v1
   ```

6. Click **Deploy**

**Option B: Using Wrangler (CLI)**

```bash
# Install Wrangler
npm install -g wrangler

# Deploy
cd frontend
wrangler pages deploy .next/export

# Or configure in wrangler.toml first:
wrangler pages deploy .next/export --project-name=movieb-frontend
```

### 3.2 Configure Custom Domain (Optional)

1. In Cloudflare Dashboard
2. Pages project → Custom domains
3. Add your domain
4. Update DNS settings if needed

## Step 4: Cloudflare Worker Proxy (Optional)

The Cloudflare Worker acts as an intermediary, providing:
- Response caching
- CORS handling
- Error handling
- Rate limiting

### 4.1 Deploy Worker

```bash
cd cloudflare-worker

# Set environment variables
wrangler secret put BACKEND_URL  # Enter: https://movieb-rsoz.onrender.com

# Deploy worker
wrangler deploy

# Bindings available at: https://moviebox-api-proxy.your-domain.com/api/*
```

### 4.2 Use Worker in Frontend (Optional)

Update `frontend/.env.production`:

```env
NEXT_PUBLIC_API_URL=https://moviebox-api-proxy.your-domain.com/api/v1
```

## Step 5: CORS Configuration

### 5.1 Backend CORS Setup (Render)

The FastAPI backend should have CORS enabled:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5.2 Test CORS

```bash
# From browser console or test:
curl -H "Origin: https://movieb-frontend.pages.dev" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS "https://movieb-rsoz.onrender.com/api/v1/search"
```

## Step 6: Deployment Checklist

- [ ] `frontend/.env.local` configured
- [ ] Backend API is running on Render
- [ ] CORS enabled on backend
- [ ] Frontend builds successfully: `npm run build`
- [ ] No Python dependencies in build output
- [ ] `.wranglerignore` excluding Python files
- [ ] Cloudflare Pages connected to repository
- [ ] Environment variables set in Cloudflare
- [ ] Custom domain configured (if applicable)
- [ ] Worker deployed (if using proxy)
- [ ] Test API endpoints from deployed frontend

## Step 7: Testing Deployment

### 7.1 Test Search Functionality

1. Open frontend: https://movieb-frontend.pages.dev
2. Search for a movie (e.g., "Inception")
3. Verify results appear

### 7.2 Test Video Streaming

1. Click on a search result
2. Verify details load
3. Click play
4. Verify stream URL loads

### 7.3 Monitor Performance

**Cloudflare Analytics:**
- Pages project → Analytics
- Monitor request rates, performance

**Backend Logs:**
- Render dashboard → Logs
- Check for any API errors

## Step 8: Troubleshooting

### Build Fails with Python Errors

**Problem**: `.venv: No such file or directory`

**Solution**:
```bash
# Ensure .wranglerignore exists
cat .wranglerignore

# Should exclude:
.venv/
.venv-1/
requirements.txt
pyproject.toml
backend/
src/
```

### API Calls Return 403/CORS Errors

**Problem**: CORS error from browser

**Solutions**:

1. Check backend CORS config
2. Use Cloudflare Worker proxy
3. Test API directly:
   ```bash
   curl "https://movieb-rsoz.onrender.com/api/v1/search?q=test"
   ```

### Frontend Not Loading

**Problem**: Blank page or 404

**Solutions**:

1. Check build output: `frontend/.next/` or `frontend/dist/`
2. Verify `NEXT_PUBLIC_API_URL` is set
3. Check Cloudflare Pages build logs
4. Test locally: `npm run build && npm run start`

### Slow Performance

**Solutions**:

1. Enable Cloudflare caching
2. Deploy Cloudflare Worker proxy with caching
3. Check backend response times
4. Enable Cloudflare auto-minification

## Step 9: Advanced: Automatic Deployments

### 9.1 GitHub Actions (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloudflare Pages

on:
  push:
    branches: [ main ]
    paths: [ 'frontend/**' ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Build
        run: |
          cd frontend
          npm run build

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: movieb-frontend
          directory: frontend/.next/export
```

## API Reference

### Search Endpoint
```bash
GET /api/v1/search?q=query
```

### Details Endpoint
```bash
GET /api/v1/details/{id}
```

### Episodes Endpoint
```bash
GET /api/v1/episodes/{id}
```

### Stream Endpoint
```bash
GET /api/v1/stream/{id}
GET /api/v1/stream/episode/{episode_id}?page_url=...
```

For full API documentation, see [FASTAPI_README.md](./FASTAPI_README.md).

## Monitoring & Maintenance

### Daily Checks

1. Check Cloudflare Analytics
2. Monitor error rates
3. Review Render backend logs
4. Test search and stream endpoints

### Weekly Tasks

1. Review performance metrics
2. Update dependencies: `npm update`
3. Check for security alerts
4. Test CORS with different origins

### Monthly Tasks

1. Review user analytics
2. Optimize caching strategy
3. Update deployment documentation
4. Plan for scaling if needed

## Support

For issues:
1. Check application logs
2. Review API responses in browser DevTools
3. Test API endpoints directly
4. Check Cloudflare status
5. Review Render backend logs

## Rollback Procedures

### Cloudflare Pages Rollback

1. Pages project → Deployments
2. Click previous successful deployment
3. Click "Rollback to this deployment"

### Backend Rollback

1. Render dashboard → Deployments
2. Select previous version
3. Deploy

## Security Considerations

- ✅ Enable Cloudflare DDoS protection
- ✅ Use environment variables for sensitive data
- ✅ Enable HTTPS everywhere
- ✅ Configure rate limiting on Cloudflare Worker
- ✅ Validate all user inputs on backend
- ✅ Use secure token storage (httpOnly cookies)
- ✅ Regular security audits

## Performance Optimization

### Frontend Optimization
- Enable asset compression
- Use next/image for image optimization
- Implement lazy loading
- Caching strategy

### Backend Optimization
- Database query optimization
- Response caching
- CDN for media files
- Load balancing (if needed)

---

**Last Updated**: April 2026
**Status**: Production Ready
