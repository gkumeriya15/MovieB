# MovieBox API - FastAPI Backend

A production-ready REST API for MovieBox built with FastAPI.

## Features

- 🔍 **Search**: Search movies and TV series
- 📋 **Details**: Get detailed information about movies/TV series
- 📺 **Episodes**: Get episode lists for TV series
- 🎬 **Stream**: Get streaming/download links
- 🏥 **Health Check**: API health monitoring
- 📚 **Swagger Docs**: Interactive API documentation at `/docs`

## API Endpoints

### Search
```
GET /api/v1/search?q=naruto&type=ALL&page=1&per_page=24
```

### Details
```
GET /api/v1/details/{item_id}
```

### Episodes
```
GET /api/v1/episodes/{item_id}
```

### Stream (Movies)
```
GET /api/v1/stream/{item_id}
```

Get streaming/download links for movies. TV series are not supported - use the episode streaming endpoint instead.

### Episode Stream (TV Series)
```
GET /api/v1/stream/episode/{episode_id}?page_url={series_page_url}
```

Get streaming/download links for specific TV series episodes with advanced features:
- ✅ **URL Normalization**: Accepts various URL formats (full URL, relative URL, numeric ID)
- ✅ **Token Expiration Detection**: Automatically detects and reports expired stream tokens
- ✅ **Intelligent Caching**: Caches results for 30 minutes with automatic refresh
- ✅ **Detailed Logging**: Full debugging information for troubleshooting

**Parameters:**
- `episode_id`: Episode identifier in format `s{season}e{episode}` (e.g., `s1e1`, `s2e5`)
- `page_url`: TV series page URL identifier (query parameter)
  - Accepts: Full URL (`https://moviebox.ph/detail/slug?id=123`)
  - Accepts: Relative URL (`/detail/slug?id=123`)
  - Accepts: Numeric ID (`123`)

**Response Example:**
```json
{
  "success": true,
  "data": {
    "id": "5203417860348986440",
    "title": "Boyfriend on Demand",
    "type": "tv_series",
    "episode_id": "s1e2",
    "season": 1,
    "episode": 2,
    "streams": [
      {
        "quality": "1080p",
        "url": "https://example.com/video.mp4?sign=xxx&t=1704067200",
        "size": 2147483648,
        "format": "mp4",
        "file_size_human": "2.0 GB",
        "expires_in_seconds": 86400,
        "expires_at": 1704067200
      }
    ],
    "best_quality": "1080p"
  }
}
```

For full documentation, see [EPISODE_STREAMING_API.md](EPISODE_STREAMING_API.md)

### Health Check
```
GET /health
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install the local moviebox-api package:
```bash
pip install -e .
```

## Running the Application

### Development
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Docker

Build and run with Docker:
```bash
docker build -t moviebox-api .
docker run -p 8000:8000 moviebox-api
```

## Deployment

### Render

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set the following:
   - **Runtime**: Docker
   - **Build Command**: (leave empty)
   - **Start Command**: (leave empty, uses Dockerfile CMD)

### Environment Variables

Add these environment variables in your deployment platform:

- `ENVIRONMENT`: `production` (optional)

## API Response Format

All endpoints return JSON responses with the following structure:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

On error:
```json
{
  "success": false,
  "error": "Error message"
}
```

## CORS

The API allows all origins by default. For production, configure specific allowed origins in `app/main.py`.

## Error Handling

- 400: Bad Request (invalid parameters)
- 404: Not Found (item not found)
- 500: Internal Server Error

## Rate Limiting

Basic rate limiting is implemented. Configure as needed for production use.