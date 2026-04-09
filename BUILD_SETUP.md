# MovieBox Build & Deployment Setup

**Status**: ✅ Ready for Production  
**Last Updated**: April 2026

## Quick Overview

This guide helps you deploy MovieBox:
- **Frontend** → Cloudflare Pages (or any static host)
- **Backend** → Render (FastAPI - https://movieb-rsoz.onrender.com)

## What Changed (Key Fixes)

| Issue | Fix | Status |
|-------|-----|--------|
| "Missing .venv file" | Created `.wranglerignore` | ✅ |
| Python in Cloudflare build | Root `wrangler.toml` with correct paths | ✅ |
| No CORS support | Updated Worker proxy | ✅ |
| No API client for streaming | Enhanced `api.ts` with all endpoints | ✅ |
| Unclear deployment process | Created comprehensive docs | ✅ |

## Files Created/Updated

### 🆕 New Files

```
/wrangler.toml                      Cloudflare Pages config (root)
/.wranglerignore                   Files to exclude from build
/frontend/.env.local               Environment for local dev
/CLOUDFLARE_DEPLOYMENT.md         Full deployment guide
/FRONTEND_QUICK_START.md           Developer quick start
/FRONTEND_BUILD_CONFIG.md          Build configuration docs
/BUILD_SETUP.md                    This file
```

### 📝 Updated Files

```
/cloudflare-worker/wrangler.toml   Updated with Render URL
/cloudflare-worker/worker.js       Enhanced with CORS & error handling
/frontend/src/lib/api.ts           Added all API endpoints (search, details, episodes, stream)
```

## Deployment Methods

### Method 1: Cloudflare Pages (RECOMMENDED)

**Best for**: Fast, global CDN, free tier available, GitHub integration

```bash
# 1. Push code to GitHub
git push origin main

# 2. Cloudflare Pages auto-deploys (5 min)
# Dashboard: cloudflare.com → Pages → movieb-frontend

# 3. Done! ✅
# Frontend: https://movieb-frontend.pages.dev
# Backend: https://movieb-rsoz.onrender.com (already running)
```

**Configuration**:
- Build command: `npm run build`
- Build output directory: `frontend/.next`
- Environment: `NEXT_PUBLIC_API_URL=https://movieb-rsoz.onrender.com/api/v1`

### Method 2: Wrangler CLI Deploy

**Best for**: Direct deployment without GitHub

```bash
# 1. Install Wrangler
npm install -g wrangler

# 2. Build frontend
cd frontend
npm run build

# 3. Deploy to Cloudflare
cd ..
wrangler pages deploy frontend/.next --project-name=movieb-frontend

# 4. Done! ✅
```

### Method 3: Netlify Deploy

**Best for**: Netlify ecosystem, build integration

```bash
# 1. Install Netlify CLI
npm install -g netlify-cli

# 2. Build
cd frontend && npm run build

# 3. Deploy
cd ..
netlify deploy --dir frontend/.next --prod

# 4. Done! ✅
```

### Method 4: Vercel Deploy (for Next.js)

**Best for**: Premium Next.js experience, automatic optimization

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy (Vercel builds automatically)
vercel --prod

# 3. Done! ✅
```

## Architecture Decision: Why This?

### Frontend on Cloudflare Pages

✅ **Advantages**:
- Fast edge network globally
- Free tier (limited)
- GitHub integration  
- HTTPS by default
- No cold starts
- Static hosting (simple)
- Auto-scaling

❌ **Limitations**:
- No backend code (Python not supported)
- Workers need separate config

### Backend on Render

✅ **Advantages**:
- Supports Python/FastAPI
- Already deployed & running
- Database included
- Auto-deploy from Git

❌ **Limitations**:
- Plus paid tier
- Cold start if using free tier
- Single region (US)

### Cloudflare Worker As Proxy

✅ **Optional extras**:
- API caching
- CORS handling
- Rate limiting
- Request transformation
- Error handling

## Build Output Explanation

### After `npm run build`:

```
frontend/
├── .next/                    # Next.js output
│   ├── server/              # Server-side code
│   ├── static/              # Static files
│   │   ├── chunks/          # JavaScript bundled
│   │   └── css/             # Compiled CSS
│   ├── public/              # Public assets
│   └── ...
└── public/                  # Source public files
    ├── favicon.ico
    ├── images/
    └── ...
```

### Deployment:

- **Cloudflare Pages**: Takes `.next/` directory automatically
- **Static Export**: If using `output: 'export'` → Creates `.next/export/` with only static files

## Environment Variables

### Local Development

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_DEBUG_MODE=true
```

### Production (Cloudflare)

Set in Cloudflare Dashboard:

```
NEXT_PUBLIC_API_URL=https://movieb-rsoz.onrender.com/api/v1
NEXT_PUBLIC_DEBUG_MODE=false
```

**Important**: Only `NEXT_PUBLIC_*` variables are exposed to browser!

```javascript
// ❌ This won't work (secret)
process.env.SECRET_API_KEY

// ✅ This works (public)
process.env.NEXT_PUBLIC_API_URL
```

## Deployment Checklist

### Pre-Deployment

- [ ] Backend running on Render
- [ ] CORS enabled on backend
- [ ] Frontend builds locally: `npm run build`
- [ ] No Python files in output
- [ ] `.wranglerignore` exists in root
- [ ] `wrangler.toml` configured correctly
- [ ] See [CLOUDFLARE_DEPLOYMENT.md](./CLOUDFLARE_DEPLOYMENT.md) section 1

### Deployment

- [ ] Push code to GitHub (if using Pages)
- [ ] Or run Wrangler CLI deploy
- [ ] Or connect to Netlify/Vercel
- [ ] Set environment variables
- [ ] Wait for build to complete (5-10 min)

### Post-Deployment

- [ ] Frontend loads at public URL
- [ ] Search works
- [ ] Video playback works
- [ ] No console errors
- [ ] Check Cloudflare Analytics

### Ongoing A

- [ ] Monitor API response times
- [ ] Check error rates
- [ ] Review cache hit ratios
- [ ] Test from different regions
- [ ] Update docs as needed

## Troubleshooting Guide

### Symptom: Build fails with "Cannot find .venv"

**Cause**: Python dependencies being scanned  
**Fix**:
```bash
# Verify .wranglerignore exists and contains:
cat .wranglerignore | grep ".venv"

# If missing, create it:
echo ".venv/" >> .wranglerignore
echo "requirements.txt" >> .wranglerignore
```

### Symptom: "CORS error" in browser

**Cause**: Backend CORS not configured  
**Fix**:
```bash
# Test backend directly
curl -i https://movieb-rsoz.onrender.com/api/v1/search?q=test

# Should have headers:
# Access-Control-Allow-Origin: *
# (or your domain)
```

### Symptom: API calls return 404

**Cause**: Wrong API URL  
**Fix**:
```bash
# Check environment var
echo $NEXT_PUBLIC_API_URL

# Should be:
# https://movieb-rsoz.onrender.com/api/v1
# NOT with trailing slash!
```

### Symptom: Build succeeds but frontend doesn't load

**Cause**: Wrangler wrong root directory  
**Fix**:
1. Check `frontend/.next/` exists
2. Check `wrangler.toml`:
   ```toml
   [build]
   command = "npm run build"
   cwd = "./frontend"
   root_dir = ".next"
   ```

## Performance Optimization

### Frontend Optimizations

1. **Lazy Loading**
   ```typescript
   import dynamic from 'next/dynamic'
   const HeavyComponent = dynamic(() => import('./Heavy'))
   ```

2. **Image Optimization**
   ```typescript
   import Image from 'next/image'
   <Image src="..." width={300} height={400} />
   ```

3. **Code Splitting**
   - Automatic via Next.js
   - One bundle per page

### Caching Strategy

1. **Cloudflare Cache**
   - Browser: 1 hour
   - Cloudflare: 1 day
   - Backend: No cache (dynamic)

2. **API Caching** (optional with Worker)
   - GET requests: 30 minutes
   - POST requests: No cache
   - Streaming: No cache

## Security Considerations

✅ **Implemented**:
- HTTPS everywhere
- No sensitive data in frontend
- CORS configured
- Input validation on backend
- Auth tokens in secure storage

⚠️ **To do**:
- Enable rate limiting
- Add DDoS protection (Cloudflare)
- Regular security audits
- Keep dependencies updated

## Rollback Procedure

If deployment fails:

### Cloudflare Pages

1. Dashboard → Pages → movieb-frontend
2. Click "Deployments" tab
3. Find previous working deployment
4. Click "Rollback to this deployment"
5. Confirm

### Wrangler CLI

```bash
# List recent deployments
wrangler pages deployments list

# Redeploy previous version
wrangler pages deploy previous-commit:./frontend/.next
```

## Monitoring

### Real-Time Monitoring

- **Cloudflare Analytics**: cloudflare.com → Pages → Analytics
- **Render Logs**: render.com → Services → moviebox-api → Logs
- **Browser DevTools**: Check Network & Console tabs

### Metrics to Track

- **Response Time**: < 500ms
- **Error Rate**: < 1%
- **Cache Hit Ratio**: > 70%
- **Availability**: > 99.9%

## Cost Estimation

| Service | Tier | Cost | Notes |
|---------|------|------|-------|
| Cloudflare Pages | Free | $0 | 500 builds/mo |
| Render | Paid | ~$7/mo | 0.5 GB RAM |
| Domain | Varies | $10-15/yr | .com, .dev, etc |
| **Total** | | **~$7-8/mo** | Minimal |

## Next: Advanced Setup

### Optional: Cloudflare Worker Proxy

To add caching and rate limiting:

```bash
cd cloudflare-worker
wrangler deploy

# Update frontend API URL:
NEXT_PUBLIC_API_URL=https://api-proxy.your-domain.com/api/v1
```

See [cloudflare-worker/wrangler.toml](./cloudflare-worker/wrangler.toml)

### Optional: Custom Domain

1. Register domain (Namecheap, GoDaddy, etc)
2. Add to Cloudflare DNS
3. Cloudflare Pages → Custom Domain
4. Point to Pages project

### Optional: GitHub Actions (Auto-Deploy)

See [CLOUDFLARE_DEPLOYMENT.md](./CLOUDFLARE_DEPLOYMENT.md) section 9

## Related Documentation

- 📘 [CLOUDFLARE_DEPLOYMENT.md](./CLOUDFLARE_DEPLOYMENT.md) - Full deployment guide
- 🚀 [FRONTEND_QUICK_START.md](./FRONTEND_QUICK_START.md) - Developer guide
- 🔧 [FRONTEND_BUILD_CONFIG.md](./FRONTEND_BUILD_CONFIG.md) - Build configuration
- 📚 [FASTAPI_README.md](./FASTAPI_README.md) - API documentation
- 🏗️ [TECHNICAL_ARCHITECTURE.md](./TECHNICAL_ARCHITECTURE.md) - Architecture deep dive

## Support

For issues:

1. Check the [Troubleshooting Guide](#troubleshooting-guide) above
2. Review [CLOUDFLARE_DEPLOYMENT.md](./CLOUDFLARE_DEPLOYMENT.md)
3. Check logs:
   - Cloudflare: Dashboard → Pages → Build Logs
   - Render: Dashboard → Services → Logs
   - Browser: DevTools → Console, Network
4. Verify API endpoint: `curl https://movieb-rsoz.onrender.com/api/v1/search?q=test`

---

**Status**: ✅ Production Ready  
**Last Reviewed**: April 2026  
**Next Review**: May 2026
