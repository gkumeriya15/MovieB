# MovieBox Frontend Build Configuration

This file contains the build configuration for Cloudflare Pages deployment.

## Key Files

### Root Configuration Files

- **wrangler.toml** - Cloudflare Pages configuration (root)
- **.wranglerignore** - Files to exclude from Cloudflare build
- **frontend/next.config.js** - Next.js build configuration
- **frontend/package.json** - Dependencies and build scripts
- **frontend/tsconfig.json** - TypeScript configuration

### Frontend Structure

```
frontend/
├── package.json              # Dependencies and scripts
├── next.config.js           # Next.js configuration
├── tsconfig.json            # TypeScript config
├── tailwind.config.ts       # Tailwind CSS config
├── .env.local              # Environment variables (local)
├── .env.example            # Environment template
└── src/
    ├── pages/              # Next.js pages (routes)
    ├── components/         # React components
    ├── lib/               # Utilities (api.ts, store.ts, etc)
    └── styles/            # Global styles
```

## Build Process

### Development Build

```bash
cd frontend
npm install
npm run dev
# Starts at http://localhost:3000
```

### Production Build

```bash
cd frontend
npm run build
npm run start
# Or... export for static hosting:
npm run build
# Output: .next/ or dist/ depending on config
```

### Cloudflare Pages Build

Environment: Cloudflare automatically runs:

```bash
npm install
npm run build  # (in frontend directory)
```

Output directory: `.next` (or configured in wrangler.toml)

## Environment Variables

### Development (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Production (Cloudflare Pages)

Set in Cloudflare Dashboard → Pages → Settings → Environment variables:

```
NEXT_PUBLIC_API_URL=https://movieb-rsoz.onrender.com/api/v1
```

## Important: Python Exclusion

Cloudflare Pages only supports static frontends and JavaScript. Python files must be excluded:

### .wranglerignore

The `.wranglerignore` file prevents Python dependencies from being uploaded:

```
.venv/
.venv-1/
requirements.txt
pyproject.toml
backend/
src/
... (see .wranglerignore for full list)
```

### Root wrangler.toml

```toml
[build]
command = "npm run build"
cwd = "./frontend"
root_dir = ".next"
```

This ensures:
1. Builds ONLY from `/frontend` directory
2. Ignores all Python files
3. Outputs to `/frontend/.next`
4. No Python interpreter needed

## API Integration

The frontend communicates with the Render backend via REST API:

```typescript
// src/lib/api.ts - Main API client

const API_URL = process.env.NEXT_PUBLIC_API_URL
// Points to: https://movieb-rsoz.onrender.com/api/v1

// Usage:
const results = await apiClient.searchContent('Inception')
const details = await apiClient.getContentDetails(id)
const episodes = await apiClient.getEpisodes(id)
const stream = await apiClient.getStreamLinks(id, pageUrl)
```

## Build Troubleshooting

### "Cannot find .venv" Error

**Cause**: Python virtual environment is being included in build

**Fix**:
1. Verify `.wranglerignore` exists in root
2. Check that `root_dir` in `wrangler.toml` points to `.next` (not root)
3. Run: `wrangler pages deploy --project-name=movieb-frontend`

### Build Fails with "npm not found"

**Fix**: 
1. Ensure `package.json` is in correct directory (`frontend/`)
2. Check `cwd` in `wrangler.toml` is set to `"./frontend"`

### API Calls Fail with CORS Error

**Fix**:
1. Verify backend supports CORS:
   ```python
   app.add_middleware(CORSMiddleware, allow_origins=["*"])
   ```
2. Check `NEXT_PUBLIC_API_URL` is set correctly
3. Use Cloudflare Worker as proxy (optional)

## Build Scripts

Defined in `frontend/package.json`:

```json
{
  "scripts": {
    "dev": "next dev",           // Local development
    "build": "next build",       // Production build
    "start": "next start",       // Run built app
    "lint": "next lint",         // Lint JS/TS
    "type-check": "tsc --noEmit" // Type checking
  }
}
```

## Dependencies

### Production Dependencies

- `next@^14.0.0` - React framework
- `react@^18.2.0` - UI library
- `react-dom@^18.2.0` - DOM rendering
- `axios@^1.6.0` - HTTP client
- `zustand@^4.4.0` - State management
- `tailwindcss@^3.3.0` - CSS framework
- `react-player@^2.13.0` - Video player

### Dev Dependencies

- `typescript@^5.3.0` - TypeScript
- `eslint@^8.52.0` - Linting
- `@types/react@^18.2.0` - Type definitions

## Output Files

After `npm run build`:

- **JavaScript**: Minified, optimized bundles
- **CSS**: Tailwind CSS compiled
- **HTML**: Server-side rendered pages
- **Images**: Optimized formats
- **Static assets**: Images, fonts, etc.

With static export (`output: 'export'`):

- **Location**: `frontend/.next/export/`
- **Files**: `.html`, `.css`, `.js`, images
- **Deployment**: Upload entire directory to CDN

## Version Compatibility

- **Node.js**: 18.0.0 or higher
- **npm**: 9.0.0 or higher
- **Next.js**: 14.0.0+
- **React**: 18.2.0+
- **TypeScript**: 5.3.0+

## Deployment Checklist

- [ ] `.wranglerignore` file exists in root
- [ ] `wrangler.toml` in root with correct `cwd` and `root_dir`
- [ ] `frontend/package.json` has build scripts
- [ ] `NEXT_PUBLIC_API_URL` environment variable set
- [ ] No Python files in build output
- [ ] `npm run build` succeeds locally
- [ ] Frontend loads and API calls work
- [ ] Cloudflare Pages build logs show no errors

---

For full deployment instructions, see [CLOUDFLARE_DEPLOYMENT.md](./CLOUDFLARE_DEPLOYMENT.md).
