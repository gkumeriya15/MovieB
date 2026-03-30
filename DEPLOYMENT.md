# MovieBox API - Deployment Guide

This guide covers deploying the MovieBox FastAPI backend and Cloudflare Worker proxy.

## 🚀 Backend Deployment (Render)

### Prerequisites
- GitHub account
- Render account (free tier available)

### Steps

1. **Fork/Clone this repository**
   ```bash
   git clone https://github.com/your-username/moviebox-api.git
   cd moviebox-api
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

3. **Configure Build Settings**
   - **Runtime**: Docker
   - **Build Command**: (leave empty)
   - **Start Command**: (leave empty, uses Dockerfile CMD)

4. **Environment Variables** (Optional)
   ```bash
   ENVIRONMENT=production
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note the service URL (e.g., `https://moviebox-api.onrender.com`)

### Render Free Tier Limits
- 750 hours/month
- 512 MB RAM
- 1 GB storage

## ☁️ Cloudflare Worker Proxy

### Prerequisites
- Cloudflare account
- Wrangler CLI installed

### Setup

1. **Install Wrangler**
   ```bash
   npm install -g wrangler
   ```

2. **Login to Cloudflare**
   ```bash
   wrangler auth login
   ```

3. **Configure Worker**
   - Edit `cloudflare-worker/wrangler.toml`
   - Replace `your-render-api.onrender.com` with your Render URL

4. **Deploy Worker**
   ```bash
   cd cloudflare-worker
   wrangler deploy
   ```

5. **Get Worker URL**
   - Note the deployed worker URL (e.g., `https://moviebox-api.your-subdomain.workers.dev`)

### Custom Domain (Optional)

1. **Add Domain to Cloudflare**
   - Go to Cloudflare Dashboard
   - Add your domain
   - Update DNS nameservers

2. **Create Worker Route**
   ```bash
   wrangler routes put "api.yourdomain.com/*" --script moviebox-api-proxy
   ```

## 🔧 Environment Variables

### Backend (Render)
```bash
ENVIRONMENT=production
```

### Worker (Cloudflare)
```toml
[vars]
BACKEND_URL = "https://your-render-deployment.onrender.com"
```

## 📊 Monitoring

### Backend (Render)
- View logs in Render Dashboard
- Monitor response times and errors

### Worker (Cloudflare)
- Analytics in Cloudflare Dashboard
- Cache hit/miss ratios
- Request/response metrics

## 🔒 Security Considerations

### Rate Limiting
- Backend: 30 requests/minute per IP
- Configure in `app/main.py`

### CORS
- Currently allows all origins
- Restrict in production:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["https://your-frontend-domain.com"],
      allow_credentials=True,
      allow_methods=["GET"],
      allow_headers=["*"],
  )
  ```

### HTTPS
- Both Render and Cloudflare provide HTTPS automatically

## 🚨 Troubleshooting

### Backend Issues
- Check Render logs for errors
- Verify environment variables
- Test locally: `uvicorn app.main:app --reload`

### Worker Issues
- Check Cloudflare Worker logs
- Verify backend URL is correct
- Test worker: `wrangler tail`

### Common Errors
- **Import errors**: Ensure all dependencies are installed
- **Rate limiting**: Reduce request frequency
- **CORS errors**: Check origin settings

## 📈 Scaling

### Backend Scaling
- Upgrade Render plan for more resources
- Consider load balancer for multiple instances

### Worker Scaling
- Cloudflare Workers scale automatically
- No additional configuration needed

## 🔄 Updates

### Backend Updates
1. Push changes to GitHub
2. Render auto-deploys (if enabled)
3. Or manually trigger deployment

### Worker Updates
1. Update `cloudflare-worker/worker.js`
2. Run `wrangler deploy`

## 📞 Support

- **Render**: [Render Support](https://render.com/docs/support)
- **Cloudflare**: [Cloudflare Support](https://support.cloudflare.com/)
- **Issues**: [GitHub Issues](https://github.com/Simatwa/moviebox-api/issues)

## 🎯 Production Checklist

- [ ] Backend deployed on Render
- [ ] Worker deployed on Cloudflare
- [ ] Environment variables configured
- [ ] Custom domain (optional)
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] CORS restricted
- [ ] Monitoring enabled
- [ ] Error handling tested
- [ ] API documentation accessible (`/docs`)