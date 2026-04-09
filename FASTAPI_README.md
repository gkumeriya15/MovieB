# MovieBox API - Simple API Guide

This is the backend API that powers the MovieBox service. It's built with FastAPI and runs on Render.

## What is This API?

The API is like a bridge between your website and moviebox.ph. It helps you:
- Search for movies and TV shows
- Get movie details
- Get TV show episodes
- Get streaming links

## API Endpoints (Simple List)

### Search
```
GET /api/v1/search?q=naruto&type=ALL&page=1&per_page=24
```
Find movies/TV shows by name.

### Details
```
GET /api/v1/details/{item_id}
```
Get info about a specific movie or TV show.

### Episodes
```
GET /api/v1/episodes/{item_id}
```
Get list of episodes for a TV show.

### Stream Movie
```
GET /api/v1/stream/{item_id}
```
Get download/stream link for a movie.

### Stream Episode
```
GET /api/v1/stream/episode/{episode_id}?page_url={series_page_url}
```
Get download/stream link for a TV episode.

**What is episode_id?** Like `s1e1` (Season 1 Episode 1)

**What is page_url?** The web address of the TV show page

## Response Format

All responses look like this:

```json
{
  "success": true,
  "data": { ... your data ... },
  "error": null
}
```

If there's an error:
```json
{
  "success": false,
  "error": "Error message"
}
```

## Health Check

```
GET /health
```

This checks if the API is working. Returns "OK" if healthy.

## Running Locally

For testing, you can run the API on your computer:

1. Install Python
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

## Deployment

The API is deployed on Render using Docker. See main README for setup.

## CORS

The API allows requests from any website. For security, you can limit this in `app/main.py`.

## Errors

- 400: Bad request (wrong parameters)
- 404: Not found (movie/show not found)
- 500: Server error

## Interactive Docs

When running locally, visit `/docs` to see interactive API documentation.