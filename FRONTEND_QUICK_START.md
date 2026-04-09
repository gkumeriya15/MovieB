# MovieBox Frontend - Quick Start Guide

## TL;DR - 3 Minutes to Local Development

### 1. Install Dependencies (1 minute)

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=https://movieb-rsoz.onrender.com/api/v1
```

### 3. Start Development Server (1 minute)

```bash
npm run dev
```

Visit: http://localhost:3000

## What to Expect

- Frontend loads → Connects to Render backend
- Search bar works → Try searching "inception"
- Results display → Click to see details
- Video player appears → Streams from backend

## Available Features Today

✅ **Search** - Search for movies/shows  
✅ **Details** - View content information  
✅ **Episodes** - Browse TV episodes  
✅ **Streaming** - Play videos  
✅ **Responsive UI** - Mobile-friendly design  

## Useful Commands

```bash
# Development
npm run dev      # Start dev server (HMR enabled)

# Building
npm run build    # Build for production
npm run start    # Run production build

# Quality
npm run lint     # Check code style
npm run type-check  # TypeScript validation

# Deployment
npm run build    # Creates optimized output
# Output: .next/ directory (Next.js) or dist/ (with export)
```

## Project Structure

```
frontend/
├── src/
│   ├── pages/         # Routes (index, auth/, etc)
│   ├── components/    # React components (ContentCard, Navbar)
│   ├── lib/          # Utilities
│   │   ├── api.ts    # API client (all endpoints)
│   │   └── store.ts  # Zustand state management
│   └── styles/       # Global CSS
├── public/           # Static files
├── package.json      # Dependencies & scripts
├── next.config.js    # Next.js configuration
└── tsconfig.json     # TypeScript config
```

## API Integration

The frontend uses `/src/lib/api.ts` to call the Render backend:

```typescript
import apiClient from '@/lib/api'

// Search
const results = await apiClient.searchContent('inception')

// Details
const details = await apiClient.getContentDetails('movie-id')

// Episodes
const episodes = await apiClient.getEpisodes('show-id')

// Stream
const stream = await apiClient.getStreamLinks('id', pageUrl)
```

All requests go to: `process.env.NEXT_PUBLIC_API_URL`

## Backend API Endpoints

Your Render backend provides:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/search` | GET | Search for content |
| `/details/{id}` | GET | Get content details |
| `/episodes/{id}` | GET | List episodes |
| `/stream/{id}` | GET | Get stream URLs |
| `/stream/episode/{id}` | GET | Stream specific episode |

See [FASTAPI_README.md](./FASTAPI_README.md) for full API docs.

## Environment Variables

### Development (`.env.local`)

```env
# Points to local backend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Or use deployed Render backend
NEXT_PUBLIC_API_URL=https://movieb-rsoz.onrender.com/api/v1
```

### Production (Cloudflare Pages)

Set in Cloudflare Dashboard:

```
NEXT_PUBLIC_API_URL=https://movieb-rsoz.onrender.com/api/v1
```

## Troubleshooting Development

### "API calls not working"

1. Check `NEXT_PUBLIC_API_URL` in `.env.local`
2. Verify backend is running
3. Test endpoint directly:
   ```bash
   curl https://movieb-rsoz.onrender.com/api/v1/search?q=test
   ```

### "CORS errors in browser console"

✓ Backend should already have CORS enabled  
✓ Check for typos in API URL  
✓ Ensure backend is accessible  

### "Module not found error"

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### "TypeScript errors"

```bash
# Check types
npm run type-check

# Show all errors
npm run type-check -- --pretty
```

## Deployment to Cloudflare Pages

### Quick Deploy (1 command)

```bash
# Build first
npm run build

# Deploy to Cloudflare
npx wrangler pages deploy .next
```

### Or via GitHub Integration

1. Push to GitHub
2. Cloudflare Pages auto-deploys from `main` branch
3. See build status in Cloudflare Dashboard

See [CLOUDFLARE_DEPLOYMENT.md](./CLOUDFLARE_DEPLOYMENT.md) for full instructions.

## Development Tips

### Hot Module Replacement (HMR)

Changes auto-reload in browser (no refresh needed):

```bash
npm run dev
# Edit a component and watch it update
```

### TypeScript Support

Full type-checking during development:

```bash
npm run type-check
# Catches type errors before deployment
```

### Debug Mode

In browser developer tools:

```typescript
// Access API client directly
import apiClient from '@/lib/api'
apiClient.searchContent('test').then(r => console.log(r))
```

## Next Steps

1. ✅ Run `npm run dev`
2. ✅ Try searching for a movie
3. ✅ Click a result to see details
4. ✅ Explore the code
5. ✅ Make a change and see HMR work

## Performance Tips

### Image Optimization

```typescript
// ✅ Good - Uses Next.js optimization
import Image from 'next/image'
<Image src="/" alt="..." width={300} height={400} />

// ❌ Avoid - Not optimized
<img src="/" alt="..." />
```

### API Caching

```typescript
// Use Zustand store for state
const { data, setData } = useStore()

// Prevents redundant API calls
if (!data) {
  const results = await api.search(q)
  setData(results)
}
```

### Bundle Size

```bash
# Analyze bundle
npx next/bundle-analyzer

# Check dependencies
npm list
```

## Common Tasks

### Add New Page

```typescript
// Create: src/pages/new-page.tsx
export default function NewPage() {
  return <div>New page</div>
}

// Accessible at: /new-page
```

### Add New Component

```typescript
// Create: src/components/MyComponent.tsx
export function MyComponent() {
  return <div>My component</div>
}

// Use: import { MyComponent } from '@/components/MyComponent'
```

### Call API Endpoint

```typescript
// Use the ApiClient in src/lib/api.ts
const apiClient = require('@/lib/api').default

const data = await apiClient.searchContent('query')
console.log(data)
```

## Support

- **Docs**: See [CLOUDFLARE_DEPLOYMENT.md](./CLOUDFLARE_DEPLOYMENT.md)
- **API Docs**: See [FASTAPI_README.md](./FASTAPI_README.md)
- **Architecture**: See [TECHNICAL_ARCHITECTURE.md](./TECHNICAL_ARCHITECTURE.md)
- **Issues**: Check build logs and browser console

---

**Happy Coding!** 🎬
