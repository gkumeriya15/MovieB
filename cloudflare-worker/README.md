# MovieBox API - Cloudflare Worker

This is a Cloudflare Worker that acts as a proxy for the MovieBox API. It makes the API faster by caching responses.

## What It Does

- **Proxy**: Forwards requests to your backend API
- **Caching**: Saves API responses for 1 hour to make things faster
- **CORS**: Allows your website to talk to the API

## Setup

1. **Install Wrangler** (command line tool)
```bash
npm install -g wrangler
```

2. **Login to Cloudflare**
```bash
wrangler auth login
```

3. **Update Config**
   - Edit `wrangler.toml`
   - Change the backend URL to your Render API URL

4. **Deploy**
```bash
wrangler deploy
```

## API Routes

The worker forwards these requests to your backend:

- `/api/search` → Backend search
- `/api/details/{id}` → Backend details
- `/api/episodes/{id}` → Backend episodes
- `/api/stream/{id}` → Backend stream

## Caching

- GET requests are cached for 1 hour
- Cache status is shown in response headers
- You can skip cache by adding `Cache-Control: no-cache` header

## Environment Variables

Set in Cloudflare Worker:

- `BACKEND_URL`: Your Render backend URL

## Monitoring

Check cache performance and requests in Cloudflare dashboard.

## Custom Domain (Optional)

To use your own domain:

1. Add domain to Cloudflare
2. Create worker route: `api.yourdomain.com/*`

## Security

- Rate limiting can be set in Cloudflare WAF
- Add authentication if needed