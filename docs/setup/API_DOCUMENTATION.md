# API Documentation

## Overview

StreamBox API is a RESTful API built with FastAPI that provides endpoints for authentication, content management, and user interactions.

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints

### Register User
**POST** `/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "User Name"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "User Name",
  "role": "user",
  "is_active": true,
  "is_email_verified": false,
  "created_at": "2024-01-01T00:00:00"
}
```

**Status Codes:**
- 201: User created successfully
- 400: Email or username already registered
- 422: Validation error

---

### Login
**POST** `/auth/login`

Authenticate user and receive tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Status Codes:**
- 200: Login successful
- 401: Invalid credentials
- 403: User inactive

---

### Refresh Token
**POST** `/auth/refresh`

Get a new access token using a refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGc..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

### Get Current User
**GET** `/auth/me`

Get authenticated user's information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "User Name",
  "avatar_url": null,
  "role": "user",
  "is_active": true,
  "is_email_verified": false,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

---

## Content Endpoints

### List Movies
**GET** `/content/movies`

Get paginated list of movies.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20, max: 100)
- `sort_by` (string): Sort field - created_at, rating, view_count (default: created_at)

**Response:**
```json
[
  {
    "id": 1,
    "title": "Movie Title",
    "slug": "movie-title",
    "description": "Movie description",
    "content_type": "movie",
    "poster_url": "http://...",
    "rating": 8.5,
    "is_featured": true,
    "is_active": true,
    "view_count": 1000,
    "created_at": "2024-01-01T00:00:00",
    "genres": [],
    "categories": []
  }
]
```

---

### List TV Shows
**GET** `/content/tv-shows`

Get paginated list of TV shows.

**Same parameters and response as `/content/movies`**

---

### List Anime
**GET** `/content/anime`

Get paginated list of anime.

**Same parameters and response as `/content/movies`**

---

### Get Featured Content
**GET** `/content/featured`

Get featured/homepage content.

**Query Parameters:**
- `limit` (int): Number of items (default: 10, max: 50)

**Response:** Array of content objects

---

### Get Trending Content
**GET** `/content/trending`

Get trending content ordered by view count.

**Query Parameters:**
- `limit` (int): Number of items (default: 20, max: 100)

**Response:** Array of content objects

---

### Search Content
**GET** `/content/search`

Search for content by title.

**Query Parameters:**
- `q` (string, required): Search query (min: 1 char, max: 255 chars)
- `content_type` (string): Filter by type - movie, tv_show, anime, live_stream
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20, max: 100)

**Response:** Array of content objects

---

### Get Content Details
**GET** `/content/{content_id}`

Get detailed information about a specific content.

**Path Parameters:**
- `content_id` (int): Content ID

**Response:**
```json
{
  "id": 1,
  "title": "Movie Title",
  "slug": "movie-title",
  "description": "...",
  "content_type": "movie",
  "poster_url": "...",
  "background_url": "...",
  "trailer_url": "...",
  "rating": 8.5,
  "release_date": "2024-01-01T00:00:00",
  "duration_minutes": 120,
  "language": "en",
  "is_featured": true,
  "is_active": true,
  "view_count": 1000,
  "created_at": "2024-01-01T00:00:00",
  "genres": [
    {
      "id": 1,
      "name": "Action",
      "slug": "action"
    }
  ],
  "categories": [],
  "videos": [
    {
      "id": 1,
      "format": "hls",
      "quality_label": "1080p",
      "url": "https://...",
      "source_name": "VidCloud",
      "is_default": true
    }
  ],
  "subtitles": [
    {
      "id": 1,
      "language": "en",
      "language_name": "English",
      "url": "https://...",
      "format": "vtt",
      "is_default": true
    }
  ],
  "episodes": []
}
```

---

## Watchlist Endpoints

### Add to Watchlist
**POST** `/content/{content_id}/add-to-watchlist`

Add content to user's watchlist.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Added to watchlist"
}
```

---

### Remove from Watchlist
**DELETE** `/content/{content_id}/remove-from-watchlist`

Remove content from watchlist.

**Response:**
```json
{
  "message": "Removed from watchlist"
}
```

---

### Get Watchlist
**GET** `/content/user/watchlist`

Get user's watchlist.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** Array of content objects

---

## Watch History Endpoints

### Update Watch History
**POST** `/content/{content_id}/watch-history`

Update watch history for a content.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "duration_watched": 3600,
  "is_completed": false
}
```

**Response:**
```json
{
  "message": "Watch history updated"
}
```

---

### Get Continue Watching
**GET** `/content/user/continue-watching`

Get list of content to continue watching.

**Query Parameters:**
- `limit` (int): Number of items (default: 20, max: 100)

**Response:** Array of content objects

---

## Admin Endpoints

All admin endpoints require `role: admin` authentication.

### Get Users
**GET** `/admin/users`

List all users.

**Query Parameters:**
- `page` (int): Page number
- `limit` (int): Items per page
- `role` (string): Filter by role - admin, moderator, user

**Response:** Array of user objects

---

### Change User Role
**PATCH** `/admin/users/{user_id}/role`

Change a user's role.

**Request Body:**
```json
{
  "new_role": "admin"  // admin | moderator | user
}
```

**Response:**
```json
{
  "message": "User role changed to admin"
}
```

---

### Get Platform Statistics
**GET** `/admin/stats`

Get platform statistics.

**Response:**
```json
{
  "total_users": 150,
  "total_content": 500,
  "total_movies": 300,
  "total_tv_shows": 150,
  "total_anime": 50
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error description"
}
```

or

```json
{
  "success": false,
  "error": "Error type",
  "message": "Error description"
}
```

### Common Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Validation Error
- 429: Too Many Requests (Rate limit)
- 500: Internal Server Error

---

## Rate Limiting

The API implements rate limiting:
- Login: 5 requests/minute
- General API: 100 requests/minute

When rate limit is exceeded, you'll receive:
```
HTTP 429 Too Many Requests
Retry-After: 60
```

---

## Pagination

List responses support pagination:

```
GET /api/v1/content/movies?page=2&limit=20
```

Response includes all items in the page.

---

## Filtering & Sorting

### Search Filters
```
GET /api/v1/content/search?q=movie&content_type=movie&page=1
```

### Sorting
```
GET /api/v1/content/movies?sort_by=rating
```

Available sort options:
- `created_at`: Newest first
- `rating`: Highest rating first
- `view_count`: Most viewed first

---

## Examples

### Register and Login
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "myusername",
    "password": "securepass123"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

### Fetch Movies
```bash
curl -X GET "http://localhost:8000/api/v1/content/movies?page=1&limit=10"
```

### Search Content
```bash
curl -X GET "http://localhost:8000/api/v1/content/search?q=action"
```

### Get User Details
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/api/v1/docs`
- **ReDoc**: `http://localhost:8000/api/v1/redoc`

---

For more information, see [MAIN_README.md](../../MAIN_README.md)
