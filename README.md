# MovieBox API - Beginner Guide

Welcome! This guide will help you set up and use the MovieBox API project. We'll explain everything step-by-step, even if you've never used these tools before.

## 1. Project Overview

### What This Project Does
MovieBox API is a free tool that lets you:
- Search for movies and TV shows
- Get details about movies and TV shows
- Download or stream videos
- Get subtitles in different languages

It works with moviebox.ph, a website that has movies and TV shows.

### Technologies Used
- **Backend**: FastAPI (Python web server)
- **Frontend**: Website hosted on Cloudflare Pages
- **Hosting**: Render (for backend), Cloudflare (for frontend)

### How It Works (Simple Diagram)
```
Your Website (Cloudflare Pages)
    ↓
MovieBox API (Render)
    ↓
MovieBox.ph (Streaming Source)
```

Your website asks the API for movie info, the API gets it from moviebox.ph, and sends it back to your website.

## 2. Prerequisites (Very Important)

Before we start, you need to create some free accounts. Don't worry, they're all free!

### What is GitHub?
GitHub is like a cloud storage for code. You can upload your project there and share it.

- **Sign up**: Go to [github.com](https://github.com) and create a free account
- **What you'll do**: Upload this project to GitHub so Render and Cloudflare can use it

### What is Cloudflare Pages?
Cloudflare Pages is a free way to host websites. It's like putting your website on the internet for free.

- **Sign up**: Go to [pages.cloudflare.com](https://pages.cloudflare.com) and create a free account
- **What you'll do**: Host your website (frontend) here

### What is Render?
Render is a free way to run web apps. It's like a computer in the cloud that runs your API.

- **Sign up**: Go to [render.com](https://render.com) and create a free account
- **What you'll do**: Run your API (backend) here

### What is an API?
API stands for Application Programming Interface. It's like a messenger between your website and the movie data.

- Your website says: "Give me info about Naruto"
- API says: "Here's the info from moviebox.ph"

## 3. Folder Structure Explanation

This project has these main folders:

- `/app` → Backend code (FastAPI server)
- `/src/moviebox_api` → Python code for downloading movies
- `/cloudflare-worker` → Proxy to make API faster
- `/docs` → Extra help files
- `/tests` → Code to check if everything works

## 4. Step-by-Step Deployment Guide

### PART 1: Backend (Render)

Let's run the API on Render first.

1. **Go to Render**
   - Open [render.com](https://render.com) in your browser
   - Sign in with your account

2. **Click "New Web Service"**
   - Look for the blue "New" button
   - Click "Web Service"

3. **Connect Your GitHub Repo**
   - Click "Connect GitHub"
   - Allow Render to access your GitHub
   - Find this project (moviebox-api) and select it

4. **Set Up the Service**
   - **Name**: moviebox-api (or any name you like)
   - **Runtime**: Docker
   - **Dockerfile Path**: ./Dockerfile
   - **Port**: 8000
   - **Health Check Path**: /health

5. **Add Environment Variable**
   - Click "Environment"
   - Add:
     - Key: ENVIRONMENT
     - Value: production

6. **Enable Auto Deploy**
   - Check "Auto Deploy" so it updates when you change code

7. **Click Deploy**
   - Click the "Create Web Service" button
   - Wait 5-10 minutes for it to build
   - You'll get a URL like: https://moviebox-api.onrender.com

**Screenshot here**

That's it! Your API is now running.

### PART 2: Frontend (Cloudflare Pages)

Now let's host the website.

**Note**: This project doesn't include frontend code. You'll need to create a simple website that calls the API. Here's how to set it up:

1. **Go to Cloudflare Pages**
   - Open [pages.cloudflare.com](https://pages.cloudflare.com)
   - Sign in

2. **Click "Create Project"**
   - Click the "Create project" button

3. **Connect GitHub Repo**
   - Click "Connect to Git"
   - Choose your GitHub account
   - Select your frontend project (not this one)

4. **Set Build Settings**
   - **Build command**: npm run build
   - **Build output directory**: dist
   - **Root directory**: / (leave empty)

5. **Add Environment Variable**
   - Click "Environment variables"
   - Add:
     - Variable name: VITE_API_URL
     - Value: https://your-render-url.onrender.com

6. **Click Deploy**
   - Click "Save and Deploy"
   - Wait for it to build
   - You'll get a URL like: https://your-project.pages.dev

**Screenshot here**

## 5. API Usage (Simple Examples)

Your API is now ready! Here are simple examples of how to use it.

### Search for Movies/TV Shows
```
GET https://your-api-url.onrender.com/api/v1/search?q=naruto
```

This returns a list of movies/TV shows with "naruto" in the name.

### Get Movie Details
```
GET https://your-api-url.onrender.com/api/v1/details/{item_id}
```

Replace {item_id} with the ID from search results.

### Get TV Show Episodes
```
GET https://your-api-url.onrender.com/api/v1/episodes?page_url={series_url}
```

page_url is the web address of the TV show page.

### Stream a Movie
```
GET https://your-api-url.onrender.com/api/v1/stream/{item_id}
```

### Stream a TV Episode
```
GET https://your-api-url.onrender.com/api/v1/stream/episode/s1e2?page_url={series_url}
```

**What is page_url?**
- It's the web address of the movie/TV show on moviebox.ph
- Example: https://moviebox.ph/detail/naruto?id=123

**What is episode_id?**
- Format: s{season}e{episode}
- s1e1 = Season 1 Episode 1
- s2e5 = Season 2 Episode 5

## 6. Common Errors & Fixes (Very Important)

### ❌ Error: .venv not found
**What it means**: Cloudflare can't run Python code.
**Fix**: Don't deploy backend on Cloudflare. Use Render for backend only.

### ❌ Error: 404 stream not working
**What it means**: The page_url is wrong.
**Fix**: Make sure page_url is correct. Copy it from moviebox.ph.

### ❌ Error: CORS issue
**What it means**: Your website can't talk to the API.
**Fix**: Add CORS headers in backend. In app/main.py, add:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your website URL
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

### ❌ Error: Build failed on Render
**Fix**: Check the logs. Make sure Dockerfile is correct.

### ❌ Error: API returns error
**Fix**: Check the API URL. Make sure it's https://your-app.onrender.com

## 7. How Streaming Works (Simple Explanation)

### Movies
- Search for movie
- Get stream URL
- Play the video directly

### TV Shows
- Search for TV show
- Get episode list
- Choose episode (like s1e1)
- Get stream URL for that episode
- Play the video

**Important**: TV shows need episodes. Movies work directly.

## 8. Tips for Beginners

- **Don't deploy backend on Cloudflare**: Cloudflare Pages is for websites, not APIs
- **Always use correct page_url**: Copy it exactly from moviebox.ph
- **Test API first**: Use browser to check API URLs work
- **Start simple**: Try searching for one movie first
- **Check logs**: If something fails, look at Render/Cloudflare logs
- **Free limits**: Render gives 750 hours/month free

## 9. Screenshots (Placeholders)

**Render New Web Service**
[Add screenshot here]

**Cloudflare Create Project**
[Add screenshot here]

**API Response Example**
[Add screenshot here]

---

Made with ❤️ for beginners
