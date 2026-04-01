# Episode Streaming API Documentation

## Overview

The Episode Streaming API provides secure access to TV series episode streams with automatic token expiration detection and intelligent caching.

## Quick Start

### 1. Search for a TV Series

```bash
curl "http://localhost:8000/api/v1/search?query=boyfriend&per_page=5"
```

Response:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "5203417860348986440",
        "title": "Boyfriend on Demand",
        "subject_type": "tv",
        "page_url": "/detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440"
      }
    ]
  }
}
```

### 2. Get Available Episodes

```bash
curl "http://localhost:8000/api/v1/episodes/detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440"
```

Response:
```json
{
  "success": true,
  "data": {
    "id": "5203417860348986440",
    "title": "Boyfriend on Demand",
    "total_seasons": 1,
    "total_episodes": 16,
    "seasons": [
      {
        "season_number": 1,
        "episode_count": 16,
        "episodes": [
          {
            "id": "s1e1",
            "title": "Episode 1",
            "episode_number": 1,
            "season_number": 1
          },
          {
            "id": "s1e2",
            "title": "Episode 2",
            "episode_number": 2,
            "season_number": 1
          }
        ]
      }
    ]
  }
}
```

### 3. Get Episode Streams

```bash
curl "http://localhost:8000/api/v1/stream/episode/s1e2?page_url=detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440"
```

Response:
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
        "url": "https://example.com/video.mp4?sign=abc123&t=1704067200",
        "size": 2147483648,
        "format": "mp4",
        "file_size_human": "2.0 GB",
        "expires_in_seconds": 86400,
        "expires_at": 1704067200
      },
      {
        "quality": "720p",
        "url": "https://example.com/video-720p.mp4?sign=xyz789&t=1704067200",
        "size": 1073741824,
        "format": "mp4",
        "file_size_human": "1.0 GB",
        "expires_in_seconds": 86400,
        "expires_at": 1704067200
      }
    ],
    "best_quality": "1080p"
  }
}
```

## API Reference

### GET /api/v1/stream/episode/{episode_id}

Get streaming links for a specific TV series episode.

**Path Parameters:**
- `episode_id` (string, required): Episode identifier in format `s{season}e{episode}`
  - Examples: `s1e1`, `s2e5`, `s10e12`

**Query Parameters:**
- `page_url` (string, required): TV series page URL identifier
  - Accepts full URL: `https://moviebox.ph/detail/slug?id=123`
  - Accepts relative URL: `/detail/slug?id=123`
  - Accepts numeric ID: `123`

**Response (Success):**
```json
{
  "success": true,
  "data": {
    "id": "subject_id",
    "title": "Series Title",
    "type": "tv_series",
    "episode_id": "s1e2",
    "season": 1,
    "episode": 2,
    "streams": [
      {
        "quality": "1080p",
        "url": "https://...",
        "size": 2147483648,
        "format": "mp4",
        "file_size_human": "2.0 GB",
        "expires_in_seconds": 86400,
        "expires_at": 1704067200
      }
    ],
    "best_quality": "1080p",
    "warning": "1 stream(s) may have expired tokens. Consider re-fetching."
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Invalid episode_id format. Expected 's{season}e{episode}', got: invalid"
}
```

**Error Codes:**
- `404`: Episode not found or invalid page_url
- `400`: Invalid episode_id format
- `422`: Missing required query parameter (page_url)

## URL Format Normalization

The API intelligently normalizes different URL formats:

### Supported Formats

1. **Full URL**
   ```
   https://moviebox.ph/detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440
   ```
   Extracted: `slug = boyfriend-on-demand-hindi-OXFhFpXHnc6`, `subject_id = 5203417860348986440`

2. **Relative URL with Query**
   ```
   /detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440
   ```
   Extracted: `slug = boyfriend-on-demand-hindi-OXFhFpXHnc6`, `subject_id = 5203417860348986440`

3. **Relative URL without Leading Slash**
   ```
   detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440
   ```
   Extracted: `slug = boyfriend-on-demand-hindi-OXFhFpXHnc6`, `subject_id = 5203417860348986440`

4. **Numeric ID Only**
   ```
   5203417860348986440
   ```
   Normalized: `/detail/5203417860348986440?id=5203417860348986440`

## Token Expiration Handling

Stream URLs contain expiration tokens that are automatically detected and reported:

### How It Works

1. **Token Detection**: Automatically extracts `t` parameter from stream URLs
2. **Expiration Calculation**: Compares against current timestamp
3. **Validity Period**: Shows remaining seconds until expiration
4. **Buffer Time**: Considers URLs expired 5 minutes before actual expiration
5. **Warnings**: Includes warnings if any streams may have expired

### Example Response with Expiration

```json
{
  "streams": [
    {
      "quality": "1080p",
      "url": "https://example.com/video.mp4?sign=xxx&t=1704067200",
      "expires_in_seconds": 86400,
      "expires_at": 1704067200
    }
  ],
  "warning": "1 stream(s) may have expired tokens. Consider re-fetching."
}
```

### Handling Expired Streams

If a stream URL is expired:
1. The warning field will include count of expired streams
2. Re-fetch the episode streams by calling the endpoint again
3. New tokens will be generated by the scraper
4. Updated URLs with new expiration times will be returned

## Caching Strategy

The API implements intelligent caching to improve performance:

- **Cache Duration**: 30 minutes for TV episodes
- **Cache Key**: `episode:{slug}:{subject_id}:{season}:{episode}`
- **Auto-Invalidation**: Cache automatically expires after TTL
- **Manual Refresh**: Call endpoint again to fetch fresh streams

### Benefits

- Reduced scraping requests
- Faster response times
- Lower resource usage on remote servers
- Concurrent request optimization

### Cache Response

Cached responses include `"cached": true` in the response for debugging:

```json
{
  "success": true,
  "data": { ... },
  "cached": true
}
```

## Episode ID Format

Episode IDs follow the standard TV notation:

```
s{season_number}e{episode_number}
```

**Valid Examples:**
- `s1e1` → Season 1, Episode 1
- `s2e5` → Season 2, Episode 5
- `s10e12` → Season 10, Episode 12
- `s01e01` → Also valid (leading zeros)

**Invalid Examples:**
- `1x2` ❌ (Use 's' and 'e' notation)
- `episode1` ❌ (Not in standard format)
- `s1-e2` ❌ (No hyphens)

## Error Handling

### Invalid Episode ID

```bash
curl "http://localhost:8000/api/v1/stream/episode/invalid?page_url=..."
```

**Response:**
```json
{
  "success": false,
  "error": "Invalid episode_id format. Expected 's{season}e{episode}', got: invalid"
}
```

### Invalid or Missing page_url

```bash
curl "http://localhost:8000/api/v1/stream/episode/s1e1"
```

**Response:**
```json
{
  "success": false,
  "error": "page_url is required (query parameter)"
}
```

### Item Not Found

```bash
curl "http://localhost:8000/api/v1/stream/episode/s1e1?page_url=nonexistent"
```

**Response:**
```json
{
  "success": false,
  "error": "Invalid page_url or item not found"
}
```

### Item is Not a TV Series

If you call the endpoint with a movie ID instead of series ID:

```json
{
  "success": false,
  "error": "Item is not a TV series (type: movie)"
}
```

### No Streams Available

```json
{
  "success": true,
  "data": {
    "episode_id": "s1e2",
    "streams": [],
    "message": "Streaming links not available: reason..."
  }
}
```

## Rate Limiting

- **Limit**: 10 requests per minute
- **Applied to**: Streaming endpoints (sensitive resources)
- **Headers**: Includes `X-RateLimit-*` headers in response

## Best Practices

1. **Cache Results Locally**: Store stream URLs in your client to reduce API calls
2. **Check Expiration**: Always check `expires_at` before streaming
3. **Refresh on Expiration**: Re-fetch streams when tokens approach expiration
4. **Handle Errors Gracefully**: Implement retry logic for failed requests
5. **Log Requests**: Track page_url and episode_id for debugging

## Example Client Implementation

### Python

```python
import requests
import time

class EpisodeStreamer:
    BASE_URL = "http://localhost:8000/api/v1"
    
    def get_episode_streams(self, series_id, episode_id):
        """Get streams for episode, with expiration checking"""
        url = f"{self.BASE_URL}/stream/episode/{episode_id}"
        
        # Get streams
        response = requests.get(url, params={"page_url": series_id})
        response.raise_for_status()
        data = response.json()
        
        if not data["success"]:
            raise Exception(f"Failed: {data['error']}")
        
        streams = data["data"]["streams"]
        
        # Check for expiration warnings
        if "warning" in data["data"]:
            print(f"⚠️ {data['data']['warning']}")
        
        # Filter unexpired streams
        now = time.time()
        valid_streams = [
            s for s in streams 
            if "expires_at" not in s or s["expires_at"] > now
        ]
        
        return valid_streams

# Usage
streamer = EpisodeStreamer()
series_id = "/detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440"
streams = streamer.get_episode_streams(series_id, "s1e2")
print(f"👍 Found {len(streams)} valid streams")
```

### JavaScript

```javascript
class EpisodeStreamer {
  constructor(baseUrl = "http://localhost:8000/api/v1") {
    this.baseUrl = baseUrl;
  }

  async getEpisodeStreams(seriesId, episodeId) {
    const url = `${this.baseUrl}/stream/episode/${episodeId}`;
    
    const response = await fetch(url, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      params: { page_url: seriesId }
    });

    const data = await response.json();
    
    if (!data.success) {
      throw new Error(`Failed: ${data.error}`);
    }

    const streams = data.data.streams;
    
    if (data.data.warning) {
      console.warn(`⚠️ ${data.data.warning}`);
    }

    // Filter unexpired streams
    const now = Math.floor(Date.now() / 1000);
    const validStreams = streams.filter(
      s => !s.expires_at || s.expires_at > now
    );

    return validStreams;
  }
}

// Usage
const streamer = new EpisodeStreamer();
const seriesId = "/detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440";
const streams = await streamer.getEpisodeStreams(seriesId, "s1e2");
console.log(`👍 Found ${streams.length} valid streams`);
```

## Debugging

Enable detailed logging by checking the API response for:

1. **Extracted URL Components**: Logged as DEBUG level
2. **Cache Operations**: Shows hits/misses
3. **Token Expiration**: Logged with timestamp comparisons
4. **Stream Extraction**: Lists quality and format details

## FAQ

**Q: Why am I getting "Invalid page_url" errors?**
A: The page_url must be in a recognized format. Try:
- Full URL from search results
- URL with both slug AND id parameter
- Just the numeric subject_id

**Q: Can I use just the subject_id?**
A: Yes! Just pass the numeric ID as page_url: `?page_url=5203417860348986440`

**Q: How long are stream URLs valid?**
A: Check the `expires_in_seconds` field in the response. Most streams are valid for 24 hours.

**Q: What if a stream has expired?**
A: Call the endpoint again to get fresh tokens. The cache will be automatically refreshed.

**Q: Do you support HLS streams?**
A: Currently, the API returns direct MP4 links. HLS support may be added in future versions.

## Changelog

### Version 1.0.0 (Current)
- Episode streaming endpoint
- URL normalization for flexible input formats
- Token expiration detection and reporting
- Intelligent 30-minute caching
- Enhanced error messages
- Comprehensive logging
- Rate limiting (10/minute)
