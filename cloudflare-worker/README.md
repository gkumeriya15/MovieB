# MovieBox API - Cloudflare Worker Proxy

A Cloudflare Worker that acts as a proxy and caching layer for the MovieBox FastAPI backend.

## Features

- 🚀 **Proxy**: Forwards API requests to your backend
- 💾 **Caching**: Caches API responses for 1 hour
- 🌐 **CORS**: Handles CORS headers
- 📊 **Analytics**: Cache hit/miss tracking
- 🛡️ **Error Handling**: Graceful error responses

## Setup

1. Install Wrangler CLI:
```bash
npm install -g wrangler
```

2. Login to Cloudflare:
```bash
wrangler auth login
```

3. Update the backend URL in `wrangler.toml`:
```toml
[vars]
BACKEND_URL = "https://your-render-deployment.onrender.com"
```

## Deployment

Deploy to Cloudflare Workers:
```bash
wrangler deploy
```

## API Routes

The worker proxies these routes from your backend:

- `/api/search` → Backend `/api/v1/search`
- `/api/details/{id}` → Backend `/api/v1/details/{id}`
- `/api/episodes/{id}` → Backend `/api/v1/episodes/{id}`
- `/api/stream/{id}` → Backend `/api/v1/stream/{id}`

## Caching

- GET requests are cached for 1 hour
- Cache status is indicated in `X-Cache-Status` header
- Cache can be bypassed by adding `Cache-Control: no-cache` header

## Environment Variables

Set these in your Cloudflare Worker environment:

- `BACKEND_URL`: Your Render backend URL

## Monitoring

Check cache performance and request metrics in the Cloudflare dashboard.

## Custom Domain (Optional)

To use a custom domain:

1. Add your domain to Cloudflare
2. Create a Worker route: `api.yourdomain.com/*`
3. Update DNS and SSL settings

## Security

- Rate limiting can be configured in Cloudflare WAF
- Consider adding authentication headers if needed
- Monitor for abuse in Cloudflare Analytics