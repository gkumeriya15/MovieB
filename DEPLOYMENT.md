# MovieBox API - Simple Deployment Guide

This guide shows how to deploy the MovieBox API backend and Cloudflare proxy.

## Backend Deployment (Render)

Render is a free service to run your API online.

### Steps

1. **Sign up for Render**
   - Go to [render.com](https://render.com)
   - Create free account

2. **Connect GitHub**
   - In Render dashboard, click "New" → "Web Service"
   - Connect your GitHub account
   - Select this repository

3. **Configure Service**
   - **Name**: moviebox-api
   - **Runtime**: Docker
   - **Dockerfile Path**: ./Dockerfile
   - **Port**: 8000
   - **Health Check Path**: /health

4. **Environment Variables**
   - Key: ENVIRONMENT
   - Value: production

5. **Deploy**
   - Click "Create Web Service"
   - Wait for build (5-10 minutes)
   - Get your API URL (like https://moviebox-api.onrender.com)

### Free Limits
- 750 hours per month
- 512 MB RAM
- 1 GB storage

## Cloudflare Worker Proxy

Cloudflare Worker makes your API faster and handles CORS.

### Setup

1. **Install Wrangler**
```bash
npm install -g wrangler
```

2. **Login to Cloudflare**
```bash
wrangler auth login
```

3. **Update Worker Config**
   - Edit `cloudflare-worker/wrangler.toml`
   - Change backend URL to your Render URL

4. **Deploy Worker**
```bash
cd cloudflare-worker
wrangler deploy
```

5. **Get Worker URL**
   - Note the URL (like https://moviebox-api.your-subdomain.workers.dev)

## Environment Variables

### Backend (Render)
```
ENVIRONMENT=production
```

### Worker (Cloudflare)
```toml
[vars]
BACKEND_URL = "https://your-render-deployment.onrender.com"
```

## Monitoring

### Backend
- Check logs in Render dashboard
- Monitor response times

### Worker
- View analytics in Cloudflare dashboard
- Check cache hit rates

## Security

### Rate Limiting
- Backend: 30 requests per minute per IP
- Change in `app/main.py` if needed

### CORS
- Allows all origins now
- For production, limit to your website URL

### HTTPS
- Both services provide HTTPS automatically

## Troubleshooting

### Backend Issues
- Check Render logs for errors
- Test locally: `uvicorn app.main:app --reload`

### Worker Issues
- Check Cloudflare Worker logs
- Verify backend URL is correct

### Common Errors
- **Import errors**: Check dependencies installed
- **Rate limiting**: Slow down requests
- **CORS errors**: Check origin settings

## Updates

### Backend
- Push code to GitHub
- Render auto-deploys if enabled
- Or manually trigger deploy

### Worker
- Update `cloudflare-worker/worker.js`
- Run `wrangler deploy`

## Support

- **Render**: [render.com/docs/support](https://render.com/docs/support)
- **Cloudflare**: [support.cloudflare.com](https://support.cloudflare.com)

## Production Checklist

- [ ] Backend deployed on Render
- [ ] Worker deployed on Cloudflare
- [ ] Environment variables set
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] CORS restricted
- [ ] Monitoring enabled
