# Quick Start - Episode Streaming API

## Overview

Get TV series episode streams with automatic token expiration handling in 3 simple steps.

## Step 1: Search for a TV Series

```bash
curl "http://localhost:8000/api/v1/search?query=boyfriend&per_page=5"
```

Response:
```json
{
  "data": {
    "items": [
      {
        "id": "5203417860348986440",
        "title": "Boyfriend on Demand",
        "page_url": "/detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440"
      }
    ]
  }
}
```

**Save**: `page_url` and number of seasons from this response

---

## Step 2: Get Available Episodes

```bash
curl "http://localhost:8000/api/v1/episodes/detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440"
```

Response shows seasons and episodes:
```json
{
  "data": {
    "seasons": [
      {
        "season_number": 1,
        "episodes": [
          {"id": "s1e1", "title": "Episode 1"},
          {"id": "s1e2", "title": "Episode 2"}
        ]
      }
    ]
  }
}
```

**Copy**: The episode `id` (e.g., `s1e2`)

---

## Step 3: Get Episode Streams

```bash
curl "http://localhost:8000/api/v1/stream/episode/s1e2?page_url=detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440"
```

Response:
```json
{
  "success": true,
  "data": {
    "episode_id": "s1e2",
    "streams": [
      {
        "quality": "1080p",
        "url": "https://example.com/video.mp4?sign=abc&t=1704067200",
        "format": "mp4",
        "expires_in_seconds": 86400,
        "expires_at": 1704067200
      }
    ],
    "best_quality": "1080p"
  }
}
```

**Use**: The stream `url` directly or check expiration!

---

## What's New?

### 1. Flexible URL Formats

All these work as `page_url`:
```
- Full URL: https://moviebox.ph/detail/slug?id=123
- Relative: /detail/slug?id=123
- No slash: detail/slug?id=123
- Just ID: 123
```

### 2. Token Expiration Tracking

Streams include expiration info:
```json
{
  "url": "...",
  "expires_in_seconds": 86400,
  "expires_at": 1704067200
}
```

Check before streaming! Re-fetch if expired.

### 3. Automatic Caching

Same episode requests are cached for 30 minutes:
- Faster responses
- Reduced server load
- Response includes `"cached": true` if cached

---

## Common Errors & Fixes

### ❌ "Invalid episode_id format"
```bash
# ❌ WRONG
curl "http://localhost:8000/api/v1/stream/episode/1"

# ✅ CORRECT
curl "http://localhost:8000/api/v1/stream/episode/s1e1"
```

### ❌ "Invalid page_url"
```bash
# ❌ MISSING ID PARAMETER
curl "http://localhost:8000/api/v1/stream/episode/s1e2?page_url=detail/boyfriend"

# ✅ WITH ID PARAMETER
curl "http://localhost:8000/api/v1/stream/episode/s1e2?page_url=detail/boyfriend?id=123"
```

### ❌ "Item is not a TV series"
```bash
# You used a movie ID instead of series ID
# Make sure episodes endpoint shows {season: 1, episode: 1} format
```

---

## Python Example

```python
import requests
import time

def stream_episode(series_id, episode_id):
    # Get streams
    resp = requests.get(
        f"http://localhost:8000/api/v1/stream/episode/{episode_id}",
        params={"page_url": series_id}
    ).json()
    
    if not resp["success"]:
        print(f"Error: {resp['error']}")
        return
    
    # Check expiration
    now = time.time()
    for stream in resp["data"]["streams"]:
        if stream.get("expires_at", now + 1) < now:
            print(f"⚠️ Stream expired: {stream['quality']}")
            continue
        
        print(f"✅ {stream['quality']}: {stream['url'][:50]}...")
        print(f"   Expires in: {stream.get('expires_in_seconds', '?')}s")

# Usage
stream_episode(
    "/detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440",
    "s1e2"
)
```

---

## JavaScript Example

```javascript
async function getEpisodeStreams(seriesId, episodeId) {
  const response = await fetch(
    `/api/v1/stream/episode/${episodeId}?page_url=${encodeURIComponent(seriesId)}`
  );
  
  const data = await response.json();
  
  if (!data.success) {
    console.error(`Error: ${data.error}`);
    return;
  }
  
  const now = Math.floor(Date.now() / 1000);
  
  data.data.streams.forEach(stream => {
    if (stream.expires_at && stream.expires_at < now) {
      console.warn(`⚠️ Stream expired: ${stream.quality}`);
      return;
    }
    
    console.log(`✅ ${stream.quality}: ${stream.url.substring(0, 50)}...`);
    console.log(`   Expires in: ${stream.expires_in_seconds}s`);
  });
}

// Usage
getEpisodeStreams(
  "/detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440",
  "s1e2"
);
```

---

## API Reference (Quick)

### Search TV Series
```
GET /api/v1/search?query=name&per_page=24
```

### Get Episodes
```
GET /api/v1/episodes/{page_url}
```

### Get Episode Streams ⭐ NEW
```
GET /api/v1/stream/episode/{episode_id}?page_url={series_url}

Parameters:
- episode_id: s1e1, s2e5, s10e12, etc.
- page_url: Series URL from search (any format accepted)

Response includes:
- streams[].url: The actual video URL
- streams[].expires_at: Unix timestamp when URL expires
- streams[].expires_in_seconds: Seconds until expiration
```

---

## Rate Limiting

**Limit**: 10 requests per minute on streaming endpoints

If you exceed the limit:
```json
{
  "detail": "rate limit exceeded"
}
```

Wait a minute and try again.

---

## Troubleshooting

### How long are streams valid?
Check the `expires_in_seconds` field. Usually 24 hours.

### Stream expired, what do I do?
Call the endpoint again to get fresh tokens.

### Can I cache streams?
Yes! Use the `id` from the response as a cache key. Cache for up to 30 minutes.

### Do you have HLS streams?
Currently MP4 only. More formats coming soon!

### What if I get "No streaming links available"?
The episode exists but no streams are available. Try again later.

---

## Full Documentation

See [EPISODE_STREAMING_API.md](EPISODE_STREAMING_API.md) for complete API reference with:
- Error codes and meanings
- Detailed response examples
- Advanced caching strategies
- Client implementation patterns
- FAQ section

---

## Next Steps

1. ✅ Search for a series
2. ✅ Get available episodes  
3. ✅ Stream an episode
4. 📖 Read [EPISODE_STREAMING_API.md](EPISODE_STREAMING_API.md) for advanced usage
5. 🐛 Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for technical details
